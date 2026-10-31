---
name: humanizer
description: |
  AI text humanizer that turns machine-generated prose into writing that reads like a person wrote it — in Chinese and English, with measurable checks instead of guesswork.

  Triggers when: 需要去掉 AI 味 / 去 AIGC 痕迹 / 把生成的内容改得像人写的 / 润色公众号、博客、公文、论文、技术文档使其自然 / 中文或英文文本被指"一眼AI" / 需要量化检查文本的 AI 特征密度。

  Commands:
  - /人话 <文本> — 人化改写（自动判语言与文体）
  - /人话 --style casual|formal <文本> — 指定口语/书面
  - /人话 --mode light|full <文本> — 润色或重写
  - /人话 --lang zh|en <文本> — 强制语言
  - /人话 check <文件|文本> — 只体检不改写
  - /人话 diff <改写前> <改写后> — 改写前后指标对比
  - /humanize <text> — English alias
  - /detect <文本> — 特征体检摘要
  - /demo — 用样例演示前后差异

  Capabilities: 双语 AI 特征库（中文 Z01–Z29 / 英文 E01–E25）、量化阈值（句长方差、名词化、AI 词密度、版面痕迹）、五遍改写协议、可执行体检脚本 humanize_lint.py（含自测）、保留原意与术语的硬约束。
license: MIT
compatibility: opencode
metadata:
  version: 2.0.0
  author: cycleuser
---

## Safety Rules

参见 [_shared/core/safety-rules.md](../_shared/core/safety-rules.md) — 所有安全规则从共享层加载。

# 人话 (Humanizer)

把 AI 生成的文字改得像人写的。核心不是换同义词，而是**先量化、再破结构、再改句法、最后清版面**，并且全程守住原意。

## 它做什么，不做什么

做：把人写的骨架装回去——删空话、破三段论、造长短句、拆名词化、清掉 markdown 痕迹、补一处真实判断。

不做：不改事实，不编细节，不承诺"降低检测率到 X%"。检测器本身不可靠（改写一轮就能大幅波动），以分数为唯一目标是错的。

一句话：**目标是"读起来像人"，不是"骗过机器"。**

## Quick Commands

| Command | 说明 |
|---------|------|
| `/人话 <文本>` | 人化改写，自动判语言与文体 |
| `/人话 --style casual <文本>` | 口语体（博客、公众号、帖子） |
| `/人话 --style formal <文本>` | 书面体（论文、公文、报告） |
| `/人话 --mode light <文本>` | 只润色，保留原结构 |
| `/人话 --mode full <文本>` | 重写，五遍全做 |
| `/人话 --lang zh\|en <文本>` | 强制语言（中英混排时用） |
| `/人话 check <文件\|文本>` | 只体检，不改写 |
| `/人话 diff <改写前> <改写后>` | 改写前后指标对比 |
| `/humanize <text>` | English alias |
| `/detect <文本>` | 体检摘要 |
| `/demo` | 样例演示 |

## 工作流

```
① 判语言/文体 → ② 跑体检 → ③ 定模式 → ④ 五遍改写 → ⑤ 复测 → ⑥ 交付（稿+摘要+指标）
```

**① 判语言与文体**

| 文体 | 判据 | profile |
|------|------|---------|
| 散文/博客/公众号 | 面向普通读者，有叙述 | `prose` |
| 技术文档/README/说明 | 面向使用者，有步骤参数 | `tech` |
| 论文/报告/公文 | 面向评审或上级，有引用规范 | `academic` |

中英混排时按主体语言判；代码块、公式、引用不计入统计。

**② 跑体检**（有文件时必跑，纯聊天输入可心算）

```bash
python3 scripts/humanize_lint.py check draft.md --lang zh --profile prose
python3 scripts/humanize_lint.py check draft.md --json          # 机器可读
cat draft.md | python3 scripts/humanize_lint.py score - --lang en
```

脚本只读、纯标准库、有自测（`python3 tests/test_lint.py`，23 项）。改写完成后用它对比前后：

```bash
python3 scripts/humanize_lint.py diff before.md after.md
```

输出分数变化、九项关键指标的前后值与方向、被清除和残留的检测项。没有脚本环境时，按 `rules/metrics.md` 的表手工抽三项：句长 CV、AI 词密度、加粗/破折号密度。

**③ 定模式**：分数 <15 不动或轻润；15–40 用 `light`；>40 用 `full`。

**④ 五遍改写**：P0 保全 → P1 骨架 → P2 句法 → P3 词汇 → P4 证据 → P5 版面。详见 `rules/rewrite-protocol.md`。

**⑤ 复测**：重跑体检，分数未达 profile 阈值就回到对应那一遍，最多 3 轮。只处理分项里最难的那一维（分数最高者），不要全文重写。

**⑥ 交付**：改写稿 + 3–6 条改动摘要 + 前后指标 + 一句限定（"启发式体检，不是检测结论"）。没有真实数据的地方标 `（待补：……）`。

