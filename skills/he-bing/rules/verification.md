# Verification / 验证循环

PR verification checklist covering CI, code review, conflict resolution, and merge readiness.

## Verification Gates / 验证门槛

A PR must pass three sequential gates before merging:

```
Gate A: CI Checks ──pass──▶ Gate B: Code Review ──pass──▶ Gate C: Approval ──pass──▶ MERGE
     │                         │                           │
     └──fail──▶ fix ──▶ re-check └──fail──▶ fix ──▶ re-review └──fail──▶ fix ──▶ re-approve
```

Each failure loops back to fix and re-verify at that gate. Maximum 5 cycles per gate before escalating.

## Gate A: CI Checks / CI 检查

### Required CI Status

```bash
# Check all CI statuses for a PR
gh pr checks "$PR_NUMBER"

# Wait for all checks to complete
gh pr checks "$PR_NUMBER" --watch

# Get individual check details
gh api "repos/{owner}/{repo}/commits/{sha}/check-runs" \
  --jq '.check_runs[] | "\(.name): \(.conclusion // .status)"'
```

### Minimum CI Requirements

| Check Category | Required Checks | Blocking |
|---------------|----------------|----------|
| **Lint** | Linter passes | Yes |
| **Typecheck** | Type checker passes | Yes |
| **Unit tests** | Core tests pass | Yes |
| **Integration tests** | Cross-module tests pass | Yes |
| **Build** | Project builds successfully | Yes |
| **Coverage** | Meets threshold (default 70%) | Soft-block |
| **Security scan** | No critical vulnerabilities | Yes |

### CI Failure Resolution

```markdown
## CI Failure Analysis Template

**Check**: {check_name}
**Status**: {failure}
**Log excerpt**:
\`\`\`
{relevant_error_lines}
\`\`\`

**Root cause**: {one-line description}
**Fix**: {what needs to change}
**Files affected**: {list of files}
```

Decision framework:

| Error Pattern | Likely Cause | Fix |
|--------------|-------------|-----|
| `ImportError` / `ModuleNotFoundError` | Missing dependency in requirements | Add to requirements, reinstall |
| `TypeError` | Type mismatch, often from API change | Fix type annotations, update callers |
| `AssertionError` in tests | Code behavior changed but tests not updated | Update test expectations or fix code |
| `SyntaxError` | Invalid syntax, often from merge conflict | Resolve conflict markers |
| `Timeout` | Slow test, infinite loop, or network hang | Add timeout, mock external calls |
| `Permission denied` | CI environment config issue | Update CI config, fix file permissions |

### Coverage Threshold

```bash
# Check coverage percentage
pytest --cov=gangdan --cov-report=term-missing 2>/dev/null | tail -5

# Identify uncovered new code
pytest --cov=gangdan --cov-report=html 2>/dev/null
# Open htmlcov/index.html to see specific uncovered lines
```

If coverage drops below threshold:
1. Identify which new lines are uncovered
2. Determine if they need tests or are legitimately untestable (e.g., `sys.exit()`)
3. Add tests or mark as `# pragma: no cover` with justification

## Gate B: Code Review / 代码审查

### Review Checklist

```markdown
## Code Review Checklist — PR #{number}

### Architecture
- [ ] Changes fit existing module structure
- [ ] No circular dependencies introduced
- [ ] Public API is backward-compatible (or breaking change is documented)

### Code Quality
- [ ] Functions <30 lines, single responsibility
- [ ] Type hints on all public functions
- [ ] Error handling for all external calls
- [ ] No hardcoded values (use config/constants)
- [ ] No commented-out code

### Testing
- [ ] New code has tests
- [ ] Edge cases tested (None, empty, invalid)
- [ ] Tests are independent (no ordering dependency)
- [ ] Test names describe scenario: `test_{given}_{when}_{then}`

### Security
- [ ] No secrets in code (API keys, passwords, tokens)
- [ ] Input validation on all external inputs
- [ ] Auth checks on sensitive endpoints

### Documentation
- [ ] Public API documented with docstrings
- [ ] README updated if new feature
- [ ] Changelog entry added
```

### Review Severity Levels

| Level | Meaning | Action Required |
|-------|---------|----------------|
| **Blocker** | Must fix before merge | Fix and re-request review |
| **Important** | Should fix, but not dangerous | Fix in this PR or create follow-up issue |
| **Nit** | Style preference, minor cleanup | Fix if easy, ignore if not |
| **Question** | Need clarification | Author responds in PR comment |

