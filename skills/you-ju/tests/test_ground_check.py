#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""test_ground_check.py — ground_check.py 自测套件

用最小构造样本逐一验证各类违规检测与合法操作放行。
不依赖 corpus（corpus 上另有端到端 A/B 检查），全部样本内嵌。

运行::

    python3 test_ground_check.py
    pytest test_ground_check.py -v

Exit code 0 仅当全部检查通过。
"""

from __future__ import annotations

import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "scripts"))

import ground_check as gc  # noqa: E402

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


def write_tmp(content, suffix=".md"):
    fd, path = tempfile.mkstemp(suffix=suffix)
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write(content)
    return path


def write_named(content, name):
    """写指定文件名的临时文件 (C1 测试需要 source_S.md 之类可映射编号的名字)"""
    d = tempfile.mkdtemp()
    path = os.path.join(d, name)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return path


# 最小源文档: 一个虚构产品 + 两个数字
SOURCE = """# 源 S — 测试芯片
星尘-7 是边缘推理芯片，采用 12nm 工艺。
算力 8 TOPS（INT8），功耗 2.1 W。
## 未提供
FP16 算力数值未给出。
"""


def make_whitelist(extra_entities=None, extra_numbers=None):
    """从 SOURCE 建白名单, 允许测试注入额外合法项"""
    fd, path = tempfile.mkstemp(suffix=".md")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write(SOURCE)
    wl = gc.build_whitelist([path])
    os.unlink(path)
    if extra_entities:
        wl["entities"] = sorted(set(wl["entities"]) | set(extra_entities))
    if extra_numbers:
        wl["numbers"] = sorted(set(wl["numbers"]) | set(extra_numbers))
    fd, path = tempfile.mkstemp(suffix=".json")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        json.dump(wl, f, ensure_ascii=False)
    return path


# ---------------------------------------------------------------- E1 实体泄漏

def test_e1_detects_fabricated_entity():
    wl = make_whitelist()
    src = write_named(SOURCE, "source_S.md")
    out = write_tmp("星尘-7 采用台积电 12nm 工艺。\n")
    r = gc.check_output(out, json.load(open(wl)), [src])
    ents = "".join(v["entity"] for v in r["E1"])
    # 报告可能给收缩窗口 '采用台积电', 断言检查目标词包含即可
    check("E1 检出编造实体『台积电』", "台积电" in ents, f"got {ents}")


def test_e1_allows_source_entity():
    wl = make_whitelist()
    src = write_named(SOURCE, "source_S.md")
    out = write_tmp("星尘-7 采用 12nm 工艺。\n")
    r = gc.check_output(out, json.load(open(wl)), [src])
    check("E1 放行来源实体『星尘-7』", len(r["E1"]) == 0, f"got {r['E1']}")


def test_e1_allows_known_english_entity():
    wl = make_whitelist(extra_entities=["MobileNetV2"])
    src = write_named(SOURCE, "source_S.md")
    out = write_tmp("星尘-7 的竞品包括 MobileNetV2 优化版本。\n")
    r = gc.check_output(out, json.load(open(wl)), [src])
    ents = [v["entity"] for v in r["E1"]]
    check("E1 放行白名单英文实体", "MobileNetV2" not in ents, f"got {ents}")


def test_e1_meta_lines_skipped():
    wl = make_whitelist()
    src = write_named(SOURCE, "source_S.md")
    out = write_tmp("> 本文件是 A/B 实验样例：T2 任务。\n星尘-7 算力 8 TOPS。\n")
    r = gc.check_output(out, json.load(open(wl)), [src])
    r = gc.check_output(out, json.load(open(wl)), [])
    ents = [v["entity"] for v in r["E1"]]
    check("E1 跳过引用块元信息行", all(e not in ents for e in ("A/B", "T2")), f"got {ents}")


# ---------------------------------------------------------------- N1 数字泄漏

def test_n1_detects_fabricated_number():
    wl = make_whitelist()
    out = write_tmp("星尘-7 功耗 2.1 W，FP16 算力 4 TOPS。\n")
    r = gc.check_output(out, json.load(open(wl)), [])
    nums = [v["number"] for v in r["N1"]]
    check("N1 检出编造数字『4 TOPS』", any("4 TOPS" in n for n in nums), f"got {nums}")


def test_n1_allows_source_number():
    wl = make_whitelist()
    out = write_tmp("星尘-7 功耗 2.1 W，算力 8 TOPS。\n")
    r = gc.check_output(out, json.load(open(wl)), [])
    check("N1 放行来源数字", len(r["N1"]) == 0, f"got {r['N1']}")


def test_n1_unit_conversion_equivalence():
    """2100 mW 与 2.1 W 是同一断言, 归一化后放行"""
    wl = make_whitelist()
    out = write_tmp("星尘-7 功耗 2100 mW。\n")
    r = gc.check_output(out, json.load(open(wl)), [])
    check("N1 单位换算等价 (2.1 W == 2100 mW)", len(r["N1"]) == 0, f"got {r['N1']}")


def test_n1_precision_drift_detected():
    """来源 3.8, 输出 3.81 — 改变精度=改变断言, 应判泄漏"""
    wl = make_whitelist()
    out = write_tmp("星尘-7 能效比约 3.81 TOPS/W。\n")
    r = gc.check_output(out, json.load(open(wl)), [])
    check("N1 检出精度漂移 (3.8→3.81)", len(r["N1"]) == 1, f"got {r['N1']}")


# ---------------------------------------------------------------- C1 引用失配

def test_c1_detects_wrong_line():
    src = write_named(SOURCE, "source_S.md")
    # FP16 声明在 L5, 标 L2 → 偏 3 行, 超出 ±1 容忍
    out = write_tmp("FP16 算力数值未给出 [S:L2]。\n")
    r = gc.check_output(out, json.load(open(make_whitelist())), [src])
    check("C1 检出行号错位", len(r["C1"]) == 1, f"got {r['C1']}")


def test_c1_allows_correct_line():
    src = write_named(SOURCE, "source_S.md")
    out = write_tmp("星尘-7 功耗 2.1 W [S:L3]。\n")
    r = gc.check_output(out, json.load(open(make_whitelist())), [src])
    check("C1 放行正确行号", len(r["C1"]) == 0, f"got {r['C1']}")


def test_c1_detects_unknown_source_id():
    src = write_named(SOURCE, "source_S.md")
    out = write_tmp("星尘-7 算力 8 TOPS [X:L2]。\n")
    r = gc.check_output(out, json.load(open(make_whitelist())), [src])
    check("C1 检出未登记来源编号", len(r["C1"]) == 1 and "X" in r["C1"][0]["reason"],
          f"got {r['C1']}")


def test_c1_multi_citation_line_split():
    """一行三标记, 各段分别回查 (回归: 曾整行只取一个片段导致误报)"""
    src = write_named(SOURCE, "source_S.md")
    out = write_tmp("星尘-7 算力 8 TOPS [S:L3]，功耗 2.1 W [S:L3]，是边缘推理芯片 [S:L2]。\n")
    r = gc.check_output(out, json.load(open(make_whitelist())), [src])
    check("C1 多标记分行回查", len(r["C1"]) == 0, f"got {r['C1']}")


# ---------------------------------------------------------------- Q1 越权回答

def test_q1_candidate_contradiction():
    wl = make_whitelist()
    out = write_tmp("来源未给出 FP16 算力，实测约 4 TOPS。\n")
    r = gc.check_output(out, json.load(open(wl)), [])
    check("Q1 候选: 同句数值+未给矛盾", len(r["Q1_candidates"]) == 1, f"got {r['Q1_candidates']}")


def test_q1_declaration_not_flagged():
    """纯声明句('来源未提及X')是正确处理, 不应触发 Q1 候选"""
    wl = make_whitelist()
    out = write_tmp("FP16 算力来源未提及。\n")
    r = gc.check_output(out, json.load(open(wl)), [])
    check("Q1 放行纯缺口声明句", len(r["Q1_candidates"]) == 0, f"got {r['Q1_candidates']}")


# ---------------------------------------------------------------- align

def test_align_grounded_vs_ungrounded():
    src = write_named(SOURCE, "source_S.md")
    out = write_tmp("星尘-7 是边缘推理芯片。\n星尘-7 支持车规级认证。\n")
    r = gc.align_output(out, [src])
    by = {x["line"]: x["status"] for x in r}
    check("align: 有据句 → grounded", by.get(1) == "grounded", f"got {by}")
    check("align: 无据句 → ungrounded", by.get(2) == "ungrounded", f"got {by}")


def test_align_declared_gap():
    src = write_named(SOURCE, "source_S.md")
    out = write_tmp("FP16 算力来源未提及。\n")
    r = gc.align_output(out, [src])
    check("align: 声明缺口句 → declared-gap", r[0]["status"] == "declared-gap", f"got {r}")


def test_align_partial():
    src = write_named(SOURCE, "source_S.md")
    out = write_tmp("星尘-7 是边缘推理芯片，采用 12nm 工艺，支持 8K 视频解码。\n")
    r = gc.align_output(out, [src])
    check("align: 半有据句 → partial", r[0]["status"] == "partial", f"got {r}")


# ---------------------------------------------------------------- coverage

def test_coverage_counts():
    src = write_named(SOURCE, "source_S.md")
    out = write_tmp("星尘-7 算力 8 TOPS。\n")
    r = gc.coverage(out, [src])
    check("coverage: 覆盖计数正确", r["total"] >= 3 and r["covered"] >= 1, f"got {r}")


# ---------------------------------------------------------------- run

def main():
    print("== ground_check 自测 ==")
    for fn in sorted(k for k in globals() if k.startswith("test_")):
        print(f"-- {fn}")
        globals()[fn]()
    print(f"\n== 结果: {PASS} passed, {FAIL} failed ==")
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())