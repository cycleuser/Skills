# 科研画图 (Research Figure / Sketch-to-SVG)

## 状态：Beta

## 用途

把老师的草图（或文字描述）变成**无任何覆盖**的科研级 SVG 流程图。核心痛点：直接让大模型"画个流程图"总有框重叠、文字溢出、箭头错位；靠"再改改"调不好。解决方案：先让大模型读草图提取精确布局，再用网格模板生成 SVG（结构上不可能重叠），最后自动校验到 0 错误。

核心一句话：读草图→转精确布局→网格生成→自动校验→0覆盖交付。

## 快速命令

| 命令 | 说明 |
|------|------|
| `/画图 <草图>` | 读草图→转JSON→生成SVG→校验→精修（完整工作链） |
| `/画图 from-json <layout.json>` | 从 layout.json 生成 SVG |
| `/画图 from-text "<描述>"` | 从文字描述生成（无草图） |
| `/画图 validate <file.svg>` | 校验已有 SVG 的覆盖/越界 |
| `/画图 template` | 显示网格模板用法 |
| `/fig <sketch>` | English alias |
| `/fig from-json/from-text/validate` | English command variants |

## 适用场景

- 老师给了草图让帮忙画科研流程图/架构图/系统框图
- 有手画草图照片/扫描，需要变成干净的 SVG
- 只有文字描述，需要生成结构化流程图
- 需要保证框不重叠、文字不溢出、箭头不悬空的严格场景
- 需要中英双语标签、色盲安全配色的出版图

## 为什么需要它

真实经历：老师发来手画草图让画个图，折腾一个多小时。核心问题不是"画不出"而是**精修**——大模型直接生成的图总有覆盖溢出，靠模糊指令调不好。最后用大模型**读草图**转成精确布局描述，再用网格系统生成，一次通过。本技能把这个工作链固化下来。

## 五步工作流

1. **读草图** Read：把草图发给多模态大模型，用结构化提示词输出 `layout.json`（框列表+箭头列表+标签）
2. **转网格** Map：把 `grid_hint` 映射到网格行列，生成 `svg_template.py` 代码
3. **生成** Generate：执行代码生成 SVG
4. **校验** Validate：`validate_svg.py` 检查8项，目标 0 failures
5. **精修** Refine：有 fail 时按修复表调整，重新生成+校验，典型2-3轮收敛

## 核心实现要点

- **网格系统**：画布分成 `cols×rows` 格，框放在格子里，不同框占不同格→天然不重叠
- **命名锚点**：每个框有8个罗盘锚点，箭头用 `fig.arrow("a","right","b","left")` 连接，绝不悬空
- **自动折行缩字**：文字超框宽自动折行，超框高自动缩字号（下限9pt）
- **data-intent 豁免**：文字在框内是有意覆盖，用 `data-intent="label-of-box-X"` 声明，校验据此豁免
- **色盲安全**：Wong 调色板 + 柔和粉彩填充
- **纯标准库**：模板和校验脚本零外部依赖（只用 `xml.dom.minidom`、`math`、`re`）

## 依赖

- **必需**：Python 标准库（零外部依赖）
- **读草图**：多模态大模型（由调用方提供，本技能提供提示词）
- 依赖 `_shared/core/safety-rules.md`

## 验证

```bash
python tests/test_skill.py       # 16项自验证
pytest tests/test_skill.py -v
```

覆盖：模板生成、校验通过良构图、校验捕获重叠/溢出、JSON生成、多行/CJK文字、箭头连接、viewBox完整、反馈环、6框6箭头端到端复杂图。

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

## 参见

- `/论文` from **academic-writer** — 学术论文写作时需要配图，本技能生成图，academic-writer 写文
- `/paper figures` from **academic-writer** — 通用图表质量标准（本技能专注流程图/架构图的结构化生成）