## 核心规则（十二条硬约束）

1. **原意优先**。数字、术语、引用、代码、直接引语逐字不动；条件与强度不许改大改小。
2. **不编细节**。原文没有的数据、案例、经历一律不补；需要补就标待补。
3. **先删后换**。套话能删就删，不要换成同义词。
4. **先结构后词汇**。三段论、三项并列、对称段没破，换词是白费。
5. **句长要方差**。全短句也是 AI 特征；每 3–5 句放一个短句，每段留一个长句。
6. **中文拆修饰**。修饰语密、句子重、互动少，是中文 AI 文的核心差异；方向是拆句、还原动词、加一点对话感。
7. **英文拆名词化与 -ing 尾巴**。不要为降分硬加被动（AI 的无施事被动本来就比人少）。
8. **版面清零**。散文里不留加粗、列表、表格、emoji、markdown 残留。
9. **词表按密度用**。单个词不构成证据；破折号在 Gemini 上甚至低于人类。
10. **留一处人味**。一个不确定、一个判断、一句没说完的话。
11. **不越改越糟**。术语口语化、过度语气词、同义词轮换、编造细节，都比 AI 味更糟。
12. **分数是体温计**。到阈值就停；为过 lint 而改坏内容是失败。

## 特征库

| 文件 | 内容 | 什么时候看 |
|------|------|-----------|
| `rules/zh-patterns.md` | 中文 Z01–Z29：空话拔高、三段论、否定平行、四字格、名词化、口播腔、拟人、版面痕迹、伪具体化 | 改中文 |
| `rules/en-patterns.md` | 英文 E01–E25：significance inflation、copula avoidance、AI 词簇、-ing 尾巴、否定平行、三的法则、助手残留、伪引用 | 改英文 |
| `rules/metrics.md` | 双语阈值表、三套 profile、分数解读、调阈值方法 | 判断"改到什么程度" |
| `rules/rewrite-protocol.md` | 五遍法、保全白名单、自检 10 条、常见误改 | 动手改 |
| `references/ai-text-features-research.md` | 证据与数字：PNAS、Science Advances、维基编者清单、中文对照研究、叙事层研究 | 想知道"为什么" |

## 阈值速查

完整表见 `rules/metrics.md`。下面是常用的几条（prose 档）：

| 指标 | 中文（prose） | 英文（prose） |
|------|---------------|---------------|
| 平均句长 | >38 字考虑拆句（仅提示） | >24 词考虑拆句（仅提示） |
| 句长 CV | ≤0.32 满分，≥0.55 免罚 | 同左 |
| 空话 / 官腔 / AI 词 | 3→15 / 千字 | 3→15 / 千词 |
| 名词化 | 8→18 / 千字 | 4.5%→10% |
| 三项并列 | 0.4→1.2 / 千字 | 0.8→2.2 / 千词 |
| 否定平行 | 0.3→1.5 / 千字 | 0.3→1.5 / 千词 |
| 连接词开场句 | 10%→35% | 10%→35% |
| 加粗 | 允许 1 处，之后 1→3 / 千字 | 允许 1 处，之后 1→3 / 千词 |
| 破折号 | 允许 1 处，之后 1→3 / 千字 | 允许 1 处，之后 1→3 / 千词 |
| 通过分数 | ≤45 | ≤45 |

`a→b` 表示测值 ≤a 不计分、≥b 满分。

技术文档与学术文本的阈值更松，务必切 `--profile`，否则会把必要的列表和术语删掉。

## 处理示例

### 示例一：中文，典型"报告体"

原文（节选，体检 33 分）：

> 人工智能技术的快速发展正在深刻改变我们的生活方式。首先，从技术层面来看……其次，从应用层面分析……最后，从发展趋势预测……综上所述，我们需要在推动技术创新的同时，关注其潜在风险。

改写（同样内容，体检 2 分。两组文本见 `tests/samples/example_zh_before.md` 与 `example_zh_after.md`，数值可直接复现）：

> 医院是最先感到变化的地方。影像科的初筛从四十分钟压到十五分钟，但放射科医生并没有少，多出来的时间用来复核。银行和工厂的采购周期也短了，代价是采购部门多了一道“模型版本确认”的流程。
>
> 至于三年后会怎样，现在下结论太早。

改动：删首段空话与三段论；把“效率提升”落到具体科室与分钟数；删“综上所述”；结尾留一处不确定。注意改写里没有用破折号——原文的“——”是刻意清掉的。

### 示例二：英文，典型助手腔

原文（节选，体检 62 分）：

> In today's fast-paced digital world, AI stands as a testament to human ingenuity. It is not just a technological advancement, but a pivotal shift… Moreover… Experts argue… Despite these challenges, the future of AI looks promising.

改写（体检 3 分，样本同上目录的 `example_en_*.md`）：

