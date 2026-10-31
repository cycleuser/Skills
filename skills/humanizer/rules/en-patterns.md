# 英文 AI 特征库（E01–E25）

每条含：**Signal**（识别特征）、**Evidence**（倍数或出处，取不到就标 editorial）、**Fix**（改法）、**False-positive boundary**（什么情况下不该动）。

总则：单一特征不构成证据。英文的破绽在**词表密度**与**句法密度**，不在个别词。判断前先看文体——学术摘要与 Reddit 帖子的基线不同。

---

## E01 Significance inflation（意义拔高）

**Signal**: `stands as / serves as a testament to / plays a crucial role / underscores the importance / reflects a broader / marks a pivotal moment / setting the stage for / indelible mark`.

**Evidence**: Wikipedia WP:AISIGNS 列为内容层首条；语料观察显示这类评价句几乎不携带事实。

**Fix**: 写实际发生的事，删掉"重要性"评价。

> Before: The station stands as a testament to the city's enduring commitment to public transit.
> After: The station opened in 1987 and handles 12,000 riders a day.

**False-positive boundary**: 讣告、颁奖词、书评确实需要评价；但评价之后要跟一件具体事。

---

## E02 Copula avoidance（回避系动词）

**Signal**: 用 `serves as / functions as / operates as / represents / boasts / features / maintains` 代替 `is / has`。

**Evidence**: Geng & Trotta (2024) 记录 2023 年起 *is* / *are* 在 arXiv 摘要中下降超过 10%；Reinhart et al. (2025) 把 `serves as` 归入 instruct 模型的偏好结构。

**Fix**: 换回 is/are/has。大多数句子会立刻短一截。

> Before: The library serves as a hub for community engagement and features a maker space.
> After: The library is a community hub. It has a maker space.

**False-positive boundary**: `serve as` 表示"代理/充任"时是准确用法（`she served as interim director`）。

---

## E03 AI vocabulary cluster（AI 词汇簇）

**Signal**: delve, tapestry, intricate, underscore, pivotal, testament, camaraderie, palpable, meticulous, multifaceted, holistic, myriad, plethora, realm, seamless, vibrant, robust, interplay, amidst, solace, fleeting, unravel, garner, showcase, foster, leverage.

**Evidence**: Reinhart et al. (PNAS 2025)：GPT-4o 的 *camaraderie* 162×、*tapestry* 155×（出现在 23% 输出中）、*intricate* 119×、*underscore* 107×、*amidst* 100×（27% 输出）。Kobak et al. (2025)：2024 年 PubMed 有 454 个超额词，66% 是动词，主流是风格词。

**Fix**: 换成你会说出口的那个词。换不出来说明这个词本来就多余。

> Before: The team's camaraderie was palpable as they delved into the intricate tapestry of the codebase.
> After: The team got along, and they spent two days reading the old code.

**False-positive boundary**: 词表随年份变化（delve 在 2024 年后锐减）；不要按单个词删，按**密度**（>2/千词才处理）。

---

## E04 Trailing `-ing` analysis（-ing 尾巴）

**Signal**: 句末 `, highlighting / underscoring / emphasizing / reflecting / fostering / showcasing / ensuring …`。

**Evidence**: Reinhart et al. (2025)：instruct 模型的现在分词从句是人类 2–5 倍，GPT-4o 达 5.3×（Cohen's d=1.38）。

**Fix**: 拆成有主语的独立从句，或删掉。这类尾巴通常是把"评价"偷偷挂到事实上。

> Before: The policy cut waiting times by 30%, highlighting the government's commitment to reform.
> After: The policy cut waiting times by 30%. Whether that counts as reform is another question.

**False-positive boundary**: 表示同时动作的分词（`She left, slamming the door`）是正常英语。

---

## E05 Negative parallelism（否定平行）

**Signal**: `not just X but Y` / `it's not X, it's Y` / `no X, no Y, just Z` / `Y rather than X`.

**Evidence**: WP:AISIGNS 单列三条子型；Pangram 语料 3×；维基中文版把它列为中文社群"罪证"级信号。

**Fix**: 直接说 Y。真要纠正误解，说明谁持 X 观点。

> Before: This isn't just a tool for writing—it's a new way of thinking.
> After: The tool writes first drafts. That's all it does.

**False-positive boundary**: 学术写作中的对照（`rather than a linear model, we fit a spline`）是必要区分。

---

## E06 Rule of three（三的法则）

**Signal**: 三个形容词、三个短语、三个并列名词。

**Evidence**: Pangram 4×（人类 5/万字，AI 19/万字）；WP:AISIGNS 单列。

**Fix**: 砍到两个，或举一个具体例子。

> Before: The system is fast, reliable, and scalable.
> After: The system answers in 80 ms. It fell over twice last quarter.

**False-positive boundary**: 固有三分（past, present, future）、清单、菜品配料。

---

## E07 Nominalization & phrasal coordination（名词化）

**Signal**: `-tion/-ment/-ness/-ity` 名词比例高；`reducing A, B, and C` 式短语并列。

