# 工作流 / Workflow

本技能的核心是**无损**：解包、编辑、重新打包一个 DOCX，**未修改的部件必须逐字节与原文件一致**，不能因为"重新保存"就出现格式漂移、布局变化、批注/脚注丢失。

## 四步工作流

```
Step 1  打开 Open
   DocxEditor(path) 把 docx 当 ZIP 读入，缓存每个 entry 的原始字节。
   不解析 XML，直到你真正访问某个 part 才惰性解析。

Step 2  编辑 Edit
   三条路径，按"改动面"由小到大选择：
   a) 高层助手（推荐）— replace_text / Paragraph.set_text / Cell.set_text /
      Table.add_row / Table.delete_column / Paragraph.insert_paragraph_after /
      Paragraph.style 等。它们只改必要的元素并自动标记 dirty。
   b) 直接操作 lxml — doc.xml("word/footnotes.xml") 拿到根元素后直接改
      t.text = ...；此时必须手动调用 doc.mark_dirty("word/footnotes.xml")，
      否则保存时不会重新序列化该部件。
   c) 整体替换部件字节 — doc.set_part_bytes("word/media/image1.png", png_bytes)，
      用于换图片、换字体等二进制部件。

Step 3  保存 Save
   doc.save(out_path) 或 doc.save()（原地覆盖，走临时文件+原子移动）。
   保存时：dirty 集合里的 XML 部件重新序列化；其余部件从缓存逐字节回写；
   ZIP 条目顺序与原文件保持一致。新部件（dirty 里但不在原 names 中的）会追加。

Step 4  校验 Verify
   重新打开输出文件，确认编辑生效；并对比原始与输出的部件字节，
   确认只有预期的那一两个 part 改了，其余全部 byte-identical。
```

## 命令行操作

```bash
# 解包到目录（每个 part 原样落盘，目录树对应包内结构）
python scripts/docxmod.py unpack report.docx report_unpacked/

# 从目录重新打包（[Content_Types].xml 自动优先写入，其余按稳定排序）
python scripts/docxmod.py pack report_unpacked/ report-rebuilt.docx

# 打印段落与表格结构
python scripts/docxmod.py dump report.docx

# 全局查找替换（跨 run 匹配，保留每个 run 的格式）
python scripts/docxmod.py replace report.docx "旧词" "新词" -o out.docx

# 按序号重写主文档段落
python scripts/docxmod.py set-para report.docx 3 "新段落文字" -o out.docx

# 重写表格单元格
python scripts/docxmod.py set-cell report.docx 0 1 2 "单元格文字" -o out.docx

# 列出所有部件（可加 --bytes 看大小）
python scripts/docxmod.py parts report.docx --bytes

# 查找包含关键词的段落
python scripts/docxmod.py find report.docx "关键词"
```

## GUI 操作

```bash
python scripts/docxmod_gui.py [file.docx]
```

- **File 菜单**：Open / Save / Save As / Unpack to Folder / Repack from Folder / Close
- **Paragraph 标签**：整段重写（保留格式）、向上/下插入、删除、改样式
- **Table 标签**：双击单元格编辑、增删行列
- **Parts 标签**：双击 XML 部件查看/编辑原始 XML；可看每个 part 字节大小

## 关键决策点

### 何时用 `mark_dirty`

`doc.xml(name)` 返回 lxml 根元素后，**直接修改元素**（如 `t.text = "x"`、`el.set(...)`、`parent.remove(child)`）**不会**自动标记 dirty。必须显式调用：

```python
root = doc.xml("word/footnotes.xml")
t.text = "EDITED"
doc.mark_dirty("word/footnotes.xml")   # 必须！否则保存时不重写
```

高层助手（`replace_text` / `Paragraph.set_text` / `Cell.set_text` 等）已经自动处理，无需手动 `mark_dirty`。

### 何时用 `set_part_bytes`

换图片、换字体等**二进制**部件，或想整体替换一个 XML 部件的字节而不经过 lxml 解析时：

```python
doc.set_part_bytes("word/media/image1.png", new_png_bytes)
```

### 保存到新路径 vs 原地覆盖

- `doc.save("out.docx")`：写到新路径，原文件不动（测试应验证原文件字节不变）
- `doc.save()`：原地覆盖，内部走 `out + ".tmp.docx"` 临时文件 + `shutil.move` 原子替换，避免中途失败损坏原件

## 校验清单

每次编辑后至少确认：

1. `set(原始 parts) == set(输出 parts)` — 没有部件丢失或新增（除非你故意加）
2. 除预期改动的 part 外，其余 `原始[n] == 输出[n]` 逐字节一致
3. 重新打开输出文件，编辑内容确实生效
4. 输出文件可被 python-docx / Word 正常打开（zip 结构完整）