> Two things changed at work this year. The first is boring: search got good enough that people stopped asking me where the docs live. The second is not: our support team handles 40% more tickets with the same headcount, and nobody has decided whether that's a win.
>
> I don't know where this goes. I do know the "AI strategy" deck hasn't been opened since March.

改动：删套话开场与展望公式；拆掉 `not just X but Y`；把 `experts argue` 换成具体观察；用短句与一处自嘲造节奏；不再给结论。

## 迭代与收敛

- 每轮只处理体检报告里权重最高的 1–2 类，不做全文重写。
- 收敛条件：分数 ≤ 阈值，且自检 10 条中 ≥8 条通过。
- 连续两轮分数下降 <2 分，停止并报告残余问题（通常是叙事层，机器改不动）。
- 最多 3 轮。第四轮开始通常是过度修改，会把文字改坏。

## 与其他技能集成

- `/简写`（brief-write）：先人化再去 AI 腔，顺序反了会丢掉作者语气。
- `/gongwen check`（official-document-writer）：公文先用 `--style formal --profile academic`，再过 GB/T 9704 格式检查。
- `/paper review`（academic-writer）：论文只做 P1/P3/P5，P2 句法改动要谨慎，避免破坏学术语域。
- `/patent disclosure`（patent-writer）：专利文本只清空话与版面，术语与权利要求的措辞不动。
- `/有据`（you-ju）：人化不能新增事实；如果原文本身有幻觉，先过有据审计再润色。

## 配置项

| 参数 | 默认 | 说明 |
|------|------|------|
| `style` | auto | auto / casual / formal |
| `mode` | auto | auto / light / full |
| `lang` | auto | auto / zh / en |
| `profile` | prose | prose / tech / academic |
| `target_score` | 45 | 收敛目标（按 profile 覆盖） |
| `max_passes` | 3 | 最大改写轮次 |
| `preserve_meaning` | true | 严格保留术语与数字 |
| `allow_placeholders` | true | 允许 `（待补：…）` 标记 |

## 边界情况

- **代码块、公式、front matter**：原样保留，不参与改写，也不计入统计。
- **直接引语**：一字不动；引语外的叙述可以改。
- **多语言混排**：分段处理，按各段主体语言选特征库。
- **短文本（<180 字）**：句长与段长统计不可靠，只看词表与版面；报告里会提示。
- **已是人写**：分数 <15 直接返回原文并说明"无需修改"，不要为了交差硬改。
- **敏感领域**（医疗、法律、金融）：只改表达，不动限定语与免责声明。
- **检测器分数**：不作为验收标准，也不写入交付结论。

## 文件结构

```
skills/humanizer/
├── SKILL.md
├── README.md
├── rules/
│   ├── zh-patterns.md          # 中文特征库 Z01–Z29
│   ├── en-patterns.md          # 英文特征库 E01–E25
│   ├── metrics.md              # 阈值与体检说明
│   ├── rewrite-protocol.md     # 五遍法 + 自检清单
│   ├── ai-features.md          # 检测模型与评分（索引）
│   ├── humanization.md         # 口语化策略
│   ├── formal-humanization.md  # 书面化策略
│   ├── iteration.md            # 迭代流程
│   ├── examples.md             # 更多前后对照
│   ├── detection-methods.md    # 检测器原理与局限
│   └── anti-aigc.md            # 薄索引（兼容旧引用）
├── scripts/
│   └── humanize_lint.py        # 双语体检器（纯标准库）
├── tests/
│   ├── test_lint.py            # 23 项自测
│   └── samples/                # 中英 AI/人类对照样本
└── references/
    └── ai-text-features-research.md
```

## 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| 1.0.0 | 2026-04-01 | 初版：AIGC 检测原理 + 六种反检测策略 |
| 1.4.0 | 2026-05-09 | 加安全规则、集成、性能、排查、边界情况 |
| 1.5.0 | 2026-10-04 | 新增寒暄开头、泛人称、口播腔、中英混杂四类 |
| 1.6.0 | 2026-10-04 | 新增段首短判断句 |
| 1.7.0 | 2026-10-04 | 新增否定-转折抖机灵/空话套话 |
| 1.8.0 | 2026-10-22 | 新增动作隐喻与版面痕迹，阈值来自 90 篇语料实测 |
| 2.0.0 | 2026-10-29 | 重构：中英双特征库（Z01–Z29 / E01–E25）、量化阈值与三套 profile、五遍改写协议、可执行体检脚本与 23 项自测、研究底稿；加入误杀边界与"不编细节"硬约束 |

## See Also

- `/简写`（brief-write）— 用户博客口吻的写作规范
- `/paper review`（academic-writer）— 学术语境的表达检查
- `/gongwen check`（official-document-writer）— 公文格式合规
- `/patent disclosure`（patent-writer）— 专利文本处理
- `/有据`（you-ju）— 防幻觉的事实审计，人化之前先做
