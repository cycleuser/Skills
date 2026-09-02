# 合并单元格填写与保格式 (Table Filling & Format Preservation)

## 定位方法

- 打印结构：`fill_docx.py dump <模板>` 输出每个表格每个 grid 位置的 `(序号:文本)`，合并区域显示 `[主序号<-合并]`。
- 值区写入：对合并区域，`row.cells[i]`（任意 i 在区域内）返回的是**同一个 tc 对象**。填值写在这个 tc 上即可，不要重复写。
- 用 `id(cell._tc)` 去重，避免把合并区域当成多个单元格。

## set_cell 保格式要点

- 清空：删 `cell.paragraphs[1:]`；清首段全部 run；按行 `add_paragraph`。
- 字体：`run.font.name = 'Times New Roman'` + `rPr.rFonts.set(qn('w:eastAsia'),'宋体')`（中文字体走 eastAsia）。
- 字号：按模板注（如小四 = 12pt、五号 = 10.5pt）。
- 保留尾部：事迹区若自带"负责人签字："，`keep_tail` 参数在正文写完后补回。

## 必校验项

- 重新打开输出文件，读取每个填充格文本核对。
- 签字行/尾部仍在。
- 只改了目标格；其余表格未动。
