---
name: ba-guan
version: "1.1.0"
description: |
  Pre-publish review with multi-layer deep analysis for code quality assurance before release.

  Triggers when: Preparing to publish an npm package, needing pre-release review, or checking code change quality.

  Commands:
  - /把关 - Start full pre-publish review
  - /把关 check - Check unpublished changes
  - /把关 version - Suggest version bump
  - /把关 report - Generate review report
  - /review <task> - English command for pre-publish review

  Capabilities: Detect unpublished changes, per-change deep analysis, multi-role review (architect/developer/tester/security/docs), version suggestion, release risk assessment
author: cycleuser
license: MIT
status: Beta
---

## Safety Rules

参见 [_shared/core/safety-rules.md](../_shared/core/safety-rules.md) — 所有安全规则从共享层加载。

# 把关 (Pre-Publish Review)

<role>
Pre-publish review orchestrator. Three-layer deep analysis: per-change review (up to 10 agents), holistic multi-role review (5 roles), synthesis (1 agent). Supports npm, Python (PyPI), and generic project release gates.
</role>

## Release Risk Taxonomy

| Risk Level | Criteria | Action |
|-----------|----------|--------|
| SAFE | Routine changes, well-tested, no breaking changes | Ready to publish |
| CAUTION | Significant changes but manageable risk | Review findings, publish with monitoring |
| RISKY | Large surface area, insufficient testing | Fix blocking issues before publish |
| BLOCK | Critical issues found | Do NOT publish |

## Audit Layers

| Layer | Scope | Question |
|-------|-------|----------|
| Per-Change | Each logical change group individually | Is this change correct and safe? |
| Holistic | Full changeset, cross-module | Do changes work together? |
| Synthesis | Overall release | Is this release ready? |

发布前核弹级审查。三层审查确保发布质量。
Nuclear-grade pre-publish review. Three-layer review ensures release quality.

## Quick Commands

| Command | Description |
|---------|-------------|
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

### Phase 2: Per-Change Review (Up to 10 Agents)

Each change group gets its own parallel review agent. Agents receive only their group's diff.

```
## Per-Change Review: {GROUP_NAME}

**变更类型/Type**: {feat/fix/refactor/docs}
**影响文件/Files**: {file_list}
**Release Layer**: {npm|pypi|generic}

### Correctness / 正确性
- [ ] Logic correct for 3+ scenarios — trace through the code
- [ ] Edge cases handled (empty/null/large/concurrent)
- [ ] Error handling proper — no empty catch, no swallowed promises
- [ ] Breaking changes? If YES, what breaks and for whom?
- [ ] Hardcoded credentials or secrets? BLOCK immediately

### Test Coverage / 测试覆盖
- [ ] Unit tests for new/changed behavior
- [ ] Tests meaningful (not coverage padding)
- [ ] Regression tests for bug fixes

### Code Quality / 代码质量
- [ ] Type safety — no `as any`, `@ts-ignore`, `@ts-expect-error`
- [ ] Follows existing patterns in the file/package
- [ ] No introduced duplication
- [ ] Imports/exports clean — no side effects

### Evidence Links / 证据链接
- [文件](https://github.com/...)#L10-L50 — specific changed code
- [提交](https://github.com/.../commit/abc) — relevant commit

### Verdict / 判定
**{PASS | FAIL | CAUTION}**
**Risk: {SAFE | CAUTION | RISKY | BLOCK}**
**Has Breaking Changes: {YES | NO}**

### Blocking Issues / 阻塞问题
[Issues that MUST be fixed before publish. Empty if PASS.]
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

## Integration with Other Skills / 与其他技能集成

- Use `/architect review` from **master-architect** for architectural review during the Layer 2 holistic phase. Run `/architect review` to validate module cohesion, interface contracts, and test coverage alongside ba-guan's own multi-role analysis.
- Use `/安检` from **an-jian** for security audit. Run `/安检 scan` as a dedicated security pass, then feed results into ba-guan's Layer 2 security review for the final report.
- Use `/审视 <URL>` from **shen-shi** for GitHub-based code review patterns. Apply `/审视` to analyze related PRs and issues before finalizing the release assessment, borrowing evidence-based review methodology.
- Use `/iterate <n>` from **iteration-manager** for iterative improvement cycles after review. When ba-guan's report identifies issues, run `/iterate 3` to fix them and re-verify before the final `/把关` decision.

## Rules

- [rules/change-detection.md](rules/change-detection.md) - 变更检测/Change Detection
- [rules/review-roles.md](rules/review-roles.md) - 审查角色/Review Roles
- [rules/version-bump.md](rules/version-bump.md) - 版本规则/Version Rules
- [rules/anti-aigc.md](rules/anti-aigc.md) - 分析报告反AIGC检测规则

## 配置选项/Configuration

| 参数/Param | 默认值/Default | 说明/Description |
|-----------|---------------|-----------------|
| change_groups | 10 | 最大变更组数/Max groups |
| reviewers | 5 | 审查角色数/Reviewers |
| coverage_threshold | 70% | 测试覆盖阈值/Coverage threshold |

## Anti-Patterns / 反模式

| 违规 | 严重度 | 后果 |
|------|--------|------|
| 不等所有审查代理完成就给出结论 | **CRITICAL** | 审查不完整 |
| 跳过 Phase 0 (变更检测) 直接审查 | **CRITICAL** | 遗漏未发布变更 |
| 串行执行审查而非并行 | HIGH | 大型变更超时 |
| 跳过一个审查层次（三层缺一不可） | HIGH | 审查盲区 |
| 将多个不相关变更放入一组 | HIGH | 稀释深度分析 |
| 审查报告只有描述无证据（无文件路径和行号） | HIGH | 报告无法验证 |
| 有阻绝问题(BLOCK)仍建议发布 | **CRITICAL** | 上线即故障 |
| 不执行整体审查就进入综合评估 | HIGH | 缺少跨模块视角 |
| 不区分发布层（npm/pypi/generic）使用统一模板 | MEDIUM | 遗漏平台特有风险 |

## Verdict Logic / 判定逻辑

```
BLOCK if:
  - Any per-change agent found CRITICAL blocking issues
  - Holistic review failed on security or correctness
  - Breaking changes without migration plan

