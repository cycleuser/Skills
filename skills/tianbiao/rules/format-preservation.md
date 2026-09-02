# 保格式技术 / Format Preservation (OOXML)

保证"填完还是原来那张表"的具体技术要点。

## 1. 可见单元格 vs 逻辑网格（最易踩坑）

python-docx 的 `table.cell(r, c)` 会把**合并单元格展开成逻辑网格**。一个横跨 4 列的单元格在逻辑网格里占 4 个索引，导致 `cell(0, 3)` 定位到错误位置——这正是"数据填错格"的根因。

正确做法：按**可见单元格**（该行实际的 `<w:tc>` 元素）定位。

```python
from docx.table import _Cell
from docx.oxml.ns import qn
def vcells(table, ri):
    tr = table.rows[ri]._tr
    return [_Cell(tc, table) for tc in tr.findall(qn('w:tc'))]

# 例：某行可见结构为 [授课单位][<单位值>][课程名称][值]
set_cell_value(vcells(T, 0)[3], "<课程名称>")
```

## 2. 保字体填值

只改单元格首个 run 的文本，删掉多余 run，剥离模板里的示例标记。

```python
def set_cell_value(cell, text):
    p0 = cell.paragraphs[0]
    for p in cell.paragraphs[1:]:
        p._p.getparent().remove(p._p)
    runs = p0.runs
    if runs:
        runs[0].text = text
        for extra in runs[1:]:
            extra._element.getparent().remove(extra._element)
        rPr = runs[0]._element.find(qn('w:rPr'))
    else:
        rPr = p0.add_run(text)._element.find(qn('w:rPr'))
    for tag in ('w:color', 'w:highlight'):   # 去掉示例红字/黄色高亮
        if rPr is not None and rPr.find(qn(tag)) is not None:
            rPr.remove(rPr.find(qn(tag)))
```

要点：**继承**原 run 的 `rPr`（字体族、字号、加粗），不要新建 run 并自己设字体——那样默认会退回 Calibri/Times，中文变形。

## 3. 分析类长文本（多段落大单元格）

学校表里常有一个大格，含"一、…… 二、…… 三、……"多段。模板里这些段落分标题段（无高亮、有首行缩进）和示例正文段（黄色高亮批注）。

做法：克隆模板中的**标题段样式**和**正文段样式**各一份，按需要重复生成新段落，保留字体、去高亮、正文段加 2 字符首行缩进。

```python
# heading_style_p / body_style_p 是从模板取的样例 <w:p>
set_multi_paragraph_cell(cell,
    [("一、……", True), ("正文……", False),
     ("二、……", True), ("正文……", False)],
    heading_style_p, body_style_p)
```

## 4. 明细表防"跨页散架"

批量名单（几十上百人）最容易排版灾难：一张表松散跨好几页、行在页脚断成两半、翻页后没了表头。三件套解决：

| 措施 | OOXML | 作用 |
|------|-------|------|
| 表头跨页重复 | 表头行 `w:trPr` 加 `<w:tblHeader/>` | 每页顶部都有列名 |
| 行不跨页断裂 | 每行 `w:trPr` 加 `<w:cantSplit/>` | 单行不被拦腰截断 |
| 紧凑排版 | `w:tblCellMar` 窄边距 + 小字号 `w:sz`（如 18=9pt）+ 单倍行距 | 一页容纳更多行 |

直接用 [scripts/fill_docx_template.py](../scripts/fill_docx_template.py) 的 `make_detail_table(headers, rows, base_rpr, sz='18')`。

## 5. 增删数据行

模板题型行数常与实际不符（如模板 5 行、你要 3 行；或模板 5 行、你要 7 行）。

- 增行：`copy.deepcopy(table.rows[template_ri]._tr)` 复制一份合适的样例行，改值后 `append` 到 `tbl`。
- 删行：`tbl.remove(tr)`。
- 合并单元格续行：`vMerge=restart` 行写值，`vMerge=continue` 行留空。

## 6. Excel 模板

用 openpyxl 打开原 `.xlsx`，**只写 `cell.value`，不碰样式**（openpyxl 默认保留原格式）。`.xls` 先用 LibreOffice 转 `.xlsx`。含公式的模板：写入分项，让公式自动算，或按模板既有公式格式写入。

## 7. 交付格式选择

- 用户要 `.docx` → 直接交填好的 docx（本技能主路径）。
- 用户要 `.doc` → docx 填好后 `soffice --convert-to doc`（LibreOffice 保表格）。
- 绝不用 textutil 生成 doc/docx 交付件（拍平表格）。

## 8. 值区本身是合并区域（推荐表/申报表常见）

很多表（评优推荐表、职称申报表）的值区本身就是合并单元格：如"所在单位"值区跨 3 列、"事迹"值区跨 8 列。此时 `vcells()` 拿到的值区是一个 `_Cell`（横跨多个逻辑网格位），用 `row.cells[i]` 任意位置访问返回的是**同一个 tc**。

先打印结构再填，避免误判：

```python
def dump_structure(table):
    for ri, row in enumerate(table.rows):
        seen = {}
        parts = []
        for ci, cell in enumerate(row.cells):
            key = id(cell._tc)
            if key in seen:
                parts.append(f"[{seen[key]}<-合并]")
            else:
                seen[key] = ci
                parts.append(f"({ci}:{cell.text.strip()[:10]})")
        print(f"R{ri}: " + " ".join(parts))
# 输出示例: R2: (0:所在单位) (1:) [1<-合并] [1<-合并] (4:推荐名称) [4<-合并] (6:) [6<-合并] [6<-合并]
# 即: 所在单位值区=grid位1-3，推荐名称值区=grid位6-8。填值时访问 row.cells[1] 和 row.cells[6] 即可。
```

## 9. 大单元格保尾（签字行/日期不被覆盖）

事迹/主要事迹类大单元格常在底部自带"负责人签字：＿＿ 年 月 日"。清空重写会把尾部一起冲掉。处理：

- 先读原 cell 文本，定位尾部标记（"负责人签字""组长签字""学校公章""年 月 日"）。
- 写法：正文按行 `add_paragraph` 写入，**最后补回尾部标记**（`keep_tail` 参数）。
- 校验：重新打开读取 cell 文本，确认尾部仍在。

```python
def set_cell_keep_tail(cell, body, tail="负责人签字："):
    # 清空 cell 段落与 run → 按 body 行 add_paragraph（宋体）→ 末尾 add_paragraph(tail)
```

## 10. 多行写入字体设置

清空重写时中文字体必须走 eastAsia，否则回落成 Calibri 中文变形：

```python
run.font.name = "Times New Roman"
run._element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")
run.font.size = Pt(12)   # 小四
```

## 自检清单 / Checklist

- [ ] 用 `vcells()` 或 `id(cell._tc)` 去重定位（值区合并也能定位）
- [ ] 填值继承原 rPr，去除示例 color/highlight
- [ ] 分析段克隆模板段落样式，保留字体
- [ ] 大单元格底部签字行/日期保尾（`keep_tail`）
- [ ] 多行写入设 eastAsia 中文字体
- [ ] 明细表带 `tblHeader` + `cantSplit` + 小字号
- [ ] 表格数量/行列与模板一致
- [ ] 输出为新文件，不覆盖模板
