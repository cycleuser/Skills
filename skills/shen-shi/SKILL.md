---
name: shen-shi
version: "1.0.0"
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

# 审视 (GitHub Triage)

GitHub 只读审查技能。分析开放的 Issues 和 PRs，生成有证据支持的报告。

Read-only GitHub analysis skill. Analyzes open issues and PRs with evidence-backed reports.

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

### Phase 2: 并行分析/Parallel Analysis

```
每个 Issue/PR = 1 个后台任务
Each Issue/PR = 1 background task

任务分配/Assignment:
- Issues → /tmp/{datetime}/issue-{N}.md
- PRs → /tmp/{datetime}/pr-{N}.md

分析内容/Analysis:
1. 问题分类/Classification (bug/feature/question)
2. 优先级评估/Priority (P0/P1/P2)
3. 相关代码定位/Code Location
4. 建议行动方案/Recommended Action
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

## 配置选项/Configuration

| 参数/Param | 默认值/Default | 说明/Description |
|-----------|---------------|-----------------|
| parallel_tasks | 10 | 最大并行任务数/Max parallel tasks |
| output_dir | /tmp | 报告输出目录/Report output dir |
| include_closed | false | 是否包含已关闭/Include closed |
