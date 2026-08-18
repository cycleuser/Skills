# SVG 布局规范 / SVG Layout Specification

本技能生成的每一张 SVG 流程图都必须满足下列规范。核心目标：**绝对无图文互相覆盖、无越界、无孤立元素**。靠人眼调"差不多"是做不到的——必须用网格系统 + 自动校验脚本双重保证。

## 铁律 / Iron Rules

1. **网格定位，不靠眼睛**。每个框、每个标签都放在网格单元里，坐标由模板计算，绝不手填像素值。
2. **文字必须在框内**。文字超出框 = 失败。模板自动折行、自动缩字号（下限 9pt）保证装得下。
3. **箭头必须连框**。箭头起止点是框的命名锚点（top/bottom/left/right/n/s/e/w/center），绝不悬空。
4. **框之间不重叠**。网格单元天然不相交，两个框占不同的格就不会重叠。
5. **一切在 viewBox 内**。viewBox 大小由网格行列数 × 单元尺寸 + padding 自动算出，不手设。
6. **data-intent 标记有意覆盖**。文字在框内是有意覆盖（标签就该在框里），用 `data-intent="label-of-box-X"` 声明，校验脚本据此豁免。
7. **生成后必须校验**。每次生成 SVG 后运行 `validate_svg.py`，0 failures 才算完成。

## 网格系统 / Grid System

模板 `svg_template.py` 的 `Figure` 类把画布分成 `cols × rows` 个格，每格 `cell_w × cell_h` 像素。

```
   col0   col1   col2   col3
  ┌─────┬─────┬─────┬─────┐
r0│     │     │     │     │  cell_h
  ├─────┼─────┼─────┼─────┤
r1│     │     │     │     │
  ├─────┼─────┼─────┼─────┤
r2│     │     │     │     │
  └─────┴─────┴─────┴─────┘
        cell_w
```

- `fig.box("name", row, col, rowspan=1, colspan=1, text="...")` 放框
- `fig.arrow("from", "right", "to", "left", label="...")` 连箭头
- 框可跨格：`rowspan=2, colspan=2` 占 2×2 格
- 不同框占不同格 → 天然不重叠

## 锚点 / Anchor Points

每个框有 8 个命名锚点（罗盘方向）+ center：

```
        nw    n    ne
         \   |   /
          \  |  /
     w ──── center ──── e
          /  |  \
         /   |   \
        sw    s    se
```

箭头用锚点连接：
```python
fig.arrow("input", "right", "model", "left", label="features")
fig.arrow("model", "bottom", "output", "top", label="predict", curve=30)
```

- `curve=30` 让箭头走弧线（正值向左偏，负值向右偏），用于绕开中间元素
- `dashed=True` 虚线，用于"可选路径"或"反馈"

## 文字处理 / Text Handling

模板自动处理多行文字和字号：

1. **折行**：文字超过框宽时按字符数折行（CJK 按全宽算，拉丁按 0.6×字号算）
2. **缩字**：折行后行数超过框高能容纳的行数时，自动缩小字号（下限 9pt）
3. **居中**：`text-anchor="middle"` + `dominant-baseline="middle"`，每行 tspan 的 x/y 由模板算
4. **最小字号 9pt**：低于 9pt 看不清，宁可换大框也不缩小

## 配色 / Colours

- **线框色**：Wong 色盲安全调色板（#0072B2, #E69F00, #009E73, #CC79A7, #F0E442, #D55E00, #56B4E9）
- **填充色**：柔和粉彩（blue=#e3f2fd, orange=#fff3e0, green=#e8f5e9, red=#ffebee, purple=#f3e5f5, ...）
- **文字色**：深灰 #1a1a1a（不是纯黑，印刷更柔和）
- **箭头色**：#333333
- **标签色**：#555（比箭头浅，不抢视觉焦点）
- **背景**：白 #ffffff

## 常见布局模式 / Common Layout Patterns

### 线性流程

```
[A] → [B] → [C] → [D]
```
横向排列，每框占一列，箭头 left→right。

### 分支 / Branch

```
        [B]
       ↗
[A] ──
       ↘
        [C]
```
A 在左，B 在右上，C 在右下，箭头 A.right→B.left，A.bottom→C.top。

### 反馈环 / Feedback Loop

```
[A] → [B]
 ↑      │
 └──────┘  (dashed)
```
正向箭头实线，反馈箭头虚线走下方弧线 `curve`。

### 层级架构

```
     [顶层]
    ╱  │  ╲
[子1] [子2] [子3]
    ╲  │  ╱
     [底层]
```
顶层居中跨列，子层横排，底层居中跨列。箭头 top→bottom 为主，bottom→top 为反馈。

## data-intent 标记 / Intent Declaration

生成的 SVG 给每个元素加 `data-intent` 属性，告诉校验脚本"这个覆盖是有意的"：

- `data-intent="box-X"` — 框 X 本身
- `data-intent="label-of-box-X"` — 框 X 的文字标签（在框内是有意的）
- `data-intent="arrow-X-Y"` — 从 X 到 Y 的箭头
- `data-intent="head-X-Y"` — 箭头头部（接触 Y 的边是有意的）
- `data-intent="arrow-label-X-Y"` — 箭头标签

校验脚本遇到带 `data-intent` 的元素时，豁免它的"被覆盖"检查（但仍检查它是否越界、是否太小）。

## 校验检查项 / Validation Checklist

`validate_svg.py` 检查：

| 检查 | 严重度 | 说明 |
|---|---|---|
| 元素越出 viewBox | WARN | 被 viewBox 裁掉，看不到 |
| 文字在框外 | WARN | 文字没在任何框里，可能孤立 |
| 文字溢出框 | FAIL | 文字比框大，被切掉 |
| 框与框重叠 | FAIL | 两个框占了同一区域 |
| 文字与文字重叠 | WARN | 两个标签叠在一起 |
| 字号 < 9pt | WARN | 印刷看不清 |
| 箭头端点不近任何框 | WARN | 箭头悬空或指错 |
| id 重复 | WARN | DOM 选择器会冲突 |

**0 failures** 是硬性要求。warnings 应尽量消除，但标题文字（在框外是正常的）和弧线箭头标签可能产生可接受的 warning。