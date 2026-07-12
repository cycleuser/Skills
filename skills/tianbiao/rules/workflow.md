# 填表工作流 / Fill Workflow

模板保真填表的完整操作流程。核心：**照着原表填，不重排**。

## Step 1 — 转换模板 Convert

学校模板常是老 `.doc`/`.xls`。转成可编辑的 `.docx`/`.xlsx`，且必须保真（保留表格、字体、合并单元格）。

```bash
# 首选 LibreOffice headless（保真度高）
soffice --headless --convert-to docx --outdir <出目录> "<模板.doc>"
soffice --headless --convert-to xlsx --outdir <出目录> "<模板.xls>"
```

macOS 上若 `soffice` 报 `LibreOffice.app: No such file or directory`（app 被删但 brew 记录还在）：

```bash
brew reinstall --cask libreoffice
# soffice 真实路径：/Applications/LibreOffice.app/Contents/MacOS/soffice
```

> ⚠️ 不要用 `textutil -convert docx`（会把表格拍平成段落）或 `pandoc`（结构走样）来生成**交付件**。它们只适合**读取/预览**内容。

## Step 2 — 摸底模板 Inspect

填之前必须先看清模板结构，尤其是合并单元格。

```python
import docx
from docx.oxml.ns import qn
d = docx.Document("template.docx")
for ti, t in enumerate(d.tables):
    print(f"TABLE {ti} rows={len(t.rows)}")
    for ri, row in enumerate(t.rows):
        cells = []
        for tc in row._tr.findall(qn('w:tc')):
            txt = ''.join(n.text or '' for n in tc.iter(qn('w:t')))
            tcPr = tc.find(qn('w:tcPr')); span = 1; vm = ''
            if tcPr is not None:
                gs = tcPr.find(qn('w:gridSpan'))
                if gs is not None: span = gs.get(qn('w:val'))
                if tcPr.find(qn('w:vMerge')) is not None:
                    vm = tcPr.find(qn('w:vMerge')).get(qn('w:val')) or 'cont'
            cells.append(f"[{txt[:20]!r} s{span}{'/'+vm if vm else ''}]")
        print(ri, ' '.join(cells))
```

记录：每个要填的值在**第几行、第几个可见单元格**；每个关键单元格首个 run 的字体 `rPr`；分析类大格用的段落样式（标题段/正文段字体）。

## Step 3 — 准备数据 Prepare Data

从源文件提取结构化数据（点名册 `.xls` 用 `xlrd`，成绩表 `.xlsx` 用 `openpyxl`）。

若模板要求的某项分数在源数据里没有直接列，需**反推计算公式**：用已知的分项和结果做最小误差搜索，并用**全体样本**验证吻合（允许四舍五入的 ±1 差异）。示例：

```
平时 = 0.2×课堂表现 + 0.4×作业平均 + 0.4×综合测验
总评 = 0.5×平时 + 0.5×期末
```

反推后务必打印"不吻合的行"，确认只剩显示取整误差。

## Step 4 — 填充 Fill

打开**原模板** docx（不是新建 Document）。

- 表头/值单元格：`set_cell_value(vcells(T, ri)[ci], "值")`
- 分析类长文本：`set_multi_paragraph_cell(cell, [(text, is_heading), ...], heading_style_p, body_style_p)`
- 需要更多数据行：先 `clone_table_row()` 复制模板行再改值
- 大批量名单：`make_detail_table(headers, rows, base_rpr)` —— 紧凑、表头跨页重复、行不断裂

见 [scripts/fill_docx_template.py](../scripts/fill_docx_template.py)。

保存为新文件，命名 `<主体>-<文档名>.docx`（例：`<课程名>-试卷质量分析表及成绩分析表.docx`）。

## Step 5 — 校验 Verify

```python
python3 scripts/fill_docx_template.py verify "输出.docx"
```

逐项核对：
- 表数量、每表行列数与模板一致
- 关键单元格字体 `rPr` 未变（值=宋体、分析段=仿宋等）
- 每条数据与源文件一致（抽查 + 全量计数：如"每张明细表都应有 N 行学生"）
- 无残留 `%d`/`%.1f` 等未格式化占位符
- 无残留模板示例内容（如样例课程名、示例学生）
- 可选：`soffice --convert-to pdf` 后数页数，确认排版整洁

## 命令映射 / Command Mapping

| 命令 | 动作 |
|------|------|
| `/填表 convert <文件>` | Step 1 |
| `/填表 inspect <模板>` | Step 2 |
| `/填表 <模板> <数据>` | Step 3–4（含必要的数据反推） |
| `/填表 check <文档>` | Step 5 |

英文命令 `/tianbiao [convert|inspect|check] ...` 行为一致。
