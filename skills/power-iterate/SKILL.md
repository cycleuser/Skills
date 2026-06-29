---
name: power-iterate
version: "2.1.0"
description: |
  Fully autonomous continuous iteration skill that works until time or token budget is exhausted.

  Triggers when: User requests power iteration, continuous development, uninterrupted work, or sets explicit time or token budgets.

  Commands:
  - /强力迭代 <任务> [预算] - Start power iteration
  - /power-iterate <task> [budget] - Start power iteration (English)

  Capabilities: Fully autonomous decision-making without user confirmation, automatic requirement understanding and evaluation design, automatic iteration path planning, time/token budget management, periodic progress reporting
author: cycleuser
license: MIT
status: Beta
---

## Safety Rules

参见 [_shared/core/safety-rules.md](../_shared/core/safety-rules.md) — 所有安全规则从共享层加载，避免跨技能重复维护。

## Quick Commands

| Command | Description |
|---------|-------------|
| `/强力迭代 <任务> [预算]` | Start fully autonomous power iteration |
| `/power-iterate <task> [budget]` | Start power iteration (English) |

# Power Iterate 强力迭代 v2.1

全自主持续迭代技能。自动理解需求、自动设计评估、自动规划迭代、自主执行直到预算耗尽。

## 核心原则：先做再说

### 四不原则

不询问：遇到选择立即用最佳实践决定，不等待用户。
不澄清：需求不明确时自行假设并标注，标注"[假设]"。
不中断：遇到错误记录并继续，不卡住。
不汇报中间过程：只在每5个任务或5分钟时汇报进度。

### 决策优先级

安全第一：选择最安全、最标准的实现方式。
简洁优先：简单方案优于复杂方案。
增量验证：每完成一个模块立即验证。
记录一切：所有假设和决策记录在案。

## 完整工作流程

接收任务 → 自主理解 → 设计方案 → 分解任务 → 执行循环 → 终止保存

### 阶段1：自主理解（不询问用户）

输入：用户的一句话或一段描述。

处理步骤：

1. 提取关键实体：技术栈、功能需求、约束条件。
2. 补充默认值：
   - 技术栈未指定 → 选择最主流的（如Python）
   - 架构未指定 → 选择最简单的可行架构
   - 风格未指定 → 采用业界最佳实践
3. 标注假设：所有自行补充的内容标注[假设:原因]
4. 输出理解文档

需求理解文档格式：

核心目标：一句话总结
技术栈：自主选择或用户指定
功能范围：理解后的范围
约束条件：列出的约束

假设清单：列出所有假设及理由

### 阶段2：自主设计评估方案（不询问用户）

自动设计评估指标：

CLI工具：功能正确性（参数解析正确，输出符合预期）、错误处理（无效输入有合理错误提示）。

Web应用：API正确性（端点返回正确状态码和数据格式）、数据层（CRUD操作正确）。

库/SDK：API设计（直观、一致、文档完善）、测试覆盖（核心函数有单元测试）。

通用：代码质量（无明显代码异味）、可运行性（代码可直接运行无语法错误）。

自动生成测试方案：

验证方法包括：语法检查（无语法错误）、导入检查（所有依赖可导入）、基本功能（核心功能可执行）、错误处理（无效输入有错误提示）。

成功标准：语法检查通过、基本功能可运行、错误处理完善。

### 阶段3：自主规划迭代（不询问用户）

迭代规划模板：

第一轮迭代（15分钟内），目标：最小可运行版本。任务1（5min，创建项目结构）、任务2（5min，实现核心功能）、任务3（5min，基本验证）。

第二轮迭代（如有时间），目标：功能完善。任务4（10min）、任务5（10min）。

第三轮迭代（如有时间），目标：质量提升。任务6（10min）、任务7（10min）。

### 阶段4：执行循环

执行流程：获取任务 → 执行 → 验证 → 记录 → 检查预算 → 继续或终止

执行规则：

不等待确认：获取任务后立即执行。
快速验证：每任务后做最小验证（语法、导入、基本运行）。
错误处理：语法错误立即修复（最多2次）、逻辑错误记录并标记[待修复]继续、环境错误记录并标记[环境问题]继续。
定期同步：每5个任务或5分钟输出进度。

## 预算管理

### 预算级别

tiny：10min，20k token，适用场景为验证概念、最小demo。
small：30min，50k token，适用场景为小功能、单一模块。
medium：60min，100k token，适用场景为中等项目。
large：120min，200k token，适用场景为复杂项目。
xlarge：240min，500k token，适用场景为完整系统。

