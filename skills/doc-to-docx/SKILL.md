---
name: doc-to-docx
version: "1.0.0"
description: |
  Pure-Python legacy Word (.doc) → .docx converter. Parses the Word 97/2000/2002/2003 binary format (and the Word-97-compatible output written by WPS Office) directly — no LibreOffice, no Microsoft Word, no textutil, no antiword/catdoc, no external binaries of any kind. Only olefile + python-docx + lxml.

  Triggers when: Converting a .doc file to .docx while preserving text, fonts (incl. 宋体/黑体/仿宋 Chinese fonts), sizes, bold/italic/underline, colours, paragraph alignment/indentation/spacing/line-spacing, page setup (A4, margins, orientation), the Normal/Heading style defaults and tables — "把 doc 原样转成 docx，但不装 Word、不用 LibreOffice".

  Commands:
  - /doc2docx <文件.doc> [-o 输出.docx] - Convert one .doc to .docx
  - /doc2docx batch <目录> [-o 输出目录] - Batch-convert every .doc in a directory
  - /doc2docx inspect <文件.doc> - Print structure: FIB, fonts, paragraphs, text preview
  - /doc2docx check <输出.docx> [--against 原.doc] - Verify the produced .docx and diff text against the original
  - /转docx <文件> - 中文命令别名（单文件转换）

  Capabilities: OLE2/CFB parsing (olefile), FIB + CLX piece-table text extraction (UTF-16LE / cp1252), CHPX/PAPX FKP-page decoding into character & paragraph formatting, STSH style-chain resolution, STTBF ffn font-name table (with WPS UTF-16 auto-detection), PlcfSed/SEPX page setup, table reconstruction from fInTable/fTtp marks + TDefTable column widths + TTableBorders, PAGE/NUMPAGES field-code preservation, python-docx + lxml OOXML output with per-run rPr / per-paragraph pPr / per-section sectPr, batch CLI, structural inspect, fidelity check, 23-check self-test with an in-memory synthetic .doc
author: cycleuser
license: MIT
status: Beta
---

## Safety Rules

参见 [_shared/core/safety-rules.md](../_shared/core/safety-rules.md) — 所有安全规则从共享层加载，避免跨技能重复维护。

关键补充：**生产环境不覆盖原文件**。输出永远是新文件（`<原名>.docx` 或 `-o` 指定路径）。转换前如对文档内容有疑虑，先 `inspect` 确认结构。

# Doc → Docx 纯 Python 转换器 (Doc2Docx)

把旧版 Word 二进制格式（`.doc`）**只用 Python** 转成现代 `.docx`。
核心原则：**不调用任何外部软件**——LibreOffice / MS Word / textutil / antiword
都不需要，只需 `pip install olefile python-docx lxml`。

The one rule that matters: **a .doc is an OLE2 container of binary structures — parse the FIB, the piece table, the FKP pages and the sprm lists by hand; rebuild the document with python-docx + raw lxml so every OOXML property is under your control.**

## Quick Commands

| Command | 说明 / Description |
|---------|-------------|
| `/doc2docx <文件.doc> [-o 输出.docx]` | 转换单个 .doc → .docx |
| `/doc2docx batch <目录> [-o 输出目录]` | 批量转换目录下全部 .doc |
| `/doc2docx inspect <文件.doc>` | 打印结构信息与文本预览 |
| `/doc2docx check <输出.docx> [--against 原.doc]` | 校验并逐字符对比 |
| `/转docx <文件>` | 中文别名 |

## 为什么不用现成转换器

大多数“doc→docx”方案都依赖外部程序：

| 方案 | 依赖 |
|------|------|
| LibreOffice headless | 需要装 LibreOffice |
| Word COM / win32com | 需要 Windows + Word |
| textutil（macOS） | 只适合简单文本，**表格会被拍平** |
| pandoc | 用 Word 内核，丢格式 |
| doc2docx（pip 包） | 实际包一层 LibreOffice/Word |

本技能 **零外部二进制**：`olefile` 读 OLE2 容器，lxml 操作 OOXML，
python-docx 建骨架，其余全部是自己实现的二进制解析——文本、字体、字号、
粗斜体、颜色、对齐、缩进、行距、页面设置、表格、页码域全部保真。

