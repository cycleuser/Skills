# Triage Report Format

Standardized output format for GitHub issue/PR triage. Every report must include executive summary, per-item analysis with evidence, priority ordering, and actionable recommendations.

## Report Structure

```markdown
# Triage Report: <repo-name>

**Date**: YYYY-MM-DD
**Scope**: Open issues and PRs as of <timestamp>
**Total Items**: N issues, M PRs

## Executive Summary

3-5 lines covering: most critical items, common patterns, recommended immediate actions.

Example:
"23 open issues analyzed: 2 P0 (build failure, data loss), 5 P1 (core feature gaps).
Most issues cluster around authentication module (8/23). Immediate action: fix #142
(build broken on Python 3.12) and #156 (session data corruption on concurrent access)."

## Priority Actions

| Priority | Item | Type | Impact | Recommended Action |
|----------|------|------|--------|-------------------|
| P0 | #142 | Bug | Build broken | Fix compatibility in `compat.py:45` |
| P0 | #156 | Bug | Data loss | Add lock in `session.py:78` |
| P1 | #89 | Feature | Auth module | Schedule for next sprint |
| ... | ... | ... | ... | ... |

## Per-Item Analysis

### Issue #142: Build failure on Python 3.12

- **Type**: Bug
- **Priority**: P0 (blocker)
- **Scope**: Module `utils`
- **Evidence**: 
  - Failing CI: [github.com/org/repo/actions/runs/12345]
  - Root cause: `compat.py:45` uses `datetime.utcnow()` removed in 3.12
- **Impact**: All users on Python 3.12 cannot install
- **Recommendation**: Replace `datetime.utcnow()` with `datetime.now(timezone.utc)`
- **Effort**: Trivial (1-line fix)

### Issue #156: Session data corruption on concurrent access

- **Type**: Bug
- **Priority**: P0 (blocker)
- **Scope**: Cross-cutting (session management)
- **Evidence**:
  - User report: [github.com/org/repo/issues/156#issuecomment-789]
  - Code path: `session.py:78` writes without lock
  - Related: #89 (auth module redesign may solve this)
- **Impact**: Data loss for concurrent users
- **Recommendation**: Add threading.Lock around session writes
- **Effort**: Small (3-5 lines)

[Continue for all items...]

## Cross-Reference Matrix

| Issue/PR | Module | Related | Blocking | Blocked By |
|----------|--------|---------|----------|-----------|
| #142 | utils | - | - | - |
| #156 | session | #89 | - | - |
| #89 | auth | #156, #201 | #201 | - |
| PR #198 | api | #89 | - | #89 |

## Trend Analysis

- Issue age distribution: [numbers]
- PR staleness: [how many PRs need attention]
- Module hotspots: [which modules have most issues]
- Common labels: [frequency analysis of labels]

## Recommendations

1. **Immediate** (this week): Fix P0 items #142, #156
2. **Short-term** (this sprint): Address P1 items, review stale PRs
3. **Strategic**: Auth module redesign (#89) would resolve 4 related issues
```

## Evidence Format

Every conclusion requires a GitHub permalink as evidence:

```
Good: "Root cause: deprecated API call at compat.py:L45 [github.com/org/repo/blob/abc123/utils/compat.py#L45]"
Bad: "There's a bug in compat.py" (no permalink, no line number)
```

### Evidence Types

1. **Code permalink**: `repo/blob/SHA/path/file.py#L123` — always use commit SHA, not branch
2. **CI run**: Link to specific failed GitHub Actions run
3. **User report**: Quote specific comment with permalink
4. **Related work**: Cross-reference issue/PR numbers
5. **External reference**: Link to docs, StackOverflow, upstream issues

## Output Variants

### Markdown (default)
Full report as above. Best for human review and Git commits.

### JSON Summary
```json
{
  "repo": "org/repo",
  "date": "2026-05-08",
  "total_issues": 23,
  "total_prs": 7,
  "priority_summary": {"P0": 2, "P1": 5, "P2": 8, "P3": 8},
  "items": [
    {
      "number": 142,
      "type": "Bug",
      "priority": "P0",
      "title": "Build failure on Python 3.12",
      "evidence": ["compat.py:L45 deprecated API"],
      "recommendation": "Replace datetime.utcnow()"
    }
  ]
}
```

### Table-only (for quick scan)
Just the Priority Actions table — useful for pasting into Slack/Discord.

## Quality Rules

1. **Every item gets analyzed** — no "low priority, skip" shortcuts
2. **Every claim has a permalink** — no unsupported assertions
3. **Recommendations are actionable** — not "should be fixed" but "fix X by changing Y"
4. **No editorial opinions** — state facts, classify, recommend. No "this is terrible code."
5. **Read-only guarantee** — triage never modifies repository state