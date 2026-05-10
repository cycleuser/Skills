---
name: humanizer
version: "1.4.0"
description: |
  AI text humanizer that rewrites AI-generated content into natural human language based on AIGC detection countermeasures.

  Triggers when: Needing to reduce AIGC detection rates, rewriting AI-generated content into natural language, optimizing text to sound more human-written, or performing humanization polish on AI text.

  Commands:
  - /人话 <文本> - Humanize text
  - /人话 --style formal <文本> - Humanize in formal style
  - /人话 --style casual <文本> - Humanize in casual style
  - /humanize <text> - Humanize AI-generated text (English)
  - /detect <文本> - Detect AIGC features in text
  - /demo - Generate high-AIGC example and demonstrate processing

  Capabilities: AIGC detection countermeasures, identifying AI-typical patterns, multi-round iterative AIGC rate reduction, preserving original meaning and logic, supporting both casual and formal styles, bilingual Chinese-English text processing
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

# 人话 (Humanizer)

AI文本人化处理技能，基于AIGC检测原理，将AI生成文本转化为自然人类语言。

## Quick Commands

| Command | Description |
|---------|-------------|
| `/人话 <文本>` | Humanize text |
| `/人话 --style formal <文本>` | Humanize in formal style |
| `/人话 --style casual <文本>` | Humanize in casual style |
| `/humanize <text>` | Humanize AI-generated text (English) |
| `/detect <文本>` | Detect AIGC features in text |
| `/demo` | Generate high-AIGC example and demonstrate processing |

## AIGC检测原理与反检测策略

### 主流检测方法

AIGC检测器主要基于以下原理工作：

困惑度 (Perplexity)：AI倾向于选择概率最高的词，困惑度低。人类写作困惑度高，会使用意外的词汇。AI文本困惑度低，用词"安全"、"正确"。

突发性 (Burstiness)：人类写作的句子长度和复杂度变化大。人类写作长短句穿插，节奏跳跃。AI文本句子长度均匀，节奏平稳。

词汇分布 (Token Distribution)：AI偏好常见词，人类会用更丰富的词汇。人类写作词汇多样，有生僻词、口语词。AI文本词汇集中在高频区域。

句式模式 (Sentence Pattern)：AI句式结构更规整、对称。人类写作句式多变，有倒装、省略、插入语。AI文本句式工整，主谓宾结构稳定。

过渡词频率 (Transition Words)：AI过度使用正式过渡词。人类写作过渡自然，少用"首先其次"。AI文本过度依赖"首先、其次、综上所述"。

内容深度 (Content Depth)：AI内容停留在概念层面。人类写作有具体案例、数据、个人经历。AI文本概念罗列，缺乏具体细节。

### 反检测策略总表

检测维度：AI特征 → 反检测策略

困惑度：用词安全、常见 → 使用意外的词汇、生僻词、口语词
突发性：句子长度均匀 → 长短句穿插，制造节奏变化
词汇分布：高频词为主 → 引入低频词、专业术语、俚语
句式模式：结构规整对称 → 打破对称，用倒装、省略、插入语
过渡词频率：高频使用 → 删除或替换为自然过渡
内容深度：概念空洞 → 加入具体数据、案例、细节

## 反检测详细策略

### 策略1：提高困惑度

原理：AI倾向于选择最可能的词汇，困惑度低。人类会使用"意外"的词汇。

操作方法：用具体词汇替换抽象词汇、用口语词替换书面词、用意外表达替换"正确"表达、加入个人感受和判断。

困惑度提升词汇表示例：

AI常用词 → 人化替换词
实现 → 搞定、弄成、跑通
进行 → 干、做、弄
具有 → 有、带着、有着
能够 → 可以、能、搞得定
提供 → 给、贡献、递过来
需要 → 得、必须、少不了

### 策略2：增加突发性

原理：AI句子长度均匀，人类长短句穿插。

操作方法：合并短句成长句、拆分长句成短句、加入极短的判断句（3-8字）、制造节奏变化。

