# 构建流程（workflow）

本文件记录 `pai-ban` 的**实际操作顺序**和实现层面的坑，规格本身看
`rules/design-spec.md`。命令一行能跑通的东西不写，写的是"为什么这么排、
排错了会怎样"。

---

## 1. 三条命令

```bash
# 1) 给一本书装脚手架（写 pai-ban.toml + 拷贝 assets + 探测章节/图目录）
python3 scripts/init.py <书稿目录> [--force]

# 2) 构建（整本 / 指定章 / 样章）
python3 scripts/build.py <书稿目录>                         # 整本
python3 scripts/build.py <书稿目录> --chapters 0,2,14,20    # 指定章
python3 scripts/build.py <书稿目录> --preview               # 样章 + 页面 PNG

# 3) 单独验收（build.py 末尾会自动调；也可事后重跑）
python3 scripts/verify.py <pdf> --manifest <pdf>.manifest.json
```

`init.py` 会把 `assets/` 复制到 `<书稿>/pai-ban-assets/`，`build.py` **优先用
书稿里的副本**。所以：

> 改了技能自带的 `assets/preamble.tex` 或 `assets/filters/*.lua` 之后，
> 必须重跑 `init.py --force`，否则构建用的还是旧副本。

这是最容易浪费半小时的坑——改了滤镜没生效，先查副本时间戳。

## 2. 流水线（spec §12，顺序不可乱）

```
CN/chapter-*.md
   │ preprocess()                    ← build.py
   │   代码围栏归一化：```python title="…" linenums="1"
   │                  → ```python {title="…" linenums="1"}
   │   图片改指矢量 PDF（svg → figures/pdf/*.pdf）
   │   缺字形替换（⚠ → 可用字形）、裸 URL → <…>
   ▼
build/pai-ban/zh/00-chapter-02-*.md
   │ pandoc -s -H preamble.tex --listings
   │   + 5 个 Lua 过滤器（顺序有意义）
   ▼
book.tex ── patch_longtable_continuation() ── xelatex ×2
   │
   ├─ verify.py（§11 八项 + §1 左边界 + §7/§8 Overfull，共十一项门禁）
   ├─ <pdf>.manifest.json（给 verify.py / 报告用）
   └─ <book>/typeset-sample/{zh-sample.pdf,pages/page-NNN.png}  （--preview）
```

### 2.1 过滤器顺序

| # | 文件 | 作用 | 为什么在这个位置 |
|---|---|---|---|
| 1 | `chapter-split.lua` | H1 → `\paibanchapter{n}{title}`；H2–H4 → `\paibansection`…；第一个编号章前发 `\paibanmainmatter` | 最先跑，后面所有块级过滤器看到的是"没有 H1"的文档 |
| 2 | `table-widths.lua` | 表格列宽 + 长 token 插 `\allowbreak` | 必须在 table-caption 之前改完 colspec，否则题注块插入会打断"表格块"的相邻判断（实际上 table-caption 只看 Table 节点，顺序不敏感，但先算宽度省得列宽被题注段落影响） |
| 3 | `code-caption.lua` | `title=` → 文件标签、`linenums=` → `numbers=left`，并**删掉这两个属性** | pandoc 会把 CodeBlock 的全部属性原样写成 lstlisting 的 key=val；留着 `linenums` 直接 `Package keyval Error` |
| 4 | `table-caption.lua` | 「表14.1：…」斜体段搬到表格上方 → `\paibantablecaption` | 必须在 figure-caption 之前（两者都按"段落 + 块"配对，先处理表的免得误配） |
| 5 | `figure-caption.lua` | 「图 + 斜体题注」→ 不浮动 minipage `\paibanfigure` | 最后跑；它把 Image 换成 RawBlock，`graphicx` 必须已在 preamble 显式加载 |

所有过滤器在 `FORMAT ~= latex` 时原样返回（DOCX 走同一份 md，标题不能丢）。

### 2.2 `--listings` 的两个后果

1. 代码块 → `\begin{lstlisting}[language=…]`，语法高亮由 listings 自己按
   `keywordstyle/stringstyle/commentstyle` 出四色（§7 只允许四类）。
2. **行内代码 → `\passthrough{\lstinline!…!}`**。全局 `breaklines=true` 时，
   `\lstinline` 边界处换行会执行 `\lst@@discretionary`，若 `postbreak` 里带
   `\mbox` 就报 `Improper discretionary list` 并中止编译。
   解法：`\renewcommand{\passthrough}[1]{{\lstset{breaklines=true,postbreak={}}#1}}`
   —— 行内代码要能断行（否则 `search_product(query, category)` 在 115mm
   栏宽里必然 Overfull），但不需要 `↪` 前缀。

### 2.3 章/节标题：两个必须用 `{#1}` 的地方

