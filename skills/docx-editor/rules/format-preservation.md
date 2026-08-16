# 无损保格式技术 / Lossless Format Preservation

本技能的所有编辑操作都遵循一个铁律：**未修改的部件必须逐字节与原文件一致**。下面是实现这一点的具体 OOXML 技术细节。

## 为什么不用 python-docx 的"重新生成"

python-docx 的 `Document.save()` 会把整个文档对象模型重新序列化，**每个被加载的部件都会被重写**，即使你没碰它。这会导致：

- 属性顺序变化（`rPr` 里子元素顺序不同）
- 空白处理差异（`xml:space="preserve"` 被加或被去）
- 自闭合标签 vs 开闭标签（`<w:b/>` vs `<w:b></w:b>`）
- XML 声明引号风格（`'1.0'` vs `"1.0"`）
- 数字格式归一化（`w:val="1"` vs `w:val="true"`）

这些差异在视觉上无影响，但会让审阅者的 diff 工具亮满全屏，也让"打开→保存"不再是幂等操作。

## 本技能的做法

### 1. 原始字节缓存

`DocxEditor.__init__` 一次性把整个 ZIP 读入 `self._raw = {name: bytes}`。这个字典是"真相之源"——只要一个 part 不在 `self._dirty` 集合里，保存时就直接从 `_raw` 写回，**完全不经过 lxml**。

### 2. 惰性解析

`doc.xml(name)` 只在你真正访问某个 part 时才用 `etree.fromstring` 解析。解析后的树放在 `self._trees[name]`。只读访问（如 `doc.paragraphs` 读文本）不会触发 dirty。

### 3. dirty 集合

只有两种途径进入 `self._dirty`：

- **高层助手自动标记**：`replace_text` 命中时 `self._dirty.add(name)`；`Paragraph.set_text` 通过 `_mark_element_dirty` 反查所属 part 并加入 dirty；`set_part_bytes` 直接加入 dirty。
- **显式 `doc.mark_dirty(name)`**：当你直接操作 lxml 元素后调用。

保存时，**只对 dirty 集合中且已解析的 part 调用 `_serialize`**，其余一律从 `_raw` 逐字节复制。

### 4. ZIP 元信息保留

保存时用 `self._zip.infolist()` 拿到每个 entry 的 `date_time`，构造 `ZipInfo` 时沿用原始时间戳，避免"所有文件时间变成现在"。

### 5. 条目顺序保留

按 `self._names`（原始 `namelist()` 顺序）写入，不排序、不重排。Word 对顺序不敏感，但某些 diff 工具和下游脚本会比对顺序。

## 段落格式保留 — `Paragraph.set_text`

整段换文字时，最容易丢格式的是 run。本技能做法：

1. 找到段落里**第一个含 `<w:t>` 的 run**（它带有你想要的 `rPr`：字体、字号、颜色、粗斜体）
2. 把新文字写进这个 run 的 `<w:t>`，`rPr` 原封不动
3. 其余 run 删掉 `<w:t>`；如果删空后 run 只剩 `rPr` 或为空，整个 run 移除
4. 段落的 `pPr`（段落样式、对齐、缩进、编号）完全不动

这样换文字后，段落级格式（样式、对齐、缩进）和首个文字 run 的字符级格式（字体、字号、颜色、粗斜体）全部继承。

## 跨 run 文字替换 — `replace_text`

OOXML 常把一个"逻辑词"拆到多个 run（例如 `"Hello"` 可能是 `<r><t>Hel</t></r><r><t>lo</t></r>`，因为前半粗体后半正常）。简单按 run 替换会漏掉跨 run 的匹配。

本技能做法（`_replace_in_paragraph`）：

1. 把段落所有 `<w:t>` 拼成完整文本 `full`
2. `full.find(old)` 定位匹配区间 `[pos, end)`
3. 遍历每个 `<w:t>`，计算它与匹配区间的交集
4. **第一个**相交的 `<w:t>` 写入 `前缀 + new + 后缀`（替换文字落在首个 run，继承它的格式）
5. **后续**相交的 `<w:t>` 只删掉匹配部分（`前缀 + 后缀`），保留 run 本身的格式
6. 循环直到 `full` 中不再出现 `old`

这样跨 run 的匹配也能替换，且替换文字继承"匹配起点所在 run"的格式。

## 表格行列增删 — 克隆而非新建

`Table.add_row()` / `Table.add_column()` **深拷贝**最后一行/列作为模板：

- `copy.deepcopy(rows[-1])` 复制整行结构（含 `tcPr`、`pPr`、`rPr`、网格跨度 `gridSpan`/`vMerge`）
- 清空每个单元格的文字（`Cell.set_text("")`）但保留段落和 run 骨架
- `tblGrid` 同步追加一个 `gridCol`（列操作时）

绝不用 `etree.SubElement` 从零建 `w:tr`/`w:tc`——那样会丢掉单元格边距、底纹、跨度等所有属性。

## 插入段落 — 克隆样式

`Paragraph.insert_paragraph_after(text, clone=True)`：

1. `copy.deepcopy(self.el)` 复制整段
2. 删掉除 `pPr` 外的所有子元素（清空内容，留段落属性）
3. 新建一个 `w:r`，从原段落第一个 run 拷贝 `rPr`（字符格式继承）
4. 写入新文字

`clone=False` 时建一个裸 `<w:p>`，不带任何格式——用于需要默认样式的场景。

## 单元格多段落 — `Cell.set_text`

单元格可能有多个段落（多行文字）。`set_text("行1\n行2")`：

1. 按 `\n` 拆行
2. 第 1 行写进单元格现有的第 1 段（保留该段格式）
3. 第 2..N 行：若已有段落就复用，没有就用最后一段 `insert_paragraph_after` 克隆
4. 多余的尾部段落 `delete()`

绝不全删重建——那样会丢掉单元格内每个段落各自的样式。

## 页眉/页脚/脚注/尾注/批注 — 直接 XML 操作

这些 part 不是 `word/document.xml`，本技能的高层段落助手不直接覆盖。统一做法：

```python
W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"

with DocxEditor("file.docx") as doc:
    root = doc.xml("word/footnotes.xml")        # 或 header1/footer1/endnotes/comments
    t = root.find(f".//{{{W}}}t")               # 找第一个文本节点
    t.text = "EDITED"
    doc.mark_dirty("word/footnotes.xml")        # 必须！
    doc.save("out.docx")
```

要点：**`doc.xml(name)` 返回的树被修改后，必须 `doc.mark_dirty(name)`**，否则保存时该 part 按原始字节写回，编辑丢失。

## 解包/重新打包的保真

`unpack` 用 `zipfile.extractall` 原样解压，目录树对应包内结构。`repack` 重新压缩时：

- `[Content_Types].xml` **总是第一个写入**（Word 要求它在前才能识别为有效 OOXML 包）
- 其余文件按稳定排序（`sorted`）写入，保证可复现
- 压缩用 `ZIP_DEFLATED`

解包→重新打包后，**每个 part 的解压字节与原文件一致**（压缩元信息如时间戳可能不同，但内容字节相同）。这由测试 `test_unpack_repack_byte_identity` 验证。