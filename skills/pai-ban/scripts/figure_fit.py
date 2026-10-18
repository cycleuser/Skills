#!/usr/bin/env python3
"""pai-ban / scripts/figure_fit.py — 图的可用性策略（裁边 → 加宽 → 旋转）

规格：rules/design-spec.md §9。本模块只做三件事，全部可复现、可量化：

  1. **量**：打开图的矢量 PDF，算「画布」与「墨迹 bbox」→ 裁边量；
     同时统计图内每个文字 span 的字号（成书后的实际字号 = 字号 × 缩放比）。
  2. **判**：按三级策略逐图选放置方式
         inline   裁边后放进版心宽（A5 = 115mm = 326pt）
         wide     仍 < 4.5pt → 加宽到 125mm（两侧各侵入白边 5mm，距纸边仍 ≥ 10mm）
         rotated  仍 < 4.5pt → 整页横向页（rotating/sidewaysfigure，可用宽 = 版心高 175mm）
     阈值：inline / wide 的最低可读字号 4.5pt；rotated 目标 5.5pt；
     任何放置下都到不了 4.5pt 的图 → `must_redraw`（源图画布/字号问题，
     版面上已无更宽的可用区域，必须重画源图，见 §9）。
  3. **说**：输出 `figure-fit.json`（图清单）+ `figure-fit.tex`（LaTeX 放置表，
     由 preamble.tex 的 `\\paibanplaced` 查表执行，过滤器不需要懂 JSON）。

为什么裁边在 LaTeX 层做（trim/clip）而不是改图文件：
    图的源资产（figures/svg、figures/pdf）是 CN/EN 共用、且由另一条渲染管线
    产出的；构建脚本只许读、不许写。`\\includegraphics[trim=…, clip]` 只影响
    这次排版，不动文件字节，回滚只需删掉 figure-fit.tex。

为什么「墨迹 bbox」要排除满幅浅色底：
    SVG 渲染出来的每张图外面都套了一个 600×300 的浅灰卡片（#F8F8F8 + 边框）。
    按像素阈值找 bbox 会量到这张卡片（占画布 97%），裁边等于没裁。所以这里用
    「文字 span + 图形 rect」，并跳过"面积 ≥ 70% 画布且填充色 ≥ 0.9 亮度"的
    底板——那层是排版的装饰边，不是内容。

用法
----
    python3 scripts/figure_fit.py <书稿目录> [--lang zh|en] [--json out.json]
    python3 scripts/figure_fit.py <书稿目录> --tex figure-fit.tex   # 只出 tex

库用法：build.py 调 `build_manifest()` + `write_tex()`。
"""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from pathlib import Path

#: 版心（A5 148×210，内 18 / 外 15，上 16 / 下 19）→ 115×175mm
MM2PT = 72.0 / 25.4
TEXTWIDTH_PT = 115 * MM2PT        # ≈ 326.0
TEXTHEIGHT_PT = 175 * MM2PT       # ≈ 496.1

#: §9 三级策略的阈值与几何
INLINE_MIN_PT = 4.5      # inline / wide 的最低可读字号
ROTATED_MIN_PT = 5.5     # rotated 的目标字号（整页横向页能拿到 496pt 宽）
WIDE_WIDTH_MM = 125.0    # wide 放置宽度：版心 115 + 两侧各 5mm
WIDE_MIN_PAPER_MM = 10.0  # wide 放置距纸边的最小距离（§9）
MAX_SCALE = 1.15         # §9 不放大超过原始尺寸 1.15 倍
FIGURE_HEIGHT_RATIO = 0.72  # inline/wide 的图高上限 = 0.72 版心高（给题注留位）
TRIM_PAD_PT = 1.0        # 裁边留 1pt 余量，避免削掉抗锯齿边缘
CAPTION_LEADING = 11.5   # 题注 9/11.5（preamble \paibanfigure）
CAPTION_GAP = 4.0        # 图与题注间距 4pt
ROTATED_SLACK_PT = 6.0   # 旋转页底部余量（浮动体内部垂直留白）

WARN = "\u26a0"


# ---------------------------------------------------------------------------
# 量图
# ---------------------------------------------------------------------------
def _import_pymupdf():
    try:
        import pymupdf  # noqa: PLC0415
    except ModuleNotFoundError:  # pragma: no cover - 环境问题
        raise SystemExit("[figure-fit] 需要 pymupdf（python3 -m pip install pymupdf）")
    return pymupdf