### 预算检查时机

每任务完成后检查、每5分钟强制检查、达到80%时减速详细检查。

### 终止决策

时间剩余>20%且Token剩余>25%时全速执行；时间剩余10-20%且Token剩余15-25%时正常执行；时间剩余5-10%且Token剩余10-15%时只做P0任务；时间剩余<5%或Token剩余<10%时立即终止并保存。

## 终止处理

### 终止前动作（按顺序执行）

停止获取新任务 → 完成当前任务的验证 → 保存所有文件 → 生成最终报告 → 输出待完成任务清单

### 最终报告模板

会话ID、开始时间、结束时间、总耗时、Token消耗。

完成情况：完成度百分比、效率评分（分数和等级）。

已完成：列出已完成的全部任务。

未完成：列出未完成的任务及状态/完成度。

假设清单：列出所有假设。

生成的代码：列出所有生成的文件。

下一步建议：列出后续建议。

## 使用示例

/强力迭代 构建一个CSV分析CLI
/power-iterate Implement user authentication --budget medium
/强力迭代 开发一个博客系统 --time 90

## Rules

- rules/task-decomposition.md：任务分解规则
- rules/autonomous-loop.md：自主执行循环
- rules/budget-manager.md：预算管理规则
- [rules/anti-aigc.md](rules/anti-aigc.md) - 流程文档反AIGC检测规则

## 配置选项

参数默认值说明：

time_limit：30，时间限制（分钟）。
token_limit：100000，Token限制。
budget_level：medium，预算级别，可选 tiny/small/medium/large/xlarge。
max_iterations：50，最大迭代次数。
checkpoint_interval：5，检查点间隔（任务数）。

## Anti-Patterns / 反模式

| 违规 | 严重度 | 后果 |
|------|--------|------|
| 无预算上限的无限循环 (while(true) without budget) | **CRITICAL** | 资源耗尽，系统崩溃 |
| 跳过回滚检查点 | **CRITICAL** | 错误无法恢复 |
| 不报告进度 (静默迭代) | HIGH | 用户不知道状态 |
| 在迭代中不检查质量指标 | HIGH | 可能在错误方向浪费预算 |
| 单次迭代做太多变更 | HIGH | 难以定位引入的问题 |
| 不设置最大迭代次数 | HIGH | 永远不会终止 |
| Token预算设置为远超实际的数字 | MEDIUM | 预算抑制机制失效 |

## 常见问题与排查

### 迭代陷入死循环
- **症状**: 同一任务反复修改但质量不提升
- **解决**: 检查收敛检测阈值，增加 `--threshold 5` 增加敏感度；手动中断并指定新策略

### 预算快速耗尽
- **症状**: 仅完成1-2轮迭代即耗尽token预算
- **解决**: 使用 `--budget high` 增加预算；缩小任务范围；优化每次迭代的代码变更量

### 评估指标不准确
- **症状**: 质量指标显示良好但实际效果差
- **解决**: 添加人工验收指标；调整指标权重；增加边界情况测试

## 边界情况

- **单文件项目**: 迭代粒度缩小到函数级别，不做模块级重构
- **超大型项目**: 指定 `--scope <module>` 限定迭代范围
- **跨语言项目**: 每种语言独立评估指标，汇总时取加权平均
- **历史代码退改**: 检测到回退时自动创建检查点，支持回滚

## AIGC检测意识

强力迭代的决策假设和状态报告必须具体可执行，不能用"假设用户需要X"。参见 `rules/anti-aigc.md` 了解流程文档的反AIGC规则。

核心要求：
- 假设必须标注[假设:理由]：不写"使用Python"，写"[假设:用户未指定技术栈，Python生态最成熟]"
- 最终报告必须包含具体完成度和待改进项，不用"进展顺利"

## 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| 2.0.0 | 2026-04-01 | 重构为自主迭代框架 |
| 2.1.0 | 2026-05-09 | 添加安全规则、边界情况、排查指南 |

## See Also / 相关技能

- `/修仙` from **sleepless** — 不眠不休执行，支持长时间迭代会话 / Non-stop execution for extended iteration sessions
- `/自控` from **zi-kong** — 跨会话记忆，支持长周期迭代 / Cross-session memory for long-running iterations
- `/iterate` from **iteration-manager** — 迭代中的质量指标追踪 / Quality metrics tracking during iteration