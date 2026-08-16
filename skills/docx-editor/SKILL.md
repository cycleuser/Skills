---
name: docx-editor
version: "1.0.0"
description: |
  Lossless DOCX unpack / edit / repack toolkit. Treats a .docx as a ZIP of OOXML parts, edits the raw XML with lxml, and on save copies every UNMODIFIED part byte-for-byte — only the parts you actually edited are re-serialised. Guarantees that opening, editing and saving a document leaves its formatting completely intact.

  Triggers when: Editing a .docx while preserving format exactly (改文字但不改格式), unpacking a .docx into a folder of raw XML/media/files then repacking it back, swapping an embedded image or font, editing headers/footers/footnotes/endnotes/comments directly, editing table cells without disturbing the table style, doing global find-and-replace across runs while keeping each run's formatting, or any task that requires "open docx → change something → save, and nothing else changes".

  Commands:
  - /docx编辑 <文件> - Open a docx in the lossless editor (describe what to edit in natural language)
  - /docx编辑 unpack <文件> [目录] - Unpack a .docx into a folder of raw parts
  - /docx编辑 pack <目录> <输出.docx> - Repack a folder back into a .docx
  - /docx编辑 dump <文件> - Print paragraph & table structure
  - /docx编辑 replace <文件> <旧> <新> [-o 输出] - Global find-and-replace (preserves formatting)
  - /docx编辑 set-para <文件> <序号> <文字> [-o 输出] - Rewrite a body paragraph
  - /docx编辑 set-cell <文件> <表> <行> <列> <文字> [-o 输出] - Rewrite a table cell
  - /docx编辑 parts <文件> [--bytes] - List every part inside the package
  - /docx编辑 find <文件> <关键词> - Find paragraphs containing a keyword
  - /docx编辑 gui [文件] - Launch the PySide6 GUI
  - /docxedit <file> - English command alias for the editor
  - /docxedit unpack <file> [dir] - Unpack a .docx into a folder
  - /docxedit pack <dir> <out.docx> - Repack a folder into a .docx
  - /docxedit gui [file] - Launch the PySide6 GUI

  Capabilities: Lossless byte-for-byte preservation of unmodified OOXML parts, lazy lxml parsing with explicit dirty-set serialisation, cross-run text replacement preserving each run's rPr, paragraph rewrite preserving pPr and first-run rPr, table row/column add/delete via deepcopy cloning, in-place header/footer/footnote/endnote/comment editing via raw XML access, embedded image/font swap via set_part_bytes, unpack-to-folder and repack-from-folder with [Content_Types].xml-first ordering, CLI (unpack/pack/dump/find/replace/set-para/set-cell/parts), PySide6 GUI with paragraph/table/parts tabs
author: cycleuser
license: MIT
status: Beta
---

## Safety Rules

参见 [_shared/core/safety-rules.md](../_shared/core/safety-rules.md) — 所有安全规则从共享层加载，避免跨技能重复维护。

关键补充：**生产环境不覆盖原文件**。所有编辑输出写为新文件（`<原名>-edited.docx` 或用户指定路径）。原地保存 `doc.save()` 虽走临时文件+原子移动，但仍属破坏性操作，仅在用户明确要求时使用。

# Docx 文档编辑 (DocxEditor / Lossless DOCX Editor)

严格"只改要改的，其余一字不动"的 DOCX 编辑技能。核心原则：**把 .docx 当 ZIP 容器，用 lxml 直接操作里面的原始 XML，保存时未修改的部件逐字节复制，只有被改动的部件才重新序列化**。绝不用 python-docx 重新生成整个文档——那样会让每个被加载的部件都被重写，导致格式漂移和"打开→保存"不再幂等。

The one rule that matters: **a .docx is a ZIP of OOXML parts. Edit only the parts you mean to change; on save, copy every other part byte-for-byte from the original. Never regenerate the whole document.**

## Quick Commands

| Command | 说明 / Description |
|---------|-------------|
| `/docx编辑 <文件>` | 用自然语言描述要改什么，技能生成编辑脚本并执行 |
| `/docx编辑 unpack <文件> [目录]` | 解包 .docx 到目录（每个 part 原样落盘） |
| `/docx编辑 pack <目录> <输出.docx>` | 从目录重新打包成 .docx |
| `/docx编辑 dump <文件>` | 打印段落与表格结构 |
| `/docx编辑 replace <文件> <旧> <新> [-o 输出]` | 全局查找替换（跨 run，保留格式） |
| `/docx编辑 set-para <文件> <序号> <文字> [-o 输出]` | 按序号重写主文档段落 |
| `/docx编辑 set-cell <文件> <表> <行> <列> <文字> [-o 输出]` | 重写表格单元格 |
| `/docx编辑 parts <文件> [--bytes]` | 列出所有部件（可加字节大小） |
| `/docx编辑 find <文件> <关键词>` | 查找包含关键词的段落 |
| `/docx编辑 gui [文件]` | 启动 PySide6 图形界面 |
| `/docxedit <file>` | English alias for the editor |
| `/docxedit unpack <file> [dir]` | Unpack a .docx into a folder |
| `/docxedit pack <dir> <out.docx>` | Repack a folder into a .docx |
| `/docxedit gui [file]` | Launch the PySide6 GUI |

