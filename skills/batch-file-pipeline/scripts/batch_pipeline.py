#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
batch_pipeline.py — 批量文件管道工具 (batch-file-pipeline skill)
用法:
  python batch_pipeline.py orient <目录>              # 检测图片旋转方向（只报告）
  python batch_pipeline.py rotate <目录> [angle]      # 批量旋转（默认按检测自动，angle可强制）
  python batch_pipeline.py rename <目录> <映射csv>    # 按 old,new 映射重命名（先校验再改）
  python batch_pipeline.py dedupe <目录>              # 按 SHA-256 去重（列出疑似重复，不删除）
  python batch_pipeline.py verify <目录> <正则>       # 校验命名规范
只读/安全：rotate 输出到 <目录>/rotated_xxx；rename 先列出映射确认；dedupe 只报告不删。
"""
import sys, os, glob, csv, re, hashlib
from PIL import Image

def detect_orientation(path):
    from rapidocr_onnxruntime import RapidOCR
    eng = RapidOCR()
    try:
        result, _ = eng(path)
    except Exception:
        return "ERROR"
    if not result:
        return "NO_TEXT"
    v = t = 0
    for box, text, conf in result[:10]:
        x1, y1 = box[0]; x2, y2 = box[2]
        w, h = x2 - x1, y2 - y1
        t += 1
        if h > w * 1.5:
            v += 1
    return "VERTICAL" if v / max(t, 1) > 0.6 else "OK"

def cmd_orient(directory):
    exts = ("*.jpg", "*.jpeg", "*.png")
    files = []
    for e in exts:
        files += glob.glob(os.path.join(directory, e))
    for f in sorted(files):
        print(f"{os.path.basename(f):40s} {detect_orientation(f)}")

def cmd_rotate(directory, angle=None):
    files = glob.glob(os.path.join(directory, "*.jpg")) + glob.glob(os.path.join(directory, "*.jpeg")) + glob.glob(os.path.join(directory, "*.png"))
    for f in sorted(files):
        base = os.path.basename(f)
        ang = angle
        if ang is None:
            st = detect_orientation(f)
            ang = -90 if st == "VERTICAL" else 0
        if ang == 0:
            print(f"SKIP {base} 方向正常")
            continue
        img = Image.open(f).rotate(ang, expand=True)
        out = os.path.join(directory, f"rotated_{base}")
        img.save(out, "JPEG", quality=95)
        print(f"ROTATE {base} -> {os.path.basename(out)} ({ang}°)")

def cmd_rename(directory, mapping_csv):
    rows = list(csv.reader(open(mapping_csv, encoding="utf-8")))
    plan = [(old.strip(), new.strip()) for old, new in rows if old and new]
    print("重命名计划（确认后执行）:")
    for old, new in plan:
        print(f"  {old}  ->  {new}")
    ok = input("确认执行? [y/N] ").strip().lower()
    if ok != "y":
        print("已取消")
        return
    for old, new in plan:
        src = os.path.join(directory, old)
        dst = os.path.join(directory, new)
        if not os.path.exists(src):
            print(f"SKIP 源不存在: {old}")
            continue
        if os.path.exists(dst):
            print(f"SKIP 目标已存在: {new}")
            continue
        os.rename(src, dst)
        print(f"OK {old} -> {new}")

def cmd_dedupe(directory):
    files = []
    for e in ("*.jpg", "*.jpeg", "*.png", "*.pdf"):
        files += glob.glob(os.path.join(directory, e))
    seen = {}
    dupes = []
    for f in sorted(files):
        h = hashlib.sha256(open(f, "rb").read()).hexdigest()
        if h in seen:
            dupes.append((seen[h], os.path.basename(f)))
        else:
            seen[h] = os.path.basename(f)
    if dupes:
        print("疑似重复（未删除，请人工确认）:")
        for keep, dup in dupes:
            print(f"  保留: {keep}")
            print(f"  重复: {dup}")
    else:
        print("无重复文件")

def cmd_verify(directory, regex):
    files = []
    for e in ("*.jpg", "*.jpeg", "*.png", "*.pdf", "*.docx", "*.xlsx"):
        files += glob.glob(os.path.join(directory, e))
    bad = [os.path.basename(f) for f in files if not re.search(regex, os.path.basename(f))]
    if bad:
        print("不合规范:")
        for b in bad:
            print("  -", b)
        sys.exit(1)
    print(f"OK: {len(files)} 个文件全部符合规范")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(__doc__); sys.exit(1)
    action, d = sys.argv[1], sys.argv[2]
    if action == "orient":
        cmd_orient(d)
    elif action == "rotate":
        cmd_rotate(d, int(sys.argv[3]) if len(sys.argv) > 3 else None)
    elif action == "rename":
        cmd_rename(d, sys.argv[3])
    elif action == "dedupe":
        cmd_dedupe(d)
    elif action == "verify":
        cmd_verify(d, sys.argv[3])
    else:
        print("未知动作"); sys.exit(2)
