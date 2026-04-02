---
name: ba-guan
version: "1.0.0"
description: |
  把关 - Pre-publish review with multi-layer deep analysis.
  
  触发条件/Triggers: 准备发布 npm 包、需要发布前审查、或检查代码变更质量。
  
  审查层次/Review Layers:
  - 逐变更审查/Per-Change: 每个变更组深度分析 (最多 10 个智能体)
  - 整体审查/Holistic: 5 角色并行审查 (架构/开发/测试/安全/文档)
  - 综合评估/Synthesis: 1 个智能体汇总审查结果
  
  命令/Commands:
  - /把关 - 启动发布前审查
  - /把关 check - 检查未发布变更
  - /把关 version - 建议版本升级
  - /把关 report - 生成审查报告
  - /review - English command
  
  能力/Capabilities: 检测未发布变更、逐变更深度分析、多角色审查、版本建议、发布风险评估。
author: cycleuser
license: MIT
---

# 把关 (Pre-Publish Review)

发布前核弹级审查。三层审查确保发布质量。
Nuclear-grade pre-publish review. Three-layer review ensures release quality.

## Quick Commands

| 命令/Command | 功能/Function |
|-------------|--------------|
| `/把关` | 启动完整发布前审查 |
| `/把关 check` | 检查未发布变更 |
| `/把关 version` | 建议版本升级 |
| `/把关 report` | 生成审查报告 |
| `/review` | Start full pre-publish review |
| `/review check` | Check unpublished changes |
| `/review version` | Suggest version bump |

## 三层审查架构/Three-Layer Review

```
┌─────────────────────────────────────────────────────────────────────┐
│                    发布前三层审查/Pre-Publish Review                 │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  Layer 1: 逐变更审查/Per-Change (最多 10 个智能体)                      │
│  ├── 变更组 A 深度分析/Group A deep analysis                         │
│  ├── 变更组 B 深度分析/Group B deep analysis                         │
│  └── ...                                                              │
│                                                                      │
│  Layer 2: 整体审查/Holistic (5 角色并行/5 roles)                       │
│  ├── 架构师/Architect: 架构合规性                                     │
│  ├── 开发者/Developer: 代码质量                                       │
│  ├── 测试员/Tester: 测试覆盖                                          │
│  ├── 安全专家/Security: 安全检查                                      │
│  └── 文档/Docs: 文档完整性                                            │
│                                                                      │
│  Layer 3: 综合评估/Synthesis (1 个智能体)                               │
│  └── 汇总所有审查结果，给出发行建议/Summary & recommendation           │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

## 审查流程/Review Workflow

### Phase 0: 检测未发布变更/Detect Changes

```bash
# 获取已发布版本/Get published version
PUBLISHED=$(npm view package-name version 2>/dev/null || echo "not published")

# 获取本地版本/Get local version
LOCAL=$(node -p "require('./package.json').version" 2>/dev/null || echo "unknown")

# 获取变更列表/Get commit list
git log "v${PUBLISHED}"..HEAD --oneline

# 获取变更文件/Get changed files
git diff --name-only "v${PUBLISHED}"..HEAD

# 获取变更统计/Get diff stats
git diff "v${PUBLISHED}"..HEAD --stat
```

### Phase 1: 变更分组/Group Changes

```markdown
## 变更分组/Change Groups

### 新功能/Features (feat)
| 范围/Scope | 文件/Files | 行数/Lines | 复杂度/Complexity |
|-----------|-----------|-----------|-----------------|
| auth | +150/-30 | +120 | 中/Medium |

### Bug 修复/Bug Fixes (fix)
| 范围/Scope | 文件/Files | 行数/Lines | 复杂度/Complexity |
|-----------|-----------|-----------|-----------------|
| api | +20/-15 | +5 | 低/Low |

### 重构/Refactoring (refactor)
...

### 文档/Documentation (docs)
...
```

### Phase 2: 逐变更审查/Per-Change Review

```markdown
## 变更审查报告/Change Review - {scope}

**变更类型/Type**: {feat/fix/refactor}
**影响文件/Files**: {file_list}
**代码变更/Changes**: +{added}/-{removed}

