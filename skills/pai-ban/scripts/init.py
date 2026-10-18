#!/usr/bin/env python3
"""pai-ban / scripts/init.py —— 给一个书稿目录脚手架

做三件事（不碰源文，不改任何 .md）：

    1. 探测章节目录（CN/ EN/ zh/ en/ chapters/ 或根目录）与章节目录名模式；
    2. 写 <book>/pai-ban.toml（从 assets/pai-ban.toml 复制后按探测结果改值）；
    3. 把 assets/ 复制成 <book>/pai-ban-assets/（preamble + filters），
       让书稿自带一份可版本化的版式快照 —— 技能升级不影响旧书的产物。

用法：
    python3 init.py /path/to/book [--lang zh|en] [--force]
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parents[1]
ASSETS = SKILL_ROOT / "assets"

CHAPTER_DIR_CANDIDATES = ["CN", "cn", "zh", "EN", "en", "chapters", "chapters/zh", "."]
CHAPTER_GLOBS = ["chapter-*.md", "ch*.md", "??-*.md"]


def detect_chapter_dir(book: Path) -> tuple[Path, str]:
    for cand in CHAPTER_DIR_CANDIDATES:
        d = book / cand
        if not d.is_dir():
            continue
        for g in CHAPTER_GLOBS:
            hits = sorted(d.glob(g))
            if len(hits) >= 2:
                return d, g
    return book, "chapter-*.md"


def detect_number_regex(glob: str, d: Path) -> str:
    """从实际文件名里推一个能抓到章号的正则。"""
    names = [p.name for p in sorted(d.glob(glob))]
    for rx in (r"chapter-(\d+)", r"ch(\d+)", r"(\d+)"):
        if names and all(re.search(rx, n) for n in names[:5]):
            return rx
    return r"(\d+)"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="pai-ban 项目脚手架")
    ap.add_argument("book")
    ap.add_argument("--lang", default="zh", choices=["zh", "en"])
    ap.add_argument("--force", action="store_true", help="覆盖已有的 pai-ban.toml")
    args = ap.parse_args(argv)

    book = Path(args.book).resolve()
    if not book.is_dir():
        print(f"[init] 不是目录：{book}", file=sys.stderr)
        return 2

    cfg_path = book / "pai-ban.toml"
    if cfg_path.exists() and not args.force:
        print(f"[init] {cfg_path} 已存在（用 --force 覆盖）")
    else:
        text = (ASSETS / "pai-ban.toml").read_text(encoding="utf-8")
        chap_dir, glob = detect_chapter_dir(book)
        rel = "." if chap_dir == book else chap_dir.name
        rx = detect_number_regex(glob, chap_dir)

        def sub(key: str, val: str) -> None:
            nonlocal text
            # 用函数替换，避免 re.sub 把 TOML 里的 \\ 当转义序列吃掉
            text = re.sub(rf'(?m)^{key}\s*=\s*"[^"]*"',
                          lambda _m, k=key, v=val: f'{k} = "{v}"',
                          text, count=1)

        sub("chapters_dir", rel)
        sub("chapter_glob", glob)
        sub("chapter_number_regex", rx.replace("\\", "\\\\"))
        sub("lang", args.lang)
        sub("title", book.name)
        sub("subtitle", "")
        sub("author", "")
        # date 留空则由构建脚本用当天日期；这里保持模板值
        cfg_path.write_text(text, encoding="utf-8")
        print(f"[init] 写入 {cfg_path}（chapters_dir={rel}, glob={glob}, regex={rx}）")

    dest = book / "pai-ban-assets"
    if dest.exists():
        shutil.rmtree(dest)
    dest.mkdir(parents=True)
    shutil.copy2(ASSETS / "preamble.tex", dest / "preamble.tex")
    shutil.copytree(ASSETS / "filters", dest / "filters")
    if (ASSETS / "reference.docx").exists():
        shutil.copy2(ASSETS / "reference.docx", dest / "reference.docx")
    print(f"[init] 复制资源 → {dest}")

    # 探测结果写一份 JSON 便于人工核对
    chap_dir, glob = detect_chapter_dir(book)
    info = {
        "book": str(book),
        "chapters_dir": str(chap_dir),
        "chapter_glob": glob,
        "chapters_found": [p.name for p in sorted(chap_dir.glob(glob))],
        "figure_dirs": sorted(
            str(p.relative_to(chap_dir)) for p in chap_dir.glob("figures/*") if p.is_dir()),
    }
    (book / "pai-ban-detect.json").write_text(
        json.dumps(info, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[init] 探测 {len(info['chapters_found'])} 个章节文件，"
          f"图片目录 {info['figure_dirs']}")
    print("[init] 下一步：python3 build.py <book> --preview")
    return 0


if __name__ == "__main__":
    sys.exit(main())