**Evidence**: Reinhart et al. (2025)：GPT-4o 名词化 2.1×、短语并列 1.9×。

**Fix**: 名词还原成动词，并列砍成两项。

> Before: The implementation of the optimization resulted in a reduction of latency.
> After: We optimized the query and latency dropped.

**False-positive boundary**: 学术写作中 nominalization 是规范（`the analysis of variance`），密度阈值放宽。

---

## E08 Passive voice（被动语态，反直觉项）

**Signal**: 常被误列为 AI 特征，实际相反——AI 的**无施事被动**约为人类一半。

**Evidence**: Reinhart et al. (2025)：GPT-4o agentless passive ≈ 0.5× human。

**Fix**: 不要为了"去 AI 味"硬加被动。该被动时被动（施事未知/不重要）。

> Note: 把主动句硬改成被动句是常见误改，会让文字更像翻译稿。

**False-positive boundary**: 本条是"不要做"的规则，没有改写动作。

---

## E09 Formulaic openers（套话开场）

**Signal**: `In today's fast-paced world` / `In an era of` / `In the realm of` / `Let's dive in` / `Great question`.

**Evidence**: Pangram 的"AI phrases"组 12×；助手式开场单独 2×。

**Fix**: 删掉，第一句给事实。

> Before: In today's fast-paced digital landscape, businesses must adapt or risk falling behind.
> After: Two of our three suppliers raised prices in January.

**False-positive boundary**: 演讲稿、播客口播需要暖场，可留一句。

---

## E10 Assistant residue（助手残留）

**Signal**: `Certainly!` / `Of course!` / `Here's a ...` / `I hope this helps` / `Let me know if` / `Would you like me to` / `As an AI`.

**Evidence**: Pangram：`Certainly! Here's` 人类 0 次/万字，AI 94 次（70×）。

**Fix**: 整段删除。这是最硬的信号，没有例外。

> Before: Certainly! Here's a breakdown of the three options.
> After: Three options, in order of cost.

**False-positive boundary**: 无。给用户的对话回复里可以保留礼貌用语，但正文不能有。

---

## E11 Hedging disclaimers（免责声明）

**Signal**: `It is important to note` / `It's worth noting` / `While specific details are limited` / `based on available information` / `should not be confused with`.

**Evidence**: WP:AISIGNS 按年份列出三波变体（2023–24 说教式、2024–25 检索式、2026 起"纠正式框架"）。

**Fix**: 说事，或者说一次"我不知道"。

> Before: It is important to note that while specific details are limited, the policy likely affects small firms.
> After: I couldn't find the text of the policy. If it covers firms under 50 people, it affects about 6,000 businesses.

**False-positive boundary**: 法律、医疗文本的限定语是责任要求，保留。

---

## E12 Vague attribution（模糊归属）

**Signal**: `Experts argue` / `Industry reports suggest` / `Observers have cited` / `Studies show`（无引用）/ `many scholars`.

**Evidence**: WP:AISIGNS 内容层；最容易被事实核查击穿的一类。

**Fix**: 点名、给时间、给链接；找不到就删。

> Before: Experts argue that remote work is here to stay.
> After: Stanford's 2024 survey of 3,000 firms found 27% kept full remote policies.

**False-positive boundary**: 保护信源的调查报道，需说明匿名理由。

---

## E13 Challenges & Future Prospects formula

**Signal**: `Despite its ..., X faces several challenges` / `Despite these challenges` / `Challenges and Legacy` / `Future Outlook`.

**Evidence**: WP:AISIGNS 单列（WP:FACESCHALLENGES）；结构上几乎总是"正面—挑战—乐观"三段。

**Fix**: 删掉公式。真有约束就写具体的约束与代价。

> Before: Despite these challenges, the future of the project looks promising.
> After: The project runs out of funding in June. Nobody has applied for the extension.

**False-positive boundary**: 真实的风险评估章节需要列挑战，但要有数据。

---

## E14 Title case & heading tics（标题格式）

**Signal**: 每个实词首字母大写的小标题；层级跳跃（## 直接到 ####）；标题只有下级标题没有正文。

**Evidence**: WP:AISIGNS 样式层；markdown 转 wikitext 的产物。

**Fix**: 按目标文体统一（英文标题句首大写或全大写跟风格指南）；补齐层级；标题下必须有正文。

**False-positive boundary**: 美式出版规范确实用 Title Case，看目标刊物。

---

## E15 Inline-header vertical lists（粗体标签列表）

**Signal**: `- **Thing:** description` 形式的行内标题列表，各项等长。

**Evidence**: WP:AISIGNS (WP:AILIST)；Pangram 项目符号 9×。

**Fix**: 写成句子；真需要列表就保留列表但不加粗标签。

> Before:
> - **Speed:** 2× faster than the old version.
> - **Cost:** 30% cheaper per request.
> After: It's about twice as fast and 30% cheaper per request.

**False-positive boundary**: 参数表、API 文档、对比评测。

---

