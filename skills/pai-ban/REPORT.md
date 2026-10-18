# pai-ban 交付报告

日期：2026-10-18
规格：`rules/design-spec.md` v1.0.0（唯一权威）
样章：`大语言模型：智能体视角`（第二版修订版）第 0 / 2 / 14 / 20 章

---

## 1. 交付物

### 1.1 技能内新增/修改

| 文件 | 行数 | 作用 |
|---|---:|---|
| `SKILL.md` | 91 | 技能说明（本次把 `pai-ban.yml` 更正为 `pai-ban.toml`，补全 5 个过滤器与输出路径） |
| `rules/design-spec.md` | 203 | 规格（未改，作为验收依据） |
| `rules/workflow.md` | 155 | **新增**：操作顺序、过滤器顺序与原因、排错表 |
| `rules/verification.md` | 120 | **新增**：§11 门禁口径、墨迹测量原理、人工复核清单、已知局限 |
| `assets/preamble.tex` | 632 | 版式实现：§1 画布、§2 字号阶梯、§3 六色、§4 章首页、§5 目录、§6 页眉、§7 listings、§8 booktabs、§9 图容器、§10 引文 |
| `assets/filters/chapter-split.lua` | 241 | H1 → `\paibanchapter{n}{title}`；H2–H4 → `\paibansection` 系列；第一个编号章前发 `\paibanmainmatter` |
| `assets/filters/table-widths.lua` | 349 | **新增**：平方根权重 + 注水法列宽、长 ASCII token 插 `\allowbreak` |
| `assets/filters/code-caption.lua` | 57 | `title`/`linenums` → 代码标签 + 行号，并删掉这两个属性（否则 listings keyval 报错） |
| `assets/filters/table-caption.lua` | 109 | **新增**：「表N.M：…」斜体段搬到表格上方 → 9pt 加粗标签 |
| `assets/filters/figure-caption.lua` | 138 | 图 + 题注 → 不浮动 minipage（图与题注同页） |
| `assets/pai-ban.toml` | 76 | 配置模板（TOML；`tomllib` 读，缺项回退 JSON） |
| `scripts/build.py` | 846 | 预处理 → pandoc → longtable 续页补丁 → xelatex ×2–3 → 产物 + manifest |
| `scripts/verify.py` | 476 | **新增**：§11 八项 + §1 左边界 + §7/§8 Overfull 共十一项门禁，非零退出，输出 pass/fail 表与最差指标 |
| `scripts/init.py` | 120 | 脚手架（写 `pai-ban.toml`、复制 `pai-ban-assets/`、探测章节与图目录） |

### 1.2 书稿侧产物（未改动任何源稿）

| 路径 | 说明 |
|---|---|
| `<book>/pai-ban.toml` | 本书配置（title/author/lang/chapters_dir…） |
| `<book>/pai-ban-assets/` | 技能 assets 的副本（build 优先用它） |
| `<book>/build/pai-ban/zh/` | 中间产物：预处理 md、book.tex、xelatex 日志、PDF/DOCX、manifest |
| `<book>/typeset-sample/zh-sample.pdf` | 样章 PDF（72 页） |
| `<book>/typeset-sample/pages/page-001.png … page-072.png` | 150dpi 页面图 |
| `<book>/typeset-sample/zh-sample.verify.json` | 门禁结果（机器可读） |

未触碰：`CN/*.md`、`EN/*.md`、`CN/LLMAP_简体中文.pdf`、`EN/LLMAP_English.pdf`、
`LLMAP_Cover_TOC.pdf`、`../第一版旧版/`、其它技能、`skills.json`。

## 2. 规格条款 → 实现映射

