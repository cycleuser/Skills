#!/usr/bin/env python3
"""pai-ban / scripts/verify.py — §11 硬门槛验收

输入是 build.py 写出的 manifest（`<pdf>.manifest.json`），内容包括 PDF 路径、
生成的 book.tex、xelatex 日志、预处理后的 md、图内字号报告与版心尺寸。
本脚本只用 pymupdf 读 PDF（本机没有 pdfinfo/pdftotext/pdffonts），
不依赖任何外部二进制。

逐条对应 rules/design-spec.md §11：

  | 约束             | 阈值                | 检查方式                          |
  |------------------|---------------------|-----------------------------------|
  | 内容越出纸边     | 0 页                | 逐页 blocks/drawings 最大 x1      |
  | 内容越出版心     | ≤6pt 且 ≤5 页       | x1 ≤ 版心右界 + 6pt               |
  | 内容越出订口     | 0 页                | x0 ≥ 左界 − 3pt（§1 左边界）       |
  | 缺失字形         | 0                   | xelatex 日志 Missing character    |
  | LaTeX 错误       | 0                   | 日志 ^! 计数                      |
  | 重复编号         | 0                   | PDF 正文「第N章 第N章」           |
  | 图数一致         | 源文 = PDF          | 源文图片引用 vs \\paibaninclude   |
  | 表数一致         | 源文 = PDF          | md 表格 vs longtable              |
  | 目录条目         | = 章数 + 节数       | PDF outline vs tex 里的章/节命令  |

另加三条规格内但不在 §11 表里的：

  * §1     左边界：x0 ≥ 订口(奇)/外白边(偶) − 3pt（12 页引文竖线 + 代码行号
           挂出版心就是这条抓出来的）
  * §7/§8  Overfull \\hbox：>1pt 的必须为 0（代码折行、表格列宽的直接指标）
  * §9     图内文字有效字号：报告最差一张（advisory，不判失败，理由见下）

为什么图内字号是 advisory：既有 figure PDF 的画布 600–645pt、内部 5.25–6.75pt，
缩到 326pt 版心后有效字号只有 3–4pt —— 这是**源图本身**的问题，重画才能解决。
构建脚本能做的已经做了（不放大、限宽限高），把它判成构建失败只会让所有章节
都红，所以按 §9 的要求"报告最差一张"，由人决定是否重画。

页边距判定用「奇偶页各自的版心右界」：recto = 纸宽 − 外白边，verso = 纸宽 −
内白边。若 PDF 第一页是 verso（某些模板会），两种约定取违反页数少的那个，
并在输出里注明用的是哪一种。

用法
----
    python3 verify.py <book.pdf> [--manifest <manifest.json>]
    python3 verify.py <book.pdf> --json out.json --quiet

退出码：0 全部硬门槛通过；1 有门槛未通过；2 输入/环境错误。
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

try:
    import pymupdf
except ModuleNotFoundError:  # pragma: no cover - 环境问题，不算验收失败
    print("[verify] 需要 pymupdf（python3 -m pip install pymupdf）", file=sys.stderr)
    sys.exit(2)

#: §1 纸边安全余量：任何内容不得超过 纸宽 − 3pt
PAPER_EDGE_TOL_PT = 3.0
#: §11 版心越界容差与页数上限
TYPEAREA_TOL_PT = 6.0
TYPEAREA_MAX_PAGES = 5
#: §1 左边界容差：内容左缘 ≥ 订口(奇)/外白边(偶) − 3pt
GUTTER_TOL_PT = 3.0
#: §7/§8 Overfull：亚磅级（<1pt）不判失败，>=1pt 必须为 0
OVERFULL_TOL_PT = 1.0
#: §9 图内文字有效字号：inline/wide 的下限与 rotated 的目标
FIGURE_MIN_PT = 4.5
FIGURE_ROTATED_PT = 5.5

MM2PT = 72.0 / 25.4


def wide_policy(man: dict) -> dict:
    """§9 wide 放置的几何许可（由 build.py 从 figure_fit.py 写进 manifest）。

    wide = 125mm 宽，比 115mm 版心宽 10mm → 两侧各侵入白边 5mm（14.17pt），
    但仍须距纸边 ≥ 10mm。缺配置时按 §9 默认值，保证老 manifest 也能验收。
    """
    p = man.get("figure_policy") or {}
    overhang = p.get("wide_overhang_pt")
    if overhang is None:
        overhang = 5.0 * MM2PT
    min_paper_mm = p.get("wide_min_paper_mm")
    if min_paper_mm is None:
        min_paper_mm = 10.0
    return {"overhang_pt": float(overhang), "min_paper_pt": float(min_paper_mm) * MM2PT}


# ---------------------------------------------------------------------------
# 读输入
# ---------------------------------------------------------------------------
def load_manifest(pdf: Path, manifest: Path | None) -> dict:
    path = manifest or pdf.with_suffix(".manifest.json")
    if not path.exists():
        raise FileNotFoundError(f"找不到 manifest：{path}（先跑 build.py，别用 --no-verify 以外的方式跳过）")
    data = json.loads(path.read_text(encoding="utf-8"))
    data["_manifest_path"] = str(path)
    return data


def layout_limits(man: dict, page_w: float) -> tuple[float, float]:
    """返回 (recto 右界, verso 右界)，单位 pt。

    recto 右界 = 纸宽 − 外白边；verso 右界 = 纸宽 − 内白边。
    配置缺项时按规格默认：内 18mm / 外 15mm。
    """
    lay = man.get("layout") or {}
    inner = _mm(lay.get("inner_mm"), 18.0)
    outer = _mm(lay.get("outer_mm"), 15.0)
    return page_w - outer * MM2PT, page_w - inner * MM2PT


def left_limits(man: dict, page_w: float) -> tuple[float, float]:
    """返回 (recto 左界, verso 左界)，单位 pt —— §1「左边界 ≥ 18mm − 3pt（奇数页）」。

    双面镜像：recto 的左缘就是订口(内白边)，verso 的左缘是外白边。
    """
    lay = man.get("layout") or {}
    inner = _mm(lay.get("inner_mm"), 18.0)
    outer = _mm(lay.get("outer_mm"), 15.0)
    return inner * MM2PT, outer * MM2PT


def _mm(v, default: float) -> float:
    if v is None:
        return default
    if isinstance(v, (int, float)):
        return float(v)
    m = re.match(r"\s*([\d.]+)\s*mm", str(v))
    return float(m.group(1)) if m else default


# ---------------------------------------------------------------------------
# 页面几何：文本块 + 矢量图 + 位图，取每页实际内容的最大/最小坐标
# ---------------------------------------------------------------------------
def page_ink_bbox(page, dpi: int = 100) -> tuple[float, float, float, float] | None:
    """页面上"真正印出来的墨迹"边界（pt）。

    为什么不用 get_text("blocks") 的 bbox：那是**字符前进宽度**的结果。
    xeCJK 对行末全角标点做压缩（把标点收进版心），PDF 里字形的 advance
    仍是 11pt，于是 bbox 比实际墨迹多出 7–8pt —— 实测一整页「Overfull
    7.63pt」全是这个假阳性。光栅化后按像素找非白点，量到的是真的墨。
    """
    pix = page.get_pixmap(dpi=dpi, colorspace=pymupdf.csGRAY, alpha=False)
    try:
        import numpy as np
    except ModuleNotFoundError:      # 没 numpy 就退回前进宽度（会偏保守）
        return _advance_bbox(page)
    a = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width)
    mask = a < 250                       # codebg #F7F8FA ≈ 248，也算内容
    rows = np.where(mask.any(axis=1))[0]
    cols = np.where(mask.any(axis=0))[0]
    if rows.size == 0 or cols.size == 0:
        return None
    s = 72.0 / dpi
    return (cols[0] * s, rows[0] * s, (cols[-1] + 1) * s, (rows[-1] + 1) * s)


def _advance_bbox(page) -> tuple[float, float, float, float] | None:
    xs0, ys0, xs1, ys1 = [], [], [], []
    for blk in page.get_text("blocks"):
        if len(blk) >= 7 and blk[6] != 0:
            continue
        if not str(blk[4]).strip():
            continue
        xs0.append(blk[0]); ys0.append(blk[1]); xs1.append(blk[2]); ys1.append(blk[3])
    for dr in page.get_drawings():
        r = dr.get("rect")
        if r is None or (r.width <= 0 and r.height <= 0):
            continue
        xs0.append(r.x0); ys0.append(r.y0); xs1.append(r.x1); ys1.append(r.y1)
    if not xs1:
        return None
    return min(xs0), min(ys0), max(xs1), max(ys1)


def scan_pages(doc) -> dict:
    """逐页量墨迹范围，返回纸边/版心越界统计。"""
    W, H = doc[0].rect.width, doc[0].rect.height
    rows = []
    for i, page in enumerate(doc):
        bb = page_ink_bbox(page)
        if bb is None:
            continue
        rows.append({
            "pdf_page": i + 1,
            "label": page.get_label() or str(i + 1),
            "x0": round(bb[0], 2), "x1": round(bb[2], 2),
            "y0": round(bb[1], 2), "y1": round(bb[3], 2),
        })
    return {"width": W, "height": H, "pages": rows}


def evaluate_geometry(geo: dict, man: dict) -> dict:
    W, H = geo["width"], geo["height"]
    recto_limit, verso_limit = layout_limits(man, W)
    wide = wide_policy(man)
    margin_min = wide["min_paper_pt"]

    # ---- §9 wide 图页：125mm 图两侧各侵入 5mm ----
    # 判据是几何的，不看"这张图叫什么"：页面内容越出版心 ≤ 5mm，且左右两侧
    # 距纸边仍 ≥10mm，就是 wide 图页。真越界（>5mm 或贴到纸边）照旧判失败。
    def is_wide_page(p: dict, dev: float) -> bool:
        return (dev <= wide["overhang_pt"] + 1.0
                and p["x0"] >= margin_min - 0.5
                and W - p["x1"] >= margin_min - 0.5)

    # 纸边：四边都不许越出 3pt
    past_paper = [
        p for p in geo["pages"]
        if p["x0"] < PAPER_EDGE_TOL_PT or p["x1"] > W - PAPER_EDGE_TOL_PT
        or p["y0"] < PAPER_EDGE_TOL_PT or p["y1"] > H - PAPER_EDGE_TOL_PT
    ]

    def past_typearea(parity: str) -> tuple[list[dict], list[dict]]:
        bad, wide_pages = [], []
        for p in geo["pages"]:
            is_recto = (p["pdf_page"] % 2 == 1) if parity == "odd-recto" else (p["pdf_page"] % 2 == 0)
            limit = recto_limit if is_recto else verso_limit
            over = p["x1"] - limit
            if over <= TYPEAREA_TOL_PT:
                continue
            if is_wide_page(p, over):
                wide_pages.append({**p, "limit": round(limit, 2), "over": round(over, 2)})
            else:
                bad.append({**p, "limit": round(limit, 2), "over": round(over, 2)})
        return bad, wide_pages

    a, a_wide = past_typearea("odd-recto")
    b, b_wide = past_typearea("even-recto")
    if len(b) + len(b_wide) < len(a) + len(a_wide):
        parity, past_area, wide_area = "even-recto", b, b_wide
    else:
        parity, past_area, wide_area = "odd-recto", a, a_wide

    # 最差指标：版心右溢的最大值（wide 图页单独统计，不混进"最差"）
    worst = {"over_pt": 0.0, "pdf_page": None, "limit": None}
    for p in geo["pages"]:
        is_recto = (p["pdf_page"] % 2 == 1) if parity == "odd-recto" else (p["pdf_page"] % 2 == 0)
        limit = recto_limit if is_recto else verso_limit
        over = p["x1"] - limit
        if over > worst["over_pt"] and not is_wide_page(p, over):
            worst = {"over_pt": round(over, 2), "pdf_page": p["pdf_page"], "limit": round(limit, 2)}

    # §1 左边界：内容左缘不得侵入订口/外白边（同一 parity 约定）
    recto_left, verso_left = left_limits(man, W)
    past_gutter = []
    wide_gutter = []
    worst_left = {"under_pt": 0.0, "pdf_page": None, "limit": None, "x0": None}
    for p in geo["pages"]:
        is_recto = (p["pdf_page"] % 2 == 1) if parity == "odd-recto" else (p["pdf_page"] % 2 == 0)
        limit = recto_left if is_recto else verso_left
        under = limit - p["x0"]
        if under > GUTTER_TOL_PT:
            if is_wide_page(p, under):
                wide_gutter.append({**p, "limit": round(limit, 2), "under": round(under, 2)})
                continue
            past_gutter.append({**p, "limit": round(limit, 2), "under": round(under, 2)})
        if under > worst_left["under_pt"] and not is_wide_page(p, under):
            worst_left = {"under_pt": round(under, 2), "pdf_page": p["pdf_page"],
                          "limit": round(limit, 2), "x0": p["x0"]}

    wide_pages = sorted({p["pdf_page"] for p in wide_area + wide_gutter})
    return {
        "paper": {"w": round(W, 2), "h": round(H, 2)},
        "recto_right_limit": round(recto_limit, 2),
        "verso_right_limit": round(verso_limit, 2),
        "recto_left_limit": round(recto_left, 2),
        "verso_left_limit": round(verso_left, 2),
        "parity": parity,
        "past_paper": past_paper,
        "past_typearea": past_area,
        "past_gutter": past_gutter,
        "wide_figure_pages": wide_pages,
        "wide_policy": wide,
        "worst_typearea_over_pt": worst["over_pt"],
        "worst_typearea_page": worst["pdf_page"],
        "worst_gutter_under_pt": worst_left["under_pt"],
        "worst_gutter_page": worst_left["pdf_page"],
    }


# ---------------------------------------------------------------------------
# 文本类检查：重复编号
# ---------------------------------------------------------------------------
DUP_CN = re.compile(r"第\s*(\d{1,3})\s*章\s*第\s*\1\s*章")
DUP_EN = re.compile(r"Chapter\s+(\d{1,3})\s+Chapter\s+\1", re.IGNORECASE)


def check_dup_numbering(doc) -> list[dict]:
    hits = []
    for i, page in enumerate(doc):
        text = page.get_text("text")
        for rx, kind in ((DUP_CN, "zh"), (DUP_EN, "en")):
            for m in rx.finditer(text):
                hits.append({"pdf_page": i + 1, "kind": kind, "match": m.group(0)})
    return hits


# ---------------------------------------------------------------------------
# 源文 vs 产物计数
# ---------------------------------------------------------------------------
IMG_MD = re.compile(r"!\[[^\]]*\]\(([^)\s]+)")
INCLUDE_TEX = re.compile(r"\\paibaninclude\{([^}]+)\}")
PLACED_TEX = re.compile(r"\\paibanplaced(?:only)?\{([^}]+)\}")
LONGTABLE_TEX = re.compile(r"\\begin\{longtable\}")
MD_TABLE_SEP = re.compile(r"^\s*\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)+\|?\s*$")
CHAPTER_TEX = re.compile(r"\\paibanchapter\*?\{")
SECTION_TEX = re.compile(r"\\paibansection\{")


def tex_body(tex: str) -> str:
    """只留正文（去掉 -H preamble）——§9 之后图走 \\paibanplaced，而 preamble
    里也有 \\paibaninclude{#1} 的定义，不去掉会数出 "#1" 这种假图。"""
    i = tex.find("\\begin{document}")
    return tex[i:] if i >= 0 else tex


def _chapter_paths(man: dict) -> list[Path]:
    """manifest 里记的是**源文件名**（chapter-02-*.md），工作目录里带 00- 前缀。"""
    workdir = Path(man.get("workdir", ""))
    out = []
    for name in man.get("chapters", []):
        p = workdir / name
        if not p.exists():
            hits = sorted(workdir.glob(f"*{name}"))
            if hits:
                p = hits[0]
        out.append(p)
    return out


def count_figures(man: dict, tex: str) -> dict:
    src_refs: list[str] = []
    for p in _chapter_paths(man):
        if not p.exists():
            continue
        for m in IMG_MD.finditer(p.read_text(encoding="utf-8", errors="replace")):
            src_refs.append(Path(m.group(1)).name)
    body = tex_body(tex)
    placed = ([Path(m.group(1)).name for m in PLACED_TEX.finditer(body)]
              + [Path(m.group(1)).name for m in INCLUDE_TEX.finditer(body)])
    # 同一张图在正文里出现两次属于内容问题；这里按多重集合比
    from collections import Counter
    a, b = Counter(src_refs), Counter(placed)
    return {
        "source": len(src_refs),
        "placed": len(placed),
        "missing": sorted((a - b).elements()),
        "extra": sorted((b - a).elements()),
        "ok": a == b,
    }


def count_tables(man: dict, tex: str) -> dict:
    md_tables = 0
    for p in _chapter_paths(man):
        if not p.exists():
            continue
        lines = p.read_text(encoding="utf-8", errors="replace").splitlines()
        for i, line in enumerate(lines[1:], start=1):
            if MD_TABLE_SEP.match(line) and "|" in lines[i - 1]:
                md_tables += 1
    tex_tables = len(LONGTABLE_TEX.findall(tex))
    return {"source": md_tables, "placed": tex_tables, "ok": md_tables == tex_tables}


def count_toc(doc, tex: str) -> dict:
    """§5：目录只收 chapter + section 两级。

    book.cls 的 tableofcontents 自己会写一条 chapter 级条目「目录」，
    所以 L1 的期望值是 章数 + 1。
    """
    body = "\n".join(l for l in tex_body(tex).splitlines() if not l.lstrip().startswith("%"))
    chapters = len(CHAPTER_TEX.findall(body))
    sections = len(SECTION_TEX.findall(body))
    toc = doc.get_toc(simple=True) or []
    lvl1 = sum(1 for it in toc if it[0] == 1)
    lvl2 = sum(1 for it in toc if it[0] == 2)
    deeper = [it for it in toc if it[0] > 2]
    has_contents_entry = any(it[1].strip() in ("目录", "Contents", "CONTENTS")
                             for it in toc if it[0] == 1)
    exp1 = chapters + (1 if has_contents_entry else 0)
    return {
        "chapters": chapters, "sections": sections,
        "expected": exp1 + sections,
        "expected_level1": exp1,
        "outline_level1": lvl1, "outline_level2": lvl2,
        "outline_deeper": len(deeper),
        "outline_total": len(toc),
        "entries": lvl1 + lvl2,
        "ok": lvl1 == exp1 and lvl2 == sections,
    }


# ---------------------------------------------------------------------------
# 门禁汇总
# ---------------------------------------------------------------------------
def gate(name: str, clause: str, threshold: str, actual: str, ok: bool,
         detail: str = "", advisory: bool = False) -> dict:
    return {
        "gate": name, "clause": clause, "threshold": threshold,
        "actual": actual, "ok": bool(ok), "detail": detail,
        "advisory": advisory,
        "status": "ADVISORY" if advisory else ("PASS" if ok else "FAIL"),
    }


def figure_font_gate(man: dict) -> dict:
    """§9 门禁 11：按**实际放置方式**算图内字号，并核对策略是否落实。

    判定分两件事，都要过：

    1. **策略落实**（引擎侧硬条件）：每张图的放置方式必须是三级策略里
       "最强且够用"的那一级——inline 够 4.5pt 就不能留着不裁边，rotated
       能拿到更大字号就不能停在 wide。用 figure-fit.json 里的三个候选值
       （inline/wide/rotated 各自的成书字号）复核，不看脚注、不看声明。
    2. **字号底线**：inline / wide ≥ 4.5pt、rotated ≥ 5.5pt（§9 目标）；
       任何方式都到不了 4.5pt 的图，必须是 `must_redraw`（源图画布/字号
       问题，A5 版心上已无更宽可用区域）——并且复核它确实到不了，
       录错/过期的 must_redraw 同样判失败。

    返回的分布是 min/median/max + 各放置方式张数（§9 要求逐次构建可量化）。
    """
    figs = [f for f in (man.get("figures") or []) if "effective_pt" in f]
    policy = man.get("figure_policy") or {}
    inline_min = float(policy.get("inline_min_pt", FIGURE_MIN_PT))
    rot_target = float(policy.get("rotated_min_pt", FIGURE_ROTATED_PT))

    vals = sorted(f["effective_pt"] for f in figs)
    dist = {
        "min": vals[0] if vals else None,
        "median": vals[len(vals) // 2] if vals else None,
        "max": vals[-1] if vals else None,
    }
    by_mode: dict[str, int] = {}
    for f in figs:
        by_mode[f.get("placement", "?")] = by_mode.get(f.get("placement", "?"), 0) + 1

    compliance, below_floor, stale_redraw, meets_target = [], [], [], []
    for f in figs:
        cand = f.get("candidates") or {}
        want = ("inline" if cand.get("inline", 0) >= inline_min
                else "wide" if cand.get("wide", 0) >= inline_min
                else "rotated" if cand.get("rotated", 0) >= cand.get("wide", 0) else "wide")
        if f.get("placement") != want:
            compliance.append(f"{f['path']}：放置 {f.get('placement')}，应为 {want}")
        floor_ok = f["effective_pt"] >= inline_min
        if not floor_ok and not f.get("must_redraw"):
            below_floor.append(f"{f['path']}={f['effective_pt']}pt")
        if f.get("must_redraw") and floor_ok:
            stale_redraw.append(f"{f['path']}={f['effective_pt']}pt")
        if f["effective_pt"] >= (rot_target if f.get("placement") == "rotated" else inline_min):
            meets_target.append(f["path"])

    redraw = [f["path"] for f in figs if f.get("must_redraw")]
    ok = not compliance and not below_floor and not stale_redraw

    detail = (f"inline/wide 目标 ≥{inline_min:g}pt、rotated 目标 ≥{rot_target:g}pt；"
              f"达标 {len(meets_target)}/{len(figs)}；"
              f"min {dist['min']}pt / 中位 {dist['median']}pt / max {dist['max']}pt；"
              + "、".join(f"{m} {n} 张" for m, n in sorted(by_mode.items())))
    if redraw:
        detail += ("；⚠ 需重画源图 " + "、".join(Path(p).stem for p in redraw)
                   + "（整页横向也只有 "
                   + "、".join(f"{f['effective_pt']}pt" for f in figs if f.get("must_redraw"))
                   + "）")
    if compliance:
        detail += "；策略未落实：" + "；".join(compliance[:5])
    if below_floor:
        detail += "；低于 4.5pt 且未列入需重画：" + "、".join(below_floor[:5])
    if stale_redraw:
        detail += "；需重画判定过期（实际已达标）：" + "、".join(stale_redraw[:5])

    return {
        "ok": ok,
        "count": len(figs),
        "distribution": dist,
        "by_placement": by_mode,
        "meets_target": len(meets_target),
        "must_redraw": redraw,
        "detail": detail,
        "actual": (f"min {dist['min']}pt / 中位 {dist['median']}pt / max {dist['max']}pt"
                   if figs else "无可报告的矢量图"),
    }



def run(pdf: Path, man: dict) -> dict:
    doc = pymupdf.open(pdf)
    try:
        geo = scan_pages(doc)
        geom = evaluate_geometry(geo, man)
        dup = check_dup_numbering(doc)
        tex = Path(man["tex"]).read_text(encoding="utf-8", errors="replace")
        figs = count_figures(man, tex)
        tabs = count_tables(man, tex)
        toc = count_toc(doc, tex)
        page_count = doc.page_count
    finally:
        doc.close()

    ts = man.get("tex_stats") or {}
    overfull_heavy = (
        ts.get("overfull_max_pt", 0.0) >= OVERFULL_TOL_PT
        and ts.get("overfull_hbox", 0) > 0
    )

    fig_gate = figure_font_gate(man)
    wide_note = (f"（§9 wide 图页 {len(geom['wide_figure_pages'])} 页："
                 f"两侧各侵入 {geom['wide_policy']['overhang_pt']:.1f}pt，"
                 f"距纸边 ≥ {geom['wide_policy']['min_paper_pt'] / MM2PT:.0f}mm）"
                 if geom["wide_figure_pages"] else "")

    def _gutter_detail(g: dict) -> str:
        parts = [f"限制 recto {g['recto_left_limit']}pt / verso {g['verso_left_limit']}pt"]
        if g["worst_gutter_page"]:
            parts.append(f"最差页 p.{g['worst_gutter_page']}")
        if g["past_gutter"]:
            parts.append("越界 " + ", ".join(f"p.{p['pdf_page']} x0={p['x0']}"
                                             for p in g["past_gutter"][:5]))
        if wide_note:
            parts.append(wide_note.strip("（）"))
        return "；".join(parts)

    gates = [
        gate("内容越出纸边", "§1/§11", "0 页",
             f"{len(geom['past_paper'])} 页",
             not geom["past_paper"],
             ", ".join(f"p.{p['pdf_page']} x1={p['x1']}" for p in geom["past_paper"][:5])),
        gate("内容越出版心", "§11", f"≤{TYPEAREA_TOL_PT:g}pt 且 ≤{TYPEAREA_MAX_PAGES} 页",
             f"最差 {geom['worst_typearea_over_pt']:g}pt，超限 {len(geom['past_typearea'])} 页",
             (not geom["past_typearea"])
             and geom["worst_typearea_over_pt"] <= TYPEAREA_TOL_PT,
             f"奇偶约定 {geom['parity']}；版心右界 recto {geom['recto_right_limit']}pt / "
             f"verso {geom['verso_right_limit']}pt"
             + (f"；最差页 p.{geom['worst_typearea_page']}" if geom["worst_typearea_page"] else "")
             + (f"；{wide_note}" if wide_note else "")),
        gate("内容越出订口", "§1", f"0 页（左缘 ≥ 白边 − {GUTTER_TOL_PT:g}pt）",
             f"最差 {geom['worst_gutter_under_pt']:g}pt，超限 {len(geom['past_gutter'])} 页",
             not geom["past_gutter"],
             _gutter_detail(geom)),
        gate("缺失字形", "§11", "0",
             str(ts.get("missing_character", "?")),
             ts.get("missing_character", 1) == 0,
             " ".join(ts.get("missing_chars") or [])),
        gate("LaTeX 错误", "§11", "0",
             str(ts.get("latex_error", "?")),
             ts.get("latex_error", 1) == 0, ""),
        gate("重复编号", "§4/§11", "0 处",
             f"{len(dup)} 处",
             not dup,
             ", ".join(f"p.{d['pdf_page']} {d['match']}" for d in dup[:5])),
        gate("图数一致", "§9/§11", f"源文 {figs['source']} = 成书 {figs['source']}",
             f"源文 {figs['source']}，成书 {figs['placed']}",
             figs["ok"],
             (f"缺 {figs['missing']}" if figs["missing"] else "")
             + (f" 多 {figs['extra']}" if figs["extra"] else "")),
        gate("表数一致", "§8/§11", f"源文 {tabs['source']} = 成书 {tabs['source']}",
             f"源文 {tabs['source']}，成书 {tabs['placed']}",
             tabs["ok"], ""),
        gate("目录条目", "§5/§11", f"= 章 {toc['chapters']} + 节 {toc['sections']}",
             f"outline {toc['entries']}（L1 {toc['outline_level1']} / L2 {toc['outline_level2']}"
             + (f" / 更深 {toc['outline_deeper']}" if toc["outline_deeper"] else "") + "）",
             toc["ok"], ""),
        gate("Overfull hbox", "§7/§8", f">={OVERFULL_TOL_PT:g}pt 的为 0",
             f"{ts.get('overfull_hbox', 0)} 处，最大 {ts.get('overfull_max_pt', 0)}pt",
             not overfull_heavy, ""),
        gate("图内字号（按放置）", "§9",
             f"inline/wide ≥{FIGURE_MIN_PT:g}pt、rotated ≥{FIGURE_ROTATED_PT:g}pt",
             fig_gate["actual"], fig_gate["ok"], fig_gate["detail"]),
    ]

    hard_fail = [g for g in gates if not g["ok"] and not g["advisory"]]
    return {
        "pdf": str(pdf),
        "manifest": man.get("_manifest_path"),
        "title": man.get("title"),
        "lang": man.get("lang"),
        "pages": page_count,
        "geometry": geom,
        "figures": figs,
        "figure_fonts": fig_gate,
        "tables": tabs,
        "toc": toc,
        "dup_numbering": dup,
        "tex_stats": ts,
        "gates": gates,
        "ok": not hard_fail,
        "failed": [g["gate"] for g in hard_fail],
    }


# ---------------------------------------------------------------------------
# 输出
# ---------------------------------------------------------------------------
def print_report(res: dict, quiet: bool = False) -> None:
    if not quiet:
        print(f"[verify] {res['title']}  lang={res['lang']}  {res['pages']} 页")
        print(f"         纸面 {res['geometry']['paper']['w']}×{res['geometry']['paper']['h']}pt"
              f"（A5 应为 419.53×595.28）")
        head = f"  {'门禁':<16}{'条款':<10}{'阈值':<28}{'实测':<40}结果"
        print(head)
        print("  " + "-" * (len(head) - 2))
        for g in res["gates"]:
            print(f"  {g['gate']:<16}{g['clause']:<10}{g['threshold']:<28}"
                  f"{g['actual']:<40}{g['status']}")
            if g["detail"]:
                print(f"  {'':<16}{'':<10}↳ {g['detail']}")
        g = res["geometry"]
        print(f"  最差指标：版心右溢 {g['worst_typearea_over_pt']:g}pt"
              + (f"（p.{g['worst_typearea_page']}）" if g["worst_typearea_page"] else "")
              + f"；容差 {TYPEAREA_TOL_PT:g}pt"
              f"；左缘最差 {g['worst_gutter_under_pt']:g}pt"
              + (f"（p.{g['worst_gutter_page']}）" if g["worst_gutter_page"] else ""))
        if g.get("wide_figure_pages"):
            print(f"             §9 wide 图页 {len(g['wide_figure_pages'])} 张"
                  f"（侵入白边 ≤{g['wide_policy']['overhang_pt']:.1f}pt、"
                  f"距纸边 ≥{g['wide_policy']['min_paper_pt'] / MM2PT:.0f}mm）："
                  + ", ".join(f"p.{p}" for p in g["wide_figure_pages"][:8]))

    if res["ok"]:
        print(f"[verify] PASS  {len(res['gates'])} 项门禁全部通过")
    else:
        print(f"[verify] FAIL  未通过：{', '.join(res['failed'])}", file=sys.stderr)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="pai-ban §11 硬门槛验收")
    ap.add_argument("pdf", help="成书 PDF")
    ap.add_argument("--manifest", default=None, help="build.py 写出的 manifest JSON")
    ap.add_argument("--json", default=None, help="把验收结果写成 JSON（默认 <pdf>.verify.json）")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args(argv)

    pdf = Path(args.pdf).resolve()
    if not pdf.exists():
        print(f"[verify] 找不到 PDF：{pdf}", file=sys.stderr)
        return 2
    try:
        man = load_manifest(pdf, Path(args.manifest).resolve() if args.manifest else None)
    except FileNotFoundError as exc:
        print(f"[verify] {exc}", file=sys.stderr)
        return 2

    res = run(pdf, man)
    print_report(res, quiet=args.quiet)

    out = Path(args.json) if args.json else pdf.with_suffix(".verify.json")
    out.write_text(json.dumps(res, ensure_ascii=False, indent=2), encoding="utf-8")
    if not args.quiet:
        print(f"[verify] 结果：{out}")
    return 0 if res["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