RISKY if:
  - Multiple per-change agents returned FAIL or CAUTION
  - Holistic review passed but with significant findings
  - Large surface area changes (>500 lines)

CAUTION if:
  - A few minor issues flagged
  - Holistic review passed cleanly
  - Medium surface area (100-500 lines)

SAFE if:
  - All per-change agents passed
  - Holistic review passed on all roles
  - Small surface area (<100 lines) OR well-tested
```

## 常见问题与排查 / Troubleshooting

### 审查无变更可发现 / No changes detected
- **症状/Symptom**: `/把关 check` 报告0个变更 / reports zero changes
- **解决/Fix**: 检查 `git diff --stat` 是否有变更；确认分支追踪正确；使用 `/把关 check --unstaged` 包含未暂存变更

### 审查角色冲突建议 / Conflicting review recommendations
- **症状/Symptom**: 架构师和开发者给出相反建议 / Architect and Developer give opposite recommendations
- **解决/Fix**: 使用 `/把关 --synthesize` 触发综合器汇总；手动审查冲突点；设定优先级：安全 > 架构 > 测试 > 文档

### 逐变更审查超时 / Per-change review timeout
- **症状/Symptom**: 单次变更审查超过5分钟上限 / Single change review exceeds 5min limit
- **解决/Fix**: 减少每个变更组的文件数；使用 `/把关 --max-files 5` 限制每组文件数；增加 `--timeout` 参数

## 边界情况 / Edge Cases

- **空仓库首次发布**: 绕过错层分析，只做整体评审和文档检查
- **大量变更(>100文件)**: 自动分组到10个智能体上限；超过部分排队处理
- **Monorepo发布**: 使用 `--scope <package>` 限定审查范围到单个包
- **紧急发布**: 使用 `/把关 --urgent` 跳过文档审查层，仅做安全+架构审查
- **回滚发布**: 比较回滚前后的diff，标记回滚引入的新风险

## AIGC-Aware Output / AIGC检测意识

Review reports must contain specific evidence (file paths, line numbers) and actionable fixes, not generic "needs improvement" statements. Every finding must have priority P0/P1/P2 classification. See `rules/anti-aigc.md` for complete anti-AIGC detection rules.

核心要求：
- 每个问题必须附文件路径和行号
- 不写"建议改进代码质量"，写"core/auth.py:47 的SQL注入，攻击者可绕过认证——P0，必须修了再上线"
- 重要问题5段话详细分析，次要问题1句带过
- 修复建议必须可操作，包含具体命令或代码修改

## 版本历史 / Version History

| 版本 | 日期 | 变更 |
|------|------|------|
| 1.0.0 | 2026-04-01 | 初始版本，三层审查架构 |
| 1.1.0 | 2026-05-09 | 添加安全规则，集成，排查，边界情况，3个rule文件 |

## See Also / 相关技能

- `/安检` from **an-jian** — 整体审查中的安全审计层 / Security audit layer in holistic review
- `/architect review` from **master-architect** — 整体审查中的架构审查层 / Architecture review layer in holistic review
- `/合并` from **he-bing** — 审查通过后的 PR 工作流 / PR workflow after review passes
- `/审视` from **shen-shi** — 基于 GitHub 的代码审查模式 / GitHub-based code review patterns