| 条款 | 要求 | 实现 |
|---|---|---|
| §0 | 基线网格、单强调色、两级线宽、正文 100% 墨色 | `preamble.tex` §0 段：`linespread 1.12`、`\definecolor{accent}` 唯一强调色、`heavyrulewidth 0.8pt` / `lightrulewidth 0.4pt`、正文 `ink` |
| §1 | A5、双面、内 18 / 外 15 / 上 16 / 下 19、版心 115×175 | `geometry`（build.py 由 toml 拼 `-V geometry=…`）+ 页边距断言 |
| §2.1 | 正文宋体 / 标题黑体 / 代码 Menlo + 宋体回退 | `\setCJKmainfont{Songti SC}`、`\heiti` → PingFang SC、`\setCJKmonofont` 保证代码里的中文 |
| §2.2 | 字号阶梯 22/14/11.5/11、正文 11/15.2、表图 9/11.5、代码 8.5/10.5、脚注 8、页眉 8 | `\paiban@opener`、`\paiban@sectionstyle` 系列、`basicstyle`、`\captionsetup`、`fancyhdr` 字号 |
| §3 | 六色，`accent #0B3D91` 等 | `\definecolor{ink/accent/accent30/rule/muted/codebg/tablehead/strgreen/num}`（调色板写死，不开放配置） |
| §4 | 章起奇数页；24mm 顶空；48pt 章号；24mm 短线；22pt 标题；18mm 空；无页眉 | `\cleardoublepage` + `\paiban@chapnum` + `\paiban@opener`；`\thispagestyle{plain}` |
| §5 | 只收 chapter+section；章 11pt 粗、节 9.5pt 缩进 1.4em；罗马页码 | `\l@chapter` / `\l@section` 重写；`\tableofcontents` 重定义（24mm 顶空 + 22pt 标题）；`tocdepth=1` |
| §6 | 偶数页书名 / 奇数页章标题（居外）；0.4pt 页眉线；页码页脚居中；前言罗马、正文阿拉伯 | `fancyhdr` + `\markboth`（chapter-split 传纯标题）；`\paibanmainmatter` 在第一编号章前 |
| §7 | listings；浅灰底 + 2pt 左线 + 4pt 内边距；8.5/10.5；行号仅 `linenums`；`breaklines` + `↪`；四色 | `\lstdefinestyle{paiban}`；`code-caption.lua` 控制行号/标签；`postbreak` 画 `↪` |
| §8 | booktabs 三线、无竖线；列宽 8%–55% 合计 1.0；9/11.5；题注在上、加粗标签 + 4pt；跨页重复表头 + 「（续）」 | `table-widths.lua`（注水法）+ `table-caption.lua` + `patch_longtable_continuation()`（`\endfirsthead`/`\endhead`） |
| §9 | 居中、≤版心宽、不放大 >1.15；题注在下 9pt；图与题注同页；来源行 8.5pt | `\paibanfigure`（不可分页 minipage）+ `\paibaninclude`（宽 ≤ `\linewidth`、高 ≤ 0.72 `\textheight`、永不放大）+ `figure-caption.lua` |
| §10 | 引文左 2pt 竖线、缩进 1em、9.5pt；列表间距 2pt | `quote` 环境重定义；`\setlist` 不可用（enumitem 禁用）→ 在 preamble 直接设 `\itemsep/\topsep` |
| §11 | 八项硬门槛 | `scripts/verify.py`（另加 §1 左边界门禁、§7/§8 的 Overfull 门禁与 §9 图字号 advisory） |
| §12 | 预处理 → Lua → pandoc → xelatex ×2–3 → 验证 → 产物 | `build.py` 的 `preprocess()` → 5 个过滤器 → `--listings` → `xelatex` 循环（`rerun` 收敛）→ `verify.py` → PDF/DOCX |

## 3. 样章实测

命令：

```bash
python3 scripts/build.py "<book>" --chapters 0,2,14,20 --preview \
    --no-docx --title "大语言模型：智能体视角" --author CycleUser
```

| 指标 | 数值 |
|---|---|
| 页数 | 72（含目录 2 页、Preface 罗马 i–vi） |
| xelatex 遍数 | 2 |
| 缺失字形 | 0 |
| LaTeX 错误 | 0 |
| Overfull \hbox | 0（最大 0.0pt） |
| 内容越出纸边 | 0 页 |
| 内容越出版心 | 0 页（最差 1.57pt，p.50，容差 6pt） |
| 内容越出订口 | 0 页（最差 2.78pt，p.39，容差 3pt；参考文献两位数标签的悬挂缩进） |
| 重复编号 | 0 处 |
| 图数 | 源文 5 = 成书 5 |
| 表数 | 源文 17 = 成书 17（其中 17 张补了续页表头） |
| 目录条目 | 45 = 章 4 + 节 40 + 目录自身 1 |
| 图内文字（最差） | 3.18pt（`fig02-llm-api-comparison.pdf`：6.0pt × 0.53）— advisory |

门禁表（`typeset-sample/zh-sample.verify.json`）：

| 门禁 | 条款 | 阈值 | 实测 | 结果 |
|---|---|---|---|---|
| 内容越出纸边 | §1/§11 | 0 页 | 0 页 | PASS |
| 内容越出版心 | §11 | ≤6pt 且 ≤5 页 | 最差 1.57pt，0 页 | PASS |
| 内容越出订口 | §1 | 0 页 | 最差 2.78pt，0 页 | PASS |
| 缺失字形 | §11 | 0 | 0 | PASS |
| LaTeX 错误 | §11 | 0 | 0 | PASS |
| 重复编号 | §4/§11 | 0 处 | 0 处 | PASS |
| 图数一致 | §9/§11 | 5 = 5 | 5 = 5 | PASS |
| 表数一致 | §8/§11 | 17 = 17 | 17 = 17 | PASS |
| 目录条目 | §5/§11 | 4 章 + 40 节 | outline 45（L1 5 / L2 40） | PASS |
| Overfull hbox | §7/§8 | ≥1pt 的为 0 | 0 处 | PASS |
| 图内文字 ≥5.5pt | §9 | 最差一张 | 3.18pt | ADVISORY |

