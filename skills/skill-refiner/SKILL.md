---
name: skill-refiner
version: "1.1.0"
description: |
  Skill refinement tool that iteratively polishes and improves any skill until it reaches optimal quality.

  Triggers when: Needing to improve an existing skill, polish skill documentation, optimize skill rules, or fix skill deficiencies.

  Commands:
  - /修炼 <技能名> - Refine a specific skill
  - /refine <skill> - Refine a specific skill (English)

  Capabilities: Deep analysis of skill deficiencies, improvement plan generation, iterative optimization until standards are met, testing to verify improvements, cultivation report generation
author: cycleuser
license: MIT
status: Beta
---

## Safety Rules

参见 [_shared/core/safety-rules.md](../_shared/core/safety-rules.md) — 所有安全规则从共享层加载。

# 修炼 (Skill Refiner)

技能修炼系统，对任意技能进行反复打磨改进，直到达到最优状态。

## Quick Commands

| Command | Description |
|---------|-------------|
| `/修炼 <技能名>` | Refine a specific skill |
| `/refine <skill>` | Refine a specific skill (English) |

## 修炼维度

对技能进行全方位审视，从以下维度进行改进：

### 1. 完整性 (Completeness)

检查项：
- SKILL.md 是否有完整的 YAML frontmatter
- 是否有清晰的功能描述
- 是否有使用示例
- 是否有规则文件支持
- 是否有配置选项说明

### 2. 可读性 (Readability)

检查项：
- 文档结构是否清晰
- 标题层级是否合理
- 是否有冗余内容
- 语言是否简洁明了
- 是否有错别字或语法错误

### 3. 实用性 (Practicality)

检查项：
- 是否解决了实际问题
- 规则是否可执行
- 示例是否真实可用
- 是否有边界情况处理
- 是否有错误处理指导

### 4. 一致性 (Consistency)

检查项：
- 命名风格是否一致
- 格式风格是否一致
- 与其他技能的风格是否统一
- 中英文版本是否对应

### 5. 可扩展性 (Extensibility)

检查项：
- 是否易于添加新规则
- 是否支持自定义配置
- 是否预留扩展接口

## 常见问题与排查

### 修炼未收敛
- **症状**: 反复修改多次但评分不提升
- **原因**: 改进策略不当，对同一缺陷重复尝试相同修复方法
- **解决**: 使用不同诊断维度重新分析；切换 `/修炼 <skill> --strategy alternative` 换策略

### 修炼过度优化
- **症状**: 技能评分高但实际使用效果差
- **原因**: 过度拟合评估指标，忽略实际可用性
- **解决**: 添加人工验收步骤；降低评估指标权重；增加场景测试

### 规则文件冲突
- **症状**: 修炼后某个规则被覆盖或丢失
- **原因**: 多个改进维度修改了同一文件
- **解决**: 使用 `/refine <skill> --merge` 合并冲突变更；按维度顺序执行避免并行修改

## 边界情况

- **空技能**: 目标技能只有SKILL.md无规则文件时，先创建规则文件再修炼
- **超大型技能**: 技能超过1000行时，使用 `--scope docs` 或 `--scope rules` 分别修炼
- **多语言技能**: 中英混合技能，评估时分别计算各语言部分得分
- **引用外部资源**: 技能引用了非标准路径的资源时，修炼前需要验证路径有效性
- **技能依赖链**: 如果技能A引用技能B，修炼A前需要确保B已达标

## AIGC检测意识

技能修炼报告的AIGC率评估是修炼的必要维度之一。修炼后的技能生成的文本必须通过AIGC检测。参见 `rules/anti-aigc.md` 了解流程文档的反AIGC规则。

核心要求：
- 评分必须附带具体改进点和证据：不写"可读性78→82"，写"可读性78→82（+4）：精简了SKILL.md从450行到380行"
- 不写"质量有所提升"，写具体的度量变化

## 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| 1.0.0 | 2026-04-01 | 初始版本，4维度诊断+迭代优化 |
| 1.1.0 | 2026-05-09 | 添加安全规则，边界情况，排查指南，rule文件名修正 |

## 修炼流程

四个阶段：诊断、方案、修炼、验证。