突发性增强模式：

模式1：长句 + 短判断
...（30字以上的长句）。这就是问题所在。
...（复杂论述）。很难。

模式2：短句 + 解释
为什么？因为...
核心是什么？是...

模式3：多短句连击
这事不简单。涉及面广。利益盘根错节。

### 策略3：丰富词汇分布

原理：AI词汇集中，人类词汇多样。

操作方法：引入专业术语、引入口语词/俚语、引入方言或网络用语、避免重复用词。

### 策略4：打破句式模式

原理：AI句式工整，人类句式多变。

操作方法：使用倒装句、使用省略句、加入插入语、使用问句。

句式变换模式：

原句：A具有B的特点

变换1（倒装）：B，这是A的典型特征
变换2（省略）：A？B是肯定的
变换3（插入）：A，在我看来，具有B的特点
变换4（问句）：A有什么特点？B

### 策略5：删除/替换过渡词

原理：AI过度使用正式过渡词。

AI过渡词： 首先，...其次，...最后，... 一方面，...另一方面，... 综上所述，...

人化过渡：（删除"首先"，直接开始）再说一点：...还有个问题是...说到底，...关键在于，...

过渡词替换表：

AI过渡词 → 人化替代
首先 → （删除）
其次 → 再说一点、另外
最后 → 最后一点、补充一句
综上所述 → 说到底、归根结底
一方面...另一方面 → 先说...再说...、...但...

### 策略6：增加内容深度

原理：AI内容空洞，人类内容具体。

操作方法：加入具体数字、加入具体案例、加入具体时间/地点、加入个人观察。

深度增强检查清单：

是否有具体数字？
是否有具体案例？
是否有对比数据？
是否有个人判断？
是否有反面观点？

## "一眼AI"特征库

### 最典型的"一眼AI"模式

这些模式几乎100%表明是AI生成：

#### 模式1：加粗标题+冒号+相似句式

AI典型写法示例：

**其一，信息来源分散。** 用户在多个网站、APP之间反复切换，时间成本高企。

**其二，语言障碍突出。** 小语种信息的获取与理解，对普通用户而言几乎不可能。

**其三，处理能力有限。** 海量信息涌入后，提炼核心观点需要大量时间。

问题分析：加粗格式过于整齐、"其一、其二、其三"机械过渡、每句结构高度相似、冒号后的句子长度相近。

人化处理后：

用户面临的第一个问题是信息来源分散——在不同网站和APP之间来回切换，时间成本相当高。语言障碍也不容忽视，小语种信息普通人根本看不懂。至于处理能力，海量信息涌入后想提炼核心观点，确实需要花不少时间。

#### 模式2："首先...其次...最后..."机械三段论

AI典型写法示例：

首先，从技术角度来看，人工智能具有强大的数据处理能力。
其次，从应用层面分析，AI已经渗透到各行各业。
最后，从发展趋势预测，人工智能将成为未来的核心技术。

人化处理后：

人工智能最核心的优势是数据处理能力。这一点在各行各业的应用中已经得到验证——医疗、金融、制造，几乎没有AI涉足不到的领域。更值得期待的是其发展潜力，AI很可能成为下一轮技术革命的核心引擎。

#### 模式3："一方面...另一方面..."对称结构

AI典型写法示例：

一方面，区块链技术具有去中心化、不可篡改等优势；另一方面，其扩展性和性能问题仍是亟待解决的挑战。

人化处理后：

区块链的去中心化和不可篡改性确实是其核心优势。但问题也很明显——扩展性和性能瓶颈一直没解决。

#### 模式4："综上所述/总而言之"总结句

AI典型写法示例：

综上所述，人工智能技术的发展前景广阔，但同时也面临诸多挑战。我们需要在推动技术创新的同时，关注其潜在风险。

人化处理后：

AI的发展前景值得期待，但风险同样不可忽视。关键在于如何在创新和风险之间找到平衡——这不是技术问题，而是治理问题。

