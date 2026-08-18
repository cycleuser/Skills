#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""validate_svg.py — SVG layout validator for the research-figure skill.

Detects the layout problems that ruin scientific figures:
  - text overflowing its container box
  - boxes / arrows / labels overlapping each other
  - elements clipped by the viewBox boundary
  - text that is too small to read or has no measurable size
  - arrows whose heads/tails don't connect to their intended boxes

The validator parses the SVG with xml.dom.minidom (no external deps beyond the
Python stdlib), extracts every <rect>, <ellipse>, <polygon>, <path> (bbox
approximation), <line>, <text> and <image> element, computes axis-aligned
bounding boxes, and reports any intersection that the author did NOT declare as
intentional.

Intentional overlaps are whitelisted via a ``data-intent`` attribute on the
overlapped element, e.g. ``<text data-intent="label-of-box-1">`` — the author
marks "I know this text sits inside box-1, that's the point". Anything not
whitelisted is reported.

Exit codes: 0 = clean, 1 = issues found, 2 = parse error.
"""

from __future__ import annotations

import math
import os
import re
import sys
from xml.dom import minidom

__version__ = "1.0.0"

PASS = 0
WARN = 0
FAIL = 0


def _ok(name, cond, detail=""):
    global PASS, WARN, FAIL
    if cond:
        PASS += 1
        print(f"  [PASS] {name}")
    else:
        FAIL += 1
        print(f"  [FAIL] {name} {detail}")


def _warn(name, detail=""):
    global WARN
    WARN += 1
    print(f"  [WARN] {name} {detail}")


# --------------------------------------------------------------------------- #
#  Geometry helpers
# --------------------------------------------------------------------------- #

def _f(v, default=0.0):
    try:
        return float(v)
    except (TypeError, ValueError):
        return default


def _num_list(s):
    """Parse an SVG attribute like '10,20 30,40' into floats."""
    if not s:
        return []
    return [float(x) for x in re.split(r"[,\s]+", s.strip()) if x]


def _path_bbox(d):
    """Approximate the bounding box of an SVG path 'd' string."""
    if not d:
        return None
    nums = _num_list(re.sub(r"[MmLlHhVvCcSsQqTtAaZz]", " ", d))
    xs = [nums[i] for i in range(0, len(nums), 2)]
    ys = [nums[i] for i in range(1, len(nums), 2)]
    if not xs:
        return None
    return (min(xs), min(ys), max(xs), max(ys))


def _polygon_bbox(points):
    nums = _num_list(points)
    xs = nums[0::2]
    ys = nums[1::2]
    if not xs:
        return None
    return (min(xs), min(ys), max(xs), max(ys))


def _ellipse_bbox(cx, cy, rx, ry):
    return (cx - rx, cy - ry, cx + rx, cy + ry)


def _rect_bbox(x, y, w, h, rx=0, ry=0):
    return (x, y, x + w, y + h)


def _line_bbox(x1, y1, x2, y2):
    return (min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2))


def _text_bbox(x, y, text, font_size=12, anchor="start", baseline="auto"):
    """Approximate text bbox.

    SVG <text> x/y is the anchor point. With ``text-anchor="middle"`` x is the
    horizontal centre; with ``dominant-baseline="middle"`` y is the vertical
    centre. We account for both.
    """
    if not text:
        return None
    cjk = sum(1 for c in text if ord(c) > 0x3000)
    latin = len(text) - cjk
    w = cjk * font_size + latin * font_size * 0.6
    h = font_size * 1.2
    if anchor == "middle":
        x0 = x - w / 2
    elif anchor == "end":
        x0 = x - w
    else:
        x0 = x
    if baseline == "middle":
        y0 = y - h / 2
    elif baseline == "hanging":
        y0 = y
    else:
        y0 = y - font_size * 0.85
    return (x0, y0, x0 + w, y0 + h)


def _intersect(a, b, tol=1.0):
    """Do two axis-aligned bboxes (x1,y1,x2,y2) overlap? tol lets touching edges pass."""
    if a is None or b is None:
        return False
    return not (a[2] <= b[0] + tol or b[2] <= a[0] + tol or
                a[3] <= b[1] + tol or b[3] <= a[1] + tol)


def _contains(outer, inner, tol=1.0):
    """Is *inner* fully inside *outer*?"""
    if outer is None or inner is None:
        return False
    return (inner[0] >= outer[0] - tol and inner[1] >= outer[1] - tol and
            inner[2] <= outer[2] + tol and inner[3] <= outer[3] + tol)


# --------------------------------------------------------------------------- #
#  SVG parsing
# --------------------------------------------------------------------------- #

def _font_size(el):
    style = el.getAttribute("style") or ""
    fs = el.getAttribute("font-size")
    if not fs:
        m = re.search(r"font-size\s*:\s*([\d.]+)", style)
        if m:
            fs = m.group(1)
    return _f(fs, 12.0)


def _text_content(el):
    """Concatenate all text under an element (including <tspan> children)."""
    parts = []
    for node in el.childNodes:
        if node.nodeType == node.TEXT_NODE:
            parts.append(node.data)
        elif node.nodeType == node.ELEMENT_NODE:
            parts.append(_text_content(node))
    return "".join(parts).strip()


def _viewbox(root):
    vb = root.getAttribute("viewBox") or root.getAttribute("viewbox")
    if not vb:
        w = _f(root.getAttribute("width"), 800)
        h = _f(root.getAttribute("height"), 600)
        return (0, 0, w, h)
    parts = _num_list(vb)
    if len(parts) >= 4:
        return (parts[0], parts[1], parts[0] + parts[2], parts[1] + parts[3])
    return (0, 0, 800, 600)


def collect_elements(svg_path):
    """Return a list of dicts describing every graphical element."""
    try:
        doc = minidom.parse(svg_path)
    except Exception as e:
        print(f"PARSE ERROR: {e}")
        return None, None
    root = doc.documentElement
    vb = _viewbox(root)
    items = []

    def walk(node, transform_stack=()):
        for el in node.childNodes:
            if el.nodeType != el.ELEMENT_NODE:
                continue
            tag = el.tagName.lower()
            if tag == "g":
                walk(el, transform_stack)
                continue
            item = {"tag": tag, "id": el.getAttribute("id") or "",
                    "intent": el.getAttribute("data-intent") or "",
                    "bbox": None, "el": el, "anchor": None}
            if tag == "rect":
                item["bbox"] = _rect_bbox(
                    _f(el.getAttribute("x")), _f(el.getAttribute("y")),
                    _f(el.getAttribute("width")), _f(el.getAttribute("height")))
            elif tag in ("circle",):
                cx, cy, r = (_f(el.getAttribute("cx")), _f(el.getAttribute("cy")),
                             _f(el.getAttribute("r")))
                item["bbox"] = (cx - r, cy - r, cx + r, cy + r)
            elif tag == "ellipse":
                item["bbox"] = _ellipse_bbox(
                    _f(el.getAttribute("cx")), _f(el.getAttribute("cy")),
                    _f(el.getAttribute("rx")), _f(el.getAttribute("ry")))
            elif tag == "line":
                item["bbox"] = _line_bbox(
                    _f(el.getAttribute("x1")), _f(el.getAttribute("y1")),
                    _f(el.getAttribute("x2")), _f(el.getAttribute("y2")))
            elif tag == "polyline" or tag == "polygon":
                item["bbox"] = _polygon_bbox(el.getAttribute("points"))
            elif tag == "path":
                item["bbox"] = _path_bbox(el.getAttribute("d"))
            elif tag == "text":
                x = _f(el.getAttribute("x"))
                y = _f(el.getAttribute("y"))
                fs = _font_size(el)
                txt = _text_content(el)
                anchor = el.getAttribute("text-anchor") or "start"
                style = el.getAttribute("style") or ""
                baseline = el.getAttribute("dominant-baseline") or "auto"
                if not baseline:
                    m = re.search(r"dominant-baseline\s*:\s*(\w+)", style)
                    if m:
                        baseline = m.group(1)
                # collect all tspans (each may have its own x/y) for multi-line
                tspans = [n for n in el.childNodes
                          if n.nodeType == n.ELEMENT_NODE and n.tagName.lower() == "tspan"]
                if tspans:
                    sub_bboxes = []
                    for ts in tspans:
                        tx = _f(ts.getAttribute("x"), x)
                        ty = _f(ts.getAttribute("y"), y)
                        tfs = _f(ts.getAttribute("font-size"), fs)
                        ttxt = _text_content(ts)
                        if not ttxt:
                            continue
                        anchor_t = ts.getAttribute("text-anchor") or anchor
                        baseline_t = ts.getAttribute("dominant-baseline") or baseline
                        sub_bboxes.append(_text_bbox(tx, ty, ttxt, tfs, anchor_t, baseline_t))
                    if sub_bboxes:
                        xs1 = min(b[0] for b in sub_bboxes)
                        ys1 = min(b[1] for b in sub_bboxes)
                        xs2 = max(b[2] for b in sub_bboxes)
                        ys2 = max(b[3] for b in sub_bboxes)
                        item["bbox"] = (xs1, ys1, xs2, ys2)
                    else:
                        item["bbox"] = _text_bbox(x, y, txt, fs, anchor, baseline)
                else:
                    item["bbox"] = _text_bbox(x, y, txt, fs, anchor, baseline)
                item["text"] = txt
                item["font_size"] = fs
                item["anchor"] = (x, y)
            elif tag == "image":
                item["bbox"] = _rect_bbox(
                    _f(el.getAttribute("x")), _f(el.getAttribute("y")),
                    _f(el.getAttribute("width")), _f(el.getAttribute("height")))
            else:
                continue
            if item["bbox"]:
                items.append(item)
    walk(root)
    return items, vb


# --------------------------------------------------------------------------- #
#  Checks
# --------------------------------------------------------------------------- #

def check_viewbox_bounds(items, vb):
    """Every element must be inside the viewBox (no clipping)."""
    x1, y1, x2, y2 = vb
    for it in items:
        bx1, by1, bx2, by2 = it["bbox"]
        if bx1 < x1 - 1 or by1 < y1 - 1 or bx2 > x2 + 1 or by2 > y2 + 1:
            _warn(f"element outside viewBox",
                  f"<{it['tag']}> bbox=({bx1:.0f},{by1:.0f},{bx2:.0f},{by2:.0f}) "
                  f"viewBox=({x1:.0f},{y1:.0f},{x2:.0f},{y2:.0f})")


def check_text_outside_box(items):
    """Text should be inside SOME box (or whitelisted as free-floating)."""
    texts = [it for it in items if it["tag"] == "text"]
    boxes = [it for it in items if it["tag"] in ("rect", "ellipse", "circle", "polygon", "path")]
    for t in texts:
        if t["intent"]:
            continue
        inside = any(_contains(b["bbox"], t["bbox"], tol=2) for b in boxes)
        if not inside:
            _warn("text outside any box",
                  f"text='{t.get('text','')[:30]}' bbox={tuple(round(v) for v in t['bbox'])}")


def check_text_overflow(items):
    """Text should not overflow its containing box."""
    texts = [it for it in items if it["tag"] == "text"]
    boxes = [it for it in items if it["tag"] in ("rect", "ellipse", "circle", "polygon")]
    for t in texts:
        if t["intent"]:
            continue
        ax, ay = t.get("anchor") or (t["bbox"][0], t["bbox"][1])
        for b in boxes:
            # use the SVG x/y anchor point to decide which box owns this text
            if _contains(b["bbox"], (ax, ay, ax, ay), tol=3):
                # anchor is inside this box — check if full text bbox fits
                if not _contains(b["bbox"], t["bbox"], tol=2):
                    _ok(f"text fits in box '{b['id'] or b['tag']}'", False,
                        f"text='{t.get('text','')[:30]}' overflows "
                        f"box={tuple(round(v) for v in b['bbox'])} "
                        f"textbbox={tuple(round(v) for v in t['bbox'])}")
                else:
                    _ok(f"text fits in box '{b['id'] or b['tag']}'", True)
                break


def check_box_overlap(items):
    """Boxes (rect/ellipse/polygon) should not overlap unless whitelisted."""
    boxes = [it for it in items if it["tag"] in ("rect", "ellipse", "circle", "polygon")]
    for i in range(len(boxes)):
        for j in range(i + 1, len(boxes)):
            a, b = boxes[i], boxes[j]
            if a["intent"] or b["intent"]:
                continue
            if _intersect(a["bbox"], b["bbox"], tol=2):
                _ok(f"no overlap: '{a['id'] or a['tag']}' vs '{b['id'] or b['tag']}'", False,
                    f"{tuple(round(v) for v in a['bbox'])} ∩ {tuple(round(v) for v in b['bbox'])}")
            else:
                _ok(f"no overlap: '{a['id'] or a['tag']}' vs '{b['id'] or b['tag']}'", True)


def check_text_text_overlap(items):
    """Two text elements should not overlap."""
    texts = [it for it in items if it["tag"] == "text"]
    for i in range(len(texts)):
        for j in range(i + 1, len(texts)):
            a, b = texts[i], texts[j]
            if _intersect(a["bbox"], b["bbox"], tol=1):
                _warn("text-text overlap",
                      f"'{a.get('text','')[:20]}' ∩ '{b.get('text','')[:20]}'")


def check_min_font_size(items, min_size=8.0):
    """No text should be smaller than min_size (default 8pt for readability)."""
    for it in items:
        if it["tag"] != "text":
            continue
        fs = it.get("font_size", 12)
        if fs < min_size:
            _warn("font too small",
                  f"text='{it.get('text','')[:30]}' size={fs} < {min_size}")


def check_arrows_connect(items):
    """Arrows (lines/polylines/paths) should start/end near a box edge.

    An arrow is "connected" if one of its endpoints is within ~15px of any box
    edge. This catches the common failure of arrows floating in space or
    pointing at the wrong thing.
    """
    arrows = [it for it in items if it["tag"] in ("line", "polyline", "path")]
    boxes = [it for it in items if it["tag"] in ("rect", "ellipse", "circle", "polygon")]
    for arr in arrows:
        bx1, by1, bx2, by2 = arr["bbox"]
        # endpoints
        if arr["tag"] == "line":
            el = arr["el"]
            pts = [(_f(el.getAttribute("x1")), _f(el.getAttribute("y1"))),
                   (_f(el.getAttribute("x2")), _f(el.getAttribute("y2")))]
        elif arr["tag"] == "polyline":
            nums = _num_list(arr["el"].getAttribute("points"))
            pts = [(nums[0], nums[1]), (nums[-2], nums[-1])]
        else:
            # path: use bbox corners as approximation
            pts = [(bx1, by1), (bx2, by2)]
        for pt in pts:
            near = any(_edge_distance(b["bbox"], pt) < 20 for b in boxes)
            if not near:
                _warn("arrow endpoint not near any box",
                      f"pt={pt} arrow={arr['tag']}")
                break


def _edge_distance(bbox, pt):
    """Distance from pt to the nearest edge of bbox."""
    x1, y1, x2, y2 = bbox
    px, py = pt
    dx = max(x1 - px, 0, px - x2)
    dy = max(y1 - py, 0, py - y2)
    return math.hypot(dx, dy)


def check_id_uniqueness(items):
    """All element ids must be unique."""
    seen = {}
    for it in items:
        if not it["id"]:
            continue
        if it["id"] in seen:
            _warn("duplicate id", it["id"])
        else:
            seen[it["id"]] = it


# --------------------------------------------------------------------------- #
#  Main
# --------------------------------------------------------------------------- #

def validate(svg_path, verbose=True):
    global PASS, WARN, FAIL
    PASS = WARN = FAIL = 0
    if verbose:
        print(f"Validating: {svg_path}")
    if not os.path.exists(svg_path):
        print(f"FILE NOT FOUND: {svg_path}")
        return 2
    items, vb = collect_elements(svg_path)
    if items is None:
        return 2
    if verbose:
        print(f"  {len(items)} elements, viewBox={tuple(round(v) for v in vb)}")
    check_viewbox_bounds(items, vb)
    check_text_outside_box(items)
    check_text_overflow(items)
    check_box_overlap(items)
    check_text_text_overlap(items)
    check_min_font_size(items)
    check_arrows_connect(items)
    check_id_uniqueness(items)
    if verbose:
        print(f"\nResult: {PASS} passed, {WARN} warnings, {FAIL} failures")
    return 1 if FAIL else 0


def main():
    if len(sys.argv) < 2:
        print("usage: validate_svg.py <file.svg> [file2.svg ...]")
        return 2
    rc = 0
    for p in sys.argv[1:]:
        r = validate(p)
        rc = max(rc, r)
    return rc


if __name__ == "__main__":
    sys.exit(main())