---
name: research-figure
version: "1.0.0"
description: |
  Scientific figure generator that turns a hand-drawn sketch (or text description) into a publication-quality SVG with guaranteed zero overlaps. Pipeline: read the sketch with a vision LLM → extract structured layout JSON → map to a grid-based SVG template → auto-validate for overlaps/overflow/clipping → iteratively refine until 0 failures.

  Triggers when: A teacher/colleague asks you to draw a scientific flowchart/diagram, you have a rough sketch (photo/scan/screenshot) and need a clean SVG, natural-language instructions are too vague for direct generation so the vision model must read the sketch first, you need SVG flowcharts with absolutely no text-box overlap or element clipping, or you want to convert a PowerPoint/whiteboard draft into a publication-quality figure.

  Commands:
  - /画图 <草图路径> [输出路径] - Full pipeline: read sketch → JSON → SVG → validate → refine
  - /画图 from-json <layout.json> [输出路径] - Build SVG from a layout.json
  - /画图 from-text "<描述>" [输出路径] - Build SVG from a text description (no sketch)
  - /画图 validate <file.svg> - Validate an existing SVG for overlaps/overflow
  - /画图 template - Show the grid-based SVG template usage
  - /fig <sketch> [out] - English command alias for the full pipeline
  - /fig from-json <layout.json> [out] - Build SVG from layout.json
  - /fig from-text "<description>" [out] - Build from text description
  - /fig validate <file.svg> - Validate an SVG

  Capabilities: Vision-LLM sketch reading with structured JSON output, grid-based SVG placement (boxes on grid cells — overlap-free by construction), named anchor-point arrows (top/bottom/left/right/compass), auto text wrapping and font-shrinking (min 9pt), Wong colorblind-safe palette, multi-line CJK+latin labels, automated overlap/overflow/clipping validation, iterative refine loop until 0 failures, feedback-loop arrows (dashed), curved arrows for routing around elements, layout.json reproducibility
author: cycleuser
license: MIT
status: Beta
---

## Safety Rules

参见 [_shared/core/safety-rules.md](../_shared/core/safety-rules.md) — 所有安全规则从共享层加载。

关键补充：**生成的 SVG 必须 0 failures 才算完成**。校验脚本报 FAIL 时绝不能交付，必须进入精修循环。warnings（标题在框外、弧线标签偏移）可接受但应尽量消除。

# 科研画图 (Research Figure / Sketch-to-SVG)

把老师的草图变成无任何覆盖的科研级 SVG 流程图。核心痛点：人给大模型的指令"画个流程图"太模糊，直接生成的图框重叠、文字溢出、箭头指错。解决方案：**先让大模型读草图提取精确布局，再用网格模板生成 SVG，最后自动校验到 0 错误**。

The key insight: natural-language instructions are too coarse for precise figure layout. The fix: have a vision LLM read the sketch first and extract a structured layout, then generate SVG on a grid system where overlaps are impossible by construction, then auto-validate.

## Quick Commands

| Command | 说明 / Description |
|---------|-------------|
| `/画图 <草图>` | 读草图→转JSON→生成SVG→校验→精修（完整工作链） |
| `/画图 from-json <layout.json>` | 从 layout.json 生成 SVG |
| `/画图 from-text "<描述>"` | 从文字描述生成（无草图） |
| `/画图 validate <file.svg>` | 校验已有 SVG 的覆盖/越界 |
| `/画图 template` | 显示网格模板用法 |
| `/fig <sketch>` | English alias for the full pipeline |
| `/fig from-json <layout.json>` | Build SVG from layout.json |
| `/fig from-text "<description>"` | Build from text description |
| `/fig validate <file.svg>` | Validate an SVG |

## 核心理念 / Core Philosophy

从一次真实经历提炼：老师发来手画草图让帮忙画个流程图，折腾一个多小时。最核心问题不是"画不出"，而是**精修和微调**——大模型直接生成的图总有覆盖、溢出、箭头错位，靠"再改改"这种模糊指令调不好。最后用大模型**读草图**，把模糊的视觉信息转成精确的结构化布局描述（layout.json），再用网格系统生成，一次通过。

四条铁律：

1. **网格定位，不靠眼睛**。每个框放在网格单元里，坐标由模板计算，两个框占不同的格就不会重叠——结构上不可能。
2. **读图转提示词**。草图→多模态模型→layout.json→网格代码。把"画个大概"变成"框A在(0,0)占1×2格，框B在(0,2)占1×2格，箭头A.right→B.left"。
3. **文字必须在框内**。模板自动折行、自动缩字号（下限9pt），保证文字不溢出框。
4. **生成后必须校验**。`validate_svg.py` 检查8项，0 failures 才算完成。

## 五步工作流 / Five-Step Workflow

