---
name: shen-shi
version: "1.1.0"
description: |
  Read-only GitHub triage for issues and PRs with evidence-backed analysis and parallel processing.

  Triggers when: Analyzing GitHub Issues or PRs, generating review reports, or triaging problems.

  Commands:
  - /审视 analyze <repo> - Analyze all open issues and PRs in a repo
  - /审视 issues <repo> - Analyze issues only
  - /审视 prs <repo> - Analyze PRs only
  - /审视 <URL> - Analyze a specific issue or PR
  - /analyze <repo> - English command for repo analysis
  - /analyze issues <repo> - Analyze issues only (English)
  - /analyze prs <repo> - Analyze PRs only (English)

  Capabilities: GitHub data reading, issue classification, evidence collection with permalinks, report generation, parallel background processing
author: cycleuser
license: MIT
status: Beta
---

## Safety Rules

参见 [_shared/core/safety-rules.md](../_shared/core/safety-rules.md) — 所有安全规则从共享层加载。

# 审视 (GitHub Triage)

GitHub 只读审查技能。分析开放的 Issues 和 PRs，生成有证据支持的报告。

Read-only GitHub analysis skill. Analyzes open issues and PRs with evidence-backed reports.

<role>
Read-only GitHub triage orchestrator. Fetch open issues/PRs, classify, spawn 1 background task per item. Each task analyzes and writes a report file. ZERO GitHub mutations.
</role>

## Quick Commands

| Command | Description |
|---------|-------------|
| `/审视 <仓库>` | 分析仓库所有开放 Issue 和 PR |
| `/审视 issues <仓库>` | 只分析 Issues |
| `/审视 prs <仓库>` | 只分析 PRs |
| `/审视 <URL>` | 分析特定 Issue 或 PR |
| `/analyze <repo>` | Analyze all open items |
| `/analyze issues <repo>` | Analyze issues only |
| `/analyze prs <repo>` | Analyze PRs only |

## 核心原则/Core Principles

### 只读不写/Read-Only Policy

```
【绝对禁止/NEVER】
- gh issue comment - 不评论
- gh issue close - 不关闭
- gh pr merge - 不合并
- gh api -X POST/PUT/PATCH/DELETE - 不写入

【允许/ALLOWED】
- gh issue view / gh pr view - 读取数据
- gh api (GET only) - 读取 API
- git log/show/blame - 读取 git 历史
- Write - 仅写入报告文件到临时目录
```

### 证据规则/Evidence Rule

```
【证据要求】
每个事实陈述必须有 GitHub permalink 作为证明。
Every factual claim requires a GitHub permalink as proof.

Permalink 格式/Format:
https://github.com/{owner}/{repo}/blob/{commit_sha}/{path}#L{start}-L{end}

示例/Example:
❌ 错误/Wrong: "代码有 bug"
✓ 正确/Correct: "代码有 bug [证据](https://github.com/owner/repo/blob/abc123/src/file.py#L45-L50)"
```

## 工作流程/Workflow

### Phase 1: 数据收集/Data Collection

```markdown
## 数据收集/Data Collection

**仓库/Repo**: {owner}/{repo}
**时间/Time**: {timestamp}

### 开放 Issues/Open Issues
| # | 标题/Title | 标签/Labels | 创建时间/Created | 优先级/Priority |
|---|-----------|------------|----------------|---------------|
| 1 | {title} | {labels} | {date} | P0/P1/P2 |

### 开放 PRs/Open PRs
| # | 标题/Title | 状态/Status | CI 状态/CI | 创建时间/Created |
|---|-----------|------------|----------|----------------|
| 1 | {title} | {status} | {ci} | {date} |
```

### Phase 2: Spawn Background Tasks

**1 ISSUE/PR = 1 BACKGROUND TASK. NO EXCEPTIONS.**

| Rule | Value |
|------|-------|
| Execution | All tasks in parallel |
| Output | `/tmp/{YYYYMMDD-HHmmss}/issue-{N}.md` or `pr-{N}.md` |
| Evidence | Every claim requires a GitHub permalink |

