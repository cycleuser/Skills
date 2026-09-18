"""Evaluate OCR / refinement output against human-labeled ground truth.

Pairing convention (default):
    test_dir/
        01.png            # source
        01.gt.md          # ground truth text  (or .gt.txt)
        01.gt.json        # optional structured GT with "text" + "keywords"
        01.raw.txt        # optional raw OCR text (no refinement)
        01.refined.txt    # optional refined text (post-LLM)
        02.png, 02.gt.md, ...

The script auto-detects which candidates are present and computes:
    - CER (Character Error Rate, normalized edit distance / len(GT))
    - WER (Word / token-level edit distance; for Chinese, character-level WER
          using jieba if installed, otherwise falls back to char-level)
    - Keyword recall (how many GT keywords appear verbatim in candidate)
    - Overall 0-100 score: 0.7 * (1 - CER) + 0.3 * keyword_recall

Usage:
    python evaluate.py <test_dir> [--report score_report.md]
                          [--json metrics.json] [--strict] [--no-keywords]

Exit codes:
    0  evaluation ran (some pairs may have failed individually)
    2  test_dir missing or no (image, gt) pairs found
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field, asdict
from pathlib import Path


IMG_EXT = {".png", ".jpg", ".jpeg", ".bmp", ".webp", ".tif", ".tiff"}


def levenshtein(a: str, b: str) -> int:
    if a == b:
        return 0
    if not a:
        return len(b)
    if not b:
        return len(a)
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        curr = [i] + [0] * len(b)
        for j, cb in enumerate(b, 1):
            curr[j] = min(
                prev[j] + 1,           # deletion
                curr[j - 1] + 1,       # insertion
                prev[j - 1] + (ca != cb),  # substitution
            )
        prev = curr
    return prev[-1]


def cer(ref: str, hyp: str) -> float:
    ref = ref.strip()
    hyp = hyp.strip()
    if not ref:
        return 0.0 if not hyp else 1.0
    return levenshtein(ref, hyp) / len(ref)


def tokenize_for_wer(text: str, use_jieba: bool) -> list[str]:
    if use_jieba:
        try:
            import jieba  # type: ignore
            return [t for t in jieba.cut(text) if t.strip()]
        except ImportError:
            pass
    # Fallback — split into CJK chars + ASCII word runs
    tokens: list[str] = []
    buf: list[str] = []
    for ch in text:
        if "\u4e00" <= ch <= "\u9fff" or "\u3400" <= ch <= "\u4dbf":
            if buf:
                tokens.append("".join(buf))
                buf = []
            tokens.append(ch)
        elif ch.isalnum():
            buf.append(ch)
        else:
            if buf:
                tokens.append("".join(buf))
                buf = []
    if buf:
        tokens.append("".join(buf))
    return tokens


def wer(ref: str, hyp: str, use_jieba: bool = True) -> float:
    ref_t = tokenize_for_wer(ref, use_jieba)
    hyp_t = tokenize_for_wer(hyp, use_jieba)
    if not ref_t:
        return 0.0 if not hyp_t else 1.0
    return levenshtein(" ".join(ref_t), " ".join(hyp_t)) / len(" ".join(ref_t))


def keyword_recall(ref_keywords: list[str], hyp: str) -> tuple[float, int, int, list[str]]:
    if not ref_keywords:
        return 0.0, 0, 0, []
    hyp_norm = hyp
    found, miss = 0, []
    for kw in ref_keywords:
        if kw and kw in hyp_norm:
            found += 1
        else:
            miss.append(kw)
    return found / len(ref_keywords), found, len(ref_keywords), miss


def load_gt(gt_path: Path) -> tuple[str, list[str]]:
    """Return (text, keywords)."""
    json_path = gt_path.with_suffix(".json")
    if json_path.exists():
        try:
            data = json.loads(json_path.read_text(encoding="utf-8"))
            return data.get("text", gt_path.read_text(encoding="utf-8").strip()), \
                list(data.get("keywords", []))
        except Exception:
            pass
    return gt_path.read_text(encoding="utf-8").strip(), []


def find_pairs(test_dir: Path) -> list[tuple[Path | None, Path, str]]:
    """Return [(image_or_None, gt, stem)] for each pair found.

    Image is optional — evaluation can run against text-only pairs (e.g. when
    the user just wants to score a refined output they already produced).
    """
    pairs: list[tuple[Path | None, Path, str]] = []
    seen: set[str] = set()

    def _try_match(stem: str) -> Path | None:
        for ext in IMG_EXT:
            cand = test_dir / f"{stem}{ext}"
            if cand.exists():
                return cand
        return None

    for gt in sorted(list(test_dir.glob("*.gt.md")) + list(test_dir.glob("*.gt.txt"))):
        if gt.name.endswith(".gt.md"):
            stem = gt.name[: -len(".gt.md")]
        elif gt.name.endswith(".gt.txt"):
            stem = gt.name[: -len(".gt.txt")]
        else:
            continue
        if stem in seen:
            continue
        seen.add(stem)
        img = _try_match(stem)
        if img is None:
            print(f"[INFO] {gt.name} 没有对应图片（文本-only 对照样，仍可评估）。", file=sys.stderr)
        pairs.append((img, gt, stem))
    return pairs


@dataclass
class PairResult:
    id: str
    image: str
    gt_chars: int
    raw: dict = field(default_factory=dict)
    refined: dict = field(default_factory=dict)


def evaluate_pair(
    stem: str,
    img: Path | None,
    gt_text: str,
    gt_keywords: list[str],
    test_dir: Path,
    use_jieba: bool,
) -> PairResult:
    res = PairResult(
        id=stem,
        image=img.name if img is not None else "(text-only)",
        gt_chars=len(gt_text),
    )

    raw_path = test_dir / f"{stem}.raw.txt"
    if raw_path.exists():
        hyp = raw_path.read_text(encoding="utf-8")
        res.raw = {
            "present": True,
            "cer": round(cer(gt_text, hyp), 4),
            "wer": round(wer(gt_text, hyp, use_jieba=use_jieba), 4),
            "char_count": len(hyp),
        }
        if gt_keywords:
            r, fcount, total, miss = keyword_recall(gt_keywords, hyp)
            res.raw["keyword_recall"] = round(r, 4)
            res.raw["keyword_found"] = fcount
            res.raw["keyword_total"] = total
            res.raw["keyword_missing"] = miss
    else:
        res.raw = {"present": False}

    ref_path = test_dir / f"{stem}.refined.txt"
    if ref_path.exists():
        hyp = ref_path.read_text(encoding="utf-8")
        res.refined = {
            "present": True,
            "cer": round(cer(gt_text, hyp), 4),
            "wer": round(wer(gt_text, hyp, use_jieba=use_jieba), 4),
            "char_count": len(hyp),
        }
        if gt_keywords:
            r, fcount, total, miss = keyword_recall(gt_keywords, hyp)
            res.refined["keyword_recall"] = round(r, 4)
            res.refined["keyword_found"] = fcount
            res.refined["keyword_total"] = total
            res.refined["keyword_missing"] = miss
    else:
        res.refined = {"present": False}
    return res


def score_from(metrics: dict, has_keywords: bool) -> float:
    cer_v = metrics.get("cer", 1.0)
    if has_keywords:
        kr = metrics.get("keyword_recall", 0.0)
        return max(0.0, min(100.0, 0.7 * (1 - cer_v) * 100 + 0.3 * kr * 100))
    return max(0.0, min(100.0, (1 - cer_v) * 100))


def summarize(results: list[PairResult]) -> dict:
    def avg(field_name: str, source: str, present_only: bool = True) -> float:
        vals = []
        for r in results:
            block = getattr(r, source)
            if not block.get("present", False) and present_only:
                continue
            if field_name in block:
                vals.append(block[field_name])
        return round(sum(vals) / len(vals), 4) if vals else 0.0

    raw_cer = avg("cer", "raw")
    raw_wer = avg("wer", "raw")
    ref_cer = avg("cer", "refined")
    ref_wer = avg("wer", "refined")
    raw_kr = avg("keyword_recall", "raw")
    ref_kr = avg("keyword_recall", "refined")

    has_kw = any(r.refined.get("keyword_total", 0) > 0 or r.raw.get("keyword_total", 0) > 0
                 for r in results)

    raw_score = score_from({"cer": raw_cer, "keyword_recall": raw_kr}, has_kw)
    ref_score = score_from({"cer": ref_cer, "keyword_recall": ref_kr}, has_kw)

    return {
        "raw_cer": raw_cer,
        "raw_wer": raw_wer,
        "raw_keyword_recall": raw_kr,
        "raw_score": round(raw_score, 2),
        "refined_cer": ref_cer,
        "refined_wer": ref_wer,
        "refined_keyword_recall": ref_kr,
        "refined_score": round(ref_score, 2),
        "has_keywords": has_kw,
        "n_pairs": len(results),
    }


def render_report(results: list[PairResult], summary: dict, test_dir: Path) -> str:
    lines: list[str] = []
    lines.append(f"# OCR 评估报告 — `{test_dir}`")
    lines.append("")
    lines.append(f"共评估 **{summary['n_pairs']}** 对样本。"
                 + (" 已启用关键词检索评估。" if summary["has_keywords"] else ""))
    lines.append("")
    lines.append("## 总分（0-100）")
    lines.append("")
    lines.append("| 阶段 | CER | WER | 关键词召回 | 综合分 |")
    lines.append("|------|-----|-----|-----------|--------|")
    lines.append(
        f"| 原始 OCR | {summary['raw_cer']:.3f} | {summary['raw_wer']:.3f} "
        f"| {summary['raw_keyword_recall']:.3f} | **{summary['raw_score']}** |"
    )
    lines.append(
        f"| LLM 润色后 | {summary['refined_cer']:.3f} | {summary['refined_wer']:.3f} "
        f"| {summary['refined_keyword_recall']:.3f} | **{summary['refined_score']}** |"
    )
    lines.append("")
    lines.append("> 综合分公式：`0.7 × (1-CER) + 0.3 × 关键词召回`（无关键词时仅 CER）。")
    lines.append("")

    lines.append("## 逐条详情")
    lines.append("")
    lines.append("| 样本 | 原始 CER | 原始关键词召回 | 润色 CER | 润色关键词召回 |")
    lines.append("|------|---------|---------------|---------|---------------|")
    for r in results:
        rk = r.raw.get("cer", "—")
        rkr = r.raw.get("keyword_recall", "—")
        ck = r.refined.get("cer", "—")
        ckr = r.refined.get("keyword_recall", "—")
        def fmt(v):
            return f"{v:.3f}" if isinstance(v, float) else v
        lines.append(
            f"| `{r.id}` | {fmt(rk)} | {fmt(rkr)} | {fmt(ck)} | {fmt(ckr)} |"
        )
    lines.append("")

    # 失败/缺失样本
    missing = [r for r in results
               if not r.raw.get("present") and not r.refined.get("present")]
    if missing:
        lines.append("## 未生成候选的样本（请先跑 OCR 与润色）")
        lines.append("")
        for r in missing:
            lines.append(f"- `{r.id}`（{r.image}）")
        lines.append("")

    # 关键词遗漏最多的样本
    if summary["has_keywords"]:
        misses = []
        for r in results:
            for stage in ("raw", "refined"):
                miss = getattr(r, stage).get("keyword_missing", [])
                if miss:
                    misses.append((r.id, stage, miss))
        if misses:
            lines.append("## 关键词遗漏（润色后仍缺）")
            lines.append("")
            for sid, stage, miss in misses:
                if stage == "refined":
                    lines.append(f"- `{sid}`：{', '.join(miss)}")
            lines.append("")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Evaluate OCR/refinement against ground truth")
    ap.add_argument("test_dir", help="测试集目录（包含 *.gt.md 与同名图片）")
    ap.add_argument("--report", default="score_report.md", help="Markdown 报告路径")
    ap.add_argument("--json", default="metrics.json", help="详细指标 JSON 路径")
    ap.add_argument("--no-jieba", action="store_true",
                    help="不使用 jieba（默认尝试加载以获得更好的中文 WER）")
    ap.add_argument("--no-keywords", action="store_true",
                    help="关闭关键词召回评估")
    args = ap.parse_args(argv)

    test_dir = Path(args.test_dir)
    if not test_dir.exists():
        print(f"[ERROR] 目录不存在: {test_dir}", file=sys.stderr)
        return 2

    pairs = find_pairs(test_dir)
    if not pairs:
        print(f"[ERROR] 在 {test_dir} 找不到 (图片, *.gt.md) 配对样本。", file=sys.stderr)
        return 2

    use_jieba = not args.no_jieba
    results: list[PairResult] = []
    for img, gt, stem in pairs:
        text, kws = load_gt(gt)
        if args.no_keywords:
            kws = []
        results.append(evaluate_pair(stem, img, text, kws, test_dir, use_jieba))

    summary = summarize(results)

    report_path = Path(args.report)
    if not report_path.is_absolute():
        report_path = (test_dir / report_path).resolve()
    json_path = Path(args.json)
    if not json_path.is_absolute():
        json_path = (test_dir / json_path).resolve()

    report_path.write_text(render_report(results, summary, test_dir), encoding="utf-8")
    json_path.write_text(
        json.dumps({
            "summary": summary,
            "pairs": [asdict(r) for r in results],
        }, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(f"[OK] 综合分（润色后）: {summary['refined_score']} / 100")
    print(f"     报告: {report_path}")
    print(f"     JSON: {json_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())