## 解析管线（每步详情见 rules/）

```
.doc (OLE2/CFB)
  ├─ FIB            → fcMin/fcMac、各结构位置
  ├─ CLX 分片表     → 文本（UTF-16LE / cp1252 压缩分片）
  ├─ PlcfBteChpx    → 字符格式（FKP 页 → grpprl → 语义属性）
  ├─ PlcfBtePapx    → 段落格式（含 fInTable/fTtp 表格标记）
  ├─ STSH           → 样式（含 Normal 默认字体/字号）
  ├─ STTBF ffn      → 字体名表（含 WPS 中文名嗅探）
  └─ PlcfSed/SEPX   → 页面设置
        │
        ▼
.docx（python-docx 骨架 + lxml 精确 OOXML 属性）
```

## 保真度速览

- **Tier 1（完整还原）**：正文文本（逐字符 100%）、字符格式（字体/字号/
  粗斜体/下划线/颜色/高亮/上下标/字距）、段落格式（对齐/缩进/段前段后/
  行距/孤行控制/大纲级别/制表位）、页面设置（A4/边距/横竖版/页码）、
  Normal/标题样式默认、表格结构与列宽、PAGE/NUMPAGES 域。
- **Tier 2（尽力而为）**：表格 gridSpan 合并、整体单线边框、样式名。
- **Tier 3（暂不还原）**：页眉/页脚、图片、脚注、批注、修订、宏。

详见 [rules/fidelity-map.md](rules/fidelity-map.md)。

## 验证 / Verification

本技能自带测试，**不依赖外部样本**：`tests/make_doc.py` 在内存里手工构造
一个最小但真实可解析的 Word 97 二进制 .doc（自写 OLE2 写入器 + FIB +
分片表 + FKP + 样式 + 字体 + 分节 + 表格），`tests/test_doc2docx.py`
转换后逐项断言：

```bash
python skills/doc-to-docx/tests/test_doc2docx.py    # 23 项检查，直接运行
pytest skills/doc-to-docx/tests/test_doc2docx.py -v
```

对真实文件建议闭环：`convert` → `check --against`。

## 依赖 / Dependencies

- **必需**：`olefile`、`python-docx`、`lxml`（全部纯 Python，`pip install`）
- **测试**：`pytest`（可选，测试脚本也可直接 `python` 运行）
- 依赖 `_shared/core/safety-rules.md`

## Rules

- [rules/workflow.md](rules/workflow.md) - 四步工作流、CLI 命令、校验方法
- [rules/binary-format.md](rules/binary-format.md) - .doc 二进制格式速查（FIB/分片表/FKP/sprm/样式/字体）
- [rules/fidelity-map.md](rules/fidelity-map.md) - 保真度地图（Tier1/2/3 与限制）
- [rules/edge-cases.md](rules/edge-cases.md) - 边界情况与排错

## 文件结构

```
skills/doc-to-docx/
├── README.md
├── SKILL.md
├── rules/
│   ├── workflow.md              # 工作流与 CLI
│   ├── binary-format.md         # 二进制格式速查
│   ├── fidelity-map.md          # 保真度地图
│   └── edge-cases.md            # 边界情况与排错
├── scripts/
│   └── doc2docx.py              # 单文件引擎（DocReader + DocxBuilder + CLI）
└── tests/
    ├── make_doc.py              # 内存构造最小合法 .doc（自写 OLE2 写入器）
    └── test_doc2docx.py         # 23 项自验证测试
```

## 版本历史 / Version History

| 版本 | 日期 | 变更 |
|------|------|------|
| 1.0.0 | 2026-08-26 | 初始版本：纯 Python .doc→.docx 引擎、批量 CLI、inspect/check、自建样本测试 |

## See Also / 相关技能

- `/docx编辑` from **docx-editor** — 无损编辑已有 .docx（本技能负责“老 .doc 转 .docx”，docx-editor 负责“转好之后只改某一处”）
- `/填表` from **tianbiao** — 照模板填数据（tianbiao 用 LibreOffice 转 .doc；本技能给纯 Python 方案）