```
Step 1  读草图 Read Sketch
   把草图发给多模态大模型（GPT-4o/Claude/Gemini），用结构化提示词
   让它输出 layout.json（框列表+箭头列表+标签）。
   详见 rules/vision-to-prompt.md

Step 2  转网格代码 Map to Grid
   把 layout.json 的 grid_hint 映射到网格行列，生成 svg_template.py 代码。
   映射表见 rules/workflow.md。

Step 3  生成 SVG Generate
   执行代码生成 SVG。

Step 4  校验 Validate
   python scripts/validate_svg.py figure.svg
   检查：越界/文字溢出/框重叠/文字重叠/字号/箭头连接/id重复。
   目标：0 failures。

Step 5  精修循环 Refine Loop
   有 fail/warn 时按修复表调整（增大框/缩短文字/调curve），重新生成+校验。
   典型2-3轮收敛。
```

## 关键实现要点 / Key Implementation Notes

- **网格系统**：`svg_template.py` 的 `Figure` 类把画布分成 `cols×rows` 格，`fig.box(name, row, col, rowspan, colspan)` 放框。不同框占不同格 → 天然不重叠。
- **命名锚点**：每个框有8个罗盘锚点+n/s/e/w/center。`fig.arrow("a", "right", "b", "left")` 连箭头，绝不悬空。
- **data-intent 豁免**：文字在框内、箭头头接触框边是"有意的覆盖"，用 `data-intent="label-of-box-X"` 声明，校验脚本据此豁免。
- **自动折行缩字**：文字超框宽时按字符数折行（CJK全宽，拉丁0.6×字号）；折行后超框高时自动缩字号（下限9pt）。
- **色盲安全**：Wong调色板（#0072B2, #E69F00, #009E73, ...）+ 柔和粉彩填充。
- **校验8项**：越界(WARN)、文字在框外(WARN)、文字溢出(FAIL)、框重叠(FAIL)、文字重叠(WARN)、字号<9pt(WARN)、箭头悬空(WARN)、id重复(WARN)。

详见 [scripts/svg_template.py](scripts/svg_template.py)（网格模板，~280行）和 [scripts/validate_svg.py](scripts/validate_svg.py)（校验器，~290行，纯标准库无依赖）。

## Rules

- [rules/workflow.md](rules/workflow.md) - 完整五步工作流、命令行操作、质量门禁
- [rules/vision-to-prompt.md](rules/vision-to-prompt.md) - 读草图转结构化JSON的提示词、grid_hint映射表、精修修复表
- [rules/layout-spec.md](rules/layout-spec.md) - SVG布局规范、网格系统、锚点、配色、data-intent标记、校验检查项

## 适用场景 / Supported Scenarios

- 老师给了草图让帮忙画科研流程图/架构图/系统框图
- 有手画草图照片/扫描，需要变成干净的SVG
- 只有文字描述，需要生成结构化流程图
- 已有PPT草稿，需要转成出版级SVG
- 需要保证框不重叠、文字不溢出、箭头不悬空的严格场景
- 需要中英双语标签的科研图
- 需要色盲安全配色的出版图

## 验证 / Verification

```bash
python tests/test_skill.py       # 16项自验证
pytest tests/test_skill.py -v
```

覆盖：模板生成有效SVG、校验通过良构图、校验捕获框重叠、校验捕获文字溢出、JSON生成、多行文字、CJK文字、箭头连接、viewBox完整、反馈环、6框6箭头端到端复杂图。

## 依赖 / Dependencies

- **必需**：Python 标准库（`xml.dom.minidom`, `math`, `re`）——校验脚本和模板脚本都纯标准库，零外部依赖
- **读草图**：多模态大模型（GPT-4o / Claude / Gemini）——由调用方提供，本技能只提供提示词
- **可选**：`PySide6`（GUI，未来计划）
- 依赖 `_shared/core/safety-rules.md`

## 文件结构

```
skills/research-figure/
├── README.md
├── SKILL.md
├── rules/
│   ├── workflow.md              # 五步工作流与命令行操作
│   ├── vision-to-prompt.md      # 读图转提示词、grid_hint映射、精修修复表
│   └── layout-spec.md           # SVG布局规范、网格系统、校验检查项
├── scripts/
│   ├── svg_template.py          # 网格SVG模板（~280行，纯标准库）
│   ├── validate_svg.py          # SVG校验器（~290行，纯标准库）
│   └── generate_from_json.py     # 从layout.json生成SVG
└── tests/
    └── test_skill.py            # 16项自验证测试
```

## 版本历史 / Version History

| 版本 | 日期 | 变更 |
|------|------|------|
| 1.0.0 | 2026-08-16 | 初始版本：读草图工作链、网格SVG模板、自动校验器、16项自验证 |

## See Also / 相关技能

- `/论文` from **academic-writer** — 学术论文写作时需要配图，本技能生成图，academic-writer 写文
- `/paper figures` from **academic-writer** — 通用图表质量标准（本技能专注流程图/架构图的结构化生成）