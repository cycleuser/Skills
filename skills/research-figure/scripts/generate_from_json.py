#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""generate_from_json.py — turn a layout.json into a validated SVG figure.

Reads a JSON file describing the figure structure (boxes + arrows, as
produced by the vision-to-prompt step) and generates an SVG using
:mod:`svg_template`, then validates it with :mod:`validate_svg`.

Usage::

    python generate_from_json.py layout.json -o figure.svg
    python generate_from_json.py layout.json -o figure.svg --fix
"""

from __future__ import annotations

import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from svg_template import Figure  # noqa: E402
from validate_svg import validate  # noqa: E402

# -- grid_hint → (row, col, rowspan, colspan) mapping (4×4 grid) -----------
GRID_MAP = {
    "top-left":      (0, 0, 1, 1),
    "top-center":    (0, 1, 1, 2),
    "top-right":     (0, 3, 1, 1),
    "mid-left":      (1, 0, 2, 1),
    "center":        (1, 1, 2, 2),
    "mid-right":     (1, 3, 2, 1),
    "bottom-left":   (3, 0, 1, 1),
    "bottom-center": (3, 1, 1, 2),
    "bottom-right":  (3, 3, 1, 1),
}

SIZE_ADJUST = {
    "small":  (1, 1),
    "medium": (1, 2),
    "large":  (2, 2),
}

ROLE_FILL = {
    "input": "blue", "process": "orange", "model": "green",
    "output": "red", "decision": "purple", "data": "cyan",
    "feedback": "grey", "other": "white",
}

ROLE_SHAPE = {
    "model": "round", "decision": "ellipse",
}


def _grid_place(hint, size, max_cols=4, max_rows=4):
    """Return (row, col, rowspan, colspan) for a grid_hint + size_hint.

    Automatically shrinks colspan/rowspan if the box would overflow the grid.
    """
    r, c, rs, cs = GRID_MAP.get(hint, (0, 0, 1, 1))
    sr, sc = SIZE_ADJUST.get(size, (1, 1))
    rs = max(rs, sr)
    cs = max(cs, sc)
    # shrink to fit within the grid
    if c + cs > max_cols:
        cs = max(1, max_cols - c)
    if r + rs > max_rows:
        rs = max(1, max_rows - r)
    return r, c, rs, cs


def _arrow_dir(from_box, to_box):
    """Pick anchor directions for an arrow from one box to another."""
    fr, fc = from_box["row"], from_box["col"]
    tr, tc = to_box["row"], to_box["col"]
    dr = tr - fr
    dc = tc - fc
    if abs(dc) > abs(dr) * 1.5:
        if dc > 0:
            return "right", "left"
        return "left", "right"
    if abs(dr) > abs(dc) * 1.5:
        if dr > 0:
            return "bottom", "top"
        return "top", "bottom"
    # diagonal
    if dr > 0 and dc > 0:
        return "bottom", "top"  # or "se", "nw" but bottom/top is safer
    if dr > 0 and dc < 0:
        return "bottom", "top"
    if dr < 0 and dc > 0:
        return "top", "bottom"
    return "bottom", "top"


def build_figure(layout, output_path, cell_w=150, cell_h=70, font_size=12,
                 cols=4, rows=4):
    """Build an SVG from a layout dict and return the path."""
    fig = Figure(cols=cols, rows=rows, cell_w=cell_w, cell_h=cell_h,
                 font_size=font_size, title_size=15)
    if "title" in layout:
        fig.title(layout["title"])

    placed = {}
    for box in layout.get("boxes", []):
        name = box["name"]
        r, c, rs, cs = _grid_place(box.get("grid_hint", "center"),
                                   box.get("size_hint", "medium"),
                                   max_cols=cols, max_rows=rows)
        box["row"], box["col"], box["rowspan"], box["colspan"] = r, c, rs, cs
        role = box.get("role", "other")
        fill = ROLE_FILL.get(role, "white")
        shape = ROLE_SHAPE.get(role, "rect")
        fig.box(name, r, c, rowspan=rs, colspan=cs,
                text=box.get("label", name), fill=fill, shape=shape)
        placed[name] = box

    for arr in layout.get("arrows", []):
        fn, tn = arr["from"], arr["to"]
        if fn not in placed or tn not in placed:
            continue
        fd, td = _arrow_dir(placed[fn], placed[tn])
        style = arr.get("style", "solid")
        dashed = style == "dashed"
        curve = arr.get("curve", 0)
        fig.arrow(fn, fd, tn, td, label=arr.get("label", ""),
                  dashed=dashed, curve=curve)

    fig.save(output_path)
    # also dump the layout with placement info for reproducibility
    layout["_placed"] = list(placed.values())
    return output_path


def main():
    ap = argparse.ArgumentParser(description="Generate SVG from layout.json")
    ap.add_argument("json_file", help="layout.json file")
    ap.add_argument("-o", "--output", default="figure.svg", help="output SVG path")
    ap.add_argument("--cell-w", type=int, default=150)
    ap.add_argument("--cell-h", type=int, default=70)
    ap.add_argument("--font-size", type=int, default=12)
    ap.add_argument("--fix", action="store_true",
                    help="auto-fix common issues and re-validate (best effort)")
    args = ap.parse_args()

    with open(args.json_file, encoding="utf-8") as f:
        layout = json.load(f)

    build_figure(layout, args.output, args.cell_w, args.cell_h, args.font_size)
    print(f"Generated: {args.output}")
    rc = validate(args.output)
    if rc != 0 and args.fix:
        print("Issues found — attempting auto-fix...")
        _auto_fix(layout, args)
        build_figure(layout, args.output, args.cell_w, args.cell_h, args.font_size)
        rc = validate(args.output)
    return rc


def _auto_fix(layout, args):
    """Best-effort auto-fix: enlarge boxes that overflow, nudge arrow labels."""
    # simplest fix: increase cell size if text is long
    max_label = max((len(b.get("label", "")) for b in layout.get("boxes", [])), default=0)
    if max_label > 20:
        args.cell_w = max(args.cell_w, 180)
        args.cell_h = max(args.cell_h, 80)


if __name__ == "__main__":
    sys.exit(main())