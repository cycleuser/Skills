---
name: project-rebuilder
version: "1.1.0"
description: |
  Project rebuilding skill that references existing projects to rewrite core features from scratch with team parallel review and persistent execution.

  Triggers when: Needing to reference an open-source project to rewrite core features, building a similar product from scratch, or deeply refactoring an existing project.

  Commands:
  - /rebuild <参考项目> <目标> - Start project rebuild
  - /rebuild analyze <项目> - Analyze reference project
  - /rebuild team - Start team parallel review
  - /rebuild ralph - Start persistent cross-session execution
  - /rebuild checkpoint - View or restore checkpoints
  - /rebuild status - View rebuild progress

  Capabilities: Reference project deep analysis, core feature extraction, multi-role parallel review (architect/developer/tester), cross-session persistent execution, rebuilding core features from scratch
author: cycleuser
license: MIT
status: Beta
---

## Safety Rules

参见 [_shared/core/safety-rules.md](../_shared/core/safety-rules.md) — 所有安全规则从共享层加载。

# Project Rebuilder 项目重建

参考现有项目从零重写核心特性的技能。采用 **team 并行审查** + **ralph 持久执行** 模式。

## Quick Commands

| Command | Description |
|---------|-------------|
| `/rebuild <参考项目> <目标>` | Start project rebuild |
| `/rebuild analyze <项目/URL>` | Analyze reference project |
| `/rebuild team` | Start team parallel review |
| `/rebuild ralph` | Start persistent cross-session execution |
| `/rebuild status` | View rebuild progress |
| `/rebuild checkpoint` | Save current progress checkpoint |

---

## 核心工作模式

### 模式一：team 并行审查

```
┌─────────────────────────────────────────────────────────────────────┐
│                    TEAM 并行审查模式                                 │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│   ┌──────────────┐    ┌──────────────┐    ┌──────────────┐         │
│   │  架构师角色   │    │  开发者角色   │    │  测试员角色   │         │
│   │  Architect   │    │  Developer   │    │  Tester      │         │
│   └──────┬───────┘    └──────┬───────┘    └──────┬───────┘         │
│          │                   │                   │                  │
│          │ 审查架构设计       │ 审查代码实现       │ 审查测试覆盖      │
│          │ 技术选型合理性     │ 代码质量规范       │ 边界情况处理      │
│          │ 模块划分清晰度     │ 功能完整性         │ 错误处理完善      │
│          │                   │                   │                  │
│          └───────────────────┼───────────────────┘                  │
│                              │                                       │
│                         ┌────▼────┐                                  │
│                         │ 合并审查 │                                  │
│                         │ 意见    │                                  │
│                         └────┬────┘                                  │
│                              │                                       │
│                              ▼                                       │
│                         ┌──────────┐                                 │
│                         │ 改进清单  │                                 │
│                         └──────────┘                                 │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

**审查流程**：

1. **架构师审查**：技术选型、模块划分、扩展性设计
2. **开发者审查**：代码规范、功能实现、边界处理
3. **测试员审查**：测试覆盖、边界情况、错误处理
4. **合并意见**：汇总三份审查报告，生成改进清单

### 模式二：ralph 持久执行

```
┌─────────────────────────────────────────────────────────────────────┐
│                   RALPH 持久执行模式                                 │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  Session 1 → Checkpoint → Session 2 → Checkpoint → Session 3        │
│      │            │            │            │            │          │
│      ▼            ▼            ▼            ▼            ▼          │
│   分析项目     保存进度     继续执行     保存进度     完成重建      │
│                                                                      │
│  跨会话记忆：                                                         │
│  - 已完成任务清单                                                      │
│  - 待完成任务队列                                                      │
│  - 假设与决策记录                                                      │
│  - 问题与解决方案                                                      │
│  - 下一步行动计划                                                      │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

**持久执行特点**：

1. **Checkpoint 机制**：每阶段保存进度
2. **跨会话记忆**：下次继续时自动恢复上下文
3. **持续迭代**：支持多轮审查 - 改进循环
4. **状态追踪**：清晰记录已完成/待完成/已跳过

---

## 项目重建流程

### 第一阶段：参考项目分析

```markdown
## 参考项目分析报告

**项目名称**: {name}
**项目 URL**: {url}
**分析时间**: {timestamp}

### 核心特性提取

| 特性 | 重要性 | 复杂度 | 是否重建 |
|-----|--------|--------|---------|
| 特性 A | P0 | 高 | 是 |
| 特性 B | P0 | 中 | 是 |
| 特性 C | P1 | 低 | 部分 |
| 特性 D | P2 | 高 | 否 |

### 技术栈分析

- 语言：{language}
- 框架：{framework}
- 关键依赖：{dependencies}
- 架构模式：{pattern}

### 代码结构

{项目目录结构分析}

### 核心算法/逻辑

{核心功能的技术分析}
```

