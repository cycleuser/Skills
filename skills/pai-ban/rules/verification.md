# 验收（verification）

验收分两层：**构建期自动门禁**（`scripts/verify.py`，不过就退出码 1）和
**人工抽样复核**（页面 PNG 看版面是否"站得住"）。规格条款见
`rules/design-spec.md` §11。

---

## 1. 怎么跑

```bash
# build.py 末尾自动调用（默认开启；--no-verify 跳过）
python3 scripts/build.py <书稿> --chapters 0,2,14,20 --preview

# 单独重跑（manifest 是 build.py 写的，含日志/tex/源 md/图字号）
python3 scripts/verify.py <pdf> --manifest <pdf>.manifest.json
```

退出码：`0` 全部硬门禁通过；`1` 有门禁未通过；`2` 输入或环境问题
（PDF/manifest 不存在、缺 pymupdf）。

结果同时写成 `<pdf>.verify.json`，字段与下面表格一一对应，报告直接从
这个文件取数，不靠人眼抄。

## 2. 门禁清单（§11）

| # | 门禁 | 阈值 | 实测口径 |
|---|---|---|---|
| 1 | 内容越出纸边 | 0 页 | 逐页墨迹 bbox 四边都在 `[3pt, 纸宽/高−3pt]` 内 |
| 2 | 内容越出版心 | ≤6pt 且 ≤5 页 | 墨迹 `x1 ≤ 版心右界 + 6pt`；右界 recto = 纸宽−15mm，verso = 纸宽−18mm |
| 3 | 内容越出订口 | 0 页 | 墨迹 `x0 ≥ 左边界 − 3pt`；左界 recto = 内白边 18mm，verso = 外白边 15mm |
| 4 | 缺失字形 | 0 | xelatex 日志 `Missing character` 计数 |
| 5 | LaTeX 错误 | 0 | 日志 `^! ` 计数 |
| 6 | 重复编号 | 0 处 | PDF 正文正则 `第N章 第N章` / `Chapter N Chapter N` |
| 7 | 图数一致 | 源文 = 成书 | 源 md 的 `![](...)` 多重集合 vs tex 的 `\paibaninclude{...}` |
| 8 | 表数一致 | 源文 = 成书 | md 表格分隔行计数 vs tex 的 `\begin{longtable}` |
| 9 | 目录条目 | = 章 + 节 | PDF outline 的 L1/L2 vs tex 的 `\paibanchapter` / `\paibansection` |
| 10 | Overfull \hbox | ≥1pt 的为 0 | 日志 `Overfull \hbox` + 最大值（§7/§8 的直接指标） |
| 11 | 图内文字 ≥5.5pt | 最差一张 | **advisory**，见 §4 |

补充说明：

- **门禁 3 是怎么来的**：§11 的表里没有它，但 §1 的验收写着"左边界 ≥
  18mm − 3pt（奇数页）"。这条门禁第一次跑就抓出 12 页——引文块的竖线挂在
  版心左缘之外 9.8pt、代码行号挂在竖线左边两位数就伸进白边。两条都已修
  （引文整块缩进 1em、行号收进灰底内），现在最差 2.8pt，来自参考文献
  两位数的列表标签，属于刻意的悬挂缩进。
- **门禁 9 的 +1**：`book` 类的 `\tableofcontents` 自己会写一条 chapter 级
  条目「目录」，所以 L1 期望值 = 章数 + 1。
- **门禁 10 的 1pt 容差**：亚磅级（<1pt）Overfull 在 600dpi 下都看不见，
  但 `\lstinline`、URL 之类偶发不可避免；≥1pt 一律算失败。规格 §7 的
  原始要求是"零 Overfull 来自代码行"，这条门禁比它更宽一点，但可执行。
- **门禁 7 用的是"多重集合"**：同一张图在正文出现两次会被算作不一致
  （这是内容问题，应该报出来）。
- 门禁 1/2/3 里的 recto/verso 约定会先做一次自检：分别按"奇数页=recto"和
  "偶数页=recto"统计违反页数，取违反更少的那种，并在输出里写明
  （`奇偶约定 odd-recto`）。三条几何门禁共用同一个约定，避免一条按奇、
  一条按偶各自"择优"后互相矛盾。

## 3. 为什么量"墨迹"而不是文字 bbox

`page.get_text("blocks")` 给的是**字符前进宽度**。xeCJK 对行末全角标点
做压缩（把标点收进版心），PDF 里字形 advance 仍是 11pt，于是 bbox 比实际
墨迹多出 7–8pt——一整页会假报「Overfull 7.63pt」。

现在的做法：把页面光栅化成灰度图（100 dpi），取"非白像素"的外接矩形。
量到的是真的墨。代价是每页多几毫秒；70 页约 2 秒，整本 400 页约 15 秒，
可以接受。