#### Classification

| Type | Detection |
|------|-----------|
| `ISSUE_QUESTION` | `[Question]`, `?`, "how to" / "why does" |
| `ISSUE_BUG` | `[Bug]`, error messages, stack traces, unexpected behavior |
| `ISSUE_FEATURE` | `[Feature]`, `[RFE]`, `Feature Request` |
| `ISSUE_OTHER` | Anything else |
| `PR_BUGFIX` | Title starts with `fix`, branch contains `fix/`/`bugfix/` |
| `PR_OTHER` | Everything else |

#### Per-Item Report Template

Each task writes to `{REPORT_DIR}/{issue|pr}-{number}.md`:

```markdown
# Issue #{number}: {title}
**Type:** {QUESTION|BUG|FEATURE|OTHER} | **Author:** {author} | **Created:** {createdAt}

## Summary
[1-2 sentence summary with permalink evidence]

## Findings
- [Finding with permalink](https://github.com/{REPO}/blob/{SHA}/{path}#L{N})

## Recommended Action
[Specific, actionable next step]

## Evidence Trail
[All permalinks used in this report]
```

### Phase 3: 报告汇总/Summary Report

```markdown
## 审视报告/Triage Report

**仓库/Repo**: {owner}/{repo}
**日期/Date**: {date}
**分析范围/Scope**: {issues_count} Issues, {prs_count} PRs

### P0 - 紧急/Urgent
| # | 类型/Type | 问题/Issue | 证据/Evidence | 建议/Action |
|---|---------|-----------|--------------|------------|
| 123 | Bug | {描述} | [link] | {action} |

### PR 状态/PR Status
| # | 标题/Title | CI | 审查/Review | 状态/Status |
|---|-----------|---|----------|----------|
| 45 | {title} | ✅ | ⏳ | 待审查/Pending |

### 建议行动/Recommended Actions
1. 优先处理 P0 Issue #123
2. PR #45 需要额外审查
3. ...
```

## 输出目录/Output Directory

```
/tmp/{YYYYMMDD-HHmmss}/
├── issue-{N}.md    # Issue 分析报告
├── pr-{N}.md       # PR 分析报告
└── summary.md      # 汇总报告
```

## 使用示例/Examples

### 示例 1：审视仓库

```
用户/User: /审视 cycleuser/Skills

→ 收集开放 Issues 和 PRs/Collect open items
→ 并行分析每个项目/Parallel analysis
→ 生成报告到 /tmp/{datetime}/Generate reports
→ 输出汇总/Output summary
```

### Example 2: Analyze Specific PR

```
用户/User: /analyze https://github.com/owner/repo/pull/123

→ 读取 PR 详情/Read PR details
→ 检查 CI 状态/Check CI status
→ 审查代码变更/Review code changes
→ 生成分析报告/Generate analysis report
```

## Rules

- [rules/evidence.md](rules/evidence.md) - 证据规则/Evidence Rules
- [rules/classification.md](rules/classification.md) - 问题分类/Classification
- [rules/report-format.md](rules/report-format.md) - 报告格式/Report Format
- [rules/anti-aigc.md](rules/anti-aigc.md) - 分析报告反AIGC检测规则
- [../_shared/core/anti-aigc.md](../_shared/core/anti-aigc.md) - 通用反AIGC检测规则（共享层）
- [../_shared/core/design-principles.md](../_shared/core/design-principles.md) - 共享设计原则

## 配置选项/Configuration

| 参数/Param | 默认值/Default | 说明/Description |
|-----------|---------------|-----------------|
| parallel_tasks | 10 | 最大并行任务数/Max parallel tasks |
| output_dir | /tmp | 报告输出目录/Report output dir |
| include_closed | false | 是否包含已关闭/Include closed |

## Anti-Patterns / 反模式

