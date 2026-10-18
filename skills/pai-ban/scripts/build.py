#!/usr/bin/env python3
"""pai-ban / scripts/build.py — 书稿目录 → 期刊级 PDF（+ DOCX）

流水线（rules/design-spec.md §12，顺序不可乱）：

    1. 预处理   代码围栏归一化 → 图片改指矢量 PDF → 缺字形替换 → 裸 URL 尖括号化
    2. Lua 过滤 章标题拆分 → 表格列宽 → 代码标题/行号 → 图与题注
    3. pandoc   --pdf-engine=xelatex（本脚本只生成 .tex，见下）
    4. xelatex  ×2–3（目录/书签收敛）
    5. 验证     §11 硬门槛（交给 verify.py）
    6. 产物     PDF（主）+ DOCX（辅）

为什么第 3 步不直接用 `pandoc --pdf-engine=xelatex`：
    pandoc 只调一次引擎，第一遍里 \\tableofcontents 是空的（页码要靠
    .aux/.toc 回填）。实测单遍出的 PDF 目录只有标题没有条目。所以先出
    .tex，再自己跑 2–3 遍 xelatex。

用法
----
    python3 build.py <book-dir>                 # 编译整本书
    python3 build.py <book-dir> --chapters 0,2  # 只编译指定章（章号取自文件名）
    python3 build.py <book-dir> --preview       # 样章 + 页面 PNG（150dpi）
    python3 build.py <book-dir> --lang zh --title "…" --author "…"
    python3 build.py <book-dir> --no-docx --no-verify

退出码：0 成功；1 编译失败或 §11 硬门槛未通过；2 配置/环境错误。
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

# ---------------------------------------------------------------------------
# 环境
# ---------------------------------------------------------------------------
SKILL_ROOT = Path(__file__).resolve().parents[1]
ASSETS = SKILL_ROOT / "assets"
FILTERS = ASSETS / "filters"

XELATEX = "/Library/TeX/texbin/xelatex"
PANDOC = shutil.which("pandoc") or "pandoc"

#: 单次 xelatex 的墙钟上限（样章 <1min，整书几百页要几分钟；给足）
XELATEX_TIMEOUT = 1800
PANDOC_TIMEOUT = 1800

#: 版心（A5, 148×210, 内 18 / 外 15）→ 115×175mm，单位 pt
TEXTWIDTH_PT = 115 * 72 / 25.4      # ≈ 326.0
TEXTHEIGHT_PT = 175 * 72 / 25.4     # ≈ 496.1

# ---------------------------------------------------------------------------
# 默认配置（与 assets/pai-ban.toml 同构；配置缺项时用这里的值）
# ---------------------------------------------------------------------------
DEFAULTS: dict = {
    "book": {
        "title": "Untitled",
        "subtitle": "",
        "author": "",
        "date": "",
        "lang": "zh",
        "chapters_dir": ".",
        "chapter_glob": "chapter-*.md",
        "chapter_number_regex": r"chapter-(\d+)",
        "extra_files": [],
        "figures_dir": "figures",
        "assets_dir": "pai-ban-assets",
    },
    "layout": {
        "paper": "a5paper",
        "documentclass": "book",
        "fontsize": "11pt",
        "twoside": True,
        "inner": "18mm",
        "outer": "15mm",
        "top": "16mm",
        "bottom": "19mm",
        "headsep": "5mm",
        "footskip": "7mm",
        "headheight": "12pt",
    },
    "fonts": {
        "main": "Times New Roman",
        "mono": "Menlo",
        "cjk": "Songti SC",
        "head": "PingFang SC",
        "symbol": "Apple Symbols",
    },
    "output": {
        "pdf": "build/pai-ban/{lang}/{title}.pdf",
        "docx": "build/pai-ban/{lang}/{title}.docx",
        "workdir": "build/pai-ban/{lang}",
        "preview_dir": "typeset-sample",
    },
    "build": {
        "passes": 3,
        "dpi": 150,
        "docx": True,
        "verify": True,
    },
}

#: 语言相关默认值（config 里没写就取这里）
LANG_DEFAULTS = {
    "zh": {"toc_title": "目录", "parindent": "2em", "cjk": True},
    "en": {"toc_title": "Contents", "parindent": "1.5em", "cjk": True},
}


# ===========================================================================
# 配置
# ===========================================================================
def _deep_merge(base: dict, over: dict) -> dict:
    out = dict(base)
    for k, v in (over or {}).items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = _deep_merge(out[k], v)
        else:
            out[k] = v
    return out


def load_config(book: Path, explicit: str | None = None) -> dict:
    """优先 tomllib 读 pai-ban.toml；缺失时回退 JSON（pai-ban.json）。

    都不存在就用默认值（但仍要求书稿目录里有章节目录）。
    """
    cands = []
    if explicit:
        cands.append(book / explicit)
    else:
        cands += [book / "pai-ban.toml", book / "pai-ban.json"]
    cfg: dict = {}
    src = None
    for p in cands:
        if not p.exists():
            continue
        src = p
        if p.suffix == ".json":
            cfg = json.loads(p.read_text(encoding="utf-8"))
        else:
            try:
                import tomllib
            except ModuleNotFoundError:  # Python < 3.11
                raise SystemExit(
                    "[pai-ban] 需要 Python 3.11+ 的 tomllib 读 pai-ban.toml；"
                    "或改用 pai-ban.json")
            cfg = tomllib.loads(p.read_text(encoding="utf-8"))
        break
    merged = _deep_merge(DEFAULTS, cfg)
    merged["_config_path"] = str(src) if src else None
    return merged


# ===========================================================================
# 预处理（§12 第 1 步）
# ===========================================================================
#: ```python title="02.01_ollama_api" linenums="1"
#:   → ```python {title="02.01_ollama_api" linenums="1"}
#: 为什么必须归一化：pandoc 3.11 遇到 mkdocs 风格的围栏属性会把整块代码
#: 降级成 inline \texttt，代码里的 \n 与弯引号直接漏进 LaTeX →
#: "! Undefined control sequence"。归一化成 pandoc 原生属性语法后，
#: title / linenums 作为 CodeBlock 属性保留，交给 code-caption.lua。
FENCE_ATTR_RE = re.compile(r"^(`{3,})([A-Za-z0-9+#_.-]+)[ \t]+(\S.*?)[ \t]*$", re.M)
IMG_RE = re.compile(r"\]\((?P<dir>[^)/]*/)?(?P<sub>svg|pdf|png)/(?P<stem>[^)]+?)\.(?:svg|pdf|png)\)")
IMG_ALT_RE = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")
INLINE_CODE_RE = re.compile(r"(`[^`\n]*`)")

WARN = "\u26a0"          # ⚠ WARNING SIGN
VS16 = "\ufe0f"          # VARIATION SELECTOR-16（无字体有字形）
WARN_RAW = r"`\warn`{=latex}"

CJK_HAN = "\u3000-\u303f\u3400-\u4dbf\u4e00-\u9fff\uff00-\uffef"
BARE_URL_RE = re.compile(
    r'(?<![<\(\"\[/])(https?://[^\s<>\[\]\"`' + CJK_HAN + r']+)')
URL_TRAILING = ".,;:!?，。；：、）)】」』"


class Stats(dict):
    def bump(self, key: str, n: int = 1) -> None:
        self[key] = self.get(key, 0) + n


def normalize_fences(text: str, stats: Stats) -> str:
    """mkdocs 围栏属性 → pandoc 原生属性（保留 title / linenums 语义）。"""

    def repl(m: re.Match) -> str:
        fence, lang, attrs = m.group(1), m.group(2), m.group(3)
        # 已经是 pandoc 语法（{...}）就原样返回
        if attrs.startswith("{"):
            return m.group(0)
        stats.bump("fence_normalized")
        return f"{fence}{lang} {{{attrs}}}"

    return FENCE_ATTR_RE.sub(repl, text)


def _rewrite_images(text: str, target: str, stats: Stats) -> str:
    ext = "pdf" if target == "latex" else "png"

    def repl(m: re.Match) -> str:
        stem = m.group("stem")
        if m.group("sub") != ext:
            stats.bump(f"image_rewritten_to_{ext}")
        return f"](figures/{ext}/{stem}.{ext})"

    return IMG_RE.sub(repl, text)


def strip_figure_labels(text: str, stats: Stats) -> str:
    r"""清掉"alt 文本就是文件名"的图片 alt。

    源文 `![fig05-transformer-architecture](figures/svg/....svg)` 的 alt 是
    文件名而非题注；pandoc 的 implicit_figures 会拿它当 \caption，产生
    "Figure N: 文件名" 伪题注，并且把图变成浮动体（图片会跑页顶/页底，
    与源文里紧跟其后的 `*图5.1：…*` 说明分离）。
    真正的题注是那个斜体段落，由 figure-caption.lua 接管。
    """
    def repl(m: re.Match) -> str:
        alt, src = m.group(1), m.group(2)
        if alt and alt == Path(src).stem:
            stats.bump("figure_label_stripped")
            return f"![]({src})"
        return m.group(0)

    return IMG_ALT_RE.sub(repl, text)


def latex_symbol_fixups(text: str, stats: Stats) -> str:
    """LaTeX 目标专用的缺字形处理（代码块与行内代码之外）。

    * U+FE0F（变体选择符）：没有任何本地字体有字形，XeTeX 每次都报
      Missing character；删掉不影响可见内容。
    * ⚠ (U+26A0)：Times / Songti 都没有字形 → preamble 里的 \\warn
      （Apple Symbols）。
    """
    out_lines = []
    in_fence = False
    for line in text.split("\n"):
        if line.startswith("```"):
            in_fence = not in_fence
            out_lines.append(line)
            continue
        if in_fence:
            if VS16 in line:
                stats.bump("vs16_removed")
                line = line.replace(VS16, "")
            out_lines.append(line)
            continue
        if VS16 in line:
            stats.bump("vs16_removed")
            line = line.replace(VS16, "")
        if WARN in line:
            parts = INLINE_CODE_RE.split(line)
            for i, seg in enumerate(parts):
                if i % 2 == 0 and WARN in seg:
                    stats.bump("warn_replaced", seg.count(WARN))
                    parts[i] = seg.replace(WARN, WARN_RAW)
            line = "".join(parts)
        out_lines.append(line)
    return "\n".join(out_lines)


def autolink_bare_urls(text: str, stats: Stats) -> str:
    """裸 URL → markdown autolink <URL>（仅 LaTeX 目标）。

    否则长 URL 在 LaTeX 里是不能断行的普通文字，直接冲出纸面。
    """
    out_lines = []
    in_fence = False
    for line in text.split("\n"):
        if line.startswith("```"):
            in_fence = not in_fence
            out_lines.append(line)
            continue
        if in_fence or "http" not in line:
            out_lines.append(line)
            continue
        parts = INLINE_CODE_RE.split(line)
        for i, seg in enumerate(parts):
            if i % 2 == 0 and "http" in seg:
                parts[i] = _wrap_urls(seg, stats)
        out_lines.append("".join(parts))
    return "\n".join(out_lines)


def _wrap_urls(seg: str, stats: Stats) -> str:
    def repl(m: re.Match) -> str:
        url = m.group(1)
        trailing = ""
        while url and url[-1] in URL_TRAILING:
            trailing = url[-1] + trailing
            url = url[:-1]
        if not url:
            return m.group(0)
        stats.bump("url_autolinked")
        return f"<{url}>{trailing}"

    return BARE_URL_RE.sub(repl, seg)


def preprocess(text: str, target: str, stats: Stats) -> str:
    text = normalize_fences(text, stats)
    text = _rewrite_images(text, target, stats)
    text = strip_figure_labels(text, stats)
    if target == "latex":
        text = latex_symbol_fixups(text, stats)
        text = autolink_bare_urls(text, stats)
    return text


# ===========================================================================
# 章节清单
# ===========================================================================
def chapter_files(cfg: dict, only: list[int] | None, preview: bool) -> list[Path]:
    src = Path(cfg["book"]["chapters_dir"])
    if not src.is_absolute():
        src = Path(cfg["_book"]) / src
    files = sorted(src.glob(cfg["book"]["chapter_glob"]))
    if not files:
        raise SystemExit(f"[pai-ban] {src} 里没有匹配 "
                         f"{cfg['book']['chapter_glob']} 的文件")

    def num_of(p: Path) -> int | None:
        m = re.search(cfg["book"]["chapter_number_regex"], p.name)
        return int(m.group(1)) if m else None

    if only is not None:
        keep = set(only)
        picked = [p for p in files if num_of(p) in keep]
        missing = keep - {num_of(p) for p in picked}
        if missing:
            raise SystemExit(f"[pai-ban] 找不到章号 {sorted(missing)}")
        return picked

    if preview and len(files) > 3:
        # 样章：跳过无编号前言，取前 3 个编号章
        numbered = [p for p in files if num_of(p) is not None]
        return numbered[:3]

    extras = [Path(cfg["_book"]) / cfg["book"]["chapters_dir"] / e
              for e in cfg["book"]["extra_files"]]
    return files + [e for e in extras if e.exists()]


# ===========================================================================
# 执行
# ===========================================================================
def run(cmd: list[str], cwd: Path, log: Path, timeout: int) -> tuple[int, float]:
    env = dict(os.environ)
    env["PATH"] = f"/Library/TeX/texbin:{env.get('PATH', '')}"
    t0 = time.time()
    with log.open("w", encoding="utf-8") as fh:
        fh.write("$ cd %s && %s\n\n" % (cwd, " ".join(str(c) for c in cmd)))
        fh.flush()
        try:
            proc = subprocess.run([str(c) for c in cmd], cwd=cwd, stdout=fh,
                                  stderr=subprocess.STDOUT, timeout=timeout,
                                  env=env)
            rc = proc.returncode
        except subprocess.TimeoutExpired:
            fh.write(f"\n*** TIMEOUT after {timeout}s ***\n")
            rc = -1
    dt = time.time() - t0
    with log.open("a", encoding="utf-8") as fh:
        fh.write(f"\n*** exit={rc} elapsed={dt:.1f}s ***\n")
    return rc, dt


def log_stats(log: Path) -> dict:
    txt = log.read_text(encoding="utf-8", errors="replace")
    missing = re.findall(r"Missing character: There is no (\S+) \(U\+([0-9A-Fa-f]+)\)", txt)
    overfull = re.findall(r"Overfull \\hbox \(([\d.]+)pt too wide\)", txt)
    return {
        "missing_character": len(missing),
        "missing_chars": sorted({f"U+{cp} {ch}" for ch, cp in missing}),
        "latex_error": len(re.findall(r"^! ", txt, re.M)),
        "undefined_cs": len(re.findall(r"Undefined control sequence", txt)),
        "overfull_hbox": len(overfull),
        "overfull_max_pt": max((float(v) for v in overfull), default=0.0),
        "rerun": "Rerun to get" in txt or "Rerun LaTeX" in txt,
        "emergency_stop": "Emergency stop" in txt,
        "font_warning": len(re.findall(r"Font shape .* undefined", txt)),
    }


# ===========================================================================
# preamble 装配
# ===========================================================================
def write_preamble(workdir: Path, cfg: dict, assets: Path) -> Path:
    src = assets / "preamble.tex"
    if not src.exists():
        raise SystemExit(f"[pai-ban] 缺少 {src}")
    text = src.read_text(encoding="utf-8")
    lang = cfg["_lang"]
    ldef = LANG_DEFAULTS[lang]
    subs = {
        "@BOOKTITLE@": cfg["book"]["title"],
        "@TITLE@": cfg["book"]["title"],
        "@SUBTITLE@": cfg["book"]["subtitle"],
        "@AUTHOR@": cfg["book"]["author"],
        "@DATE@": cfg["book"]["date"],
        "@MAINFONT@": cfg["fonts"]["main"],
        "@MONOFONT@": cfg["fonts"]["mono"],
        "@CJKFONT@": cfg["fonts"]["cjk"],
        "@HEADFONT@": cfg["fonts"]["head"],
        "@SYMBOLFONT@": cfg["fonts"]["symbol"],
        "@TOCNAME@": cfg["_toc_title"],
        "@PARINDENT@": ldef["parindent"],
        "@BOOKLANG@": lang,
        # 目录条目的章号样式：zh = 「第2章」；en = 「Chapter 2:」
        "@CHAPNUMBEFORE@": "第" if lang == "zh" else "Chapter ",
        "@CHAPNUMAFTER@": "章" if lang == "zh" else ":",
    }
    for k, v in subs.items():
        text = text.replace(k, str(v))
    leftover = re.findall(r"@[A-Z]{3,}@", text)
    if leftover:
        raise SystemExit(f"[pai-ban] preamble.tex 还有未替换的占位符：{sorted(set(leftover))}")
    dest = workdir / "preamble.tex"
    dest.write_text(text, encoding="utf-8")
    return dest


# ===========================================================================
# 构建
# ===========================================================================
def pandoc_common(cfg: dict) -> list[str]:
    args = [
        "--from=markdown",
        "-M", f"title={cfg['book']['title']}",
        "-M", f"author={cfg['book']['author']}",
        "-M", f"date={cfg['book']['date']}",
        "-M", f"toc-title={cfg['_toc_title']}",
        "--toc",
        "--toc-depth=2",           # §5 只收 chapter + section
    ]
    if cfg["book"]["subtitle"]:
        args += ["-M", f"subtitle={cfg['book']['subtitle']}"]
    return args


def pdf_args(cfg: dict) -> list[str]:
    lay, fonts = cfg["layout"], cfg["fonts"]
    geom = ",".join([
        lay["paper"],
        f"inner={lay['inner']}", f"outer={lay['outer']}",
        f"top={lay['top']}", f"bottom={lay['bottom']}",
        f"headsep={lay['headsep']}", f"footskip={lay['footskip']}",
        f"headheight={lay['headheight']}",
        "nomarginpar",
    ])
    return [
        "--syntax-highlighting=idiomatic",   # §12：listings 语法高亮
        "-V", f"documentclass={lay['documentclass']}",
        "-V", f"fontsize={lay['fontsize']}",
        "-V", f"geometry={geom}",
        "-V", f"mainfont={fonts['main']}",
        "-V", f"monofont={fonts['mono']}",
        "-V", f"CJKmainfont={fonts['cjk']}",
    ] + (["-V", "classoption=twoside"] if lay["twoside"] else [])


def patch_longtable_continuation(tex_path: Path, lang: str = "zh") -> int:
    """给每个 longtable 补「续页顶部（续）+ 重复表头」（spec §8）。

    pandoc 生成的形态是固定的：

        \\toprule\\noalign{}
        <表头行> \\\\
        \\midrule\\noalign{}
        \\endhead
        \\bottomrule\\noalign{}
        \\endlastfoot
        <表体>

    longtable 只有在同时存在 \\endfirsthead 时才能区分首末页表头，所以把
    原来的 \\endhead 改成 \\endfirsthead，再复制一份表头作为 \\endhead，
    并在它前面加一行右对齐的「（续）」。短表不会走到续页，这个改动无害。

    返回补过的表格数（写进构建日志，便于核对 filter 是否生效）。
    """
    tex = tex_path.read_text(encoding="utf-8")
    head_re = re.compile(
        r"(\\toprule\\noalign\{\}\n)(.*?)(\\midrule\\noalign\{\}\n\\endhead)", re.S)
    count = 0

    def repl(m: re.Match) -> str:
        nonlocal count
        block = m.group(0)
        hm = head_re.search(block)
        if not hm:
            return block
        header = hm.group(2)
        # 列数：表头行里未转义的 & 数 + 1（\& 是单元格里的文字）
        ncols = header.replace("\\&", "").count("&") + 1
        # 续页标记按语言给：中文「（续）」/ 英文「continued」
        # （英文版写死中文会在英文书里印出「（续）」——实测 24 处）
        marker = "continued" if lang == "en" else "（续）"
        cont = ("\\multicolumn{%d}{@{}r@{}}{\\fontsize{8.5}{10}\\selectfont"
                "\\color{muted}%s}\\\\" % (ncols, marker))
        new = (hm.group(1) + header + hm.group(3).replace("\\endhead", "\\endfirsthead")
               + "\n" + cont + "\n"
               + hm.group(1) + header + hm.group(3))
        count += 1
        return block.replace(hm.group(0), new)

    tex = re.sub(r"\\begin\{longtable\}.*?\\end\{longtable\}", repl, tex, flags=re.S)
    tex_path.write_text(tex, encoding="utf-8")
    return count


def build_pdf(ctx: dict) -> dict:
    cfg, workdir = ctx["cfg"], ctx["workdir"]
    pdf_filters = [f for f in ("break-long-tokens.lua", "chapter-split.lua",
                               "table-widths.lua",
                               "code-caption.lua", "table-caption.lua",
                               "figure-caption.lua")
                   if (ctx["assets"] / "filters" / f).exists()]
    cmd = [PANDOC, *ctx["md_names"], "-s", "-o", "book.tex",
           "-H", "preamble.tex", *pandoc_common(cfg), *pdf_args(cfg)]
    for f in pdf_filters:
        cmd += ["--lua-filter", str(ctx["assets"] / "filters" / f)]
    log_pandoc = workdir / "pandoc.log"
    rc, dt = run(cmd, workdir, log_pandoc, PANDOC_TIMEOUT)
    tex = workdir / "book.tex"
    if rc != 0 or not tex.exists():
        return {"ok": False, "stage": "pandoc", "log": log_pandoc, "elapsed": f"{dt:.1f}s"}

    # pandoc 的 longtable 只有一个 \endhead，跨页时续页直接重复表头，
    # 没有「（续）」标记（spec §8）。这里在 LaTeX 层补一个：
    # 第一页走 \endfirsthead，续页走「（续）+ 表头」的 \endhead。
    n_cont = patch_longtable_continuation(tex, cfg["_lang"])

    total, runs = 0.0, 0
    stats: dict = {}
    logs: list[Path] = []
    for i in range(max(2, cfg["build"]["passes"])):
        log_i = workdir / f"xelatex-{i + 1}.log"
        logs.append(log_i)
        rc, dt = run([XELATEX, "-interaction=nonstopmode", "-file-line-error",
                      "-halt-on-error", "book.tex"], workdir, log_i, XELATEX_TIMEOUT)
        total += dt
        runs += 1
        stats = log_stats(log_i)
        if rc != 0 or not (workdir / "book.pdf").exists():
            return {"ok": False, "stage": f"xelatex pass {i + 1}", "log": log_i,
                    "elapsed": f"{total:.1f}s", "runs": runs, "tex": tex,
                    "tex_stats": stats}
        if i >= 1 and not stats["rerun"]:
            break
    return {"ok": True, "stage": "done", "log": logs[-1], "logs": logs,
            "longtable_cont": n_cont,
            "elapsed": f"{total:.1f}s", "runs": runs, "tex": tex,
            "pdf": workdir / "book.pdf", "tex_stats": stats}


def build_docx(ctx: dict) -> dict:
    cfg, workdir = ctx["cfg"], ctx["workdir"] / "docx"
    workdir.mkdir(parents=True, exist_ok=True)
    for name in ctx["md_names"]:
        shutil.copy2(ctx["workdir"] / name, workdir / name)
    ref = ctx["assets"] / "reference.docx"
    cmd = [PANDOC, *ctx["md_names"], "-o", "book.docx",
           "--toc-depth=2", *pandoc_common(cfg)]
    # 图片路径是相对 chapters_dir 的 figures/png/…，而本函数的 pandoc 工作目录
    # 是 <workdir>/src-docx/docx，既没有 figures 软链也不在其下；不给
    # --resource-path 时 pandoc 全部 "Could not fetch resource"，
    # 图退化成 alt 文本（实测 word/media/ = 0、docx 从 5.9MB 掉到 0.3MB）。
    res_path = Path(cfg["book"]["chapters_dir"])
    if not res_path.is_absolute():
        res_path = Path(cfg["_book"]) / res_path
    cmd += ["--resource-path", str(res_path)]
    if ref.exists():
        cmd.append(f"--reference-doc={ref}")
    tw = ctx["assets"] / "filters" / "table-widths.lua"
    if tw.exists():
        cmd += ["--lua-filter", str(tw)]
    log = ctx["workdir"] / "pandoc-docx.log"
    rc, dt = run(cmd, workdir, log, PANDOC_TIMEOUT)
    out = workdir / "book.docx"
    return {"ok": rc == 0 and out.exists(), "log": log, "docx": out,
            "elapsed": f"{dt:.1f}s"}


# ===========================================================================
# 图可用性策略（§9）：裁边 → 加宽 → 旋转
# ===========================================================================
def figure_plan(md_files: list[Path], src_dir: Path, workdir: Path) -> dict:
    """量图 + 判放置 + 写 figure-fit.tex / figure-fit.json。

    量与判都在 scripts/figure_fit.py（同一份代码给 verify.py 复核），这里
    只负责调用与落盘。返回的 dict 直接进 manifest。
    """
    sys.path.insert(0, str(SKILL_ROOT / "scripts"))
    import figure_fit  # noqa: PLC0415  — 同目录模块

    refs = figure_fit.collect(md_files)
    man = figure_fit.build_manifest(refs, src_dir,
                                    textwidth_pt=TEXTWIDTH_PT,
                                    textheight_pt=TEXTHEIGHT_PT)
    n = figure_fit.write_tex(man, workdir / "figure-fit.tex")
    (workdir / "figure-fit.json").write_text(
        json.dumps(man, ensure_ascii=False, indent=2), encoding="utf-8")
    man["_tex_rows"] = n
    return man


# ===========================================================================
# PNG 渲染
# ===========================================================================
def render_pngs(pdf: Path, outdir: Path, dpi: int = 150,
                max_pages: int | None = None) -> list[Path]:
    import pymupdf
    outdir.mkdir(parents=True, exist_ok=True)
    doc = pymupdf.open(pdf)
    paths = []
    n = doc.page_count if max_pages is None else min(max_pages, doc.page_count)
    for i in range(n):
        png = outdir / f"page-{i + 1:03d}.png"
        pix = doc[i].get_pixmap(dpi=dpi)
        pix.save(png)
        paths.append(png)
    doc.close()
    return paths


# ===========================================================================
# main
# ===========================================================================
def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="pai-ban 排版构建")
    ap.add_argument("book", help="书稿目录")
    ap.add_argument("--config", default=None, help="配置文件名（默认 pai-ban.toml）")
    ap.add_argument("--lang", default=None, choices=["zh", "en"])
    ap.add_argument("--title", default=None)
    ap.add_argument("--author", default=None)
    ap.add_argument("--chapters", default=None,
                    help="只编译指定章号，逗号分隔，例：0,2,14")
    ap.add_argument("--preview", action="store_true",
                    help="样章模式：产物写进 <book>/typeset-sample/ 并渲染页面 PNG")
    ap.add_argument("--dpi", type=int, default=None)
    ap.add_argument("--no-docx", action="store_true")
    ap.add_argument("--no-verify", action="store_true")
    args = ap.parse_args(argv)

    book = Path(args.book).resolve()
    if not book.is_dir():
        print(f"[pai-ban] 不是目录：{book}", file=sys.stderr)
        return 2

    cfg = load_config(book, args.config)
    cfg["_book"] = str(book)
    if args.lang:
        cfg["book"]["lang"] = args.lang
    cfg["_lang"] = cfg["book"]["lang"]
    cfg["_toc_title"] = cfg["book"].get("toc_title") or LANG_DEFAULTS[cfg["_lang"]]["toc_title"]
    # Lua 过滤器（table-caption / figure-caption）从这里取语言：pandoc 3.11 的
    # 过滤器遍历自底向上（Blocks 先于 Meta），元数据在 Blocks 里读不到，只能走环境变量。
    os.environ["PAIBAN_LANG"] = cfg["_lang"]
    if args.title:
        cfg["book"]["title"] = args.title
    if args.author:
        cfg["book"]["author"] = args.author
    if args.dpi:
        cfg["build"]["dpi"] = args.dpi

    # 资源目录：优先书稿目录里的副本（init.py 生成），否则用技能自带
    local_assets = book / cfg["book"].get("assets_dir", "pai-ban-assets")
    assets = local_assets if (local_assets / "preamble.tex").exists() else ASSETS
    if not (assets / "preamble.tex").exists():
        print(f"[pai-ban] 找不到 preamble.tex（{assets}）", file=sys.stderr)
        return 2

    only = [int(x) for x in args.chapters.split(",")] if args.chapters else None
    files = chapter_files(cfg, only, args.preview)
    src_dir = Path(cfg["book"]["chapters_dir"])
    if not src_dir.is_absolute():
        src_dir = book / src_dir

    lang = cfg["_lang"]
    workdir = book / cfg["output"]["workdir"].format(lang=lang, title=slug(cfg["book"]["title"]))
    if workdir.exists():
        shutil.rmtree(workdir)
    workdir.mkdir(parents=True, exist_ok=True)
    # 图片软链：不改源目录、不复制几十张图
    fig_src = src_dir / cfg["book"]["figures_dir"]
    if fig_src.exists():
        os.symlink(fig_src.resolve(), workdir / "figures")
    else:
        print(f"[pai-ban] 警告：找不到图片目录 {fig_src}", file=sys.stderr)

    stats = Stats()
    md_names = []
    for i, src in enumerate(files):
        target = "latex"
        text = preprocess(src.read_text(encoding="utf-8"), target, stats)
        name = f"{i:02d}-{src.name}"
        (workdir / name).write_text(text, encoding="utf-8")
        md_names.append(name)

    write_preamble(workdir, cfg, assets)

    # 图可用性策略（§9）：量图 → 判三级放置 → 写 figure-fit.tex（preamble 查表执行）
    fig_man = figure_plan([workdir / n for n in md_names], src_dir, workdir)
    print(f"[pai-ban] 图 {fig_man['counts']['figures']} 张："
          + " / ".join(f"{m} {n}" for m, n in fig_man["counts"]["by_placement"].items())
          + f"；达标 {fig_man['counts']['meets_target']}/{fig_man['counts']['figures']}"
          + f"；图内字号 min {fig_man['distribution']['min_pt']}pt"
          f" / 中位 {fig_man['distribution']['median_pt']}pt"
          f" / max {fig_man['distribution']['max_pt']}pt")
    for f in fig_man["figures"]:
        if f.get("must_redraw"):
            print(f"[pai-ban] 警告：图内字号最小的那张放不进 A5 版心 "
                  f"{f['path']} → {f['effective_pt']}pt，必须重画源图（§9）",
                  file=sys.stderr)

    # docx 侧用 png 图，重新生成一份
    docx_ctx = {"cfg": cfg, "assets": assets, "workdir": workdir, "md_names": []}
    docx_dir = workdir / "src-docx"
    docx_dir.mkdir(exist_ok=True)
    for i, src in enumerate(files):
        text = preprocess(src.read_text(encoding="utf-8"), "docx", stats)
        name = f"{i:02d}-{src.name}"
        (docx_dir / name).write_text(text, encoding="utf-8")
        docx_ctx["md_names"].append(name)
    docx_ctx["workdir"] = docx_dir

    print(f"[pai-ban] {cfg['book']['title']}  lang={lang}  "
          f"章节 {len(files)} 个 → {workdir}")
    print(f"          配置：{cfg['_config_path'] or '（默认值）'}")

    ctx = {"cfg": cfg, "assets": assets, "workdir": workdir, "md_names": md_names}
    print("[pai-ban] pandoc → book.tex → xelatex ×2–3 …")
    res = build_pdf(ctx)
    if not res["ok"]:
        print(f"[pai-ban] 失败于 {res['stage']}，日志：{res['log']}", file=sys.stderr)
        return 1
    ts = res["tex_stats"]
    print(f"[pai-ban] PDF OK  {res['elapsed']}  passes={res['runs']}  "
          f"missing={ts['missing_character']}  errors={ts['latex_error']}  "
          f"overfull={ts['overfull_hbox']} (max {ts['overfull_max_pt']}pt)  "
          f"longtable续={res.get('longtable_cont', 0)}")

    docx_res = {"ok": False}
    if cfg["build"]["docx"] and not args.no_docx:
        print("[pai-ban] docx …")
        docx_res = build_docx(docx_ctx)
        print(f"[pai-ban] DOCX {'OK' if docx_res['ok'] else 'FAIL'} {docx_res['elapsed']}")

    # ---- 产物落地 ----
    import pymupdf
    pdf = res["pdf"]
    doc = pymupdf.open(pdf)
    pages = doc.page_count
    doc.close()

    if args.preview:
        outdir = book / cfg["output"]["preview_dir"]
        outdir.mkdir(parents=True, exist_ok=True)
        final_pdf = outdir / f"{lang}-sample.pdf"
        shutil.copy2(pdf, final_pdf)
        pngs = render_pngs(final_pdf, outdir / "pages", cfg["build"]["dpi"])
        print(f"[pai-ban] 页面 PNG：{len(pngs)} 张 → {outdir / 'pages'}")
    else:
        final_pdf = book / cfg["output"]["pdf"].format(
            lang=lang, title=slug(cfg["book"]["title"]))
        final_pdf.parent.mkdir(parents=True, exist_ok=True)
        if final_pdf.resolve() != pdf.resolve():
            shutil.copy2(pdf, final_pdf)
        pngs = []

    final_docx = None
    if docx_res.get("ok"):
        if args.preview:
            final_docx = book / cfg["output"]["preview_dir"] / f"{lang}-sample.docx"
        else:
            final_docx = book / cfg["output"]["docx"].format(
                lang=lang, title=slug(cfg["book"]["title"]))
        final_docx.parent.mkdir(parents=True, exist_ok=True)
        if final_docx.resolve() != docx_res["docx"].resolve():
            shutil.copy2(docx_res["docx"], final_docx)

    # ---- manifest（verify.py 的输入）----
    manifest = {
        "pdf": str(final_pdf),
        "workdir": str(workdir),
        "tex": str(res["tex"]),
        "log": str(res["log"]),
        "logs": [str(p) for p in res.get("logs", [])],
        "lang": lang,
        "title": cfg["book"]["title"],
        "pages": pages,
        "preview": bool(args.preview),
        "chapters": [p.name for p in files],
        "source_dir": str(src_dir),
        "tex_stats": ts,
        "longtable_continuation": res.get("longtable_cont", 0),
        "figures": fig_man["figures"],
        "figure_policy": fig_man["policy"],
        "figure_counts": fig_man["counts"],
        "figure_distribution": fig_man["distribution"],
        "figure_must_redraw": fig_man["must_redraw"],
        "figure_fit": str(workdir / "figure-fit.json"),
        "docx": str(final_docx) if final_docx else None,
        "pngs": [str(p) for p in pngs],
        "stats": dict(stats),
        "layout": {
            "textwidth_pt": round(TEXTWIDTH_PT, 2),
            "textheight_pt": round(TEXTHEIGHT_PT, 2),
            "inner_mm": cfg["layout"]["inner"],
            "outer_mm": cfg["layout"]["outer"],
            "top_mm": cfg["layout"]["top"],
            "bottom_mm": cfg["layout"]["bottom"],
        },
    }
    mpath = final_pdf.with_suffix(".manifest.json")
    mpath.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    # 图清单单独落一份（审稿/复核用；verify.py 也读同一份）
    fig_json = final_pdf.with_name(final_pdf.stem + ".figure-fit.json")
    shutil.copy2(workdir / "figure-fit.json", fig_json)
    print(f"[pai-ban] 产物：{final_pdf}（{pages} 页）")
    if final_docx:
        print(f"[pai-ban] 辅产物：{final_docx}")

    if cfg["build"]["verify"] and not args.no_verify:
        sys.path.insert(0, str(SKILL_ROOT / "scripts"))
        import verify as verify_mod
        # verify.main 返回的是**退出码**（0 = 通过），别拿它当布尔用：
        # 0 是 falsy，写成 `0 if ok else 1` 会让通过的构建反而退出 1。
        rc = verify_mod.main([str(final_pdf), "--manifest", str(mpath)])
        return 0 if rc == 0 else 1
    return 0


def slug(s: str) -> str:
    s = re.sub(r"[\\/:*?\"<>|\s]+", "-", s).strip("-")
    return s or "book"


if __name__ == "__main__":
    sys.exit(main())
