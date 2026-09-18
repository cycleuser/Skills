---
name: you-ju
version: "1.0.0"
description: |
  有据 (Grounded Generation) — 防幻觉的严格转述技能。在知识库检索、网页搜索、
  文档整合的每一步生成中，强制执行"闭世界"约束：输出中的每个实体、数字、
  因果关系必须能在给定来源中逐字或近逐字找到对应；禁止新增实体、新增数字、
  新增逻辑关系。每步生成后运行 grounded 审计，幻觉检出即退回重写。

  Triggers when: 检索增强生成 (RAG)、总结多份文档、写文献综述/调研报告、
  转述网页内容、向用户汇报搜索结果、整合知识库片段，或任何"内容必须严格
  忠于来源"的场景；也用于对已有输出做幻觉审计。

  Commands:
  - /有据 <任务> - 以严格有据模式执行检索/整合/转述任务
  - /有据 审计 <输出> [来源目录] - 对已有输出做幻觉审计
  - /有据 对照 <输出> <来源> - 逐句对齐输出与来源，标记无据句
  - /有据 实验 - 运行基线vs受控对照实验（见 tests/）
  - /grounded <task> - English command
  - /grounded audit <output> [sources] - Audit existing output
  - /grounded experiment - Run baseline vs controlled comparison

  Capabilities: 闭世界约束（实体/数字/关系三类白名单）、三步一审计
  （检索后/生成中/交付前）、逐句引用溯源（[A:L12] 句级标注）、无据句
  降级处理（删除或显式标注"来源未提及"）、脚本化实体/数字泄漏检测
  （ground_check.py）、基线vs受控 A/B 对照实验框架
author: cycleuser
license: MIT
status: Beta
---

## Safety Rules

参见 [_shared/core/safety-rules.md](../_shared/core/safety-rules.md)

关键补充：ground_check.py 为只读脚本，仅检测不修改；审计报告写入新文件，不覆盖原输出。

# 有据 (Grounded Generation)

防幻觉的严格转述技能。核心主张：**幻觉不是靠"小心"避免的，是靠"每步审计+无据即删"的机制避免的。**

The one rule that matters: **输出中的每个实体、每个数字、每条逻辑关系，都必须能在来源中找到出处；找不到的，删掉或显式标注"来源未提及"，绝不润色进去。**

## Quick Commands

| Command | 说明 / Description |
|---------|-------------|
| `/有据 <任务>` | 严格有据模式执行检索/整合/转述 / Run task in grounded mode |
| `/有据 审计 <输出> [来源目录]` | 对已有输出做幻觉审计 / Audit existing output for hallucinations |
| `/有据 对照 <输出> <来源>` | 逐句对齐标记无据句 / Sentence-level alignment |
| `/有据 实验` | 基线vs受控对照实验 / Run baseline vs controlled experiment |
| `/grounded <task>` | Full English workflow |
| `/grounded audit <output> [sources]` | Audit existing output |
| `/grounded experiment` | Run comparison experiment |

## 核心理念 / Core Philosophy

幻觉的三个来源，对应三类可检测的违规：

1. **实体增加**。来源说"星尘-3 采用 12nm 工艺"，输出写成"星尘-3 采用台积电 12nm 工艺"——"台积电"是凭空补出的实体。人类写作者会自动补全"显然"的背景，这就是幻觉的第一来源。
2. **数字增加**。来源没给 FP16 算力，输出"补全"了一个"典型值"。数字幻觉最危险：看起来最精确，编造得也最顺口。
3. **逻辑关系增加**。来源只并列陈述 A 和 B，输出写成"因为 A 所以 B"或"A 优于 B"。来源未做的推断都算幻觉，哪怕推断本身"很可能对"。

三条铁律：

