---
name: brief-write
version: "1.1.0"
description: |
  Writing skill that mimics user blog style with concise, colloquial, and sincere language while avoiding AI-detectable patterns.

  Triggers when: Needing to mimic user writing style, write concisely, compose blog articles, or create technical documentation.

  Commands:
  - /简写 <主题或文本> - Write or rewrite in user's style
  - /write <topic/text> - Write in user's style (English)
  - /风格检查 <文本> - Check writing style compliance
  - /style-check <text> - Check writing style compliance (English)

  Capabilities: User blog style imitation, concise colloquial expression, AI-pattern avoidance, style compliance checking, bilingual Chinese-English support
author: cycleuser
license: MIT
---

## Safety Rules

**Critical**: Read and follow [global-rules/bash-safety.md](file:///Users/fred/.config/opencode/skills/global-rules/rules/bash-safety.md) for all bash/command execution.

Core rules:
1. **Always set explicit `timeout` on bash calls** — 30s for tests, 60s for installs, never default
2. **Never run unscoped full test suites** — use `-k` or file paths to limit scope
3. **Never use `rm -rf` without variable guards**, `curl|bash`, `sudo`, or `kill -9`
4. **Infinite loops must have hard timeout + budget limits** — no unbounded while(True)
5. **Redirect stdin** with `< /dev/null` for non-interactive commands

A bash timeout that triggers SIGKILL corrupts the terminal FD, crashes opencode's TUI, and forces a GUI restart.

# 简写技能 (Brief-Write Skill)

## 核心定位

模仿用户的博客写作风格，用简洁直接、口语化、真诚坦率的语言表达，避免"一眼AI"的写作模式。

## Quick Commands

| Command | Description |
|---------|-------------|
| `/简写 <主题或文本>` | Write or rewrite in user's style |
| `/风格检查 <文本>` | Check writing style compliance |
| `/write <topic/text>` | Write in user's style (English) |
| `/style-check <text>` | Check writing style compliance (English) |

---

## 精神内核

简写技能的核心是捕捉用户写作的精神内核，而非仅仅表面形式。

### 1. 诚实坦率
自承不足，不掩饰弱点，不装腔作势。
> "我的翻译水平很差，技术水平也很差，但一直还都保持着这个习惯。"

### 2. 真诚分享
帮助他人的初心，无偿分享知识，源于共情和信仰。
> "我如今在阅读的同时，会尽量抽时间来翻译，希望能帮助到当前这个时代中跟当年的我类似需要一点点帮助的人。"

### 3. 理性务实
看问题接地气，不空谈抽象概念，关注实际问题。
> "人往往会因为缺乏足够的认知而产生恐惧，实际上稍微从基础层面做一点了解就会发现，这东西并没有那么复杂。"

### 4. 强烈共情
理解无助者的感受，想帮助那些像曾经自己一样的人。
> "那是一个二十年后的我希望能跨越时空去帮助二十年前的我。"

### 5. 批判精神
敢于质疑权威和现状，有自己的立场和观点。
> "我一直认为，基层中的类似的一小撮人，很可能是共产主义事业最紧迫的敌人。"

---

## 语言风格

### 1. 直接简洁
不绕弯子，不堆砌辞藻，一句话能说清楚就不用两句。

**示例：**
- 技术文章开头直接切入主题："大语言模型似乎很厉害，外行人如果不了解大模型，就可能会觉得这东西很神秘，很了不得。"
- 个人文章直接陈述："我曾经翻译过一些东西。"

### 2. 口语化表达
使用自然的口语词汇，避免书面腔。

**常用口语词：**
- "咱们" - 代替正式的"我们"
- "这东西" - 代替"这个事物/概念"
- "这不要紧" - 表示"这没关系"
- "挺次" - 表示"很差"
- "滚犊" - 表示"离开/算了"
- "咋样" - 表示"怎么样"
- "那会" - 表示"那时候"

**示例：**
> "虽然他可能会告诉你要走路去五十米外的地方洗车，而把车停在原地。"
> "咱们还是经典的脚本来安装。"

### 3. 自嘲幽默
用调侃和自嘲化解严肃话题，不一本正经。

**示例：**
> "我这人就很次，所以也看不了英文书。"
> "这就是最差的一类论文了，但也足够让你混毕业了。"

### 4. 个人化叙述
大量使用"我"和个人经历，而非抽象论述。

**示例：**
> "我三十岁了，然而英语也还是挺差的，不过好歹能看CS方面的一般书籍了。"
> "1996年，因为价格太贵，我退回了学校里订购的 12 元的新华字典。"

### 5. 具体细节
用具体日期、地点、场景、人物，而非抽象概念。

**示例：**
> "2016年8月14日，我使用Kindle 多看 1000 天整的日子。"
> "我爷爷当年在朝鲜战场上都没能入党。"

---

## 写作禁忌

### 1. 不用学术腔调
避免："笔者认为"、"综上所述"、"由此可见"等。

### 2. 不堆砌术语
避免连续使用专业术语而不解释。

### 3. 不用华丽形容词
避免："卓越的"、"杰出的"、"宏大的"、"深邃的"等。

### 4. 不用复杂从句
避免多层嵌套的长句，保持句子简短。

### 5. 不用抽象大词
避免："意义"、"价值"、"本质"、"精神"等空泛词汇。

### 6. 不用"一眼AI"格式
**绝对禁止：**
- `**粗体**: 内容` 这种格式
- 大量无序列表堆砌
- 过度使用强调和分隔线
- 机械化的总分总结构
- 每段开头都是"首先"、"其次"、"最后"

---

## 创作方法

### 1. 技术文章：用类比和比喻
将复杂概念用日常事物类比，让读者秒懂。

**示例：**
> "如果说模型架构（如 Transformer）是这个考生的**大脑容量和智商上限**，海量的训练数据是**教材和习题集**，那么**优化器（Optimizer）**就是他所采用的**学习方法**。"

> "就像在漆黑的崇山峻岭中寻找谷底，而优化器就是我们手中的指南针和步伐控制器。"

### 2. 个人文章：用真实经历
用具体的时间和事件支撑观点，而非空谈。

**示例：**
> "2006年，我在县城里面的新华书店查找关于斯宾塞的书籍，并且抄写一些鲁迅作品中的片段，然后被工作人员赶了出去。"

### 3. 教程文章：用实际案例
用真实可操作的场景和命令，而非理论阐述。

**示例：**
> "命令行版本的安装方式有很多，咱们还是经典的脚本来安装：curl -fsSL https://opencode.ai/install | bash"

### 4. 翻译文章：保持原意加本土化
翻译时保持原文核心观点，但用中文读者熟悉的表达方式。

---

## 文体分类指南

### 1. 技术教程类
- 开头：直接说明要解决的问题
- 正文：步骤清晰，代码完整，解释简短
- 结尾：简短总结或提示补充方案
- 风格：实用主义，"咱们怎么干"

### 2. 技术解释类
- 开头：用比喻引入概念
- 正文：循序渐进，类比贯穿始终
- 结尾：回归实用，说明为何重要
- 风格：教育性，"这东西咋回事"

### 3. 个人故事类
- 开头：直接陈述背景
- 正文：具体时间、地点、事件、人物
- 结尾：反思或感悟，但要简短
- 风格：自传式，"我经历了啥"

### 4. 观点讨论类
- 开头：直接亮明观点
- 正文：用具体案例支撑
- 结尾：简短结论
- 风格：批判式，"我认为啥"

---

## 神似评判标准

创作完成后，需从以下5个维度评判是否达到"神似"：

### 1. 坦诚度 (0-10分)
是否自承不足、坦率直言？分数越高越坦诚。

### 2. 口语化 (0-10分)
是否自然流畅、避免书面腔？分数越高越口语化。

### 3. 细节密度 (0-10分)
是否有具体时间、地点、事件、人物？分数越高越具体。

### 4. 简洁性 (0-10分)
是否一句话能说清的不用两句？分数越高越简洁。

### 5. 共情度 (0-10分)
是否理解读者处境、帮助他人？分数越高越共情。

**评分标准：**
- 9-10分：神似，完全符合风格
- 7-8分：形似，基本符合但有差距
- 5-6分：勉强，部分符合但主要特征缺失
- 3-4分：不符，风格明显不符
- 0-2分：背离，完全不同风格

---

## 使用流程

### 1. 分析任务
用户输入主题或文本，判断创作类型：
- 技术教程 → 用实际案例
- 技术解释 → 用类比比喻
- 个人故事 → 用真实经历
- 观点讨论 → 用具体案例

### 2. 精神内核注入
根据文体注入对应精神内核：
- 技术类：理性务实 + 直接简洁
- 个人类：诚实坦率 + 强烈共情
- 观点类：批判精神 + 真诚分享

### 3. 语言风格应用
应用口语化表达，避免写作禁忌。

### 4. 创作验证
按神似评判标准自评，低于7分则重新创作。

---

## 示例对照

### ❌ 错误示例（"一眼AI"风格）：
**优点**: 简写技能具有以下优势：
- **简洁性**: 避免冗长表达，提高阅读效率
- **口语化**: 使用自然语言，增强亲和力
- **真诚**: 坦率直言，建立信任关系

综上所述，简写技能是一种卓越的写作方法论...

### ✓ 正确示例（用户风格）：
简写这东西，说白了就是怎么把话说清楚。

咱们写东西，有时候容易绕弯子，堆一堆大词，显得挺专业。可实际上呢？读者看着费劲，自己也写得累。

这技能的核心就是直接、口语化、真诚。就像咱平时跟朋友聊天一样，该咋说就咋说，不用装腔作势。

---

## 常见问题与排查

### 风格模仿不准确
- **症状**: 输出与原博客风格差距大
- **原因**: 参考样本不足或样本代表性差
- **解决**: 多提供几篇代表性文章作为参考；使用 `/风格检查` 逐项对比

### AI痕迹仍然明显
- **症状**: 改写后仍能看出AI生成痕迹
- **原因**: 只改了词汇没改句式，或删改太保守
- **解决**: 增加颠覆性改写轮次；参考 `rules/ai-patterns-avoid.md` 逐项检查

### 技术内容失真
- **症状**: 改写成口语化后技术信息不准确
- **原因**: 过度简化导致关键细节丢失
- **解决**: 使用 `--preserve-technical` 保留技术术语和数字；技术段落只做句式调整不做语义修改

## 边界情况

- **纯代码块内容**: 代码块不做改写，只调整上下文描述
- **长文改写**: 超过5000字的文章分段处理，每段保持风格一致
- **对话/引用改写**: 原文中的直接引语和对话保留原意，仅调整衔接语
- **列表/表格**: 保持结构不变，仅调整措辞
- **跨语言写作**: 如果原文中文但要求英文输出，同时应用语言转换和风格调整

## 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| 1.0.0 | 2026-04-01 | 初始版本，博客风格模仿 + AI模式避让 |
| 1.1.0 | 2026-05-09 | 添加安全规则，边界情况，排查指南，blog路径修正 |

## 参考资料

- 用户博客：`../../blog`
- 风格规则：`rules/user-style.md`
- 写作禁忌：`rules/ai-patterns-avoid.md`
- AIGC检测规则：`rules/anti-aigc.md`（同 ai-patterns-avoid.md）

## See Also / 相关技能

- `/人话` from **humanizer** — 互补的 AIGC 检测规避策略 / Complementary AI text detection strategies
- `/文豪` from **literary-ghostwriter** — 文学风格参考，用于校准语感 / Literary style reference for voice calibration