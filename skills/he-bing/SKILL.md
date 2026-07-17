---
name: he-bing
version: "1.2.0"
description: |
  Complete PR lifecycle management from worktree creation through implementation, commits, PR creation, verification loop, to merge and cleanup.

  Triggers when: Implementing a feature and submitting a PR, fixing an Issue, or completing merge work after code review.

  Commands:
  - /合并 <任务> - Start full PR workflow
  - /合并 create <任务> - Create PR
  - /合并 check - Check verification status
  - /合并 status - View PR status
  - /pr <task> - English command for PR workflow
  - /pr create <task> - Create PR (English)
  - /pr check - Check verification status (English)
  - /pr status - View PR status (English)

  Capabilities: Worktree management, feature implementation, atomic commits, PR creation, verification loop (CI + Review + Approval), merge and cleanup
author: cycleuser
license: MIT
status: Beta
---

## Safety Rules

参见 [_shared/core/safety-rules.md](../_shared/core/safety-rules.md) — 所有安全规则从共享层加载。

# 合并 (Work With PR)

完整 PR 生命周期管理。从工作树到合并，自动化全流程。
Complete PR lifecycle management. From worktree to merge, automated end-to-end.

## Quick Commands

| Command | Description |
|---------|-------------|
| `/合并 <任务>` | 启动完整 PR 工作流 |
| `/合并 create <任务>` | 创建 PR |
| `/合并 check` | 检查验证状态 |
| `/合并 status` | 查看 PR 状态 |
| `/pr <task>` | Start full PR workflow |
| `/pr create <task>` | Create PR |
| `/pr check` | Check verification status |
| `/pr status` | Check PR status |

## 工作流架构/Workflow

```
┌─────────────────────────────────────────────────────────────────────┐
│                  PR 完整生命周期/Complete PR Lifecycle               │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  Phase 0: 准备/Preparation                                          │
│  ├── 解析仓库上下文/Resolve repo context                            │
│  ├── 创建分支/Create branch                                         │
│  └── 设置工作树/Setup worktree (git worktree)                       │
│                                                                      │
│  Phase 1: 实现/Implementation                                       │
│  ├── 实现功能/Implement feature                                     │
│  ├── 原子提交/Atomic commits                                        │
│  └── 本地验证/Local verification                                    │
│                                                                      │
│  Phase 2: PR 创建/PR Creation                                        │
│  ├── 推送分支/Push branch                                           │
│  ├── 创建 PR/Create PR (target: dev branch)                         │
│  └── 填写 PR 模板/Fill PR template                                    │
│                                                                      │
│  Phase 3: 验证循环/Verification Loop                                │
│  ├── Gate A: CI 检查/CI checks                                       │
│  ├── Gate B: 代码审查/Code review                                    │
│  ├── Gate C: Cubic 批准/Cubic approval                               │
│  └── {任一失败/Any fail → 修复/fix → 重新验证/re-verify}             │
│                                                                      │
│  Phase 4: 合并/Merge                                                │
│  ├── 压缩合并/Squash merge                                          │
│  ├── 清理工作树/Cleanup worktree                                    │
│  └── 输出合并报告/Output merge report                               │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

## Phase 0: 准备工作树/Setup Worktree

```bash
# 1. 解析仓库上下文/Resolve context
REPO=$(gh repo view --json nameWithOwner -q .nameWithOwner)
REPO_NAME=$(basename "$PWD")
BASE_BRANCH="dev"  # 默认目标分支/Default target

# 2. 创建分支/Create branch
BRANCH_NAME="feature/$(echo "$TASK" | tr '[:upper:] ' '[:lower:]-' | head -c 50)"
git fetch origin "$BASE_BRANCH"
git branch "$BRANCH_NAME" "origin/$BASE_BRANCH"

# 3. 创建工作树 (目录外)/Create worktree (outside repo)
WORKTREE_PATH="../${REPO_NAME}-wt/${BRANCH_NAME}"
mkdir -p "$(dirname "$WORKTREE_PATH")"
git worktree add "$WORKTREE_PATH" "$BRANCH_NAME"