## 处理流程

输入文本 → "一眼AI"检测 → 风格判断 → 策略选择 → 迭代优化 → 输出结果+报告

"一眼AI"检测：检测加粗标题+冒号、其一其二其三、首先其次最后、句式重复度等特征。

风格判断：确定口语化还是书面化。

策略选择：根据检测结果和风格选择改写策略。

迭代优化：多轮迭代直到达到目标AIGC率。

输出结果：展示改写前后对比和详细报告。

## 处理示例

### 示例1：打破"其一其二其三"

输入（AI率98%）：**其一，信息来源分散。** 用户在多个网站、APP之间反复切换，时间成本高企。**其二，语言障碍突出。** 小语种信息的获取与理解，对普通用户而言几乎不可能。**其三，处理能力有限。** 海量信息涌入后，提炼核心观点需要大量时间。

处理步骤：删除加粗和"其一其二其三"、打散句式结构、用口语化表达、有详有略。

输出（AI率25%）：用户面临的第一个问题是信息来源分散——在不同网站和APP之间来回切换，时间成本相当高。语言障碍也不容忽视，小语种信息普通人根本看不懂。至于处理能力，海量信息涌入后想提炼核心观点，确实需要花不少时间。

### 示例2：打破"首先其次最后"

输入（AI率95%）：首先，从技术角度来看，人工智能具有强大的数据处理能力。其次，从应用层面分析，AI已经渗透到各行各业。最后，从发展趋势预测，人工智能将成为未来的核心技术。

输出（AI率22%）：人工智能最核心的优势是数据处理能力。这一点在各行各业的应用中已经得到验证——医疗、金融、制造，几乎没有AI涉足不到的领域。更值得期待的是其发展潜力，AI很可能成为下一轮技术革命的核心引擎。

### 示例3：删除"综上所述"

输入（AI率92%）：综上所述，人工智能技术的发展前景广阔，但同时也面临诸多挑战。我们需要在推动技术创新的同时，关注其潜在风险。

输出（AI率20%）：AI的发展前景值得期待，但风险同样不可忽视。关键在于如何在创新和风险之间找到平衡——这不是技术问题，而是治理问题。

### 示例4：替换空洞套话

输入（AI率89%）：数字经济的发展对传统产业转型具有深远意义。它不仅提供了新的技术手段，也推动了商业模式的创新。

输出（AI率18%）：数字经济正在重塑传统产业。这不是简单的技术升级，而是商业模式的根本变革。那些还在观望的企业，恐怕很快就会发现已经掉队了。

## 书面化人化五原则

1. 有取舍：不追求全面，聚焦核心问题
2. 有立场：敢于表达判断，有明确观点
3. 有分析：提出问题，剖析本质
4. 有证据：引用具体数据、案例、研究
5. 有痕迹：展现推理过程，承认不确定性

## Integration with Other Skills / 与其他技能集成

- Use `/paper new <topic>` and `/paper cite` from **academic-writer** when humanizing academic content. Feed academic drafts through `/humanize` to remove AI patterns while preserving scholarly tone.
- Use `/简写 <text>` from **brief-write** for complementary style-aware writing. After humanization with `/人话`, pipe to `/简写` for the user's concise, direct blog style.
- Use `/gongwen check <document>` from **official-document-writer** for official document humanization. Review 公文 with `/gongwen check`, then apply `/人话 --style formal` to reduce AIGC markers while maintaining GB/T 9704-2012 compliance.
- Use `/patent disclosure <invention>` from **patent-writer** for patent-related text humanization. Run `/detect` on patent drafts to identify AI patterns, then `/人话` to humanize while preserving technical precision.

## Rules

- rules/ai-features.md：AI文本特征识别规则
- rules/humanization.md：口语化人化策略
- rules/formal-humanization.md：书面化人化策略
- rules/iteration.md：迭代优化流程
- rules/examples.md：更多示例和案例
- rules/detection-methods.md：AIGC检测方法总结

## 配置选项

参数默认值说明：