1. **闭世界运行**。生成期间，世界只包含本次任务给定的来源。来源没提的事，不是"未知"，是"不存在"。需要外部事实时必须先检索并把新来源加入白名单，再继续。
2. **三步一审计**。检索后、每次生成后、交付前各跑一次审计（见 rules/audit-protocol.md）。幻觉检出即退回重写该句，不是"下次注意"。
3. **句句可溯源**。输出中每个断言后附句级引用标记（`[A:L12]` = 源文档 A 第 12 行）。审计脚本按标记回查，无标记且无据的句子按幻觉处理。

## 工作流 / Workflow

```
Step 0  建立来源清单 Manifest
   1) 列出本次任务允许引用的全部来源（文件路径/URL/检索结果）
   2) 记录每个来源的编号（A/B/C…）——后续引用标记用编号
   3) 用 ground_check.py entities 建立"实体白名单+数字白名单"
   4) 之后任何新检索结果必须先登记编号才可引用

Step 1  检索（带记录的检索）
   1) 每次检索记录：关键词、来源、命中文档、命中文档的编号
   2) 检索结果只做两件事：登记为新来源编号；或丢弃
   3) 检索后即跑第一次审计：确认引用计划中每条断言都能定位到来源行

Step 2  生成（闭世界转述）
   1) 只做三类操作：压缩（合并来源中相邻信息）、换序（按用户需要的
      结构重排）、同义改写（不引入新实体/新数字/新关系）
   2) 每个断言句尾写引用标记 [编号:行号]
   3) 来源明确写"未提供/未覆盖/未定"的问题：转述为"来源未提及"，
      禁止补全。这是最高频的幻觉触发点
   4) 用户问的问题超出语料：明确回答"本次来源未覆盖"，不猜测

Step 3  生成后审计（逐句）
   1) ground_check.py check <输出> --sources <来源...>：
      - 实体检查：输出实体是否都在白名单内
      - 数字检查：输出数字是否都在数字白名单内
      - 引用检查：每个 [A:L12] 标记回查源文档该行，确认断言确实在该行
      - 覆盖检查（可选）：来源要点是否被输出覆盖
   2) 违规句处理：删除该句 → 重写（只允许用来源内容）→ 再审计
   3) 最多 3 轮，仍有违规则整段降级为"带引号的原文摘录"

Step 4  交付前审计
   1) 重跑完整 check，全绿才交付
   2) 汇报顺序：①结论（全部有据）②来源清单 ③审计结果（检出并修复了什么）
   3) 输出必须携带"来源未覆盖"清单：哪些子问题因语料不足未回答
```

## 三类违规的判定 / Violation Taxonomy

详见 [rules/grounding-rules.md](rules/grounding-rules.md)

| 类型 | 定义 | 例（源：星尘-3 为 12nm，8 TOPS） | 判定 |
|------|------|------|------|
| E1 实体增加 | 输出含来源没有的命名实体 | "台积电 12nm 工艺" | E1 |
| N1 数字增加 | 输出含来源没有的数值 | "FP16 算力 4 TOPS" | N1 |
| R1 关系增加 | 输出含来源没有的因果/比较/时序 | "能效优于竞品" | R1 |
| Q1 越权回答 | 来源明说"未提供"，输出了答案 | 来源:"FP16 数值未给出"→输出给值 | Q1 |
| C1 引用失配 | 引用标记指向的行不含该断言 | 断言标 [A:L12] 但 L12 无此内容 | C1 |

注意边界：**同义改写不是幻觉**（"功耗 2.1 W"→"典型功耗为 2.1 瓦"合法）；
**合并不是幻觉**（来源 A、B 各说一半，合并陈述且双引用合法）；
**删减不是幻觉**。判定只看三样：实体、数字、关系是否可溯源。

## 审计协议 / Audit Protocol

详见 [rules/audit-protocol.md](rules/audit-protocol.md)

三步一审计的时间点、每步的检查项、违规句的降级处理流程。

## 校验脚本 / Verification Script

[scripts/ground_check.py](scripts/ground_check.py) — 只读检测工具：