# 4. 设置工作上下文/Setup context
cd "$WORKTREE_PATH"
[ -f "bun.lock" ] && bun install
```

## Phase 1: 实现功能/Implementation

```markdown
## 实现原则/Implementation Principles

### 范围纪律/Scope Discipline
- Bug 修复/Bug fix: 最小改动/Minimal changes，只修复 bug+测试
- 新功能/Feature: 按需求实现/As specified，不额外重构/no extra refactor
- 技术债/Tech debt: 单独 PR/Separate PR，不与功能混合/not mixed

### 原子提交/Atomic Commits
每个提交应该/Each commit should:
- [ ] 完成一个独立功能/Complete one feature
- [ ] 有清晰的提交信息/Clear commit message
- [ ] 可通过测试/Passes tests
- [ ] 不破坏现有功能/No breaking changes

### 提交信息格式/Commit Format
```
<type>(<scope>): <subject>

<body>

<footer>
```

示例/Example:
```
feat(auth): 添加 JWT 认证/Add JWT auth

- 实现 JWT 生成和验证/Implement JWT
- 添加认证中间件/Add middleware
- 更新 API 文档/Update docs

Closes #123
```
```

## Phase 2: 创建 PR/Create PR

```bash
# 1. 推送分支/Push branch
git push -u origin "$BRANCH_NAME"

# 2. 创建 PR/Create PR
gh pr create \
  --base "$BASE_BRANCH" \
  --head "$BRANCH_NAME" \
  --title "<type>: <subject>" \
  --body-file "pr-template.md"

# 3. 关联 Issue/Link Issue (if any)
gh pr edit "$PR_NUMBER" --add-label "bug" --add-label "urgent"
```

## Phase 3: 验证循环/Verification Loop

```
┌─────────────────────────────────────────────────────────────────────┐
│                  验证循环/Verification Loop                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│    ┌──────────┐                                                     │
│    │  开始    │                                                     │
│    └────┬─────┘                                                     │
│         │                                                           │
│         ▼                                                           │
│    ┌──────────┐     ┌──────────┐     ┌──────────┐                  │
│    │ Gate A:  │────▶│ Gate B:  │────▶│ Gate C:  │                  │
│    │   CI     │     │  审查    │     │  Cubic   │                  │
│    └────┬─────┘     └────┬─────┘     └────┬─────┘                  │
│         │                │                │                         │
│    ┌────▼─────┐    ┌─────▼─────┐   ┌─────▼─────┐                   │
│    │ 通过？   │    │  通过？   │   │  通过？   │                   │
│    └────┬─────┘    └─────┬─────┘   └─────┬─────┘                   │
│         │                │                │                         │
│    YES  │  NO       YES  │  NO      YES  │  NO                     │
│    ┌────┴─────┐    ┌─────┴─────┐   ┌─────┴─────┐                   │
│    ▼          ▼    ▼           ▼   ▼           ▼                   │
│  [下一门]  [修复] [下一门]   [修复] [合并]   [修复]                  │
│                                                                      │
│  修复后回到对应的 Gate 重新验证/After fix, re-verify at that gate      │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### Gate A: CI 检查

```bash
# 检查 CI 状态/Check CI status
gh pr checks "$PR_NUMBER"

# 等待 CI 完成/Wait for CI
gh pr checks "$PR_NUMBER" --watch
```

### Gate B: 代码审查/Code Review

```markdown
## 审查清单/Review Checklist

### 架构/Architecture
- [ ] 模块划分合理/Good modularity
- [ ] 依赖关系清晰/Clear dependencies

### 代码/Code
- [ ] 命名清晰/Clear naming
- [ ] 函数简短/Short functions
- [ ] 无重复代码/No duplication

### 测试/Tests
- [ ] 有单元测试/Unit tests
- [ ] 测试通过/Tests pass

### 文档/Docs
- [ ] 更新了文档/Docs updated
- [ ] 有使用说明/Usage examples
```

### Gate C: Cubic 批准

等待 Cubic-dev-ai bot 的"No issues found"评论。
Wait for Cubic-dev-ai bot comment "No issues found".