target_rate：30，目标AIGC率(%)
style：auto，风格选择，可选 auto/formal/casual
max_iterations：10，最大迭代次数
preserve_meaning：true，保留原文语义
language：auto，语言选择，可选 auto/zh/en

## 性能与资源管理

### 批量处理优化
- **分段处理**：对于长文本，分段进行人化处理而不是一次性处理整个文档
- **批量大小**：每次处理500-1000字符的段落，平衡效率和质量
- **缓存利用**：对于相同或相似文本段落，缓存已处理结果

### 迭代效率
- **早期停止**：当AIGC率改善低于1%时提前停止迭代
- **增量改进**：每次迭代专注于解决最主要的AI特征，而不是全面重写
- **智能重试**：如果某段文本多次迭代仍无法降低AIGC率，则跳过并标记

### 资源管理
- **内存优化**：处理大文档时，及时释放中间结果的内存
- **超时控制**：每个文本段落的处理设置最大时间限制
- **并发控制**：批量处理时限制并发数量，避免资源竞争

## 使用示例 / Usage Examples

```
/人话 "人工智能技术正在深刻改变我们的生活方式，从智能家居到自动驾驶，AI 的应用无处不在。"
/humanize "The implementation of machine learning algorithms has significantly improved the efficiency of data processing pipelines."
/人话 --style formal "本文提出了一种基于深度学习的新型图像识别方法，在多个基准数据集上取得了最优性能。"
/detect "Furthermore, it is noteworthy that the aforementioned methodology demonstrates considerable efficacy."
/demo
```

## 常见问题与排查 / Troubleshooting

### AIGC率不降反升 / AIGC rate increases after humanization
- **症状/Symptom**: 人化处理后检测率反而升高 / Detection rate rises after humanization
- **解决/Fix**: 过度修改可能引入新的AI模式；减少 `max_iterations` 至3轮；使用 `--style casual` 增加变化幅度；检查是否替换成了另一个AI模型的特征词

### 语义被改变 / Original meaning altered
- **症状/Symptom**: 人化后技术内容不准确 / Technical content inaccurate after humanization
- **解决/Fix**: 设置 `preserve_meaning: strict` 严格保留关键术语；技术类段落使用 `--style formal` 减少改动幅度；使用 `/detect` 逐段检查而非全文

### 长文本处理超时 / Long text processing timeout
- **症状/Symptom**: 超过5000字的文本人化处理超时 / Text >5000 chars times out
- **解决/Fix**: 分段处理，每段500-1000字；使用 `/人话 --batch` 批处理模式；增加 `max_iterations: 5` 减少迭代次数

## 边界情况 / Edge Cases

- **代码块处理**: 代码块完全保留原样，不执行任何人化处理
- **数学公式**: LaTeX公式保留原样，仅人化周围说明文字
- **多语言混合文本**: 中英混合文本分别用两种策略处理；标注语言边界
- **引用/对话**: 直接引语和对话保持原样，不改变引用内容
- **敏感内容**: 医疗、法律、金融专业术语保持不动，仅调整表达方式
- **最大保留模式**: 如果文本本身AIGC率低于 `target_rate`，不执行任何修改并标注"已达目标"

## 版本历史 / Version History

| 版本 | 日期 | 变更 |
|------|------|------|
| 1.0.0 | 2026-04-01 | 初始版本，AIGC检测和基础人化处理 |
| 1.4.0 | 2026-05-09 | 添加安全规则，集成，性能管理，示例，排查，边界情况，6个rule文件 |

## See Also / 相关技能

- `/简写` from **brief-write** — 带反AI模式的博客风格写作 / Blog-style writing with anti-AI patterns
- `/paper review` from **academic-writer** — 学术语境中的 AIGC 检测 / AIGC detection in academic context
- `/gongwen check` from **official-document-writer** — 人化处理公文文本 / Humanize official documents
- `/patent disclosure` from **patent-writer** — 人化处理专利描述 / Humanize patent descriptions