### 第二阶段：重建规划

```markdown
## 重建规划

**目标**: {重建目标}
**技术选型**: {技术栈选择及理由}
**架构设计**: {新项目的架构}

### 任务分解

#### P0 - 核心功能（必须完成）
| # | 任务 | 预计时间 | 负责人 | 状态 |
|---|-----|---------|-------|------|
| 0.1 | 项目骨架 | 30min | - | 待执行 |
| 0.2 | 核心模块 A | 2h | - | 待执行 |
| 0.3 | 核心模块 B | 2h | - | 待执行 |

#### P1 - 完整功能（尽量完成）
| # | 任务 | 预计时间 | 负责人 | 状态 |
|---|-----|---------|-------|------|
| 1.1 | 功能模块 C | 3h | - | 待执行 |
| 1.2 | 功能模块 D | 3h | - | 待执行 |

#### P2 - 完善优化（有时间再做）
| # | 任务 | 预计时间 | 负责人 | 状态 |
|---|-----|---------|-------|------|
| 2.1 | 性能优化 | 2h | - | 待执行 |
| 2.2 | 文档完善 | 2h | - | 待执行 |
```

### 第三阶段：team 并行审查

```markdown
## 审查报告 - 迭代 N

### 架构师审查

**审查内容**: 架构设计、技术选型、模块划分

**通过项**:
- ✅ 技术选型合理
- ✅ 模块划分清晰

**改进项**:
- ⚠️ 建议增加配置模块
- ⚠️ 建议抽象数据层接口

### 开发者审查

**审查内容**: 代码规范、功能实现、边界处理

**通过项**:
- ✅ 代码风格一致
- ✅ 核心功能完整

**改进项**:
- ⚠️ 部分函数过长，建议拆分
- ⚠️ 错误处理不够完善

### 测试员审查

**审查内容**: 测试覆盖、边界情况、错误处理

**通过项**:
- ✅ 核心功能有测试

**改进项**:
- ⚠️ 边界情况测试不足
- ⚠️ 缺少集成测试

### 合并改进清单

| 优先级 | 改进项 | 来源 | 状态 |
|-------|-------|------|------|
| P0 | 增加错误处理 | 开发者 | 待执行 |
| P0 | 补充边界测试 | 测试员 | 待执行 |
| P1 | 拆分过长函数 | 开发者 | 待执行 |
| P1 | 增加配置模块 | 架构师 | 待执行 |
```

### 第四阶段：ralph 持久执行

```markdown
## 执行记录

### Session 1

**时间**: 2h
**完成**:
- ✅ 项目骨架创建
- ✅ 核心模块 A 基础实现
- ✅ 单元测试框架搭建

**Checkpoint**:
```json
{
  "completed": ["0.1", "0.2"],
  "in_progress": "0.3",
  "pending": ["1.1", "1.2", "2.1", "2.2"],
  "assumptions": [...],
  "issues": [...]
}
```

**问题记录**:
- 问题 A：{描述} → 解决方案：{方案}

**下一步**:
- 继续核心模块 B 实现
- 补充错误处理

---

### Session 2

**时间**: 2h
**完成**:
- ✅ 核心模块 B 实现
- ✅ 错误处理完善
- ✅ 边界测试补充

**Checkpoint**: {...}

---

### Session N (完成)

**总耗时**: {total_time}
**完成率**: {completion_rate}
**测试覆盖**: {coverage}
```

---

## Checkpoint 格式

```json
{
  "project": {
    "name": "项目名称",
    "reference": "参考项目",
    "goal": "重建目标"
  },
  "progress": {
    "completed": ["任务 ID 列表"],
    "in_progress": "当前任务 ID",
    "pending": ["待完成任务 ID 列表"],
    "skipped": ["已跳过任务 ID 列表"]
  },
  "context": {
    "assumptions": [
      {"id": 1, "content": "假设内容", "verified": true/false}
    ],
    "decisions": [
      {"id": 1, "content": "决策内容", "rationale": "理由"}
    ],
    "issues": [
      {"id": 1, "description": "问题描述", "solution": "解决方案", "status": "open/resolved"}
    ]
  },
  "next_steps": [
    "下一步行动 1",
    "下一步行动 2"
  ],
  "timestamp": "2024-01-01T12:00:00Z"
}
```

---

## 使用示例

### 示例 1：参考 flink 重写流处理核心

```
用户：/rebuild https://github.com/apache/flink 流处理核心引擎
目标：用 Python 重写 Flink 的流处理核心特性

→ 分析参考项目
  - 核心特性：DataStream API、窗口计算、状态管理
  - 技术栈：Java → Python
  - 复杂度：高

→ 重建规划
  - P0: 数据流模型、基础算子、执行引擎
  - P1: 窗口计算、状态管理
  - P2: 优化器、监控

→ team 审查
  - 架构师：建议抽象执行接口
  - 开发者：注意 Python GIL 影响
  - 测试员：需要压力测试

→ ralph 持久执行
  - Session 1: 完成数据流模型
  - Session 2: 完成基础算子
  - Session 3: 完成执行引擎
  - ...
```