```latex
\@startsection{section}{1}{\z@}{14pt}{6pt}{\paiban@sectionstyle}{#1}
```

- **标题必须带花括号**。`\@startsection` 的第 7 个参数由 `\@dblarg` 读，
  它只吃"下一个 token"；写 `#1` 时展开后没有括号，于是标题 `2.1 用Ollama…`
  只被吃掉 `2`，剩下的 `.1 用Ollama…` 掉进正文。症状：目录里出现孤立条目
  「2」、正文标题排成「.1 用Ollama…」。
- **不要自己 `\addcontentsline`**。LaTeX 内核的 `\@sect` 已经按
  `\c@tocdepth` 写好目录条目；再写一次就是两条（一条完整、一条截断）。
  `\phantomsection` 仍要保留，它给内核那条目录条目提供 hyperref 锚点。

（`chapter` 级不用 `\@startsection`，是自己写的 `\paiban@chapnum`，
所以章那条 `\addcontentsline` 是必须的。）

## 3. 版面实现要点

| 规格 | 实现位置 | 备注 |
|---|---|---|
| §1 版心 115×175mm | `geometry`（pandoc `-V geometry`）+ preamble | 内 18 / 外 15 / 上 16 / 下 19 |
| §2 字号阶梯 | preamble 各 `\fontsize` | 正文 11/15.2（linespread 1.12） |
| §3 六色 | `\definecolor`，色值写死 | 不开放配置：规范是 normative |
| §4 章首页 | `\paiban@opener` | 24mm 顶空 / 48pt 章号 accent30 / 24mm 0.8pt 线 / 22pt 标题 / 18mm 空 |
| §5 目录 | 重写 `\l@chapter`/`\l@section` | 不用 tocloft；`tocdepth=1`（book 类里 = 章+节） |
| §6 页眉页码 | `fancyhdr` + `\markboth` | 页码只在页脚居中 |
| §7 代码 | `listings` `style=paiban` | `framesep=4pt`、左侧 2pt accent、`xleftmargin=10pt` |
| §8 表格 | `booktabs` + `longtable` + `table-widths.lua` | 题注由 `table-caption.lua` 搬到表上方 |
| §9 图 | `\paibanfigure` + `\paibaninclude` | minipage 保证图与题注同页；不放大 |
| §10 引文 | `quote` 环境重定义（2pt rule 竖线） | |

### 3.1 页码体制

pandoc 的 book 模板会无条件在正文前插 `\mainmatter`。preamble 把它改成
`\relax`，改由 `chapter-split.lua` 在**第一个编号章**前发
`\paibanmainmatter`。于是：目录/前言 = 罗马数字，正文从阿拉伯 1 起。

单独编译某一章（`--chapters 2`）时，这一章就是"第一个编号章"，页码从 1 起；
样章（`0,2,14,20`）里 Preface 在罗马区，第 2 章起阿拉伯 1。

### 3.2 表列宽（`table-widths.lua`）

- 每列权重 = `sqrt(最长单元格显示宽度)`（CJK 按 2 计）；
- 归一化到 1.0，夹在 `[0.08, 0.55]`（列数少时上限放宽到 `1 − 0.08(n−1)`）；
- 注水法（water-filling）保证合计严格 1.0；
- 单列下限还要兜住"最长不可断 token"的宽度，并给长于 14 单位的
  ASCII 片段的 `/ : . _` 后插 `\allowbreak`——否则
  `OpenAI/Anthropic/xAI` 会压到隔壁列的字上（旧实现实测 42pt Overfull）。

估算常量在文件顶部：`TEXTWIDTH_PT=326`、`PT_PER_UNIT=4.7`（表内 9pt）、
`TABCOLSEP_PT=4`。换纸张/字号要跟着改。

### 3.3 表格续页「（续）」

pandoc 的 longtable 只有一个 `\endhead`，续页直接重复表头。`build.py` 在
pandoc 之后、xelatex 之前做一次文本改写（`patch_longtable_continuation`）：
原来的 `\endhead` 改成 `\endfirsthead`，再复制一份表头作为新的 `\endhead`，
前面加一行右对齐的「（续）」。列数由表头行未转义的 `&` 数推出。

## 4. 常见故障

