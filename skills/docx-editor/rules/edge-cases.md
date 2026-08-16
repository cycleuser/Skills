# 边界情况与排错 / Edge Cases & Troubleshooting

## 边界情况

### 合并单元格

`Table.cell(r, c)` 按**物理 `w:tc`** 索引。遇到 `gridSpan`（横向合并）或 `vMerge`（纵向合并）时：

- `col_count()` 返回的是"所有行中最大的 `tc` 数"，可能小于逻辑列数
- 被合并的单元格在 XML 里**不存在**对应 `tc`（横向合并只留一个 `tc` 带 `gridSpan`）
- `vMerge="continue"` 的单元格存在但应留空，只在 `vMerge="restart"` 行写值

**对策**：遍历 `tb.rows[r].findall(w("tc"))` 拿到实际 `tc` 列表，按物理顺序定位；或用 `tc.find(w("tcPr")/w("gridSpan"))` 读取跨度自行映射逻辑列。

### 表格内段落

`doc.paragraphs` 只返回 body 直属段落。表格内的段落要用：

- `doc.all_paragraphs()` — 全文档所有段落（含表格内、嵌套表格内）
- `doc.tables[i].cell(r, c).paragraphs` — 某单元格内段落

### 空单元格

空单元格仍含一个空 `<w:p>`。`Cell.set_text("x")` 会把文字写进这个已有段落，保留它的 `pPr`。`Cell.set_text("")` 清空但不删段落（单元格必须至少有一个段落，否则 Word 报错）。

### 段落是单元格唯一段落时的 delete

`Paragraph.delete()` 检测到本段是所在单元格的唯一段落时，只 `set_text("")` 不真删——避免单元格变空导致 OOXML 非法。

### 嵌套表格

`doc.tables` 只返回 body 直属表格。嵌套表格内的表格要用 `doc.body.iter(w("tbl"))` 遍历，或访问 `cell.paragraphs` 后再找其下的 `tbl`。

### 跨 run 的样式继承

一个"逻辑段落"可能由多个 run 组成，每个 run 有不同 `rPr`（如前半粗体后半正常）。`Paragraph.set_text("新文字")` 把所有文字写进**第一个有 `<w:t>` 的 run**，其余 run 清空。这意味着：

- 新文字继承的是"第一个有文字 run"的格式
- 如果你想保留多个 run 的不同格式，不要用 `set_text`，改用 `runs[i].text = ...` 逐个改

### 页码域不要动

页脚里的页码是 `<w:fldChar fldCharType="begin">` + `<w:instrText> PAGE </w:instrText>` + `<w:fldChar fldCharType="end">`。编辑页脚时：

- 只改域前后的文字 `<w:t>`（如 `"Page "` → `"第 "`）
- **不要动 `instrText`**（`PAGE`/`NUMPAGES` 指令文字）
- **不要动 `fldChar`**（域起止标记）

### 命名空间

OOXML 主命名空间是 `w = http://schemas.openxmlformats.org/wordprocessingml/2006/main`。但某些部件用别的：

- `docProps/core.xml` — `dc`（Dublin Core）、`cp`、`dcterms`
- `[Content_Types].xml` — 包内容类型命名空间
- `_rels/*.rels` — 关系命名空间

用 `root.find(f"{{{NS}}}tag")` 时务必带正确的 NS，`w` 命名空间不适用于这些部件。

### 大文件

`DocxEditor.__init__` 一次性把整个 ZIP 读入内存（`self._raw`）。对极大 docx（含大量高清图片）会占内存。若只需编辑小部件，可先用 `unpack` 解包，只改需要的文件，再 `repack`——这样内存占用只取决于改动文件大小。

## 排错

| 症状 | 原因 | 对策 |
|---|---|---|
| 保存后编辑丢失 | 直接改了 lxml 元素但没 `mark_dirty` | 在 `doc.save()` 前调用 `doc.mark_dirty(part_name)` |
| 保存后所有部件都变了 | 用了 python-docx 的 `Document.save()` 而非本技能的 `DocxEditor.save()` | 改用 `from docxmod import DocxEditor` |
| 页眉/脚注/批注改了没生效 | 这些 part 不被 `replace_text` 覆盖，且直接改 XML 后没 `mark_dirty` | 用 `doc.xml(name)` + `mark_dirty(name)` |
| 表格行列数对不上 | 合并单元格导致物理 `tc` 数 ≠ 逻辑列数 | 用 `rows[r].findall(w("tc"))` 按物理定位 |
| Word 打开报"文件已损坏" | 改了 `[Content_Types].xml` 但没加对 override；或删了单元格唯一段落 | 检查 Content Types；不要删单元格最后一段，用 `set_text("")` |
| 跨 run 替换没命中 | `replace_text` 已处理跨 run，但若 run 被 `<w:proofErr>` 等中间元素打断可能漏 | 检查 XML 结构；必要时先 `unpack` 手工处理再 `repack` |
| `doc.paragraphs` 漏了表格内段落 | 这是设计行为，`paragraphs` 只含 body 直属 | 用 `doc.all_paragraphs()` 或 `cell.paragraphs` |
| 原地保存后原文件变了 | `doc.save()` 不带参数就是原地覆盖 | 想保留原件用 `doc.save("out.docx")` |
| 字体名写进去但 Word 不认 | 只设了 `w:ascii` 没设 `w:eastAsia` | 中文/日文需同时设 `w:eastAsia`，见 `format-preservation.md` |
| `lxml` 报 `XMLSyntaxError` | part 不是合法 XML（可能是二进制） | 用 `doc.part_bytes(name)` 读原始字节，不要用 `doc.xml(name)` |

## 安全边界

- **不覆盖原文件**：生产环境建议总是 `doc.save("新文件.docx")`，保留原件作回滚。`doc.save()` 原地覆盖虽走临时文件+原子移动，但仍是破坏性操作。
- **编辑前备份**：对重要文档，先 `shutil.copy(原, 备份)` 再编辑。
- **校验**：编辑后用 `python-docx` 打开输出文件确认无结构损坏；对比部件字节确认只改了预期 part。
- **不要动 `[Content_Types].xml` 的扩展映射**：除非你真的新增了部件类型。改错了 Word 会拒绝打开。