#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""test_skill.py — self-contained test suite for the research-figure skill.

Tests:
  1. svg_template produces a valid SVG
  2. validate_svg passes on a well-formed figure (0 failures)
  3. validate_svg catches overlapping boxes
  4. validate_svg catches text overflow
  5. generate_from_json builds a figure from layout.json
  6. end-to-end: build → validate → 0 failures
  7. multi-line text fits in box
  8. CJK text fits in box
  9. arrows connect to boxes (no floating)
 10. elements inside viewBox
"""

from __future__ import annotations

import json
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "scripts"))

from svg_template import Figure  # noqa: E402
from validate_svg import validate, collect_elements  # noqa: E402
from generate_from_json import build_figure  # noqa: E402

PASS = 0
FAIL = 0


def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  [PASS] {name}")
    else:
        FAIL += 1
        print(f"  [FAIL] {name} {detail}")


def _tmpdir():
    return tempfile.mkdtemp(prefix="rfig_")


def _quiet_validate(path):
    """Run validate but suppress stdout, return (pass, warn, fail)."""
    import io
    import contextlib
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = validate(path, verbose=False)
    return rc


def test_template_generates_valid_svg():
    print("\n== svg_template produces valid SVG ==")
    d = _tmpdir()
    p = os.path.join(d, "fig.svg")
    fig = Figure(cols=4, rows=4)
    fig.box("a", 0, 0, text="A")
    fig.box("b", 0, 2, colspan=2, text="B")
    fig.arrow("a", "right", "b", "left")
    fig.save(p)
    check("file created", os.path.exists(p) and os.path.getsize(p) > 0)
    check("has xmlns", 'xmlns="http://www.w3.org/2000/svg"' in open(p).read())
    shutil.rmtree(d)


def test_validate_passes_good_figure():
    print("\n== validate passes a well-formed figure ==")
    d = _tmpdir()
    p = os.path.join(d, "fig.svg")
    fig = Figure(cols=4, rows=4, cell_w=160, cell_h=70)
    fig.title("Test / 测试")
    fig.box("a", 0, 0, colspan=2, text="Input\n输入", fill="blue")
    fig.box("b", 0, 2, colspan=2, text="Process\n处理", fill="orange")
    fig.box("c", 2, 1, colspan=2, text="Output\n输出", fill="green")
    fig.arrow("a", "right", "b", "left", label="raw")
    fig.arrow("b", "bottom", "c", "top", label="result")
    fig.save(p)
    rc = _quiet_validate(p)
    check("0 failures", rc == 0, f"rc={rc}")
    shutil.rmtree(d)


def test_validate_catches_overlap():
    print("\n== validate catches overlapping boxes ==")
    d = _tmpdir()
    p = os.path.join(d, "bad.svg")
    with open(p, "w") as f:
        f.write('''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 300">
<rect id="a" x="10" y="10" width="100" height="60" fill="#e3f2fd" stroke="#333"/>
<rect id="b" x="50" y="40" width="100" height="60" fill="#fff3e0" stroke="#333"/>
</svg>''')
    rc = _quiet_validate(p)
    check("detected overlap (rc=1)", rc == 1, f"rc={rc}")
    shutil.rmtree(d)


def test_validate_catches_overflow():
    print("\n== validate catches text overflow ==")
    d = _tmpdir()
    p = os.path.join(d, "bad.svg")
    with open(p, "w") as f:
        f.write('''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 300">
<rect id="box" x="10" y="10" width="60" height="30" fill="#e3f2fd" stroke="#333"/>
<text x="40" y="25" font-size="12" text-anchor="middle" dominant-baseline="middle">This text is way too long for the box</text>
</svg>''')
    rc = _quiet_validate(p)
    check("detected overflow (rc=1)", rc == 1, f"rc={rc}")
    shutil.rmtree(d)


def test_generate_from_json():
    print("\n== generate_from_json builds figure ==")
    d = _tmpdir()
    jp = os.path.join(d, "layout.json")
    op = os.path.join(d, "fig.svg")
    layout = {
        "title": "Pipeline / 流程",
        "boxes": [
            {"name": "a", "label": "Input\n输入", "role": "input",
             "grid_hint": "top-left", "size_hint": "medium"},
            {"name": "b", "label": "Model\n模型", "role": "model",
             "grid_hint": "top-right", "size_hint": "medium"},
            {"name": "c", "label": "Output\n输出", "role": "output",
             "grid_hint": "bottom-right", "size_hint": "small"},
        ],
        "arrows": [
            {"from": "a", "to": "b", "label": "features", "style": "solid"},
            {"from": "b", "to": "c", "label": "predict", "style": "solid"},
        ],
    }
    with open(jp, "w", encoding="utf-8") as f:
        json.dump(layout, f, ensure_ascii=False)
    build_figure(layout, op)
    check("SVG generated", os.path.exists(op))
    check("has boxes", "<rect" in open(op).read() or "<ellipse" in open(op).read())
    check("has arrows", "<line" in open(op).read() or "<path" in open(op).read())
    rc = _quiet_validate(op)
    check("0 failures", rc == 0, f"rc={rc}")
    shutil.rmtree(d)


def test_multiline_text_fits():
    print("\n== multi-line text fits in box ==")
    d = _tmpdir()
    p = os.path.join(d, "fig.svg")
    fig = Figure(cols=4, rows=4, cell_w=160, cell_h=80)
    fig.box("x", 0, 0, colspan=2, rowspan=2,
            text="First line\n第二行\nThird line\n第四行", fill="blue")
    fig.save(p)
    rc = _quiet_validate(p)
    check("multiline fits (0 failures)", rc == 0, f"rc={rc}")
    shutil.rmtree(d)


def test_cjk_text_fits():
    print("\n== CJK text fits in box ==")
    d = _tmpdir()
    p = os.path.join(d, "fig.svg")
    fig = Figure(cols=4, rows=4, cell_w=160, cell_h=80)
    fig.box("x", 0, 0, colspan=2, text="数据处理模块\n数据处理模块", fill="green")
    fig.save(p)
    rc = _quiet_validate(p)
    check("CJK fits (0 failures)", rc == 0, f"rc={rc}")
    shutil.rmtree(d)


def test_arrows_connect():
    print("\n== arrows connect to boxes ==")
    d = _tmpdir()
    p = os.path.join(d, "fig.svg")
    fig = Figure(cols=4, rows=4)
    fig.box("a", 0, 0, text="A")
    fig.box("b", 0, 2, colspan=2, text="B")
    fig.box("c", 2, 2, colspan=2, text="C")
    fig.arrow("a", "right", "b", "left", label="x")
    fig.arrow("b", "bottom", "c", "top", label="y")
    fig.save(p)
    rc = _quiet_validate(p)
    check("arrows connect (0 failures)", rc == 0, f"rc={rc}")
    shutil.rmtree(d)


def test_elements_inside_viewbox():
    print("\n== elements inside viewBox ==")
    d = _tmpdir()
    p = os.path.join(d, "fig.svg")
    fig = Figure(cols=5, rows=5, cell_w=140, cell_h=60)
    fig.box("a", 0, 0, colspan=3, text="Wide box / 宽框", fill="blue")
    fig.box("b", 4, 4, text="End", fill="red")
    fig.arrow("a", "bottom", "b", "top", label="flow", curve=40)
    fig.save(p)
    rc = _quiet_validate(p)
    check("all inside viewBox (0 failures)", rc == 0, f"rc={rc}")
    shutil.rmtree(d)


def test_feedback_loop():
    print("\n== feedback loop (dashed arrow) ==")
    d = _tmpdir()
    p = os.path.join(d, "fig.svg")
    fig = Figure(cols=4, rows=4, cell_w=150, cell_h=70)
    fig.box("a", 0, 0, text="Start", fill="blue")
    fig.box("b", 0, 2, colspan=2, text="Process", fill="orange")
    fig.arrow("a", "right", "b", "left", label="go")
    fig.arrow("b", "bottom", "a", "bottom", label="feedback", dashed=True, curve=-50)
    fig.save(p)
    rc = _quiet_validate(p)
    check("feedback loop (0 failures)", rc == 0, f"rc={rc}")
    shutil.rmtree(d)


def test_end_to_end():
    print("\n== end-to-end: complex figure with 6 boxes + 6 arrows ==")
    d = _tmpdir()
    p = os.path.join(d, "complex.svg")
    fig = Figure(cols=5, rows=5, cell_w=140, cell_h=65, font_size=11)
    fig.title("End-to-end pipeline / 端到端流程")
    fig.box("data", 0, 0, colspan=2, text="Dataset\n数据集", fill="blue")
    fig.box("prep", 0, 2, colspan=2, text="Preprocessing\n预处理", fill="orange")
    fig.box("train", 2, 0, colspan=2, text="Training\n训练", fill="green", shape="round")
    fig.box("eval", 2, 2, colspan=2, text="Evaluation\n评估", fill="purple", shape="round")
    fig.box("deploy", 4, 1, colspan=3, text="Deployment\n部署", fill="red")
    fig.box("monitor", 4, 0, text="Monitor\n监控", fill="grey")
    fig.arrow("data", "right", "prep", "left", label="raw")
    fig.arrow("prep", "bottom", "train", "top", label="features")
    fig.arrow("prep", "bottom", "eval", "top", label="test set")
    fig.arrow("train", "right", "eval", "left", label="model")
    fig.arrow("eval", "bottom", "deploy", "top", label="approved")
    fig.arrow("deploy", "left", "monitor", "right", label="metrics", dashed=True)
    fig.save(p)
    rc = _quiet_validate(p)
    check("complex figure (0 failures)", rc == 0, f"rc={rc}")
    # also verify element count
    items, vb = collect_elements(p)
    boxes = [i for i in items if i["tag"] in ("rect", "ellipse")]
    check("6 boxes present", len(boxes) >= 6, f"got {len(boxes)}")
    shutil.rmtree(d)


def main():
    print("=" * 60)
    print("research-figure skill — test suite")
    print("=" * 60)
    test_template_generates_valid_svg()
    test_validate_passes_good_figure()
    test_validate_catches_overlap()
    test_validate_catches_overflow()
    test_generate_from_json()
    test_multiline_text_fits()
    test_cjk_text_fits()
    test_arrows_connect()
    test_elements_inside_viewbox()
    test_feedback_loop()
    test_end_to_end()
    print(f"\n{'='*60}\nResult: {PASS} passed, {FAIL} failed\n{'='*60}")
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())