| 违规 | 严重度 | 后果 |
|------|--------|------|
| 任何 GitHub 写入操作 (comment/close/merge/review/label) | **CRITICAL** | 违反只读原则 |
| 声明无 permalink 证据 | **CRITICAL** | 报告不可信 |
| 多个 Issue/PR 合并为一个分析 | HIGH | 丢失单个项的分析深度 |
| 不使用后台任务 (串行分析) | HIGH | 大仓库超时 |
| 分支名而非 commit SHA 用于 permalink | HIGH | 链接可能失效 |
| 猜测问题根因而非搜索代码库 | HIGH | 报告不准确 |
| 不写报告到 `{REPORT_DIR}` | MAJOR | 输出丢失 |
| 跳过数据收集阶段直接分析 | MAJOR | 缺少上下文 |

## Zero-Action Policy (强化版)

```
【FORBIDDEN - 绝对禁止】
gh issue comment / gh issue close / gh issue edit / gh issue reopen
gh pr comment / gh pr merge / gh pr review / gh pr edit / gh pr close
gh api -X POST / gh api -X PUT / gh api -X PATCH / gh api -X DELETE
git push / git checkout / git fetch / git pull / git worktree
curl -X POST to GitHub API

【ALLOWED - 允许】
gh issue view / gh pr view / gh api (GET only)
git log / git show / git blame / git diff
Write - 仅写入报告文件到临时目录
Grep / Read / Glob - 搜索代码库
```

## Troubleshooting / 排查

### GitHub API rate limit / API限流
- **Symptom / 症状**: 403 errors when querying Issues/PRs
- **Fix / 解决**: Use `--token <ghp_token>` for authenticated requests (5000/hr vs 60/hr); cache results locally to reduce API calls

### Large repository timeout / 大仓库超时
- **Symptom / 症状**: Analyzing repos with >1000 open issues times out
- **Fix / 解决**: Use `/审视 issues <repo> --limit 100` to paginate; increase `--timeout` parameter; analyze by label filter

### Report generation stalls / 报告生成卡住
- **Symptom / 症状**: Report writing hangs at evidence collection phase
- **Fix / 解决**: Check for broken links in issue bodies; use `--skip-links` to skip link validation; reduce `--max-depth` for comment threads

### Mixed-language issues / 多语言议题
- **Symptom / 症状**: Classification accuracy drops on bilingual repositories
- **Fix / 解决**: Use `/审视 <URL> --lang zh` or `--lang en` to force language detection; review classification rules for language-specific patterns

## Edge Cases / 边界情况

- **Empty repository**: If repo has zero open issues/PRs, output "No issues or PRs found" instead of failing
- **Archived repository**: Issues are read-only, mark all as "archived" and skip classification
- **Cross-repository references**: When Issue references another repo's PR, fetch the reference but annotate it as external
- **Deleted comments**: Placeholder text may contain "[deleted]" — skip these in sentiment analysis
- **Bot-generated issues**: Issues from bots (dependabot, stale bot) flagged as `automated` type
- **Issue templates**: Template text in issue body skipped for analysis, only user-filled content used

## AIGC-Aware Output / AIGC检测意识

GitHub triage analysis must include permalink evidence for every claim, specific priority classification, and actionable recommendations. No generic "this seems like a bug" without code-level evidence. See `rules/anti-aigc.md` for anti-AIGC detection rules.

核心要求：
- 每个判断必须有GitHub permalink作为证据
- 不写"这个问题涉及多个方面"，写具体分类和优先级P0/P1/P2
- 建议必须可操作，包含具体修复方案或指派建议

## Version History / 版本历史

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-04-01 | Initial version with read-only GitHub triage |
| 1.1.0 | 2026-05-09 | Added safety rules, evidence.md, classification.md, report-format.md, troubleshooting, edge cases |

## See Also / 相关技能

- `/把关` from **ba-guan** — 基于证据模式的发布前审查 / Pre-publish review with evidence patterns
- `/安检` from **an-jian** — Issues 的安全分类审查 / Security classification of issues