def _is_background(drawing: dict, page_area: float) -> bool:
    """满幅浅色底板（SVG 渲染器的卡片背景）→ 不算内容。"""
    r = drawing.get("rect")
    if r is None:
        return False
    if r.width * r.height < 0.70 * page_area:
        return False
    fill = drawing.get("fill")
    if fill is None:
        return False
    return all(c >= 0.9 for c in fill)


def measure(pdf: Path) -> dict:
    """量一张图：画布、墨迹 bbox（pt）、图内字号分布。"""
    pymupdf = _import_pymupdf()
    doc = pymupdf.open(pdf)
    try:
        page = doc[0]
        W, H = page.rect.width, page.rect.height
        page_area = W * H
        xs0, ys0, xs1, ys1 = [], [], [], []
        sizes: list[float] = []
        for block in page.get_text("dict")["blocks"]:
            if block.get("type") == 0:                    # 文字
                for line in block.get("lines", []):
                    for span in line["spans"]:
                        if not span["text"].strip():
                            continue
                        sizes.append(round(span["size"], 2))
                        xs0.append(span["bbox"][0]); ys0.append(span["bbox"][1])
                        xs1.append(span["bbox"][2]); ys1.append(span["bbox"][3])
            elif block.get("type") == 1:                  # 位图（本项目的图是纯矢量，通常为 0）
                xs0.append(block["bbox"][0]); ys0.append(block["bbox"][1])
                xs1.append(block["bbox"][2]); ys1.append(block["bbox"][3])
        for dr in page.get_drawings():
            r = dr.get("rect")
            if r is None or (r.width <= 0 and r.height <= 0):
                continue
            if _is_background(dr, page_area):
                continue
            xs0.append(r.x0); ys0.append(r.y0); xs1.append(r.x1); ys1.append(r.y1)
        n_pages = doc.page_count
    finally:
        doc.close()

    if not xs1:
        return {"error": "no ink found", "canvas_pt": [round(W, 1), round(H, 1)]}

    ink = (max(0.0, min(xs0) - TRIM_PAD_PT), max(0.0, min(ys0) - TRIM_PAD_PT),
           min(W, max(xs1) + TRIM_PAD_PT), min(H, max(ys1) + TRIM_PAD_PT))
    trim = (ink[0], H - ink[3], W - ink[2], ink[1])       # left, bottom, right, top
    content_w, content_h = ink[2] - ink[0], ink[3] - ink[1]
    sizes_sorted = sorted(sizes)
    return {
        "canvas_pt": [round(W, 1), round(H, 1)],
        "pages": n_pages,
        "ink_bbox_pt": [round(v, 1) for v in ink],
        "trim_pt": [round(v, 1) for v in trim],
        "content_pt": [round(content_w, 1), round(content_h, 1)],
        "trim_ratio": round(content_w / W, 3),
        "min_font_pt": round(sizes_sorted[0], 2) if sizes_sorted else 0.0,
        "median_font_pt": round(sizes_sorted[len(sizes_sorted) // 2], 2) if sizes_sorted else 0.0,
        "max_font_pt": round(sizes_sorted[-1], 2) if sizes_sorted else 0.0,
        "text_spans": len(sizes_sorted),
        "distinct_sizes": sorted(set(sizes_sorted)),
    }


# ---------------------------------------------------------------------------
# 题注高度（旋转页要把题注一起转，必须预留它的高度）
# ---------------------------------------------------------------------------
CJK_RE = re.compile(r"[\u3000-\u303f\u3400-\u4dbf\u4e00-\u9fff\uff00-\uffef]")


def estimate_caption_height(caption: str | None, width_pt: float,
                            size_pt: float = 9.0, leading: float = CAPTION_LEADING,
                            has_source: bool = False) -> float:
    """估算题注在 `width_pt` 宽的旋转框里占几行。

    9pt Times 的 ASCII 平均字宽约 4.2pt，CJK 全角 9pt。宁可估多一行
    （旋转页一旦算矮，图会顶出纸边，直接触发 §11 门禁 1）。
    """
    if not caption:
        return CAPTION_GAP
    cjk = len(CJK_RE.findall(caption))
    ascii_n = len(caption) - cjk
    w = cjk * size_pt + ascii_n * 4.35
    lines = max(1, math.ceil(w / (width_pt - 2.0)) + 0)
    h = CAPTION_GAP + lines * leading + 2.0
    if has_source:
        h += 2.0 + 10.5
    return h


# ---------------------------------------------------------------------------
# 判放置
# ---------------------------------------------------------------------------
def _fit(content_w: float, content_h: float, avail_w: float, avail_h: float) -> float:
    return min(avail_w / content_w, avail_h / content_h, MAX_SCALE)


def decide(fig: dict, *, textwidth_pt: float = TEXTWIDTH_PT,
           textheight_pt: float = TEXTHEIGHT_PT,
           caption: str | None = None, has_source: bool = False) -> dict:
    """三级策略：inline → wide → rotated。

    rotated 先算「题注预留」再定图高：整页横向页的可用宽 = 版心高（496pt），
    可用高 = 版心宽（326pt）− 题注 − 余量。只在 rotated 真的比 wide 更大时
    才用 rotated（近方形的图旋转后高度受限，可能反而不如加宽）。
    """
    out = dict(fig)
    if "error" in fig:
        out.update({"placement": "inline", "scale": 1.0, "effective_pt": 0.0,
                    "threshold_pt": INLINE_MIN_PT, "meets_target": False,
                    "must_redraw": True, "note": fig["error"]})
        return out

    cw, ch = fig["content_pt"]
    f0 = fig["min_font_pt"]
    h_cap = FIGURE_HEIGHT_RATIO * textheight_pt

    s_inline = _fit(cw, ch, textwidth_pt, h_cap)
    s_wide = _fit(cw, ch, WIDE_WIDTH_MM * MM2PT, h_cap)
    caption_h = estimate_caption_height(caption, textheight_pt, has_source=has_source)
    rot_avail_h = textwidth_pt - caption_h - ROTATED_SLACK_PT
    s_rot = _fit(cw, ch, textheight_pt, max(rot_avail_h, 0.3 * textwidth_pt))

    eff_inline = round(f0 * s_inline, 2)
    eff_wide = round(f0 * s_wide, 2)
    eff_rot = round(f0 * s_rot, 2)

    if eff_inline >= INLINE_MIN_PT:
        placement, scale, eff = "inline", s_inline, eff_inline
    elif eff_wide >= INLINE_MIN_PT:
        placement, scale, eff = "wide", s_wide, eff_wide
    elif eff_rot >= eff_wide:
        placement, scale, eff = "rotated", s_rot, eff_rot
    else:
        placement, scale, eff = "wide", s_wide, eff_wide

    threshold = ROTATED_MIN_PT if placement == "rotated" else INLINE_MIN_PT
    must_redraw = eff < INLINE_MIN_PT      # 任何方式都到不了可读底线 → 源图问题
    note = ""
    if must_redraw:
        note = ("A5 版心下最强的放置（%s）也只有 %.2fpt < %.1fpt：源图画布 %.0fpt、"
                "最小字号 %.2fpt，必须重画源图（§9）"
                % (placement, eff, INLINE_MIN_PT, fig["canvas_pt"][0], f0))
    elif placement == "rotated" and eff < ROTATED_MIN_PT:
        note = ("rotated 目标 %.1fpt 未达（%.2fpt）：裁边后内容宽 %.0fpt，"
                "旋转页可用宽 %.0fpt" % (ROTATED_MIN_PT, eff, cw, textheight_pt))

    placed_w = round(cw * scale, 1)
    placed_h = round(ch * scale, 1)
    out.update({
        "placement": placement,
        "scale": round(scale, 4),
        "placed_pt": [placed_w, placed_h],
        "effective_pt": eff,
        "threshold_pt": threshold,
        "meets_target": eff >= threshold,
        "must_redraw": must_redraw,
        "candidates": {"inline": eff_inline, "wide": eff_wide, "rotated": eff_rot},
        "rotated_caption_reserve_pt": round(caption_h, 1),
        "note": note,
    })
    return out


# ---------------------------------------------------------------------------
# 从源文取图引用与题注
# ---------------------------------------------------------------------------
IMG_RE = re.compile(r"!\[[^\]]*\]\((figures/pdf/[^)\s]+\.pdf)\)")
#: 题注段：*图1.1：…* / *Fig. 1.1：…* / *Figure 1.1: …*
CAP_RE = re.compile(r"^\s*[*_](图|Fig\.?|Figure)\s*([\d]+(?:[.\-][\d]+)?)")


def collect(md_files: list[Path]) -> list[dict]:
    """按文档顺序收集 (图路径, 题注文本, 是否紧跟来源行)。"""
    out = []
    for md in md_files:
        lines = md.read_text(encoding="utf-8", errors="replace").split("\n")
        for i, line in enumerate(lines):
            m = IMG_RE.search(line)
            if not m:
                continue
            path = m.group(1)
            caption, has_source = None, False
            j = i + 1
            while j < len(lines) and not lines[j].strip():
                j += 1
            if j < len(lines) and CAP_RE.match(lines[j]):
                caption = lines[j].strip().strip("*_")
                k = j + 1
                while k < len(lines) and not lines[k].strip():
                    k += 1
                if k < len(lines) and lines[k].lstrip().startswith(">"):
                    has_source = True
            out.append({"path": path, "caption": caption, "has_source": has_source})
    return out


# ---------------------------------------------------------------------------
# 汇总
# ---------------------------------------------------------------------------
def build_manifest(refs: list[dict], src_dir: Path, *,
                   textwidth_pt: float = TEXTWIDTH_PT,
                   textheight_pt: float = TEXTHEIGHT_PT) -> dict:
    """量 + 判 全部图，返回可直接写 JSON 的字典（同名图只量一次）。"""
    cache: dict[str, dict] = {}
    figures: list[dict] = []
    for ref in refs:
        path = ref["path"]
        if path not in cache:
            pdf = src_dir / path
            if not pdf.exists():
                cache[path] = {"path": path, "error": "missing"}
            else:
                cache[path] = {"path": path, **measure(pdf)}
        fig = decide(cache[path], textwidth_pt=textwidth_pt, textheight_pt=textheight_pt,
                     caption=ref.get("caption"), has_source=ref.get("has_source", False))
        fig["caption"] = (ref.get("caption") or "")[:200]
        # 同一张图在书里可能出现两次（不同题注）；只有第一次进清单做决策，
        # 后面重复出现的沿用同一放置（LaTeX 查表也是按路径）。
        figures.append(fig)

    uniq: dict[str, dict] = {}
    for f in figures:
        uniq.setdefault(f["path"], f)

    vals = [f["effective_pt"] for f in uniq.values() if "effective_pt" in f]
    vals_sorted = sorted(vals)
    by_mode: dict[str, int] = {}
    for f in uniq.values():
        by_mode[f.get("placement", "inline")] = by_mode.get(f.get("placement", "inline"), 0) + 1
    redraw = [f["path"] for f in uniq.values() if f.get("must_redraw")]
    return {
        "policy": {
            "inline_min_pt": INLINE_MIN_PT,
            "rotated_min_pt": ROTATED_MIN_PT,
            "wide_width_mm": WIDE_WIDTH_MM,
            "wide_min_paper_mm": WIDE_MIN_PAPER_MM,
            "wide_overhang_pt": round((WIDE_WIDTH_MM - 115.0) / 2 * MM2PT, 2),
            "max_scale": MAX_SCALE,
            "textwidth_pt": round(textwidth_pt, 2),
            "textheight_pt": round(textheight_pt, 2),
        },
        "counts": {
            "figures": len(uniq),
            "by_placement": by_mode,
            "meets_target": sum(1 for f in uniq.values() if f.get("meets_target")),
            "below_floor": len(redraw),
        },
        "distribution": {
            "min_pt": round(vals_sorted[0], 2) if vals_sorted else None,
            "median_pt": round(vals_sorted[len(vals_sorted) // 2], 2) if vals_sorted else None,
            "max_pt": round(vals_sorted[-1], 2) if vals_sorted else None,
        },
        "must_redraw": redraw,
        "figures": figures,
    }


# ---------------------------------------------------------------------------
# 落盘
# ---------------------------------------------------------------------------
def write_tex(manifest: dict, path: Path) -> int:
    """生成 LaTeX 放置表：每张图一行 `\\paibanfigdef{路径}{方式}{裁边}{宽}{高}`。

    preamble.tex 的 `\\paibanplaced{路径}{题注}` 查这张表执行；查不到就退回
    「不裁边、限宽限高」的老行为（figure-fit.json 丢了也不会编译失败）。
    """
    seen, lines = set(), []
    for f in manifest.get("figures", []):
        p = f["path"]
        if p in seen or "error" in f and "content_pt" not in f:
            continue
        seen.add(p)
        trim = " ".join(f"{v:g}" for v in f["trim_pt"])
        w, h = f["placed_pt"]
        lines.append("\\paibanfigdef{%s}{%s}{%s}{%.2fpt}{%.2fpt}"
                     % (p, f["placement"], trim, w, h))
    header = ("%% 由 scripts/figure_fit.py 生成（%d 张图）—— 不要手改；"
              "改策略请改 rules/design-spec.md §9 + figure_fit.py。\n" % len(lines))
    path.write_text(header + "\n".join(lines) + "\n", encoding="utf-8")
    return len(lines)


def summary_lines(manifest: dict) -> list[str]:
    c, d = manifest["counts"], manifest["distribution"]
    modes = c["by_placement"]
    order = [m for m in ("inline", "wide", "rotated") if m in modes]
    out = [f"图 {c['figures']} 张：" + " / ".join(f"{m} {modes[m]}" for m in order)
           + f"；达标 {c['meets_target']}/{c['figures']}"
           + (f"；需重画 {c['below_floor']}" if c["below_floor"] else ""),
           f"图内最小字号：min {d['min_pt']}pt / 中位 {d['median_pt']}pt / max {d['max_pt']}pt"]
    for f in manifest["figures"]:
        if f.get("must_redraw"):
            out.append(f"{WARN} 需重画：{f['path']}（{f['effective_pt']}pt，"
                       f"画布 {f['canvas_pt'][0]}pt，字号 {f['min_font_pt']}pt）")
    return out


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="pai-ban 图可用性策略（裁边→加宽→旋转）")
    ap.add_argument("book", help="书稿目录")
    ap.add_argument("--config", default=None)
    ap.add_argument("--lang", default=None, choices=["zh", "en"])
    ap.add_argument("--json", default=None, help="图清单 JSON 输出路径")
    ap.add_argument("--tex", default=None, help="LaTeX 放置表输出路径")
    ap.add_argument("--all", action="store_true", help="不按 md 引用，直接量 figures/pdf 下全部图")
    args = ap.parse_args(argv)

    book = Path(args.book).resolve()
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import build as build_mod  # noqa: PLC0415  — 复用配置/章节解析

    cfg = build_mod.load_config(book, args.config)
    cfg["_book"] = str(book)
    if args.lang:
        cfg["book"]["lang"] = args.lang
    cfg["_lang"] = cfg["book"]["lang"]
    files = build_mod.chapter_files(cfg, None, False)
    src_dir = Path(cfg["book"]["chapters_dir"])
    if not src_dir.is_absolute():
        src_dir = book / src_dir

    if args.all:
        refs = [{"path": f"figures/pdf/{p.name}"} for p in sorted((src_dir / "figures" / "pdf").glob("*.pdf"))]
    else:
        # 源文写的是 figures/svg/x.svg，构建期才改指 figures/pdf/x.pdf；
        # 这里走一遍同样的预处理，量到的才是真正会排进书里的那张图。
        stats = build_mod.Stats()
        tmp = Path("/tmp") / "pai-ban-figfit"
        tmp.mkdir(parents=True, exist_ok=True)
        norm = []
        for i, f in enumerate(files):
            p = tmp / f"{i:02d}-{f.name}"
            p.write_text(build_mod.preprocess(f.read_text(encoding="utf-8"), "latex", stats),
                         encoding="utf-8")
            norm.append(p)
        refs = collect(norm)

    man = build_manifest(refs, src_dir,
                         textwidth_pt=build_mod.TEXTWIDTH_PT,
                         textheight_pt=build_mod.TEXTHEIGHT_PT)
    for line in summary_lines(man):
        print(line)
    print()
    print(f"{'图':40}{'画布':>12}{'裁边比':>7}{'最小字':>7}{'方式':>9}{'缩放':>7}{'成书字号':>9}")
    for f in man["figures"]:
        if "content_pt" not in f:
            print(f"{f['path']:40}  缺失/无内容")
            continue
        print(f"{f['path'].replace('figures/pdf/',''):40}"
              f"{f['canvas_pt'][0]:>8.0f}×{f['canvas_pt'][1]:<4.0f}"
              f"{f['trim_ratio']:>7.2f}{f['min_font_pt']:>7.2f}"
              f"{f['placement']:>9}{f['scale']:>7.2f}{f['effective_pt']:>9.2f}"
              + ("  ⚠需重画" if f.get("must_redraw") else ""))

    if args.json:
        Path(args.json).write_text(json.dumps(man, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"\n[figure-fit] {args.json}")
    if args.tex:
        n = write_tex(man, Path(args.tex))
        print(f"[figure-fit] {args.tex}（{n} 行放置表）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