## 核心理念 / Core Philosophy

从一次真实的"改个字却毁了整个文档格式"的事故中提炼：用 python-docx 打开一个精心排版的 docx，改一个段落文字，保存——结果字体、字号、行距、表格边框、页眉页脚全变了，因为 python-docx 把整个文档对象模型重新序列化了。

四条铁律：

1. **不重写没改的**。`.docx` 是 ZIP，每个 entry（`document.xml`、`styles.xml`、`header1.xml`、`footnotes.xml`、`comments.xml`、图片...）都是独立部件。只重新序列化你真正改过的部件，其余从原始字节缓存逐字节回写。
2. **惰性解析**。只有当你访问某个 part 时才用 lxml 解析它。只读（如读段落文字）不触发 dirty。解析后的树被修改，必须显式 `mark_dirty(name)`。
3. **保留 ZIP 元信息**。保存时沿用每个 entry 的原始 `date_time`，条目顺序与原文件一致——不排序、不重排。
4. **克隆而非新建**。增删表格行列、插入段落时，深拷贝已有元素作为模板（含 `rPr`/`pPr`/`tcPr`/`gridSpan`/`vMerge` 全部属性），绝不用 `etree.SubElement` 从零建——那样会丢光格式。

## 四步工作流 / Four-Step Workflow

```
Step 1  打开 Open
   DocxEditor(path) 把 docx 当 ZIP 读入，缓存每个 entry 的原始字节到 _raw 字典。
   不解析 XML，直到你真正访问某个 part 才惰性解析到 _trees。

Step 2  编辑 Edit（三条路径，按改动面由小到大）
   a) 高层助手（推荐）— replace_text / Paragraph.set_text / Cell.set_text /
      Table.add_row / Table.delete_column / Paragraph.insert_paragraph_after /
      Paragraph.style。只改必要元素，自动标记 dirty。
   b) 直接操作 lxml — doc.xml("word/footnotes.xml") 拿到根元素后直接改
      t.text = ...；必须手动 doc.mark_dirty("word/footnotes.xml")。
   c) 整体替换部件字节 — doc.set_part_bytes("word/media/image1.png", png_bytes)，
      用于换图片/字体等二进制部件，不经过 lxml。

Step 3  保存 Save
   doc.save(out) 或 doc.save()（原地覆盖，走临时文件+原子移动）。
   dirty 集合里的 XML 部件重新序列化；其余从 _raw 逐字节回写；
   ZIP 条目顺序与原文件一致。新部件（dirty 里但不在原 names 中）追加。

Step 4  校验 Verify
   重新打开输出文件，确认编辑生效；对比原始与输出的部件字节，
   确认只有预期 part 改了，其余全部 byte-identical。
```

## 关键实现要点 / Key Implementation Notes

- **dirty 集合是唯一真相**：`save()` 只重写 `self._dirty` 中的 part。高层助手自动标记；直接改 lxml 元素后必须 `doc.mark_dirty(name)`。
- **跨 run 替换**：`replace_text` 把段落所有 `<w:t>` 拼成完整文本定位匹配，替换文字落入首个命中 run（继承其格式），其余命中 run 只删匹配部分。OOXML 常把一个词拆到多个 run，简单按 run 替换会漏匹配。
- **段落重写保格式**：`Paragraph.set_text` 把新文字写进第一个有 `<w:t>` 的 run（保留它的 `rPr`：字体/字号/颜色/粗斜体），清空其余 run；段落 `pPr`（样式/对齐/缩进/编号）不动。
- **表格行列克隆**：`Table.add_row`/`add_column` 用 `copy.deepcopy` 复制最后一行/列（含 `tcPr`/`gridSpan`/`vMerge`/底纹），清空文字但保留段落和 run 骨架。
- **页眉/页脚/脚注/尾注/批注**：这些 part 不是 `document.xml`，高层助手不直接覆盖。统一用 `doc.xml(name)` + 改元素 + `doc.mark_dirty(name)`。页脚的页码域（`PAGE`/`NUMPAGES`）不要动 `instrText`/`fldChar`，只改域前后的文字 `<w:t>`。
- **换图片/二进制**：`doc.set_part_bytes("word/media/image1.png", new_bytes)` 走原始字节替换，不经过 lxml，对二进制最安全。
- **解包/打包**：`unpack` 用 `zipfile.extractall` 原样解压；`repack` 把 `[Content_Types].xml` 写在首位（Word 要求），其余按稳定排序。解包→重新打包后每个 part 内容字节与原文件一致。

详见 [scripts/docxmod_skill.py](scripts/docxmod_skill.py) —— 单文件可嵌入的完整引擎（约 480 行，依赖 lxml）。
GUI 见 [scripts/docxmod_gui.py](scripts/docxmod_gui.py) —— PySide6 界面（约 360 行）。

## Rules

