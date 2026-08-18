# 读图转精修提示词 / Vision-to-Prompt Workflow

这是本技能的核心创新——把"人给的草图 + 模糊描述"转化为"大模型能精确执行的 SVG 生成提示词"。

## 为什么要这一步

真实场景：老师发来一张手画草图（拍照或扫描）加一句"画个流程图，大概就是数据进来、预处理、模型、输出"。你用大模型直接生成 SVG，结果框重叠、文字溢出、箭头指错——因为大模型不知道草图的精确布局意图。

解决方案：先让多模态大模型（GPT-4o / Claude / Gemini）**读草图**，提取出精确的结构化布局描述（哪个框在哪、哪个连哪个、标签是什么），再把这个描述转化为本技能网格模板能直接执行的代码。

## 工作流 / Workflow

```
Step 1  读草图
   输入：手画草图（照片/扫描/PDF截图/PowerPoint草稿）
   操作：把草图发给多模态模型，要求输出结构化 JSON
   输出：layout.json（框列表、箭头列表、标签列表）

Step 2  转提示词
   把 layout.json 转成 svg_template.py 的 Python 代码
   （网格坐标计算 + 模板调用）

Step 3  生成
   执行代码生成 SVG

Step 4  校验
   validate_svg.py 检查无覆盖/越界/重叠

Step 5  精修微调
   若有 warning/fail，读校验报告定位问题，调网格坐标/字号/箭头路径，重新生成
```

## Step 1：读草图的结构化提示词

把草图发给多模态模型时，用这个提示词：

```
你是科研流程图结构分析专家。请分析附图（手画草图/截图），输出严格的 JSON 描述图的布局结构。

输出格式（必须严格 JSON，不要 markdown 代码块）：
{
  "title": "图标题（中英双语，如 \"Two-stage pipeline / 两阶段流程\"）",
  "boxes": [
    {
      "name": "唯一标识符（英文，如 input/preprocess/model/output）",
      "label": "框内文字（中英双语，\\n 分行）",
      "role": "input|process|model|output|decision|data|feedback|other",
      "grid_hint": "草图中的大致位置（top-left/top-center/top-right/mid-left/center/mid-right/bottom-left/bottom-center/bottom-right）",
      "size_hint": "small|medium|large（草图里这个框看起来多大）"
    }
  ],
  "arrows": [
    {
      "from": "起点框 name",
      "to": "终点框 name",
      "label": "箭头标签（如有）",
      "style": "solid|dashed|bold（实线/虚线/粗线）",
      "curve": 0
    }
  ],
  "notes": ["任何你观察到的额外信息，如分组、颜色含义、特殊标注等"]
}

注意：
- 框的 name 必须唯一且是英文标识符
- label 用 \\n 表示换行
- grid_hint 描述草图中的视觉位置，用于后续网格映射
- 如果箭头有弧度，curve 填大概的弧度（正数左偏，负数右偏）
- 只输出 JSON，不要任何解释文字
```

示例：草图画的是"输入→预处理→模型→输出"的横向流程，模型读出：

```json
{
  "title": "Two-stage pipeline / 两阶段流程",
  "boxes": [
    {"name": "input", "label": "Input Data\n输入数据", "role": "input", "grid_hint": "top-left", "size_hint": "medium"},
    {"name": "preprocess", "label": "Preprocessing\n预处理", "role": "process", "grid_hint": "top-center", "size_hint": "medium"},
    {"name": "model", "label": "Model\n模型", "role": "model", "grid_hint": "mid-right", "size_hint": "medium"},
    {"name": "output", "label": "Output\n输出", "role": "output", "grid_hint": "bottom-right", "size_hint": "small"}
  ],
  "arrows": [
    {"from": "input", "to": "preprocess", "label": "raw", "style": "solid", "curve": 0},
    {"from": "preprocess", "to": "model", "label": "features", "style": "solid", "curve": 0},
    {"from": "model", "to": "output", "label": "predict", "style": "solid", "curve": 0}
  ],
  "notes": ["横向流程", "模型框用了圆角"]
}
```

## Step 2：layout.json → 网格坐标映射

拿到 JSON 后，把 `grid_hint` 映射到网格行列。标准映射表（4×4 网格）：

| grid_hint | row | col | 备注 |
|---|---|---|---|
| top-left | 0 | 0 | 左上角 |
| top-center | 0 | 1 (colspan=2) | 顶部居中跨2列 |
| top-right | 0 | 3 | 右上角 |
| mid-left | 1 (rowspan=2) | 0 | 左侧跨2行 |
| center | 1 (rowspan=2) | 1 (colspan=2) | 正中跨2×2 |
| mid-right | 1 (rowspan=2) | 3 | 右侧跨2行 |
| bottom-left | 3 | 0 | 左下角 |
| bottom-center | 3 | 1 (colspan=2) | 底部居中跨2列 |
| bottom-right | 3 | 3 | 右下角 |

size_hint 映射：
- small → 1×1 格
- medium → 1×2 格（colspan=2）或 2×1（rowspan=2）
- large → 2×2 格（rowspan=2, colspan=2）

遇到多个框映射到同一格时，自动顺延到相邻空格（由模板的占位检查保证不冲突）。

## Step 3：生成代码模板

把映射结果填入这个代码模板：

```python
from svg_template import Figure

fig = Figure(cols={{COLS}}, rows={{ROWS}}, cell_w={{CELL_W}}, cell_h={{CELL_H}},
             font_size=12, title_size=15)
fig.title("{{TITLE}}")

{{BOXES}}  # 每个 fig.box(...)
{{ARROWS}}  # 每个 fig.arrow(...)

fig.save("{{OUTPUT_PATH}}")
```

每个 `box` 行：
```python
fig.box("{{name}}", {{row}}, {{col}}, rowspan={{rowspan}}, colspan={{colspan}},
        text="{{label}}", fill="{{color}}", shape="{{shape}}")
```

每个 `arrow` 行：
```python
fig.arrow("{{from}}", "{{from_dir}}", "{{to}}", "{{to_dir}}",
          label="{{label}}", dashed={{dashed}}, curve={{curve}})
```

箭头方向自动推断：从 from 的中心朝 to 的中心，选最近的边：
- from 在 to 左侧 → from.right → to.left
- from 在 to 上方 → from.bottom → to.top
- 对角线 → from.bottom → to.top（或按视觉习惯选）

## Step 5：精修微调循环

校验脚本报 warning/fail 时，按类型修复：

| 问题 | 修复 |
|---|---|
| 文字溢出框 | 增大框的 colspan/rowspan，或缩短 label 文字 |
| 字号太小 | 增大框，让字号自动放大 |
| 框重叠 | 检查两个框是否映射到同一格，调整其中一个到空格 |
| 箭头悬空 | 检查 from/to 的 name 是否拼写正确，锚点方向是否合理 |
| 文字重叠 | 检查两个框是否太近，增大间距或调整箭头标签的 curve 偏移 |
| 越出 viewBox | 增大 cols/rows 或 cell_w/cell_h |

每次修复后重新 `save()` + `validate()`，循环直到 0 failures。

## 无草图时的退化路径

如果用户只有文字描述没有草图，跳过 Step 1，直接从文字描述提取结构：

```
请把下面的流程描述转化为布局 JSON（格式同上）：

"用户描述：..."
```

用文本模型（不需要多模态）就能完成，但精度不如读草图——因为没有视觉位置信息，`grid_hint` 要靠语义推断（"先...然后...最后..."→ 横向 left→right；"上面是...下面是..."→ 纵向 top→bottom）。