光栅化的量化误差是 1 像素 = 0.72pt，远小于门禁 2 的 6pt 容差，但报告里
会出现 `0.27pt` 这种"看起来越界"的数字——那是抗锯齿边缘，不是问题。

没有 numpy 时退化为前进宽度 bbox（偏保守，会多报），并在代码注释里写明。

## 4. 图内文字为什么是 advisory

§9 要求"图内文字在成书 PDF 中的实际字号 ≥5.5pt"。实测既有 figure PDF
的画布 600–645pt、内部字号 5.25–6.75pt；缩到 326pt 版心后有效字号只有
3.2–3.7pt。

这不是排版引擎能修的：**源图本身字号就不够**，只能重画（把画布做小、
字号做大）。构建脚本能做的已经做了（限宽、限高 0.72 版心高、永不放大），
再把它判成构建失败，只会让所有章节都红。所以按 §9 的"构建脚本必须报告
最差一张"处理：`verify.py` 输出最差一张的 `原始字号 × 缩放比`，
`build.py` 在 stderr 逐张警告。

报告里要把这个数字写出来，由人决定是否重画。

## 5. 人工复核（自动门禁管不到的）

自动门禁只管"数字"，下面这些必须看 PNG：

1. **章首页**：24mm 顶空、"2" 的灰调、短线长度 24mm、标题与短线 8pt；
2. **目录**：章条目 11pt 粗、节条目 9.5pt 缩进 1.4em、引导点是否连到页码；
   有没有"某页只有 1–2 条"的孤立目录页（§5）；
3. **代码块**：左侧 2pt 竖线是否完整、`↪` 续行前缀、行号是否只在
   `linenums` 块出现、跨页时续页是否有 ≥2 行（§7）；
4. **表格**：三线表无竖线、题注在表上方且与表间距 4pt、续页「（续）」+
   重复表头（§8）；
5. **图**：图与题注同页、题注在图下方、来源行紧跟题注（§9）；
6. **引文/提示块**：左侧 2pt 竖线、缩进 1em（§10）。

样章产物：`typeset-sample/zh-sample.pdf` + `typeset-sample/pages/page-NNN.png`
（150dpi）。

## 6. 失败时的排查顺序

1. **先看 `verify.py` 的 `detail` 列**，它给出具体页码与数值；
2. 版心越界 → 打开该页，量是哪一类元素（代码块 / 表格 / 长 URL / 图）；
   - 代码：`\lstinline` 是否被禁了 `breaklines`；
   - 表格：`table-widths.lua` 是否跑了（pandoc log 里应有
     `[table-widths] tables=N …`）；
   - URL：`\emergencystretch`（现为 6em）；
3. 缺失字形 → 查 `xelatex-2.log` 的 `Missing character`，多数是 Lua 过滤器
   按字节切了 UTF-8（见 workflow §4）；
4. 目录条目数不对 → 先看 tex 里 `\paibanchapter` / `\paibansection` 的计数
   是否被注释里的示例骗了（`verify.py` 已剔除 `%` 开头的行）；
5. Overfull → 日志里 `Overfull \hbox (Xpt too wide) in paragraph at lines …`
   直接给出 book.tex 行号，回查该段。

## 7. 已知局限

- 有序列表两位数的标签会伸出左边界 ≈2.8pt：§10 规定缩进 1.5em，而
  `19.` 在 11pt 下宽 16.5pt，右对齐到 1.5em − `\labelsep` 后必然外挂。
  这在书上是常见的 optically-hanging 编号，且仍在 §1 的 3pt 容差内；
  但如果列表到 **100 条以上**（三位数），外挂会到 8pt 并让门禁 3 失败。
  遇到长参考文献表要么拆章、要么把 `\leftmargini` 提到 2.2em
  （那就偏离 §10 的 1.5em，需要改规格）。
- 表数按"md 分隔行"识别，grid table / 复杂表头可能漏计；本书是 pipe table。
- 图字号报告只覆盖矢量 PDF（`figures/pdf/*.pdf`），位图图没有可比的字号。
- 「目录无孤立条目页」没有自动判定，靠人工看图。
- **中西文字号一致性没有自动门禁**：必须有一步半自动核对——用 pymupdf 取任一标题行内 CJK span 与 Latin span 的 `size`，两者必须相等（差 >0.2pt 即判失败）。典型失败是 pandoc 模板的 `Scale=MatchLowercase` 让 CJK 缩到 0.74 倍，肉眼看"中文好像小一点"，量一下就是 22pt vs 16.3pt。已在本项目实测到一次，修法见 `workflow.md` §4。
