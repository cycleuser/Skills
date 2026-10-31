#!/usr/bin/env python3
"""humanize_lint.py 的自测：指标、命中、打分、退出码。

跑法：
    cd Skills/skills/humanizer && python3 tests/test_lint.py
"""
from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "humanize_lint.py"
SAMPLES = ROOT / "tests" / "samples"

sys.path.insert(0, str(SCRIPT.parent))
import humanize_lint as H


def run(args: list[str], stdin: str | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        input=stdin, capture_output=True, text=True, check=False,
    )


def read(name: str) -> str:
    return (SAMPLES / name).read_text(encoding="utf-8")


class TestBasics(unittest.TestCase):
    def test_lang_detection(self):
        self.assertEqual(H.detect_lang("这是一段纯中文，用来测试语言判断。"), "zh")
        self.assertEqual(H.detect_lang("This is a plain English sentence."), "en")
        self.assertEqual(H.detect_lang("我们用 skill 做 workflow。"), "zh")

    def test_sentence_split_zh(self):
        sents = H.split_sentences("今天下雨。我没带伞！你呢？", "zh")
        self.assertEqual(len(sents), 3)

    def test_sentence_split_en_handles_abbrev(self):
        sents = H.split_sentences("Dr. Chen wrote it. We read it.", "en")
        self.assertEqual(len(sents), 2)

    def test_short_text_note(self):
        rep = H.analyze("很短。", "zh")
        self.assertTrue(any("样本偏短" in n for n in rep.notes))


class TestScoring(unittest.TestCase):
    def test_ai_beats_human_zh(self):
        ai = H.analyze(read("ai_zh.md"), "zh")
        hu = H.analyze(read("human_zh.md"), "zh")
        self.assertGreater(ai.score, 60, f"AI zh score too low: {ai.score:.1f}")
        self.assertLess(hu.score, 35, f"human zh score too high: {hu.score:.1f}")
        self.assertGreater(ai.score - hu.score, 30)

    def test_ai_beats_human_en(self):
        ai = H.analyze(read("ai_en.md"), "en")
        hu = H.analyze(read("human_en.md"), "en")
        self.assertGreater(ai.score, 55, f"AI en score too low: {ai.score:.1f}")
        self.assertLess(hu.score, 35, f"human en score too high: {hu.score:.1f}")
        self.assertGreater(ai.score - hu.score, 30)

    def test_expected_hits_zh(self):
        rep = H.analyze(read("ai_zh.md"), "zh")
        ids = {h.id for h in rep.hits}
        for need in ("Z01", "Z02", "Z03", "Z05", "Z18", "Z21"):
            self.assertIn(need, ids, f"missing pattern {need}")

    def test_expected_hits_en(self):
        rep = H.analyze(read("ai_en.md"), "en")
        ids = {h.id for h in rep.hits}
        for need in ("E01", "E03", "E06", "E11", "E13"):
            self.assertIn(need, ids, f"missing pattern {need}")

    def test_no_duplicate_pattern_ids(self):
        rep = H.analyze(read("ai_en.md"), "en")
        ids = [h.id for h in rep.hits]
        self.assertEqual(len(ids), len(set(ids)), f"duplicate ids: {ids}")

    def test_tech_profile_is_looser(self):
        text = read("ai_en.md")
        prose = H.analyze(text, "en", "prose").score
        tech = H.analyze(text, "en", "tech").score
        self.assertLessEqual(tech, prose)

    def test_tech_doc_needs_tech_profile(self):
        text = read("human_en_tech.md")
        prose = H.analyze(text, "en", "prose").score
        tech = H.analyze(text, "en", "tech").score
        self.assertLess(tech, prose, "tech profile should forgive legitimate lists")
        self.assertLess(tech, 20)

    def test_formal_human_samples_stay_low(self):
        for name, lang in (("human_zh_doc.md", "zh"),
                           ("human_zh_academic.md", "zh")):
            score = H.analyze(read(name), lang).score
            self.assertLess(score, 20, f"{name} false positive: {score:.1f}")

    def test_documented_examples_improve(self):
        for before, after, lang in (("example_zh_before.md", "example_zh_after.md", "zh"),
                                    ("example_en_before.md", "example_en_after.md", "en")):
            b = H.analyze(read(before), lang).score
            a = H.analyze(read(after), lang).score
            self.assertGreater(b - a, 25, f"{before}: {b:.1f} -> {a:.1f}")

    def test_mid_sample_in_light_band(self):
        score = H.analyze(read("mid_zh.md"), "zh").score
        self.assertGreater(score, 6)
        self.assertLess(score, 40)

    def test_chinese_curly_quotes_are_not_residue(self):
        text = "他写道：“这个方案我不同意。”然后合上了本子。"
        rep = H.analyze(text, "zh")
        self.assertLess(rep.subscores["residue"], 30)


class TestCli(unittest.TestCase):
    def test_score_output(self):
        r = run(["score", str(SAMPLES / "ai_zh.md")])
        self.assertEqual(r.returncode, 1)
        parts = r.stdout.strip().split("\t")
        self.assertGreater(float(parts[0]), 60)
        self.assertEqual(parts[2], "zh")

    def test_json_schema(self):
        r = run(["check", str(SAMPLES / "ai_en.md"), "--json"])
        self.assertEqual(r.returncode, 1)
        data = json.loads(r.stdout)
        for key in ("lang", "score", "band", "subscores", "metrics", "hits", "pass"):
            self.assertIn(key, data)
        self.assertFalse(data["pass"])
        self.assertTrue(data["hits"][0]["advice"])

    def test_stdin(self):
        r = run(["score", "-"], stdin=read("human_en.md"))
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_max_score_override(self):
        r = run(["check", str(SAMPLES / "human_zh.md"), "--max-score", "1"])
        self.assertEqual(r.returncode, 1)
        r = run(["check", str(SAMPLES / "ai_zh.md"), "--max-score", "99"])
        self.assertEqual(r.returncode, 0)

    def test_empty_input(self):
        r = run(["check", "-"], stdin="   ")
        self.assertEqual(r.returncode, 2)

    def test_diff_mode(self):
        r = run(["diff", str(SAMPLES / "ai_zh.md"), str(SAMPLES / "human_zh.md"), "--no-color"])
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("改写前", r.stdout)
        self.assertIn("已清除", r.stdout)

    def test_diff_requires_two_files(self):
        r = run(["diff", str(SAMPLES / "ai_zh.md")])
        self.assertEqual(r.returncode, 2)

    def test_rules_listing(self):
        r = run(["rules"])
        self.assertEqual(r.returncode, 0)
        self.assertIn("Z01", r.stdout)
        self.assertIn("E01", r.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=2)
