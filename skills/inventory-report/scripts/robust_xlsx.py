#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
robust_xlsx.py — 健壮 xlsx → 文本行解析器（兼容 WPS/异常样式文件）
openpyxl 遇到 WPS 生成的异常 stylesheet 常抛 TypeError(Fill 等)，本脚本绕过
样式层，直接用 zipfile+XML 解析 sharedStrings + 各 sheet 的单元格文本。

用法:
  python robust_xlsx.py <file.xlsx> [sheet名...]   # 转储文本
  python robust_xlsx.py <file.xlsx> list           # 列出 sheet 名
只读操作。
"""
import sys, re, zipfile
import xml.etree.ElementTree as ET

NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
T = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}t"

def col_to_idx(ref):
    m = re.match(r"([A-Z]+)(\d+)", ref)
    col = m.group(1)
    idx = 0
    for ch in col:
        idx = idx * 26 + (ord(ch) - 64)
    return idx - 1

def load_shared(z):
    shared = []
    if "xl/sharedStrings.xml" in z.namelist():
        root = ET.fromstring(z.read("xl/sharedStrings.xml"))
        for si in root.findall("m:si", NS):
            shared.append("".join(t.text or "" for t in si.iter(T)))
    return shared

def sheet_targets(z):
    wb = ET.fromstring(z.read("xl/workbook.xml"))
    wbrels = ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))
    targets = {}
    for rel in wbrels:
        targets[rel.get("Id")] = rel.get("Target")
    out = []
    for sh in wb.find("m:sheets", NS):
        name = sh.get("name")
        rid = sh.get("{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id")
        tgt = (targets.get(rid) or "").lstrip("/")
        if not tgt.startswith("xl/"):
            tgt = "xl/" + tgt
        out.append((name, tgt))
    return out

def dump(path, wanted=None):
    z = zipfile.ZipFile(path)
    shared = load_shared(z)
    for name, tgt in sheet_targets(z):
        if wanted and name not in wanted:
            continue
        if tgt not in z.namelist():
            continue
        root = ET.fromstring(z.read(tgt))
        print(f"\n===== SHEET: {name} =====")
        for row in root.findall("m:sheetData/m:row", NS):
            cells = {}
            for c in row.findall("m:c", NS):
                cidx = col_to_idx(c.get("r"))
                v = c.find("m:v", NS)
                istr = c.find("m:is", NS)
                val = ""
                if istr is not None:
                    val = "".join(t.text or "" for t in istr.iter(T))
                elif v is not None:
                    val = v.text or ""
                    if c.get("t") == "s" and val.isdigit() and int(val) < len(shared):
                        val = shared[int(val)]
                cells[cidx] = val
            if cells:
                maxc = max(cells)
                line = " | ".join(str(cells.get(i, "")) for i in range(maxc + 1))
                if line.strip(" |"):
                    print(line)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    path = sys.argv[1]
    if len(sys.argv) >= 3 and sys.argv[2] == "list":
        z = zipfile.ZipFile(path)
        for name, tgt in sheet_targets(z):
            print(name)
    else:
        dump(path, set(sys.argv[2:]) if len(sys.argv) > 2 else None)
