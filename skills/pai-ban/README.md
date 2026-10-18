# 排版 (pai-ban / Typeset)

## 状态：Beta

## EN Summary

Publication-grade typesetting for Markdown books and long documents: journal-level typographic discipline on a book canvas (A5 baseline grid, single accent colour, chapter openers, running heads, code highlighting, three-line tables), compiled to PDF/DOCX via pandoc + XeLaTeX and verified against 11 hard quality gates (zero overflow, zero missing glyphs, zero LaTeX errors, zero Overfull ≥1pt). `/typeset <dir>` is the English alias.

## 用途

把「一堆 Markdown」变成「出版社级的书」。面对一个章节目录（中/英文分开的 md 文件夹），产出一本版式纪律严明的书：章必起于奇数页、字号严格落在 1.25 模数的阶梯上、全书只允许一种强调色（藏青）、表格只用三线、代码块带标签与行号、图与题注不分离。**每一步产出都要过 11 项硬门禁，不通过就报错退出**——版式不是「差不多」，是「逐条站得住」。

核心一句话：声明式配置 + 固定流水线 + 硬门禁验收，让同一个项目两次构建结果完全一致。

## 快速命令

| 命令 | 说明 |
|------|------|
| `/排版 <目录>` | 从 Markdown 章节目录构建 PDF（默认同时出 DOCX，并自动跑验收） |
| `/排版 init <目录>` | 在书稿目录脚手架 `pai-ban.toml` 配置 + assets 副本 |
| `/排版 check <pdf\|目录>` | 跑硬排版门禁，输出 pass/fail 表 |
| `/排版 preview <目录>` | 编译 2–3 章样张并渲染页面 PNG，供人工/视觉复核 |
| `/排版 spec` | 打印权威设计规格 |
| `/typeset <dir>` | Build a PDF (and DOCX) from a Markdown chapter folder |
| `/typeset check <pdf>` | English alias for the audit |
| `/typeset preview <dir>` | English alias for the sample build |
| `/typeset spec` | English alias for the design spec |

## 适用场景

- 把一个文件夹的 Markdown 章节变成可印刷的 PDF/DOCX（教材、专著、讲义）
- 书稿/文档需要「顶刊级」「出版社级」排版
- 内容改完后重建全书（可复现，改一处版式不用全书重来）
- 中英文两个版本共用一套设计规格
- 审计既有 PDF 的排版缺陷（越界、孤立标题、图内文字过小）

## 为什么需要它

手工调排版的问题不是「做不到」，而是**不可复现**：同一项目两次构建不一样，换个人改就崩。本技能把版式变成声明式配置（`pai-ban.toml`，书名/开本/字体/输出路径）+ 固定流水线（`build.py`：预处理 → pandoc → longtable 续页补丁 → xelatex ×2–3 → 产物 + manifest）+ 硬验收（`verify.py`：11 项门禁，机器可读结果落 `<pdf>.verify.json`）。规格唯一权威在 `rules/design-spec.md`，实现全部在 `assets/preamble.tex`（不依赖 titlesec/tocloft/tcolorbox 等缺失宏包），结构变换在 `assets/filters/*.lua`。

## 设计要点

- **画布**：A5 双面，订口 18mm / 外 15mm / 上 16mm / 下 19mm，版心 115×175mm
- **字号阶梯**：章 22pt → 节 14pt → 小节 11.5pt → 正文 11pt，严格模数，行距上基线网格
- **颜色 ≤ 6 种，强调色只有 1 种**（藏青），线宽只两档（0.4/0.8pt），黑白打印仍可辨
- **PDF 为权威产物，DOCX 为可编辑副本**——DOCX 仅供批注修改，不能作为最终交印格式
- **缺宏包会明确报错**：不静默降级、不 `tlmgr install`；TeX Live basic 里没有的东西（minted/tcolorbox/titlesec 等）一律不用
- **零宽容硬门槛**：内容越出纸边 0 页、缺失字形 0、LaTeX 错误 0、Overfull ≥1pt 为 0、章必起于奇数页、章首页无页眉

## 工作流

1. **init**：`python3 scripts/init.py <书稿>` 写入 `pai-ban.toml` 并复制 `pai-ban-assets/`
2. **build**：`python3 scripts/build.py <书稿> --lang zh`（末尾自动跑验收）
3. **verify**：单独重跑 `python3 scripts/verify.py <pdf> --manifest <pdf>.manifest.json`
4. **preview**：`--chapters 0,2,14 --preview` 出样章 + 150dpi 页图

## 依赖

- **TeX Live**（需含 xeCJK、listings、booktabs、fancyhdr、microtype、hyperref；缺失时 `build.py` 明确报出缺什么）
- **pandoc**（Markdown → LaTeX 转换主力）
- Python 3.11+（`tomllib` 读配置）；`pymupdf`（verify 的墨迹测量）
- 字体（macOS 系统自带）：宋体 Songti SC、黑体 PingFang SC、Menlo、Times New Roman
- 依赖 `_shared/core/safety-rules.md`

## 文件结构

```
skills/pai-ban/
├── README.md
├── SKILL.md
├── rules/
│   ├── design-spec.md      # 唯一权威规格（数值、验收门槛，normative）
│   ├── workflow.md         # 操作流程、过滤器顺序与原因、排错表、安装记录
│   └── verification.md     # 实测口径、人工抽样复核清单、已知局限
├── assets/
│   ├── preamble.tex        # 版式实现（章首页/字号阶梯/代码/表格/页眉）
│   ├── pai-ban.toml        # 默认配置模板
│   └── filters/            # chapter-split / table-widths / code / table / figure caption
└── scripts/
    ├── build.py            # 预处理 → pandoc → xelatex → 产物 + manifest
    ├── verify.py           # 11 项硬门禁（不通过退出码非 0）
    └── init.py             # 项目脚手架
```

## 参见

- `research-figure` — 生成图／流程图 SVG；本技能只负责把图排好，不生成图
- `docx-to-knowledge` — 同一份 Markdown 出网页知识库；本技能出纸质/PDF
- `verify-deliver` — 通用验证协议；本技能的 `verify.py` 是它在排版场景的具体实现
- `tianbiao` — 需要保原模板格式的表格填写时