第一阶段：诊断
- 读取技能文件
- 分析各维度得分
- 识别主要缺陷
- 生成诊断报告

第二阶段：方案
- 针对缺陷生成改进方案
- 评估方案可行性
- 确定改进优先级
- 生成改进计划

第三阶段：修炼
- 按计划执行改进
- 重新评估各维度得分
- 检查是否达标
- 未达标则继续迭代

第四阶段：验证
- 模拟使用场景测试
- 检查改进效果
- 生成修炼报告
- 建议后续优化方向

## 评分标准

各维度评分说明（0-100）：

90-100分为优秀：该维度表现卓越，无需改进
80-89分为良好：该维度表现良好，可微调
70-79分为合格：该维度表现一般，建议改进
60-69分为较差：该维度有明显缺陷，必须改进
0-59分为不合格：该维度严重缺失，需重构

综合评分计算方式：
综合评分 = 完整性 × 0.25 + 可读性 × 0.20 + 实用性 × 0.30 + 一致性 × 0.15 + 可扩展性 × 0.10

达标标准：综合评分 ≥ 80，各维度评分 ≥ 70，无明显缺陷。

## 修炼策略

### 策略1：快速修炼

适用情况：时间有限，只需修复明显问题。

步骤：
1. 快速扫描，识别明显缺陷
2. 只修复关键问题
3. 简单验证后完成

### 策略2：标准修炼

适用情况：常规改进，提升整体质量。

步骤：
1. 全面诊断，生成详细报告
2. 制定改进计划
3. 逐项执行改进
4. 迭代验证，直到达标

### 策略3：深度修炼

适用情况：需要根本性改进。

步骤：
1. 深度分析，理解技能本质
2. 重新设计结构和规则
3. 全面重写或重构
4. 多轮迭代验证
5. 生成完整修炼报告

## 修炼报告模板

修炼报告格式：

修炼时间：{timestamp}
修炼模式：{快速/标准/深度}

诊断结果表格：维度、修炼前、修炼后、变化

主要改进：列出主要改进项

修改文件：列出修改的文件及修改说明

待优化项：列出未优化的项目

建议：后续建议

## 使用示例

### 示例1：标准修炼

用户输入：/修炼 humanizer

诊断阶段：正在分析 humanizer 技能，诊断结果为完整性85（良好）、可读性78（合格，文档过长建议精简）、实用性88（良好）、一致性72（合格，与其他技能风格不一致）、可扩展性80（良好）、综合81（达标但有改进空间）。

主要缺陷包括：SKILL.md 文档过长可读性不佳、规则文件命名不够规范、缺少快速上手指南。

方案阶段生成改进计划：精简 SKILL.md 提取核心内容、重命名规则文件统一命名规范、添加 Quick Start 章节、调整文档结构与其他技能对齐。

修炼阶段执行改进并验证效果。

### 示例2：深度修炼

用户输入：/修炼 power-iterate --depth deep

诊断阶段深度分析 power-iterate 技能，诊断结果为完整性90（优秀）、可读性75（合格，结构复杂理解门槛高）、实用性85（良好）、一致性80（良好）、可扩展性70（合格，扩展机制不够灵活）、综合80（达标）。

深层问题包括：自主执行机制不够完善、预算管理策略缺乏灵活性、错误处理机制不足、与其他技能的集成不够。

核心改进包括：重构自主执行循环增强决策能力、引入动态预算调整机制、完善错误处理和恢复策略、设计技能集成接口。

迭代执行重构自主执行循环、动态预算调整、错误处理机制、技能集成等四项改进，最终综合评分提升至89。

## Rules

- rules/diagnosis.md：诊断规则
- rules/improvement.md：改进策略
- rules/validation.md：验证方法
- rules/templates.md：模板库
- [rules/anti-aigc.md](rules/anti-aigc.md) - 流程文档反AIGC检测规则

## 配置选项

参数默认值说明：

depth：standard，修炼深度，可选 quick/standard/deep
target_score：80，目标综合评分
max_iterations：5，最大迭代次数
aspects：all，修炼维度，可选 all 或指定维度

## 相关技能

- `/skills` from **skill-manager** — 浏览技能注册表找到需要修炼的技能
- `/安检` from **an-jian** — 在部署修炼过的技能前执行安全审计