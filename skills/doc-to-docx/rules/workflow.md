# 转换工作流 / Conversion Workflow

本技能用**纯 Python**把旧版 Word 二进制格式（.doc，Word 97/2000/2002/2003，
以及 WPS 输出的 Word 97 兼容格式）无损地转换为现代 OOXML（.docx）。
**全程不调用 LibreOffice、Microsoft Word、textutil、antiword/catdoc 等任何
外部程序**——只依赖 `olefile`、`python-docx`、`lxml` 三个纯 Python 包。

## 核心命令

| 命令 | 说明 |
|------|------|
| `/doc2docx <文件.doc> [-o 输出.docx]` | 转换单个文件 |
| `/doc2docx batch <目录> [-o 输出目录]` | 批量转换目录下所有 .doc |
| `/doc2docx inspect <文件.doc>` | 打印结构信息（FIB/字体/段落/文本预览） |
| `/doc2docx check <输出.docx> [--against 原.doc]` | 校验生成的 docx 并对比原文件 |
| `/转docx <文件>` | 中文命令别名 |

引擎入口（脚本内 CLI 相同）：

```bash
python skills/doc-to-docx/scripts/doc2docx.py convert in.doc -o out.docx
python skills/doc-to-docx/scripts/doc2docx.py batch ./docs -o ./out
python skills/doc-to-docx/scripts/doc2docx.py inspect in.doc
python skills/doc-to-docx/scripts/doc2docx.py check out.docx --against in.doc
```

## 四步工作流

```
Step 1  解析容器   DocReader(path) 用 olefile 打开 OLE2/CFB，读出
                  WordDocument 流和 0Table/1Table 流。自动在 0Table /
                  1Table 之间挑选真正装着分片表的那一个（WPS 文件常把
                  fWhichTblStm 标志位写错）。

Step 2  解析结构   FIB → 文本分片表（CLX/PlcPcd）→ 文本；
                  PlcfBteChpx / PlcfBtePapx 的 FKP 页 → 字符/段落格式；
                  PlcfSed + SEPX → 分节页面设置；STSH → 样式；
                  STTBF ffn → 字体名表。

Step 3  解析格式   把每个 sprm（单属性修饰符）解码成语义属性：
                  粗体/斜体/下划线/字号/字体/颜色/高亮/上下标/字距，
                  对齐/缩进/段前段后/行距/孤行控制/大纲级别，
                  页宽/页高/四边距/装订线/页眉页脚距离/横竖版。

Step 4  写出 docx  用 python-docx 建立文档骨架，用 lxml 直接写 OOXML
                  属性（w:rPr / w:pPr / w:tblPr / w:sectPr），保证每个
                  属性字节级可控。段落级联 = 样式链 + 直接格式；表格按
                  fInTable/fTtp 单元格标记 + TDefTable 重建；页码域
                  （PAGE 等）保留为 OOXML 域代码。
```

## 输出原则

- **不覆盖原文件**。输出始终是新的 `.docx`（`<原名>.docx` 或 `-o` 指定路径）。
- 转换结束后建议跑 `check`，把输出文本与原文件逐字符对比。
- 依赖纯 Python：`pip install olefile python-docx lxml`。

## 校验

自带的 `tests/test_doc2docx.py` 不依赖任何外部样本：它在内存中手工构造一个
最小但真实可解析的 Word 97 二进制 `.doc`（含 FIB/分片表/FKP/样式/字体/分节/
表格），转换后逐项断言文本、字体、字号、粗斜体、对齐、页面设置、表格结构都
原样保留。

```bash
python tests/test_doc2docx.py     # 直接运行，23 项检查
pytest tests/test_doc2docx.py -v  # 或用 pytest
```