### 正确性/Correctness
- [ ] 逻辑正确/Logic correct
- [ ] 边界处理/Edge cases
- [ ] 错误处理/Error handling

### 测试覆盖/Test Coverage
- [ ] 有单元测试/Unit tests
- [ ] 有集成测试/Integration tests
- [ ] 边界测试/Edge case tests

### 代码质量/Code Quality
- [ ] 命名清晰/Clear naming
- [ ] 函数简短/Short functions
- [ ] 无重复代码/No duplication

### 证据链接/Evidence Links
- [文件链接](https://github.com/...)#L10-L50
```

### Phase 3: 整体审查/Holistic Review

```markdown
## 整体审查报告/Holistic Review

### 架构审查/Architecture
**通过/Pass**:
- ✅ 架构设计合理/Design reasonable
- ✅ 模块划分清晰/Modules clear

**改进/Improve**:
- ⚠️ 建议增加配置层/Add config layer

### 代码审查/Code
**通过/Pass**:
- ✅ 代码风格一致/Consistent style
- ✅ 无严重问题/No critical issues

**改进/Improve**:
- ⚠️ 部分函数过长/Some functions too long

### 测试审查/Tests
**通过/Pass**:
- ✅ 核心功能有测试/Core tested

**改进/Improve**:
- ⚠️ 边界测试不足/Edge tests insufficient

### 安全审查/Security
...

### 文档审查/Docs
...
```

### Phase 4: 综合评估/Synthesis

```markdown
## 发布综合评估/Release Assessment

**版本建议/Version**: {patch/minor/major}
**发布风险/Risk**: {低/Low/中/Medium/高/High}

### 审查汇总/Summary
| 层次/Layer | 状态/Status | 问题数/Issues |
|-----------|------------|--------------|
| 逐变更/Per-Change | ✅/⚠️ | {count} |
| 整体/Holistic | ✅/⚠️ | {count} |
| 综合/Synthesis | ✅/⚠️ | {count} |

### 发布清单/Checklist
- [ ] 所有 P0 问题已解决/All P0 resolved
- [ ] 测试覆盖率达标/Coverage达标
- [ ] 文档已更新/Docs updated
- [ ] 版本号已升级/Version bumped

### 决策/Decision
{可以发布/Ready / 需要修复/Fix needed / 不建议发布/Not ready}
```

## 版本建议规则/Version Rules

```
【版本升级/Version Bump】

Major (主版本):
- 有破坏性变更/Breaking changes
- API 不兼容/API incompatible

Minor (次版本):
- 有新功能/New features
- 向后兼容/Backward compatible

Patch (修订号):
- 只有 Bug 修复/Bug fixes only
- 文档更新/Docs only
```

## 输出报告/Output Reports

```
/tmp/{YYYYMMDD-HHmmss}/
├── changes.md        # 变更分析/Change analysis
├── per-change-*.md   # 逐变更审查/Per-change review
├── holistic.md       # 整体审查/Holistic review
└── release-review.md # 综合报告/Final report
```

## 使用示例/Examples

```
用户/User: /把关

→ Phase 0: 检测未发布变更/Detect changes
→ Phase 1: 变更分组/Group changes
→ Phase 2: 逐变更审查/Per-change review (parallel)
→ Phase 3: 整体审查/Holistic review (5 roles)
→ Phase 4: 综合评估/Synthesis
→ 输出发行建议/Output recommendation
```

## Rules

- [rules/change-detection.md](rules/change-detection.md) - 变更检测/Change Detection
- [rules/review-roles.md](rules/review-roles.md) - 审查角色/Review Roles
- [rules/version-bump.md](rules/version-bump.md) - 版本规则/Version Rules

## 配置选项/Configuration

| 参数/Param | 默认值/Default | 说明/Description |
|-----------|---------------|-----------------|
| change_groups | 10 | 最大变更组数/Max groups |
| reviewers | 5 | 审查角色数/Reviewers |
| coverage_threshold | 70% | 测试覆盖阈值/Coverage threshold |
