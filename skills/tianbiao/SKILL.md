---
name: tianbiao
version: "1.1.0"
description: |
  Template-preserving form/report filler. Extracts text from mixed reference materials (PDF/OCR/images/Office), corrects misaligned lines and OCR errors, then fills the content into a Word/Excel template while keeping the ORIGINAL fonts, borders, merged cells and layout — never rebuilds from scratch.

  Triggers when: Filling official forms/reports based on a fixed template (成绩单、试卷质量分析表、成绩分析表、过程性评价档案、考查课报告、各类表格), extracting text from reference materials (PDF/扫描件/图片) then filling into template, when output MUST match the original template format exactly, or when converting .doc/.xls templates and populating them with data.

  Commands:
  - /填表 <模板> <数据> - Fill a template with data, preserving format
  - /填表 convert <文件> - Convert .doc/.xls template to editable .docx/.xlsx
  - /填表 inspect <模板> - Map a template's tables/cells/fonts before filling
  - /填表 extract <资料目录> - Extract text from reference materials (PDF/OCR/images)
  - /填表 check <文档> - Verify filled doc format fidelity & data integrity
  - /tianbiao <template> <data> - English command for template-preserving fill
  - /tianbiao convert <file> - Convert legacy template to editable format
  - /tianbiao inspect <template> - Map template structure & fonts
  - /tianbiao extract <dir> - Extract text from reference materials
  - /tianbiao check <doc> - Verify fidelity & data integrity

  Capabilities: Text extraction from PDF/images/Office (pdfplumber/pymupdf/PaddleOCR/Tesseract), OCR error correction and misaligned-line fixing, in-place cell filling on original templates, .doc/.xls to .docx/.xlsx conversion via LibreOffice, font/border/merge preservation, compact roster tables with repeating headers and non-splitting rows, formula reverse-engineering from source data, format-fidelity verification, bilingual Chinese-English operation
author: cycleuser
license: MIT
status: Beta
---

## Safety Rules

参见 [_shared/core/safety-rules.md](../_shared/core/safety-rules.md) — 所有安全规则从共享层加载，避免跨技能重复维护。

关键补充：**永不覆盖原始模板**。所有输出写为新文件（课程/主体名 + `-` + 文档名）。填表前先备份或只读打开源数据。

# 填表 (TianBiao / Template-Preserving Form Filler)

严格"照着原表填"的填表技能。核心原则：**复制原模板 → 把数据填进对应单元格 → 保持原有字体、边框、合并单元格与版式**，绝不从零重排。

The one rule that matters: **copy the original template, drop text into the right cells, keep the original formatting. Never rebuild the table from scratch.**

## Quick Commands

| Command | 说明 / Description |
|---------|-------------|
| `/填表 <模板> <数据>` | 按模板填充数据，保持格式 |
| `/填表 convert <文件>` | 将 .doc/.xls 模板转为可编辑的 .docx/.xlsx |
| `/填表 inspect <模板>` | 填写前先摸清模板的表格/单元格/字体结构 |
| `/填表 extract <资料目录>` | 从参考资料（PDF/图片/扫描件）提取文本并纠正 |
| `/填表 check <文档>` | 校验填好的文档格式保真度与数据一致性 |
| `/tianbiao <template> <data>` | Fill template preserving format |
| `/tianbiao convert <file>` | Convert legacy template to editable format |
| `/tianbiao inspect <template>` | Map template structure & fonts |
| `/tianbiao extract <dir>` | Extract text from reference materials (PDF/OCR/images) |
| `/tianbiao check <doc>` | Verify fidelity & data integrity |

## 核心理念 / Core Philosophy

从一次真实的期末材料填表任务中提炼：教师给出固定的学校模板（试卷质量分析表、成绩分析表、过程性评价档案等）和原始数据（点名册、作业、讨论记录），要求"严谨地按照原来的格式，只填写内容"。

三条铁律：

1. **不重排，只填充**。绝不用 python-docx 从零画表——那样字体、字号、边框、行高、合并单元格都会走样。必须打开**原模板**，只替换单元格里的文字。
2. **保原字体**。填入的文字继承该单元格原有 run 的 `rPr`（字体、字号、颜色）。仅去除模板里的"示例红字"和"黄色高亮批注"。
3. **明细表要规整**。大批量名单（如全班成绩明细）必须：小号字体、表头跨页重复（`tblHeader`）、行不跨页断裂（`cantSplit`）、紧凑单元格边距——绝不能让一张表松散地跨好几页还错行。

## 五步工作流 / Five-Step Workflow

