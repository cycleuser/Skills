# 工作流 / Workflow

本技能的完整工作链：从草图（或文字描述）到一张通过自动校验、无任何覆盖的科研 SVG 流程图。

## 完整工作链 / Full Pipeline

```
用户输入                      本技能处理                        输出
─────────────────────────────────────────────────────────────────────
草图（照片/截图）   →  Step 1 读图转 JSON  →  layout.json
                           ↓
                     Step 2 JSON 转网格代码   →  build_figure.py
                           ↓
                     Step 3 生成 SVG          →  figure.svg
                           ↓
                     Step 4 校验              →  校验报告
                           ↓
                     Step 5 精修循环          →  figure-final.svg（0 failures）
```

## 五步详解

### Step 1：读草图转 JSON（读图转提示词）

**输入**：用户提供的草图（手机拍照、扫描、PPT截图、手画）+ 文字描述

**操作**：把草图发给多模态大模型，用 `vision-to-prompt.md` 里的结构化提示词，让模型输出 `layout.json`：

```json
{
  "title": "Two-stage pipeline / 两阶段流程",
  "boxes": [
    {"name": "input", "label": "Input Data\n输入数据", "role": "input", "grid_hint": "top-left", "size_hint": "medium"},
    ...
  ],
  "arrows": [
    {"from": "input", "to": "preprocess", "label": "raw", "style": "solid", "curve": 0},
    ...
  ],
  "notes": ["横向流程"]
}
```

**无草图退化**：只有文字描述时，用文本模型从描述提取结构化 JSON，`grid_hint` 靠语义推断。

详见 [rules/vision-to-prompt.md](vision-to-prompt.md)。

### Step 2：JSON 转网格代码

把 `layout.json` 里的 `grid_hint` 映射到网格行列，生成 `svg_template.py` 的调用代码。

**映射表**（4×4 网格）：

| grid_hint | row | col | size_hint=small | medium | large |
|---|---|---|---|---|---|
| top-left | 0 | 0 | 1×1 | 1×2 | 2×2 |
| top-center | 0 | 1 | colspan=1 | colspan=2 | colspan=2,rowspan=2 |
| top-right | 0 | 3 | 1×1 | 1×2(colspan→往左) | 2×2 |
| mid-left | 1 | 0 | 1×1 | rowspan=2 | rowspan=2,colspan=2 |
| center | 1 | 1 | colspan=1,rowspan=1 | colspan=2,rowspan=2 | colspan=2,rowspan=2 |
| mid-right | 1 | 3 | 1×1 | rowspan=2 | rowspan=2,colspan=2(→往左) |
| bottom-left | 3 | 0 | 1×1 | 1×2 | 2×2 |
| bottom-center | 3 | 1 | colspan=1 | colspan=2 | colspan=2,rowspan=2 |
| bottom-right | 3 | 3 | 1×1 | 1×2(→往左) | 2×2(→往左) |

**箭头方向自动推断**：从 from 中心到 to 中心，选最近边：
- from.col < to.col 且同行 → from.right → to.left
- from.col == to.col 且 from.row < to.row → from.bottom → to.top
- 对角 → from.bottom → to.top（最通用）

**颜色映射**（按 role）：
- input → blue (#e3f2fd)
- process → orange (#fff3e0)
- model → green (#e8f5e9)
- output → red (#ffebee)
- decision → purple (#f3e5f5)
- data → cyan (#e0f7fa)
- feedback → grey (#f5f5f5)
- other → white (#ffffff)

**形状映射**（按 role）：
- model → round（圆角矩形）
- decision → ellipse
- 其他 → rect

### Step 3：生成 SVG

执行 Step 2 生成的代码：

```python
from svg_template import Figure

fig = Figure(cols=4, rows=4, cell_w=150, cell_h=70, font_size=12)
fig.title("Two-stage pipeline / 两阶段流程")
fig.box("input", 0, 0, colspan=2, text="Input Data\n输入数据", fill="blue")
fig.box("preprocess", 0, 2, colspan=2, text="Preprocessing\n预处理", fill="orange")
fig.box("model", 2, 1, colspan=2, text="Model\n模型", fill="green", shape="round")
fig.box("output", 2, 3, text="Output\n输出", fill="red")
fig.arrow("input", "right", "preprocess", "left", label="raw")
fig.arrow("preprocess", "bottom", "model", "top", label="features")
fig.arrow("model", "right", "output", "left", label="predict")
fig.save("figure.svg")
```

### Step 4：校验

```bash
python scripts/validate_svg.py figure.svg
```

校验脚本检查 8 项（详见 `layout-spec.md`）。目标：**0 failures**。warnings 尽量消除。

### Step 5：精修微调循环

校验报问题时，按 `vision-to-prompt.md` 的修复表调整，重新 save + validate，直到 0 failures。

典型循环 2-3 轮即可收敛：
1. 第一轮：文字溢出 → 增大框 colspan 或缩短文字
2. 第二轮：箭头标签与框重叠 → 增大箭头 curve 偏移
3. 第三轮：0 failures，完成

## 命令行操作

```bash
# 从草图生成（草图路径 + 输出路径）
# 技能会：读图→转JSON→生成代码→生成SVG→校验→精修循环
python scripts/generate_from_sketch.py sketch.jpg -o figure.svg

# 从 JSON 生成（已有 layout.json）
python scripts/generate_from_json.py layout.json -o figure.svg

# 从文字描述生成（无草图，纯文本描述）
python scripts/generate_from_text.py "输入→预处理→模型→输出" -o figure.svg

# 校验已有 SVG
python scripts/validate_svg.py figure.svg

# 用模板直接手写（高级用户）
python -c "
from svg_template import Figure
fig = Figure(cols=4, rows=4)
...
fig.save('figure.svg')
"
```

## GUI 操作（可选）

```bash
python scripts/figure_gui.py
```

- 左侧：草图预览 + layout.json 编辑器
- 右侧：SVG 实时预览 + 校验报告
- 按钮：读图（选草图文件）→ 生成 → 校验 → 精修 → 导出

## 输出文件

每次生成会产出：

| 文件 | 说明 |
|---|---|
| `figure.svg` | 最终 SVG（通过校验，0 failures） |
| `figure.json` | layout.json（草图结构化描述，可复现） |
| `figure.py` | 生成脚本（可单独运行复现 SVG） |
| `figure_report.txt` | 校验报告 |

## 质量门禁 / Quality Gate

一张图"完成"的判定标准：

- [ ] `validate_svg.py` 报 **0 failures**
- [ ] warnings ≤ 2（标题文字在框外、弧线标签偏移可接受）
- [ ] 所有文字 ≥ 9pt
- [ ] 所有箭头连接到框（无悬空）
- [ ] viewBox 完整包含所有元素（无越界）
- [ ] 颜色用 Wong 色盲安全调色板
- [ ] 中英双语标签（除非用户明确说只要一种语言）