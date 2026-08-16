# 可编辑目标 / Editable Targets

本技能能编辑 DOCX 包内的下列部件。每项给出定位方法、编辑示例和注意事项。

## 部件地图

| 部件路径 | 内容 | 高层助手 | 直接 XML 时需 `mark_dirty` |
|---|---|---|---|
| `word/document.xml` | 正文（段落、表格、 sectPr） | `paragraphs` / `tables` / `replace_text` | 自动 |
| `word/header1.xml` … | 页眉 | — | `mark_dirty("word/header1.xml")` |
| `word/footer1.xml` … | 页脚（含页码域 `PAGE`/`NUMPAGES`） | — | `mark_dirty("word/footer1.xml")` |
| `word/footnotes.xml` | 脚注内容 | — | `mark_dirty("word/footnotes.xml")` |
| `word/endnotes.xml` | 尾注内容 | — | `mark_dirty("word/endnotes.xml")` |
| `word/comments.xml` | 批注内容（`w:comment` 元素） | — | `mark_dirty("word/comments.xml")` |
| `word/styles.xml` | 段落/字符样式定义 | — | `mark_dirty("word/styles.xml")` |
| `word/numbering.xml` | 列表编号定义 | — | `mark_dirty("word/numbering.xml")` |
| `word/settings.xml` | 文档设置（页码起始、视图等） | — | `mark_dirty("word/settings.xml")` |
| `word/theme/theme1.xml` | 主题颜色/字体 | — | `mark_dirty("word/theme/theme1.xml")` |
| `word/fontTable.xml` | 字体表 | — | `mark_dirty("word/fontTable.xml")` |
| `word/media/imageN.png` 等 | 嵌入图片（二进制） | `set_part_bytes` | 自动 |
| `word/embeddings/...` | OLE 嵌入对象 | `set_part_bytes` | 自动 |
| `[Content_Types].xml` | 包内容类型声明 | — | `mark_dirty("[Content_Types].xml")` |
| `docProps/core.xml` | 标题、作者、修改时间 | — | `mark_dirty("docProps/core.xml")` |

## 正文段落 / 段落文字

```python
with DocxEditor("f.docx") as doc:
    # 读
    print(doc.paragraphs[3].text)
    # 整段重写（保留格式）
    doc.paragraphs[3].set_text("新文字")
    # 插入
    doc.paragraphs[3].insert_paragraph_after("新段落", clone=True)
    # 删除
    doc.paragraphs[3].delete()
    # 改样式
    doc.paragraphs[3].style = "Heading1"
```

注意：`doc.paragraphs` 只含 body 直属段落，不含表格内段落。要遍历全部用 `doc.all_paragraphs()`。

## 表格 / 单元格

```python
with DocxEditor("f.docx") as doc:
    tb = doc.tables[0]
    # 读
    print(tb.row_count(), tb.col_count())
    print(tb.cell(1, 2).text)
    # 写单元格
    tb.cell(1, 2).set_text("值")
    # 增删行列（克隆最后一行/列的格式）
    tb.add_row()
    tb.delete_row(0)
    tb.add_column()
    tb.delete_column(1)
```

注意：合并单元格会导致 `col_count()` 返回的是"最大物理 `tc` 数"，与逻辑列数可能不同。定位用 `tb.cell(r, c)` 是按物理 `tc` 索引，遇到 `gridSpan`/`vMerge` 要自行判断。

## Run（字符级）

```python
with DocxEditor("f.docx") as doc:
    p = doc.paragraphs[2]
    for r in p.runs:
        print(repr(r.text), "bold" if r.rpr is not None and r.rpr.find(w("b")) is not None else "")
    # 改某个 run 的文字，保留它的 rPr
    p.runs[0].text = "新字符"
```

注意：`Run.text = ` 只改第一个 `<w:t>`，删多余 `<w:t>`，`rPr` 不动。

## 全局查找替换

```python
with DocxEditor("f.docx") as doc:
    n = doc.replace_text("2024版", "2025版")
    # 默认覆盖 document + 所有 header/footer/footnotes/endnotes
    # 只在 document 替换：
    # doc.replace_text("x", "y", parts=["word/document.xml"])
    doc.save("out.docx")
```

注意：跨 run 的匹配也能处理，替换文字继承"匹配起点 run"的格式。

## 页眉 / 页脚

```python
W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"

with DocxEditor("f.docx") as doc:
    root = doc.xml("word/header1.xml")
    t = root.find(f".//{{{W}}}t")
    t.text = "新页眉"
    doc.mark_dirty("word/header1.xml")
    doc.save("out.docx")
```

页脚里的页码是域代码（`<w:fldChar>` + `<w:instrText>PAGE</w:instrText>`），**不要动 `instrText`**，只改域前后的文字 run（如 `"Page "` 这个 `<w:t>`）。

## 脚注 / 尾注

```python
with DocxEditor("f.docx") as doc:
    root = doc.xml("word/footnotes.xml")
    for fn in root.findall(f"{{{W}}}footnote"):
        # 跳过 separator/continuationSeparator（id 为 -1/0）
        if fn.get(f"{{{W}}}id") in ("-1", "0"):
            continue
        t = fn.find(f".//{{{W}}}t")
        t.text = "新脚注"
    doc.mark_dirty("word/footnotes.xml")
    doc.save("out.docx")
```

尾注同理，部件名 `word/endnotes.xml`，元素 `w:endnote`。

## 批注 / Comment

```python
with DocxEditor("f.docx") as doc:
    root = doc.xml("word/comments.xml")
    for c in root.findall(f"{{{W}}}comment"):
        author = c.get(f"{{{W}}}author")
        t = c.find(f".//{{{W}}}t")
        t.text = f"{author} said: 新批注"
    doc.mark_dirty("word/comments.xml")
    doc.save("out.docx")
```

注意：批注在 `word/document.xml` 里有锚点（`commentRangeStart`/`commentRangeEnd`/`commentReference`），不要动这些锚点，只改 `word/comments.xml` 里的内容。

## 换图片 / 二进制部件

```python
with open("new.png", "rb") as f:
    new_png = f.read()

with DocxEditor("f.docx") as doc:
    # 找到图片部件名
    images = [n for n in doc.parts if n.startswith("word/media/")]
    doc.set_part_bytes(images[0], new_png)
    doc.save("out.docx")
```

注意：`set_part_bytes` 走原始字节替换，不经过 lxml，对二进制部件最安全。

## 直接编辑原始 XML

```python
with DocxEditor("f.docx") as doc:
    data = doc.part_bytes("word/styles.xml")
    new_data = data.replace(b"</w:styles>", b"<!-- mark --></w:styles>")
    doc.set_part_bytes("word/styles.xml", new_data)
    doc.save("out.docx")
```

适用于批量文本替换、加注释标记等不希望经过 lxml 重新序列化的场景（避免属性顺序/引号风格变化）。

## 修改文档属性

```python
with DocxEditor("f.docx") as doc:
    root = doc.xml("docProps/core.xml")
    # core.xml 用的是 dc 命名空间，不是 w
    DC = "http://purl.org/dc/elements/1.1/"
    title = root.find(f"{{{DC}}}title")
    if title is not None:
        title.text = "新标题"
    doc.mark_dirty("docProps/core.xml")
    doc.save("out.docx")
```

注意：`docProps/core.xml` 的命名空间是 `dc` / `cp` / `dcterms`，不是 `w`。用 `find` 时要带正确的 Clark 记法。