补跑说明（同一天，加左边界门禁时发现并修掉两处真实越界）：

1. **引文块竖线挂到版心外**：原实现用 `\llap` 把 2pt 竖线画在版心左缘之外
   （内容从 0 缩进开始），竖线落进订口 9.8pt，12 页被门禁抓出。现改为
   整块右移 1em、竖线画在 1em 处、内容盒宽 = 版心 − 2em − (2pt+0.8em)，
   右缘仍留 1em；顺带用 `\raisebox[-\dp][0pt][0pt]` 让竖线盖住末行降部。
2. **代码行号挂在竖线左侧**：`xleftmargin=10pt` / `framexleftmargin=0pt`
   时行号在灰底外、两位数即伸进白边 2.9pt，三位数必然越界。现改为
   `xleftmargin=20pt` / `framexleftmargin=12pt`，行号收进灰底内，3 位数
   左缘仍在版心内（1.4pt）。

两处改完页数、缺失字形、Overfull 均不变（仍 72 页 / 0 / 0），节标题与
目录条目数也不变。

页面 PNG（150dpi，共 72 张）：

```
<book>/typeset-sample/pages/page-001.png   # 标题页
<book>/typeset-sample/pages/page-003.png   # 目录
<book>/typeset-sample/pages/page-005.png   # Preface（无编号章）
<book>/typeset-sample/pages/page-009.png   # 第 2 章章首页
<book>/typeset-sample/pages/page-041.png   # 第 14 章章首页
<book>/typeset-sample/pages/page-053.png   # 表 14.1 续页（「（续）」+ 重复表头）
<book>/typeset-sample/pages/page-061.png   # 第 20 章章首页
```

## 4. 与规格的偏差（有意为之，均已注释在代码里）

1. **`figure-caption.lua` 是规格外的第 5 个过滤器**。规格 §9 要求"图与题注
   必须同页"，但源文是"图片段落 + 紧跟斜体题注"，pandoc 默认会把它变成
   浮动体。改成不可分页 minipage 是唯一不依赖 `needspace`（TeX Live basic
   没有）的稳妥做法。
2. **`table-caption.lua` 把题注从表下搬到表上**。源文习惯写在表下（§8 要求
   在上），构建期搬迁比要求作者改稿更可行。
3. **§9 图内字号是 advisory，不是硬门禁**。源图字号本身只有 3.2–3.7pt
   有效值，重画才能解决；判失败只会让所有章节都红。
4. **Overfull 门禁取 ≥1pt**（§7 原文是"零 Overfull 来自代码行"）。亚磅级
   Overfull 不可见且偶发，1pt 是可执行的下限。
5. **章首页 24mm 顶空**从版心顶算起（即纸顶 40mm），与 §4 的图示一致。

## 5. 风险与建议补的测试

| 风险 | 说明 | 建议 |
|---|---|---|
| 其它 17 章未编译 | 只验证了 0/2/14/20；第 4–13 章有大表、公式、更长的代码块 | 全量构建一次（约 8–12 分钟），重点看表格续页与公式行距 |
| 图字号 | 5 张样章图全部 <5.5pt | 重画 figure PDF（画布缩到 ~330pt 宽、字号 ≥7pt）后复测 |
| 表题注只在有「表N.M：」的章节生效 | 第 2 章的 14 张表源文无题注 | 给第 2 章补 `*表2.1：…*`，或接受无题注 |
| `table-caption.lua` 的相邻判断 | 题注远离表格（中间隔空行/段落）时不会搬 | 用行号抽查 5 张长表 |
| `\emergencystretch=6em` | 为压住 `modelcontextprotocol.io` 那行加到 6em | 全量构建后抽查 10 个长 URL 段落是否过松 |
| 三位数列表标签 | §10 规定缩进 1.5em，`100.` 会外挂约 8pt，直接顶穿 §1 的 3pt 容差 | 若出现 ≥100 条的参考文献表，先看门禁 3；要么拆章，要么把 `\leftmargini` 提到 2.2em（需改规格） |
| `quote` 环境不可分页 | 引文块整块移页，1–4 行的来源说明没问题，长引文会留大片空白 | 若某章出现 >8 行引文，考虑分页版竖线（`\vrule` 逐行） |

## 6. 复现

```bash
BOOK="/path/to/大语言模型简明教程/第二版修订版"

python3 scripts/init.py  "$BOOK" --force
python3 scripts/build.py "$BOOK" --chapters 0,2,14,20 --preview \
        --title "大语言模型：智能体视角" --author CycleUser
# 退出码 0 = 十一项门禁全过；1 = 见 [verify] 表里的 FAIL 行
```