## E16 Em dash（破折号）

**Signal**: 用 `—` 替代逗号、括号、冒号，密度高。

**Evidence**: Pangram 10×（人类 2/万字，AI 17/万字）；但按模型分：OpenAI 9×、开源 8×、Anthropic 7×、**Gemini 3 Pro 0.7×**。

**Fix**: 改成逗号、冒号或句号。多数情况下句子会更有力。

> Before: The fix was simple—four characters—but it took three weeks to find.
> After: The fix was four characters. Finding it took three weeks.

**False-positive boundary**: 破折号是合法标点。不要因为这一条就全删；Gemini 输出里它甚至是负信号。

---

## E17 Curly quotes & apostrophes（弯引号）

**Signal**: `“ ” ‘ ’` 出现在纯文本、代码、终端输出里。

**Evidence**: Wikipedia：ChatGPT 与 DeepSeek 默认弯引号；Gemini 与 Claude 通常不用。

**Fix**: 纯文本/代码环境统一成直引号；正式排版环境统一成弯引号。一致性比选哪种更重要。

**False-positive boundary**: Word、macOS 默认智能引号；出版排版规范要求弯引号。

---

## E18 Markdown leakage（markdown 残留）

**Signal**: 纯文本里出现 `**bold**`、`## heading`、反引号、`---` 分隔线。

**Evidence**: Pangram 12×（8 vs 90/万字），粗体单独 43×、标题 23×。

**Fix**: 按目标载体转换；散文里全部清除。

**False-positive boundary**: README、issue、聊天回复本来就是 markdown。

---

## E19 Emoji as formatting（emoji 当图标）

**Signal**: ✅ ⚠️ 1️⃣ 🚀 ❌ 出现在标题或列表开头。

**Evidence**: Pangram：总频率仅 2×，但 ✅ 167×、2️⃣ 129×、🚀 26×；而 😊 0.6×、❤️ 0.2×——人用 emoji 表情绪，AI 用来做版式。

**Fix**: 删除；情绪表达可以保留一两个。

**False-positive boundary**: 社媒文案、面向消费者的产品公告。

---

## E20 Unusual Unicode（非常规字符）

**Signal**: ─ ≈ → ≥ ★ ※ §。

**Evidence**: Pangram 3×；U+2500 框线 940×，≈ 241×，⚠ 57×，→ 48×。

**Fix**: 换成 ASCII 或规范符号（`about`、`to`、`>=`）。

**False-positive boundary**: 数学、化学、工程文本中这些符号是内容本身。

---

## E21 Unrequested tables（表格化散文）

**Signal**: 两三行的小表格，内容其实是并列短句；表格列名空泛。

**Evidence**: WP:AISIGNS (WP:AITABLE)。

**Fix**: 改写成句子。

**False-positive boundary**: 真矩阵数据（多实体 × 多属性）。

---

## E22 Marketing verbs（营销动词）

**Signal**: boasts, features, offers, delivers, empowers, elevates, unlocks, revolutionizes.

**Evidence**: WP:AISIGNS 广告腔条目；WP:PEACOCK。

**Fix**: 换成 has / does / costs / takes。

> Before: The platform empowers teams to unlock insights at scale.
> After: The platform runs queries on 40 GB of logs in about a second.

**False-positive boundary**: 真实广告文案、产品页；此时问题不是 AI 味而是夸大，按事实核。

---

## E23 Latinate inflation（拉丁词膨胀）

**Signal**: utilize, facilitate, endeavor, ascertain, commence, terminate, prior to, in order to.

**Evidence**: editorial（编辑经验），无统计检验。

**Fix**: use, help, try, find out, start, end, before, to.

**False-positive boundary**: 法律合同、正式技术规范。

---

## E24 List-ese（列表化）

**Signal**: 每段都要点列；列表项数量恰好三；列表项等长。

**Evidence**: Pangram 项目符号 9×。

**Fix**: 能写成一句的写成一句。列表只用于真正并列、可跳读的内容。

**False-positive boundary**: 步骤、参数、检查清单。

---

## E25 Fabricated references（伪引用）

**Signal**: DOI 指向不相关论文；`et al., 2024` 无标题；书引无页码无 URL；`access-date` 是占位符。

**Evidence**: WP:AISIGNS 引用层：无效 ISBN 校验位、DOI 解析到无关文章，都是幻觉引用的硬指标。

**Fix**: 逐条核验 DOI/ISBN；核不到就删。

**False-positive boundary**: 预印本、内部报告可能确实无 DOI。

---

## 速查：英文改写优先级

1. 删 E10（助手残留）、E11（免责）、E13（展望公式）——整段级动作，收益最大。
2. 拆 E04（-ing 尾巴）、E07（名词化）——句法级动作，最影响"读起来像不像人"。
3. 换 E03（词表）、E22（营销动词）——词汇级动作，注意按密度而非单词。
4. 清 E18/E19/E20（版面与符号）——机械动作，最后做。
5. E16（破折号）只做减法不做加法，且不要单独作为判据。
