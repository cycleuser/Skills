#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
embed_evidence.py — 证据图收集与嵌入 (application-bundle skill)
用法:
  python embed_evidence.py prep <目录> <输出目录>   # 收集证书图：jpg/png直拷，pdf转首屏png
  python embed_evidence.py build <正文模板.py>      # 见 SKILL.md：用 python-docx 逐图嵌入并加注
说明：证据图为只读引用，不改原件；pdf 转 png 用 pymupdf，jpg 必须转真 PNG 才能被 python-docx 嵌入。
"""
import sys, os, glob, shutil
from PIL import Image
import fitz

def prep(src_dir, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    exts = ("*.jpg", "*.jpeg", "*.png", "*.pdf")
    files = []
    for e in exts:
        files += glob.glob(os.path.join(src_dir, e))
    files = sorted(files)
    for f in files:
        base = os.path.basename(f)
        ext = os.path.splitext(f)[1].lower()
        if ext in (".jpg", ".jpeg"):
            img = Image.open(f).convert("RGB")
            out = os.path.join(out_dir, os.path.splitext(base)[0] + ".png")
            img.save(out, "PNG")
            print(f"PNG  {base} -> {os.path.basename(out)}")
        elif ext == ".png":
            shutil.copy(f, os.path.join(out_dir, base))
            print(f"COPY {base}")
        elif ext == ".pdf":
            doc = fitz.open(f)
            pix = doc[0].get_pixmap(dpi=110)
            out = os.path.join(out_dir, os.path.splitext(base)[0] + ".png")
            pix.save(out)
            print(f"PDF->PNG {base} ({len(doc)}页,取第1页)")
    print(f"完成，共 {len(files)} 个源文件，输出到 {out_dir}")

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print(__doc__); sys.exit(1)
    if sys.argv[1] == "prep":
        prep(sys.argv[2], sys.argv[3])
    else:
        print("未知命令"); sys.exit(2)
