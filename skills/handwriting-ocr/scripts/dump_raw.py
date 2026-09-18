"""Dump per-source `.raw.txt` and `.raw.md` files from raw_ocr.json.

After `batch_ocr.py` produces raw_ocr.json, this helper breaks the JSON into
per-source plain-text and markdown files so the evaluation script can read
them as `<stem>.raw.txt`.

For multi-page PDFs, all page text is joined with `\n\n---\n\n` separators so
page boundaries are recoverable from the text alone.

Usage:
    python dump_raw.py raw_ocr.json [--out-dir .] [--format txt,md]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path


def natural_key(s: str):
    return [int(t) if t.isdigit() else t for t in re.split(r"(\d+)", s)]


def group_by_source(items: list[dict]) -> dict[str, list[dict]]:
    groups: dict[str, list[dict]] = defaultdict(list)
    for it in items:
        groups[it["source_file"]].append(it)
    for k in groups:
        groups[k].sort(key=lambda x: x.get("page", 1))
    return dict(sorted(groups.items(), key=lambda kv: natural_key(kv[0])))


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Dump per-source text files from raw_ocr.json")
    ap.add_argument("json_path", help="batch_ocr.py 生成的 raw_ocr.json")
    ap.add_argument("--out-dir", default=".", help="输出目录（默认 JSON 同级）")
    ap.add_argument("--format", default="txt,md",
                    help="输出格式，逗号分隔，可选: txt, md（默认 txt,md）")
    args = ap.parse_args(argv)

    json_path = Path(args.json_path)
    if not json_path.exists():
        print(f"[ERROR] 找不到 {json_path}", file=sys.stderr)
        return 2
    data = json.loads(json_path.read_text(encoding="utf-8"))
    items = data.get("items", [])
    if not items:
        print("[ERROR] raw_ocr.json 中没有 items。", file=sys.stderr)
        return 2

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    formats = {f.strip().lower() for f in args.format.split(",") if f.strip()}

    groups = group_by_source(items)
    n_total = 0
    for source_file, group in groups.items():
        stem = Path(source_file).stem
        n_total += 1
        joined_text = "\n\n---\n\n".join(
            (it.get("raw_text") or it.get("error") or "")
            for it in group
        )
        joined_with_pages = []
        for it in group:
            tag = f"[[page {it['page']} | conf={it['confidence']}]]"
            joined_with_pages.append(tag + "\n" + (it.get("raw_text") or it.get("error") or ""))
        annotated = "\n\n---\n\n".join(joined_with_pages)

        if "txt" in formats:
            (out_dir / f"{stem}.raw.txt").write_text(joined_text, encoding="utf-8")
        if "md" in formats:
            md = [f"# Raw OCR — {source_file}",
                  "",
                  f"> 来源文件: `{source_file}`  ",
                  f"> 页数: {len(group)}  ",
                  f"> 平均置信度: {sum(it.get('confidence', 0) for it in group) / len(group):.3f}",
                  ""]
            for it in group:
                md.append(f"## 第 {it['page']} 页（置信度 {it.get('confidence', 0):.3f}）")
                md.append("")
                md.append(it.get("raw_text") or f"_OCR 失败: {it.get('error')}_")
                md.append("")
            (out_dir / f"{stem}.raw.md").write_text("\n".join(md), encoding="utf-8")

    print(f"[OK] 共导出 {n_total} 个源文件 → {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())