- [rules/workflow.md](rules/workflow.md) - 完整四步工作流与命令行操作
- [rules/format-preservation.md](rules/format-preservation.md) - 无损保格式的具体 OOXML 技术（字节缓存、dirty 集合、跨 run 替换、克隆增删）
- [rules/editable-targets.md](rules/editable-targets.md) - 所有可编辑部件的定位方法与代码示例（段落/表格/页眉/脚注/批注/图片/属性）
- [rules/edge-cases.md](rules/edge-cases.md) - 边界情况（合并单元格、嵌套表格、页码域、命名空间）与排错表

## 适用场景 / Supported Scenarios

- 改文档里的文字但**不能让格式有任何变化**（如改合同金额、改报告年份、改名字）
- 全局查找替换（含跨 run 的词、含页眉页脚脚注里的词）
- 编辑表格单元格、增删行列（保留表格样式）
- 编辑页眉/页脚/脚注/尾注/批注的文字
- 换文档里的图片、签名、Logo（保留其他一切）
- 批量修改文档属性（标题、作者）
- 解包 .docx 到目录，用任意工具改原始 XML/图片，再重新打包
- 需要确认"只有我改的那一处变了，其余逐字节一致"的审计场景

## 边界情况 / Edge Cases

- **合并单元格**：`Table.cell(r,c)` 按物理 `tc` 索引，`col_count()` 是最大物理 `tc` 数，与逻辑列数可能不同。用 `rows[r].findall(w("tc"))` 按物理定位。
- **表格内段落**：`doc.paragraphs` 只含 body 直属段落。表格内用 `doc.all_paragraphs()` 或 `cell.paragraphs`。
- **页码域**：页脚的 `PAGE`/`NUMPAGES` 是域代码，只改域前后的文字 `<w:t>`，不要动 `instrText`/`fldChar`。
- **命名空间**：`docProps/core.xml` 用 `dc` 命名空间，不是 `w`。`[Content_Types].xml` 用包内容类型命名空间。
- **大文件**：`DocxEditor` 一次性读入整个 ZIP 到内存。对极大 docx 先 `unpack` 解包，改完再 `repack` 更省内存。

## 常见问题排查 / Troubleshooting

- **保存后编辑丢失** → 直接改了 lxml 元素但没 `mark_dirty`。在 `save()` 前调 `doc.mark_dirty(part_name)`。
- **保存后所有部件都变了** → 用了 python-docx 的 `Document.save()` 而非本技能的 `DocxEditor.save()`。改用 `from docxmod import DocxEditor`。
- **页眉/脚注/批注改了没生效** → 这些 part 不被 `replace_text` 覆盖；直接改 XML 后必须 `mark_dirty`。
- **Word 打开报损坏** → 改了 `[Content_Types].xml` 但没加对 override；或删了单元格唯一段落（单元格必须至少有一段，用 `set_text("")` 而非 `delete()`）。
- **跨 run 替换没命中** → `replace_text` 已处理跨 run，但若 run 被 `<w:proofErr>` 打断可能漏。检查 XML，必要时 `unpack` 手工处理再 `repack`。

## 验证 / Verification

本技能自带测试 [tests/test_docxmod.py](tests/test_docxmod.py)（约 280 行，无需外部样本，自建最小合法 docx）：

```bash
python tests/test_docxmod.py    # 直接运行
# 或
pytest tests/test_docxmod.py -v
```

覆盖 16 项检查：解包↔打包字节级一致、打开→保存(不改)无损、全局替换、跨 run 替换、段落重写、段落增删、表格单元格、表格行列增删、段落样式、页眉编辑、脚注编辑、批注编辑、部件字节替换、原地保存、查找、原文件不被破坏。

## 依赖 / Dependencies

- **必需**：`lxml`（`pip install lxml`）
- **可选**：`PySide6`（GUI，`pip install PySide6`）
- **测试**：`pytest`（可选，测试脚本也可直接 `python` 运行）
- 依赖 `_shared/core/safety-rules.md`

## 文件结构

```
skills/docx-editor/
├── README.md
├── SKILL.md
├── rules/
│   ├── workflow.md              # 四步工作流与命令行操作
│   ├── format-preservation.md   # 无损保格式的 OOXML 技术
│   ├── editable-targets.md      # 所有可编辑部件的定位与示例
│   └── edge-cases.md            # 边界情况与排错
├── scripts/
│   ├── docxmod_skill.py         # 单文件引擎（核心，约 480 行）
│   └── docxmod_gui.py           # PySide6 GUI（约 360 行）
└── tests/
    └── test_docxmod.py          # 自验证测试（约 280 行）
```

## 版本历史 / Version History

| 版本 | 日期 | 变更 |
|------|------|------|
| 1.0.0 | 2026-08-16 | 初始版本：无损 DOCX 引擎、CLI、PySide6 GUI、四步工作流、16 项自验证测试 |

## See Also / 相关技能

- `/填表` from **tianbiao** — 照固定模板填数据（本技能侧重"改已有内容"，填表侧重"往空模板里填"）
- `/公文` from **official-document-writer** — 从零撰写公文正文（本技能不生成内容，只编辑已有文档）