## Phase 4: 合并清理/Merge & Cleanup

```bash
# 1. 压缩合并/Squash merge
gh pr merge "$PR_NUMBER" --squash --admin

# 2. 删除分支/Delete branch
git push origin --delete "$BRANCH_NAME"

# 3. 清理工作树/Cleanup worktree
git worktree remove "$WORKTREE_PATH"
if [ -n "$WORKTREE_PATH" ] && [ "$WORKTREE_PATH" != "/" ]; then rm -rf "$WORKTREE_PATH"; fi

# 4. 返回主工作目录/Return to main
cd "$ORIGINAL_PATH"

# 5. 更新主分支/Update main
git fetch origin
git checkout "$BASE_BRANCH"
git pull origin "$BASE_BRANCH"
```

## 合并报告/Merge Report

```markdown
## PR 合并报告/PR Merge Report

**PR**: #{number} - {title}
**分支/Branch**: {branch_name}
**合并时间/Merged**: {timestamp}

### 验证结果/Verification
| Gate | 状态/Status | 尝试次数/Attempts |
|-----|------------|-----------------|
| CI | ✅ | 1 |
| 审查/Review | ✅ | 2 |
| Cubic | ✅ | 1 |

### 提交摘要/Commits
| Hash | 信息/Message |
|------|-------------|
| abc123 | feat: 添加功能 A/Add feature A |
| def456 | fix: 修复问题 B/Fix issue B |

### 工作树/Worktree
- 路径/Path: {worktree_path}
- 清理/Cleanup: ✅

### 后续行动/Next Steps
- [ ] 通知相关人员/Notify team
- [ ] 更新 Issue 状态/Update issues
- [ ] 部署验证/Deploy verify
```

## 使用示例/Examples

### 示例 1：完整 PR 流程

```
用户/User: /合并 添加用户登录功能/Add user login

→ Phase 0: 创建工作树/Create worktree
→ Phase 1: 实现登录功能/Implement login
→ Phase 2: 创建 PR/Create PR
→ Phase 3: 验证循环/Verify loop (CI/Review/Cubic)
→ Phase 4: 合并清理/Merge & cleanup
```

### Example 2: Fix Bug

```
用户/User: /pr fix auth bug in Issue #123

→ 最小改动修复 bug/Minimal fix
→ 添加测试/Add tests
→ 创建 PR/Create PR
→ 验证 → 合并/Verify → Merge
```

## Performance & Resource Management / 性能与资源管理

### Worktree Optimization / 工作树优化
- **Shallow clone for large repos**: Use `git clone --depth 1` for repos >500MB to reduce worktree creation time
- **Worktree cleanup**: Automatically remove worktrees older than 24 hours; use `/合并 --cleanup` for manual cleanup
- **Shared object store**: Worktrees share the main repo's object store — no need to re-clone; only new working directory is created

### CI Verification Efficiency / CI验证效率
- **Parallel verification**: Run lint, typecheck, security scan, and test suite in parallel across separate jobs
- **Incremental verification**: Skip unchanged modules by comparing against base branch; use `--skip-unchanged` flag
- **Cached dependencies**: Use CI caching for pip/npm dependencies across verification runs; avoid reinstalling from scratch

### Commit Optimization / 提交优化
- **Atomic commit size**: Keep commits under 200 lines changed for faster review; split large changes with `--split` option
- **Pre-commit hook caching**: Cache hook results for unchanged files; only re-run hooks on modified files
- **Rebase vs merge**: Prefer rebase for feature branches (cleaner history); merge for long-running branches (preserves context)

### Resource Cleanup / 资源清理
- **Auto-cleanup schedule**: Configure auto-cleanup for worktrees, merged branches, and stale PRs; default: 7 days
- **Disk space monitoring**: Alert if worktree directory exceeds 10% of disk; suggest cleanup before proceeding
- **Stale PR detection**: Mark PRs as stale after 14 days of inactivity; auto-close after 30 days with no response

## Rules

