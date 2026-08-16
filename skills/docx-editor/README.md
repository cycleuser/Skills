# Docx 文档编辑 (DocxEditor)

## 状态：Beta

## 用途

无损 DOCX 编辑技能。把 `.docx` 当 ZIP 容器，用 lxml 直接操作里面的原始 XML，保存时**未修改的部件逐字节复制**，只有被改动的部件才重新序列化。保证"打开→改一处→保存"后，其余所有部件（字体、样式、页眉、脚注、批注、图片...）与原文件**逐字节一致**，绝无格式漂移。

核心一句话：只改要改的，其余一字不动。

## 快速命令

| 命令 | 说明 |
|------|------|
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
| `/docxedit <file>` | English alias |
| `/docxedit unpack/pack/gui ...` | English command variants |

## 适用场景

- 改文档文字但**不能让格式有任何变化**（合同金额、报告年份、人名）
- 全局查找替换（含跨 run 的词、含页眉页脚脚注里的词）
- 编辑表格单元格、增删行列（保留表格样式）
- 编辑页眉/页脚/脚注/尾注/批注的文字
- 换文档里的图片、签名、Logo（保留其他一切）
- 批量修改文档属性（标题、作者）
- 解包 .docx 到目录，用任意工具改原始 XML/图片，再重新打包
- 需要确认"只有我改的那一处变了，其余逐字节一致"的审计场景

## 为什么需要它

用 python-docx 打开一个精心排版的 docx，改一个段落文字，保存——结果字体、字号、行距、表格边框、页眉页脚全变了，因为 python-docx 把整个文档对象模型重新序列化了。本技能的做法是：把 `.docx` 当 ZIP，只重新序列化你真正改过的部件，其余从原始字节缓存逐字节回写。

## 四步工作流

1. **打开** Open：`DocxEditor(path)` 把 docx 当 ZIP 读入，缓存每个 entry 的原始字节
2. **编辑** Edit：高层助手（`replace_text`/`set_text`/`add_row`...）或直接操作 lxml（需 `mark_dirty`）或 `set_part_bytes`（换图片）
3. **保存** Save：`doc.save(out)`；dirty 部件重新序列化，其余逐字节回写，ZIP 条目顺序不变
4. **校验** Verify：重新打开确认编辑生效，对比部件字节确认只改了预期 part

## 核心实现要点

- **dirty 集合是唯一真相**：`save()` 只重写 dirty 集合中的 part。高层助手自动标记；直接改 lxml 后必须 `doc.mark_dirty(name)`
- **跨 run 替换**：`replace_text` 把段落所有 `<w:t>` 拼成完整文本定位匹配，替换文字落入首个命中 run（继承其格式），其余命中 run 只删匹配部分
- **段落重写保格式**：`Paragraph.set_text` 把新文字写进第一个有 `<w:t>` 的 run（保留 `rPr`），清空其余 run；段落 `pPr` 不动
- **表格行列克隆**：`add_row`/`add_column` 用 `copy.deepcopy` 复制最后一行/列（含 `tcPr`/`gridSpan`/底纹），清空文字但保留结构
- **解包/打包**：`unpack` 用 `extractall` 原样解压；`repack` 把 `[Content_Types].xml` 写首位（Word 要求），其余按稳定排序

## 依赖

- **必需**：`lxml`（`pip install lxml`）
- **可选**：`PySide6`（GUI，`pip install PySide6`）
- **测试**：`pytest`（可选，测试脚本也可直接 `python` 运行）
- 依赖 `_shared/core/safety-rules.md`

## 验证

本技能自带测试 `tests/test_docxmod.py`（无需外部样本，自建最小合法 docx）：

```bash
python tests/test_docxmod.py       # 直接运行，16 项检查
pytest tests/test_docxmod.py -v    # 或用 pytest
```

覆盖：解包↔打包字节一致、打开→保存(不改)无损、全局替换、跨 run 替换、段落重写/增删、表格单元格/行列、段落样式、页眉/脚注/批注编辑、部件字节替换、原地保存、查找、原文件不被破坏。

## 数据与合规原则

- **生产环境不覆盖原文件**，输出为新文件（`<原名>-edited.docx` 或用户指定路径）
- 原地保存 `doc.save()` 虽走临时文件+原子移动，仍属破坏性操作，仅在用户明确要求时使用
- 编辑前对重要文档先备份

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
│   ├── docxmod_skill.py         # 单文件引擎（核心，约 480 行，依赖 lxml）
│   └── docxmod_gui.py           # PySide6 GUI（约 360 行）
└── tests/
    └── test_docxmod.py          # 自验证测试（约 280 行）
```

## 参见

- `/填表` from **tianbiao** — 照固定模板填数据（本技能侧重"改已有内容"，填表侧重"往空模板里填"）
- `/公文` from **official-document-writer** — 从零撰写公文正文（本技能不生成内容，只编辑已有文档）