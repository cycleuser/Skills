# Doc 转 Docx（纯 Python）

## 状态：Beta

## 用途

把旧版 Word 二进制格式（`.doc`，Word 97/2000/2002/2003 及 WPS 兼容输出）
**只用 Python** 转换为现代 `.docx`——不装 Word、不用 LibreOffice、不调用
任何外部二进制。依赖 `olefile`、`python-docx`、`lxml` 三个纯 Python 包。

核心一句话：解析二进制结构（FIB / 分片表 / FKP / sprm），用 lxml 写出
精确的 OOXML，文本与格式原样保留。

## 快速命令

| 命令 | 说明 |
|------|------|
| `/doc2docx <文件.doc> [-o 输出.docx]` | 转换单个文件 |
| `/doc2docx batch <目录> [-o 输出目录]` | 批量转换目录下全部 .doc |
| `/doc2docx inspect <文件.doc>` | 打印结构信息与文本预览 |
| `/doc2docx check <输出.docx> [--against 原.doc]` | 校验并逐字符对比 |
| `/转docx <文件>` | 中文命令别名 |

## 保真度

- **完整还原**：正文文本（逐字符）、字体（含 宋体/黑体/仿宋_GB2312 等中文
  字体名）、字号、粗斜体、下划线、颜色、高亮、上下标、字距、对齐、缩进、
  段前段后、行距、孤行控制、大纲级别、页面设置（A4/边距/横竖版/页码）、
  Normal/标题样式默认、表格结构/列宽/边框、PAGE 页码域。
- **尽力而为**：表格 gridSpan 合并、样式名。
- **暂不还原**：页眉/页脚、图片、脚注、批注、修订、宏。

## 为什么不用现成方案

大多数 doc→docx 方案都依赖外部程序（LibreOffice headless、Word COM、
textutil、pandoc），要么需安装，要么拍平表格、丢格式。本技能零外部二进制，
用 olefile 读 OLE2 容器、手写全部二进制解析、lxml 直写 OOXML。

## 安装与依赖

```bash
pip install olefile python-docx lxml
```

## 验证

自带自验证测试，不依赖外部样本（`tests/make_doc.py` 内存构造最小合法 .doc）：

```bash
python tests/test_doc2docx.py       # 23 项检查
pytest tests/test_doc2docx.py -v
```

真实文件闭环：`convert` → `check --against`。

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
│   └── doc2docx.py              # 单文件引擎 + CLI
└── tests/
    ├── make_doc.py              # 内存构造最小合法 .doc
    └── test_doc2docx.py         # 23 项自验证测试
```

## 参见

- `/docx编辑` from **docx-editor** — 转好之后需要无损改某一处格式时
- `/填表` from **tianbiao** — 需要照模板填数据时（tianbiao 用 LibreOffice 转 .doc）