### Review Response Template

```markdown
## Review Response

**Overall**: {approve/request-changes/comment}

### Blockers
1. [{file}:{line}] {issue} — {why it must be fixed}

### Important
1. [{file}:{line}] {suggestion} — {why it matters}

### Nits
1. [{file}:{line}] {style preference}

### Questions
1. {question about design decision}
```

## Conflict Resolution / 冲突解决

### Detection

```bash
# Check if PR has merge conflicts
gh pr view "$PR_NUMBER" --json mergeable -q .mergeable
# Returns: MERGEABLE, CONFLICTING, or UNKNOWN

# If UNKNOWN, wait and check again (GitHub is computing)
sleep 10
gh pr view "$PR_NUMBER" --json mergeable -q .mergeable
```

### Resolution Strategy

```bash
# Step 1: Enter worktree
cd "$WORKTREE_PATH"

# Step 2: Rebase onto target branch
git fetch origin dev
git rebase origin/dev

# Step 3: If conflicts occur, resolve each
# Git will pause at each conflicting file
# For each conflict:
#   - Open file, find <<<<<<< markers
#   - Choose correct resolution (ours, theirs, or manual)
#   - Stage resolved file: git add <file>
#   - Continue rebase: git rebase --continue

# Step 4: Force push to update PR
git push --force-with-lease origin "$BRANCH_NAME"
```

### Conflict Resolution Decision Tree

```
Conflict in file:
├── Our changes only (theirs deleted/renamed)
│   → Re-apply our changes to new file location
├── Their changes only (we modified, they changed different lines)
│   → Accept both, verify logic still works
├── Both modified same lines
│   → Manual merge: understand both intents, combine correctly
└── Both deleted
    → Confirm deletion intent, remove file
```

### Common Conflict Patterns

| Pattern | Resolution |
|---------|-----------|
| Import conflict | Merge both import sections, sort alphabetically |
| Config conflict | Take ours for defaults, add theirs if new keys |
| Test conflict | Take both test additions, verify they don't overlap |
| Interface conflict | Prefer the version matching current API contract |

## Merge Readiness / 合并就绪

### Pre-Merge Checklist

```markdown
## Merge Readiness — PR #{number}

### Gate A: CI
- [ ] All CI checks pass (green)
- [ ] Coverage meets threshold
- [ ] No security vulnerabilities

### Gate B: Review
- [ ] At least 1 approval received
- [ ] No unresolved change requests
- [ ] All review comments addressed

### Gate C: Approval
- [ ] Required reviewers approved
- [ ] No pending author responses
- [ ] No requested changes pending

### Housekeeping
- [ ] Branch is up to date with target (no conflicts)
- [ ] PR description is complete and accurate
- [ ] Linked issues are referenced (Closes #xxx)
- [ ] No merge commits in branch history (clean rebase)
```

### Merge Command Sequence

```bash
# Final pre-merge verification
gh pr view "$PR_NUMBER" --json \
  mergeable,mergeStateStatus,reviews,statusCheckRollup \
  --jq '{mergeable: .mergeable, state: .mergeStateStatus, reviews: .reviews | map(.state), checks: .statusCheckRollup | map(.conclusion)}'

# Merge (squash by default)
gh pr merge "$PR_NUMBER" --squash --admin

# Verify merge completed
gh pr view "$PR_NUMBER" --json state -q .state
# Expected: MERGED
```

## Post-Merge Cleanup / 合并后清理

```bash
# Step 1: Delete remote branch
git push origin --delete "$BRANCH_NAME"

# Step 2: Remove worktree
git worktree remove "$WORKTREE_PATH"

# Step 3: Delete local branch
git branch -d "$BRANCH_NAME"

# Step 4: Prune stale references
git worktree prune
git fetch origin --prune

# Step 5: Update local main
cd "$MAIN_REPO"
git checkout dev
git pull origin dev

# Step 6: Verify clean state
git worktree list
git branch --list "${BRANCH_NAME}"
# Both should show no results for the merged branch
```

### Cleanup Verification

```bash
# Confirm no orphaned resources remain
git worktree list | grep -c "$BRANCH_NAME"  # Should be 0
git branch --list "$BRANCH_NAME"            # Should be empty
git ls-remote origin "$BRANCH_NAME"         # Should be empty

# Confirm local repo is up to date
git log origin/dev --oneline -1
# Should show the merge commit
```