```bash
# 建立白名单（从语料提取实体与数字）
python3 ground_check.py whitelist <来源目录> -o whitelist.json

# 审计：实体泄漏 + 数字泄漏 + 引用标记回查
python3 ground_check.py check <输出.md> --whitelist whitelist.json [--sources a.md b.md]

# 逐句对照：输出每句标注 有据/无据
python3 ground_check.py align <输出.md> <来源...>
```

脚本只覆盖**机械可判定**的违规（E1/N1/C1）。R1（关系增加）与 Q1（越权回答）
需人工/模型审计，脚本给出疑似句候选。

## A/B 对照实验 / Baseline vs Controlled Experiment

本技能是否有效，用可复现实验回答，不靠感觉。详见
[rules/ab-experiment.md](rules/ab-experiment.md) 与
[tests/](tests/) 目录：

```
实验设计（闭世界语料，虚构实体，幻觉可精确判定）
  组1 baseline：同样的检索材料，不加任何约束，正常生成
  组2 grounded：同样的检索材料，按本技能协议生成
  评测：ground_check.py 对两组跑同一套检查
  指标：E1 实体泄漏数、N1 数字泄漏数、Q1 越权回答数、句级有据率
结果：见 test/you-ju.md（本仓库测试报告）
```

## Rules

- [rules/grounding-rules.md](rules/grounding-rules.md) - 三类违规定义与边界案例
- [rules/audit-protocol.md](rules/audit-protocol.md) - 三步一审计的完整流程
- [rules/ab-experiment.md](rules/ab-experiment.md) - 对照实验设计与指标
- [rules/anti-aigc.md](rules/anti-aigc.md) - 审计报告的反AIGC规则

## 使用示例 / Examples

### 示例 1：有据模式总结文档

```
用户/User: /有据 总结 tests/corpus 里三份文档的关键规格

→ Step 0: 来源清单 A=source_A.md B=source_B.md C=source_C.md
→ Step 2: 生成，句句带 [A:L..] 标记；FP16 算力一句写"来源未提及"
→ Step 3: ground_check.py check 全绿（0 实体泄漏 0 数字泄漏）
→ 交付：总结 + 来源未覆盖清单（FP16 算力、价格、级联方案）
```

### Example 2: Audit an existing summary

```
用户/User: /grounded audit summary.md --sources source_A.md

→ 实体检查: "台积电" 不在白名单 → E1 违规（第3句）
→ 数字检查: "4 TOPS" 不在数字白名单 → N1 违规（第5句）
→ 引用检查: [A:L12] 实际指向功耗行，断言是算力 → C1 违规
→ 输出审计报告：3 处违规，逐条给出证据行号与修复建议
```

### 示例 3：越权问题处理

```
用户/User: 星尘-3 和隔壁家芯片比怎么样？

→ 语料无任何竞品信息（三份文档均未提及竞品）
→ 闭世界规则：不检索就不存在竞品；用户未要求联网检索
→ 回答："本次三份来源文档未包含任何竞品信息，无法对比。"
→ 禁止行为：凭训练知识补充"隔壁家"的参数——哪怕全对也是违规
   （本次任务的输出只能由来源支撑，不能由模型记忆支撑）
```

## 边界情况 / Edge Cases

- **用户主动要求外推**：明确说"请基于常识推测"时，退出闭世界模式，但推测段必须整体显式标注"以下为来源外推测"，且推测段不参与有据审计。
- **来源之间冲突**：列出冲突双方各自的出处（编号:行号），不静默选择，不调和出一个"中间值"——调和出的值必然无据。
- **同义实体**："星尘-3"与"星尘 3 号"按同一实体处理（白名单支持别名行，见 ground_check.py 注释）；数字单位换算（"2100 mW" vs "2.1 W"）算等价，脚本按归一化后的值比对。
- **引用标记错位**：内容正确但 [A:L12] 行号错 → C1 违规，修标记不算修内容，审计仍记一次。
- **检索引入新实体**：新检索结果登记编号后才可引用；未登记就引用按 E1 处理。
- **输出语言转换**：中文输出译自英文来源时，专名保留原文并加译名，数字不变；译文专名不在白名单时用别名机制登记。