```
Step 1  转换 Convert
  .doc/.xls 老格式 → .docx/.xlsx（用 LibreOffice headless，保真度远高于 textutil/pandoc）
  soffice --headless --convert-to docx --outdir <dir> <template.doc>

Step 2  摸底 Inspect
  读出模板每个表的可见单元格结构（含 gridSpan/vMerge）、每个关键单元格的字体 rPr。
  确认"哪一行哪一列填什么"，特别注意合并单元格导致的逻辑网格 vs 可见网格差异。

Step 3  准备数据 Prepare Data（两条路径）
  3a. 非结构化资料 → 文本提取 + OCR + 错行纠正 → 结构化字段
      按文件类型路由提取器（PDF文本层/OCR/Office解析），纠正OCR错字和错行，
      校验关键数字回查原文位置，未提取字段列入"需人工补"。详见 rules/text-extraction.md
  3b. 结构化源文件 → 直接读取 + 公式反推
      点名册/成绩表等结构化数据，必要时反推计算公式（如平时=0.2×课堂+0.4×作业均+0.4×测验），
      用全体样本验证吻合。

Step 4  填充 Fill
  打开原模板 docx，按可见单元格索引 vcells(table, row_idx) 定位并写入。
  分析类长文本：克隆模板段落样式（标题段/正文段），保留字体，去高亮，加正文首行缩进。
  明细表：新建紧凑表格（小号宋体 + tblHeader + cantSplit + 窄边距）。

Step 5  校验 Verify
  重新打开输出文件，逐表核对：表数量、行列、字体、边框、每条数据与源一致。
  可选：转 PDF 数页数，确认排版整洁不散乱。
```

## 关键实现要点 / Key Implementation Notes

- **可见单元格 vs 逻辑网格**：python-docx 的 `table.cell(r,c)` 会把合并单元格展开成逻辑网格，导致定位错位。填表务必用"可见单元格"：
  ```python
  from docx.table import _Cell
  from docx.oxml.ns import qn
  def vcells(table, ri):
      tr = table.rows[ri]._tr
      return [_Cell(tc, table) for tc in tr.findall(qn('w:tc'))]
  ```
- **保字体填值**：改单元格首个 run 的 text，删多余 run，剥离 `w:color`/`w:highlight`。
- **明细表防散架**：每行 `w:trPr` 加 `w:cantSplit`；表头行加 `w:tblHeader`；`w:tblCellMar` 设窄边距；正文 run 用小字号（如 `w:sz`=18，即 9pt）。
- **转换引擎**：优先 LibreOffice（`soffice --headless`）。macOS 若缺 `LibreOffice.app`，`brew reinstall --cask libreoffice`。`textutil`/`pandoc` 只用于**读取**，不用于生成交付件。

详见 [scripts/fill_docx_template.py](scripts/fill_docx_template.py) —— 可复用的填表工具函数库。

## Rules

- [rules/workflow.md](rules/workflow.md) - 完整五步工作流与命令行操作
- [rules/text-extraction.md](rules/text-extraction.md) - 从非结构化资料提取文本、OCR识别、错行纠正
- [rules/format-preservation.md](rules/format-preservation.md) - 保格式的具体 OOXML 技术（可见单元格、字体继承、明细表防散架）
- [rules/data-integrity.md](rules/data-integrity.md) - 数据提取、公式反推与校验
- [rules/writing-analysis.md](rules/writing-analysis.md) - 分析类表格文字的填写原则（客观、实事求是、尊重学情、不甩锅）
- [rules/anti-aigc.md](rules/anti-aigc.md) - 填表文字反AIGC与套话规避

## 适用表格类型 / Supported Form Types

- 试卷质量分析表、试卷成绩分析表（考试课，按试卷/教师为单位）
- 考查课成绩分析报告表（考查课）
- 过程性评价材料档案（封面+评价方案+各环节标准+全体学生成绩明细表）
- 成绩单、考核成绩登记表、点名册
- 各类含固定表头、需要批量填人名/分数的学校表格

## 边界情况 / Edge Cases

- **模板题型行数 ≠ 数据项数**：先增/删模板中可复制的数据行（克隆 `w:tr`），再填。
- **多班合并 vs 分班**：成绩分析"以教师为单位"多班合并填 1 份；质量分析"以试卷为单位"。可同时产出合并版与分班版。
- **合并单元格的续行**：填 `vMerge=continue` 的单元格要留空，只在 `restart` 行写值。
- **超长名单**：拆分到多页时靠 `tblHeader`+`cantSplit` 保持每页有表头、行不断裂；必要时进一步缩小字号。
- **纯 Excel 模板**：用 openpyxl 打开原 xlsx，只写值不动样式；.xls 先转 .xlsx。

## 常见问题排查 / Troubleshooting

- **填完字体变了** → 没有继承原 run 的 rPr，或用 python-docx 新建了段落/表格。改为在原单元格上改 text。
- **数据填错格** → 用了 `table.cell(r,c)` 遇到合并单元格错位。改用 `vcells()` 可见单元格定位。
- **表格跨页散架/错行** → 缺 `cantSplit`/`tblHeader`，或字号过大。补齐并缩小字号。
- **`%d`/`%.1f` 原样出现在文档里** → 字符串格式化没生效（少了 `% (...)`）。校验步骤应能抓到。
- **`.doc` 转换丢表格** → 用了 textutil 转 docx（会拍平表格）。改用 LibreOffice。

## 版本历史 / Version History

| 版本 | 日期 | 变更 |
|------|------|------|
| 1.0.0 | 2026-07-12 | 初始版本：模板保真填表工作流、可复用脚本、五步法与校验 |
| 1.1.0 | 2026-07-17 | 新增文本提取能力：从非结构化资料（PDF/图片/扫描件）提取文本、OCR识别、错行纠正、OCR纠错，新增 text-extraction.md 规则 |

## See Also / 相关技能

- `/公文` from **official-document-writer** — 需要从零撰写公文正文时（本技能侧重"照模板填"，公文技能侧重"写内容"）
- `/人话` from **humanizer** — 分析类文字需要去AI味、更自然时
