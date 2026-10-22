---
name: pai-ban
version: "1.1.1"
description: |
  Publication-grade typesetting for Markdown books and long documents — journal-level typographic discipline on a book canvas (baseline grid, restrained palette, chapter openers, running heads, code highlighting, three-line tables), compiled to PDF/DOCX and verified against hard quality gates.

  Triggers when: Turning a folder of Markdown chapters into a print-ready PDF/DOCX; a book/document needs "top-journal" or "publisher" typography; rebuilding a textbook after content edits; unifying Chinese and English editions under one design; auditing an existing PDF for layout defects (overflow, orphan headings, unreadable figure text); or producing a reusable, versioned style so future books share one look.

  Commands:
  - /排版 <目录>             Build a PDF (and DOCX) from a Markdown chapter folder
  - /排版 init <目录>        Scaffold a pai-ban.toml config + assets into a project
  - /排版 check <pdf|目录>   Run the hard typography gates and report a pass/fail table
  - /排版 preview <目录>     Compile a 2–3 chapter sample and render page PNGs for review
  - /排版 spec               Print the authoritative design spec
  - /typeset <dir>           English alias for the build command
  - /typeset check <pdf>     English alias for the audit
---

# 排版 (pai-ban)

把「一堆 Markdown」变成「出版社级的书」。本技能固化一套**经过验收的版式规格**（见 `rules/design-spec.md`），并提供可直接复用的构建器、LaTeX 导言区、Lua 过滤器与验收脚本。

## 为什么需要它

手工调排版的问题不是"做不到"，而是**不可复现**：同一个项目两次构建出来不一样，换个人改就崩，改一处版式要全书重来。本技能把版式变成**声明式配置 + 固定流水线**：

- 版式参数全部集中在 `pai-ban.toml`（书名、开本、字体、输出路径）；颜色与字号阶梯写死在 `assets/preamble.tex`（规格是 normative，不开放配置）；
- 版式实现全部集中在 `assets/preamble.tex`（不依赖 titlesec/tocloft/tcolorbox 等缺失宏包）；
- 结构变换集中在 `assets/filters/*.lua`（章标题拆分、表格列宽、代码标题、表题注、图题注）；
- 验收集中在 `scripts/verify.py`（§11 八项 + §1 左边界 + §7/§8 Overfull，共十一项，不通过就报错退出）。

## 快速开始

```bash
# 1. 在书稿目录初始化配置（会写入 pai-ban.toml 与 pai-ban-assets/ 副本）
python3 scripts/init.py /path/to/book

# 2. 编译（默认输出 <book>/build/pai-ban/<lang>/<title>.pdf，并自动跑验收）
python3 scripts/build.py /path/to/book --lang zh

# 3. 验收（硬门槛；不通过退出码非 0）
python3 scripts/verify.py /path/to/book/build/pai-ban/zh/<title>.pdf

# 4. 只出样章 + 页面 PNG，供人工/视觉复核
python3 scripts/build.py /path/to/book --lang zh --chapters 0,2,14 --preview
```

## 目录结构（技能内）

```
pai-ban/
├── SKILL.md
├── rules/
│   ├── design-spec.md      # 唯一权威规格（数值、验收门槛）
│   ├── workflow.md         # 从书稿到成品的操作流程与排错
│   └── verification.md     # 验收清单与典型失败案例
├── assets/
│   ├── preamble.tex        # 版式实现（章首页/字号阶梯/代码/表格/页眉）
│   ├── filters/
│   │   ├── chapter-split.lua   # 「第N章」/「Chapter N」→ 编号+标题；H2–H4 → 节
│   │   ├── table-widths.lua    # 相对列宽 + 长 token 断点，消灭表格越界
│   │   ├── code-caption.lua    # title/linenums → 代码标签与行号
│   │   ├── table-caption.lua   # 「表N.M：…」搬表上方，9pt 加粗标签
│   │   └── figure-caption.lua  # 图 + 题注 → 不浮动 minipage（同页）
│   ├── pai-ban.toml        # 默认配置模板（TOML，Python 3.11+ tomllib）
├── scripts/
│   ├── build.py            # 预处理 → pandoc → xelatex → 产物
│   ├── verify.py           # 硬门槛检查（pymupdf）
│   └── init.py             # 项目脚手架
└── README.md
```

## 硬约束（不满足即失败）

- 零内容越出纸边；缺失字形 0；LaTeX 错误 0。
- 章必须起于奇数页；章首页无页眉。
- 代码块与表格禁止横向溢出；表格只用三线。
- 颜色 ≤ 6 种；强调色只有一种。
- 正文/标题字号必须落在 §2.2 的阶梯上。

## 与其它技能的关系

- `docx-to-knowledge`：本技能管**纸质/PDF 排版**，它管**网页知识库**；同一份 Markdown 可以两头出。
- `academic-writer`：管论文内容与引用格式；本技能管版面。投稿模板请用目标期刊自己的类文件，不要硬套本技能。
- `verify-deliver`：本技能的 `verify.py` 是它在排版场景的具体实现，两者门槛口径一致。

## 已知边界

- 依赖 TeX Live（xeCJK + listings + booktabs + fancyhdr + microtype + hyperref）。缺宏包时 `build.py` 会明确报出缺哪个，不会静默降级。
- 不做图片生成（用 `research-figure` / 绘图脚本），只负责把图排好。
- 不支持 InDesign/Word 手工微调回写；DOCX 是"可编辑副本"，PDF 才是权威产物。