| 症状 | 原因 | 处理 |
|---|---|---|
| `Package keyval Error: linenums undefined` | CodeBlock 属性没被删 | 查 `code-caption.lua` 是否在过滤器列表里 |
| `Improper discretionary list` | `\lstinline` + `postbreak` 里的 `\mbox` | 见 §2.2 的 `\passthrough` 重定义 |
| 日志 `Missing character (U+FFFD)` | Lua 把字节 0xA0 当空白切了汉字 | 所有 Lua 空白匹配用 `[\t\r\n ]`，禁用 `%s`；字符类禁用全角字符 |
| 目录出现孤立条目「2」「练」 | `\@startsection` 标题没加花括号 | 见 §2.3 |
| 改了滤镜没生效 | 构建用的是书稿里的 `pai-ban-assets/` 副本 | `init.py --force` |
| 表格压字 / Overfull 几十 pt | 列宽按字符数线性分，长 token 放不下 | `table-widths.lua` 的 token 下限 + `\allowbreak` |
| 图与题注分页 | 用了浮动 `figure` | `figure-caption.lua` 的 minipage 方案 |
| 中文标题明显比西文小（约 0.74 倍） | pandoc 模板的 `\defaultfontfeatures{Scale=MatchLowercase}` 被带选项的 `\setCJKfamilyfont` 继承，CJK 按拉丁小写字母高度缩放 | 在 `\setCJKfamilyfont` 里显式写 `Scale=1`（见 `assets/preamble.tex` 的 `heiti` 族）；验收时用 pymupdf 对比同一行 CJK/Latin 的 span 字号，必须相等 |
| 目录页出现页眉 | `\thispagestyle{plain}` 只作用于目录第一页 | `{\pagestyle{plain}\@starttoc{toc}}` 包住整个目录 |

## 5. 不做什么

- 不改 `CN/*.md`、`EN/*.md`（源稿只读）；
- 不覆盖已有的 `CN/LLMAP_简体中文.pdf`、`EN/LLMAP_English.pdf`、
  `LLMAP_Cover_TOC.pdf`；
- 不用 `-shell-escape`、不调 minted/tcolorbox/fvextra/framed/enumitem/
  adjustbox/mdframed/needspace/titlesec/tocloft（TeX Live basic 里没有）；
- 不 `tlmgr install`、不 `pip install`。

## 6. 安装位置

2026-10-18 打包注册与安装完成，三处一致（逐文件 md5 相同，排除 `__pycache__`/`.ruff_cache`）：

| 位置 | 路径 |
|---|---|
| 仓库源 | `/Users/fred/Documents/GitHub/cycleuser/Skills/skills/pai-ban/` |
| opencode | `~/.config/opencode/skills/pai-ban/` |
| pi | `~/.pi/agent/skills/pai-ban/` |

安装方式：`rsync -a --delete --exclude='__pycache__' --exclude='.ruff_cache'` 到目标子目录（只同步本技能目录）。注册表 `skills.json` 追加 `pai-ban` 条目（version 1.0.0，auto_load false，rules 列 design-spec/workflow/verification）；仓库命令 `commands/排版.md` 与 `commands/typeset.md`（英文别名）；`scripts/*.py` 已加可执行位。

## 7. 图内字号：三级放置策略（spec §9.1）

### 为什么要管

书的插图常按 A4/网页宽度画（画布 600–840pt、内部字号 6–9pt），直接塞进 A5 版心（115mm ≈ 326pt）会被压到 2.7–4pt —— 打印出来是不可读的灰色小字。这不是排版 bug，是**资产与开本不匹配**。

### 三条命令管什么

`scripts/figure_fit.py` 在 pandoc 之前逐图量算，`build.py` 据此生成 `figure-fit.tex` / `figure-fit.json`：

1. **裁边**：pymupdf 取墨迹 bbox，生成 `trim=<l> <b> <r> <t>, clip`，把画布四周空白去掉（通常能多出 10%–35%）。
2. **加宽**：算出来仍 < 4.5pt 的，居中放到 125mm（两侧各侵入白边 5mm，距纸边仍 ≥10mm）。
3. **旋转**：仍 < 4.5pt 的，整页横向（`sidewaysfigure`），可用宽 = 版心高 175mm。

判定结果写进 manifest，`verify.py` 的门禁 11 按**实际放置方式**核算字号：inline/wide ≥4.5pt、rotated ≥5.5pt。

### 操作要点

- 先 `--chapters 0,2,14,20 --preview`，看 manifest 的 `counts.by_placement` 与 `distribution`，再决定是否全量。
- 旋转页会多占页（每图一页），整书页数上升 5%–8% 属正常；若读者更在意翻页，可把 `figure_fit.py` 的 `inline_min_pt` 调到 3.6（代价是图字更小）。
- `must_redraw` 列表里的图，**排版层救不了**：画布要按目标宽度重做、图内字号 ≥9pt。这份清单必须原样交给内容作者。
- 旋转页不排页眉；题注随图旋转；页码仍在页脚。

### 实测（《大语言模型简明教程》第二版，29 张图）

| 放置 | 张数 | 图内最小字号 |
|---|---|---|
| inline | 3 | 3.76–4.1pt |
| wide | 4 | 4.5–5.0pt |
| rotated | 22 | 4.6–6.2pt（中位 5.27） |
| 需重画 | 2 | 整页横向仍只有 3.76/4.44pt |

改动前中位 3.26pt，改动后 5.27pt。