### 示例 2：参考 vscode 重写编辑器核心

```
用户：/rebuild vscode 轻量级代码编辑器
目标：用 Rust 重写 VSCode 的核心编辑功能

→ 分析参考项目
→ 重建规划
→ team 审查
→ ralph 持久执行
```

---

## Troubleshooting / 排查

### Reference project analysis fails / 参考项目分析失败
- **Symptom / 症状**: `/rebuild analyze <project>` returns incomplete or no results
- **Cause / 原因**: Large project, complex dependency graph, or missing build tools
- **Fix / 解决**: Run analysis on specific submodules, use `--depth 2` for shallow analysis, check build dependencies are installed

### Team review produces conflicting recommendations / 团队审查意见冲突
- **Symptom / 症状**: Architect, Developer, and Tester agents disagree on approach
- **Cause / 原因**: Different quality priorities or architectural philosophies
- **Fix / 解决**: Use `/rebuild team --resolve` to trigger resolution pass, or manually select the approach using `/rebuild --approach <name>`

### Ralph execution stalls / Ralph 执行卡住
- **Symptom / 症状**: Ralph persistent execution locks up at checkpoint
- **Cause / 原因**: Network timeout, disk full, or infinite loop in generated code
- **Fix / 解决**: Use `/rebuild status` to identify the stalled checkpoint, `/rebuild --resume` from last valid checkpoint, increase timeout settings

### Rebuilt project doesn't match original behavior / 重建项目行为不一致
- **Symptom / 症状**: Output differs from reference despite passing tests
- **Cause / 原因**: Edge cases not covered in reference analysis, implicit state dependencies
- **Fix / 解决**: Run `/rebuild compare` for behavioral diff, add missing edge cases to analysis, iterate with targeted test cases

## Edge Cases / 边界情况

- **Monorepo analysis / 多包仓库**: Multi-package repos need per-package analysis scope; use `/rebuild analyze <repo> --scope <package>`
- **Binary-only dependencies / 纯二进制依赖**: If reference uses compiled libraries without source, mark as "black box" and re-implement interface only
- **Legacy language migration / 旧语言迁移**: Python 2→3, ES5→ES6+ need syntax transformation rules in analysis phase
- **Database schema mismatch / 数据库模式不匹配**: If reference DB schema differs from target, generate migration scripts as separate checkpoint
- **Large file handling / 大文件处理**: Files >5MB analyzed as "external assets", not rebuilt — only references tracked
- **Concurrent rebuilds / 并发重建**: Two rebuilds on same project auto-sequentialize via checkpoint lock; second waits for first to complete

## AIGC-Aware Output

Project analysis and rebuild reports must contain specific evidence with line numbers and code references, not generic assessments. See `rules/anti-aigc.md` for anti-AIGC rules applicable to analysis reports.

Key requirements:
- Every feature assessment must include complexity score with justification
- Analysis conclusions must reference specific file paths and line numbers
- Priority classifications (P0/P1/P2) must be backed by specific risks, not "important" or "nice-to-have"

## Version History / 版本历史

| Version / 版本 | Date / 日期 | Changes / 变更 |
|---------|------|---------|
| 1.0.0 | 2026-04-01 | Initial version with team+ralph parallel review pattern |
| 1.1.0 | 2026-05-09 | Added safety rules, edge cases, troubleshooting, 4 rule files |

## Rules

- [rules/project-analysis.md](rules/project-analysis.md) - 参考项目分析方法
- [rules/team-review.md](rules/team-review.md) - 团队并行审查流程
- [rules/ralph-execution.md](rules/ralph-execution.md) - 持久执行机制
- [rules/checkpoint.md](rules/checkpoint.md) - 进度保存与恢复
- [rules/anti-aigc.md](rules/anti-aigc.md) - 分析报告反AIGC检测规则

---

## 配置选项

| 参数 | 默认值 | 说明 |
|-----|-------|------|
| review_iterations | 3 | 审查 - 改进迭代次数 |
| checkpoint_interval | 30min | 自动保存间隔 |
| parallel_reviewers | 3 | 并行审查角色数 |

## See Also / 相关技能

- `/architect design` from **master-architect** — 对参考项目进行架构分析 / Architecture analysis for reference project
- `/iterate` from **iteration-manager** — 对重建组件进行迭代测试 / Iterative testing of rebuilt components
- `/python-project` from **python-project-developer** — 搭建重建项目的项目结构 / Scaffold rebuilt project structure