- [rules/worktree.md](rules/worktree.md) - 工作树管理/Worktree
- [rules/commit-atomic.md](rules/commit-atomic.md) - 原子提交/Atomic Commits
- [rules/verification.md](rules/verification.md) - 验证循环/Verification
- [rules/anti-aigc.md](rules/anti-aigc.md) - 流程文档反AIGC检测规则

## 配置选项/Configuration

| 参数/Param | 默认值/Default | 说明/Description |
|-----------|---------------|-----------------|
| base_branch | dev | 目标分支/Target branch |
| worktree_parent | ../ | 工作树父目录/Parent dir |
| max_review_cycles | 5 | 最大审查循环/Max cycles |

## Anti-Patterns / 反模式

| 违规 | 严重度 | 后果 |
|------|--------|------|
| 在main分支上直接开发而非创建worktree/分支 | **CRITICAL** | 污染主分支，难以回滚 |
| 未经CI通过就合并PR | **CRITICAL** | 破坏主分支 |
| 跳过代码审查直接合并 | HIGH | 质量问题未被发现 |
| 一个PR包含多个不相关变更 | HIGH | 难以审查，回滚困难 |
| PR描述为空或只有标题 | HIGH | 审查者不知道变更意图 |
| force push已推送的分支 | HIGH | 审查历史丢失 |
| 合并后不清理worktree | MEDIUM | 磁盘空间浪费 |
| 不验证PR模板字段 | MEDIUM | 元数据不完整 |

## 常见问题与排查 / Troubleshooting

### Worktree创建失败 / Worktree creation fails
- **症状/Symptom**: `git worktree add` 报错路径已存在或权限不足
- **解决/Fix**: 清理旧worktree: `git worktree prune`；检查磁盘空间 `df -h`；使用 `/合并 --cleanup` 清理过期worktree

### PR验证循环卡住 / PR verification stuck in loop
- **症状/Symptom**: CI通过但审批人没有响应 / CI passes but no reviewer response
- **解决/Fix**: 检查PR是否分配正确的reviewer；使用 `/合并 check --notify` 发送提醒；如果超过48h，提请其他reviewer

### 合并冲突 / Merge conflicts
- **症状/Symptom**: 自动合并失败，存在不可自动解决的冲突
- **解决/Fix**: 使用 `/合并 --resolve` 启动冲突解决模式；先rebase base branch再重试；标记需要手动解决的冲突块

## 边界情况 / Edge Cases

- **Force push保护**: 检测到 `--force` 时要求双重确认；禁止对 main/master 的force push
- **PR分支被删除**: 远程分支已被合并后删除 — 从本地worktree恢复，使用 `--recover` 重建
- **超大PR (>500 files)**: 使用 `--split` 拆分为多个小PR；建议审查按模块分组
- **Draft PR转换**: Draft转换为Ready后，重新触发全部验证流程
- **跨仓库PR**: 涉及多个仓库的变更使用 `/合并 --cross-repo` 协调多个PR的合并顺序

## AIGC检测意识 / AIGC-Aware Output

合并报告和PR描述必须包含具体命令、量化判断条件和数字状态，不能用"进展顺利""已完成大部分"等空洞表述。参见 `rules/anti-aigc.md` 了解流程文档的反AIGC规则。

核心要求：
- 每个操作步骤必须可直接复制粘贴执行
- 判断条件必须量化：用退出码、百分比、具体数值，不用"通过""足够"
- 状态报告必须用数字：11/15、73%，不用"大部分""一些"

## 版本历史 / Version History

| 版本 | 日期 | 变更 |
|------|------|------|
| 1.0.0 | 2026-04-01 | 初始版本，5阶段PR工作流 |
| 1.1.0 | 2026-05-09 | 添加安全规则，性能管理，排查，边界情况，3个rule文件 |

## See Also / 相关技能

- `/把关` from **ba-guan** — 合并前的发布前审查 / Pre-publish review before merge
- `/architect phase` from **master-architect** — 按阶段进行架构验证 / Phase-by-phase architecture validation
- `/自控` from **zi-kong** — 带自我审查的自主 PR 迭代 / Autonomous PR iteration with self-review