## 常见问题排查 / Troubleshooting

- **check 报大量实体泄漏但内容看着没错** → 白名单未包含别名或新登记的检索来源；先补白名单再重跑，不要直接改输出。
- **引用标记太密影响阅读** → 段落级合并标记（[A:L12-15]）合法；但一个标记最多覆盖来源中连续的 5 行，防止"大引用刷白"。
- **脚本对关系类问题无能为力** → R1/Q1 必须模型自审；SKILL.md Step 3 中人工审计不可跳过。
- **对照组跑出来 grounded 也有泄漏** → 检查是否漏跑了 Step 3 的第 2 轮重写；单轮生成不构成完整的受控条件。

## 配置选项 / Configuration

| 参数/Param | 默认值/Default | 说明/Description |
|-----------|---------------|-----------------|
| strictness | strict | strict=无据即删 / lenient=无据标注保留 |
| citation_style | [编号:行号] | 句级引用标记格式 |
| max_rewrite_rounds | 3 | 违规句最大重写轮数 |
| quote_fallback | true | 3 轮重写仍违规时降级为原文引号摘录 |
| spec_gap_report | true | 交付时附带"来源未覆盖"清单 |

## 集成 / Integration

```
/学术导览 academic-guide
    ↓ 引用验证通过后，正文转述用 /有据 约束
/盘点 inventory-report
    ↓ 多源汇总的"一段话总结"按有据模式生成
/先验证 verify-deliver
    ↓ 交付前审计中的"内容正确性"检查由本技能审计协议承担
/humanizer
    ↓ 人化改写后重跑本技能审计，防止改写引入新实体
```

## Anti-Patterns

| 违规 / Violation | 严重度 / Severity | 后果 / Consequence |
|------|--------|------|
| 生成时不建来源清单直接开写 | 高/High | 无溯源基准，审计无从下手 |
| 引用标记只标文档不标行号 | 高/High | 回查不可行，等于没标 |
| 来源说"未提供"仍补了答案 | 严重/Critical | Q1 越权回答，最高频幻觉 |
| 用训练记忆补语料外常识 | 严重/Critical | 输出脱离来源，闭世界被破坏 |
| 审计出违规只改一处不重跑 | 高/High | 修复引入新违规未检出 |
| 把同义改写误判为幻觉删掉 | 中/Medium | 过度删减，信息损失 |
| 推测段未显式标注混入正文 | 高/High | 读者无法区分有据与推测 |

## AIGC检测意识 / AIGC-Aware Output

审计报告必须给出具体违规类型、句位置、证据行号，不写"存在幻觉风险"。参见 [rules/anti-aigc.md](rules/anti-aigc.md)。

核心要求：
- 不写"检测到一些幻觉"，写"E1×2、N1×1：第3句'台积电'无据（白名单无此实体），第5句'4 TOPS'无据，第7句 [A:L12] 引用失配（L12 实为功耗行）"
- 对照实验结论必须带数字："baseline E1=4 N1=2，grounded E1=0 N1=0"，不写"有明显改善"

## 版本历史 / Version History

| 版本 | 日期 | 变更 |
|------|------|------|
| 1.0.0 | 2026-09-12 | 初始版本：闭世界约束、三步一审计、句级溯源、ground_check.py、A/B 对照实验框架与虚构语料测试 |

## See Also / 相关技能

- `/先验证` from **verify-deliver** — 交付前验证总协议，本技能承担其中"内容正确性"的来源一致性检查
- `/学术导览` from **academic-guide** — 引用链接验证；链接可用性归它管，链接内容的转述忠实性归本技能
- `/盘点` from **inventory-report** — 多源盘点，其"一段话总结"应按本技能有据模式生成
- `/人话` from **humanizer** — 人化改写降低 AIGC 率；改写后需重跑本技能审计防止引入新实体
- `_shared/core/anti-aigc.md` — 共享反AIGC规则（数字优先/理由优先），与本技能的数字白名单互补