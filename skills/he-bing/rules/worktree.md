# Worktree Management / 工作树管理

Git worktree management for PR isolation. Create, manage, and clean up worktrees safely.

## Why Worktrees / 为什么用工作树

Worktrees allow working on multiple branches simultaneously without stashing or cloning:

- **Isolation**: Each PR gets its own directory, no file conflicts
- **Parallelism**: Implement feature while main repo stays clean
- **Safety**: Original working directory untouched; no accidental commits to wrong branch
- **Speed**: No full clone needed, shared .git objects save disk space

## Creating Worktrees / 创建工作树

### Standard Flow

```bash
# Step 1: Fetch latest base branch
git fetch origin dev

# Step 2: Create new branch from base
BRANCH_NAME="feat/add-user-auth"
git branch "$BRANCH_NAME" "origin/dev"

# Step 3: Create worktree (outside current repo directory)
WORKTREE_PATH="../$(basename "$PWD")-wt/${BRANCH_NAME}"
mkdir -p "$(dirname "$WORKTREE_PATH")"
git worktree add "$WORKTREE_PATH" "$BRANCH_NAME"

# Step 4: Enter worktree and install dependencies
cd "$WORKTREE_PATH"
[ -f "package-lock.json" ] && npm ci
[ -f "bun.lock" ] && bun install
[ -f "poetry.lock" ] && poetry install
```

### Branch Naming Convention

Format: `<type>/<scope>-<description>`

| Type | Use When | Example |
|------|----------|---------|
| `feat/` | New feature | `feat/auth-jwt-login` |
| `fix/` | Bug fix | `fix/null-pointer-api` |
| `docs/` | Documentation | `docs/api-reference` |
| `refactor/` | Code refactoring | `refactor/extract-validator` |
| `test/` | Test additions | `test/auth-coverage` |
| `chore/` | Maintenance | `chore/update-deps` |
| `perf/` | Performance | `perf/query-optimization` |

Rules:
- Lowercase, hyphenated
- Max 50 characters total
- Include issue number if applicable: `fix/login-timeout-#123`
- No special characters except hyphens and `#`

### Worktree Directory Structure

```
project-root/                    # Main repo (main/dev branch)
project-root-wt/                 # Worktrees parent directory
├── feat/
│   └── add-user-auth/          # Full path: ../project-root-wt/feat/add-user-auth
├── fix/
│   └── login-timeout/          # Full path: ../project-root-wt/fix/login-timeout
└── docs/
    └── api-reference/          # Full path: ../project-root-wt/docs/api-reference
```

## Managing Worktrees / 管理工作树

### List Existing Worktrees

```bash
# Show all worktrees with details
git worktree list

# Output format:
# /path/to/main          abc1234 [dev]
# /path/to/wt/feat/auth  def5678 [feat/auth-jwt]
```

### Switch Between Worktrees

```bash
# Simply cd between directories — no git checkout needed
cd "$MAIN_REPO"       # Back to main
cd "$WORKTREE_PATH"   # To feature worktree
```

### Sync Changes Between Worktrees

```bash
# From any worktree, fetch gets all remote refs
git fetch origin

# If base branch has new commits, rebase feature branch
cd "$WORKTREE_PATH"
git rebase origin/dev
```

### Handle Detached HEAD Worktrees

```bash
# If worktree is in detached HEAD state, create a branch for it
git worktree add --detach "$WORKTREE_PATH" origin/dev
cd "$WORKTREE_PATH"
git checkout -b "$BRANCH_NAME"

# Or create branch directly during worktree creation
git worktree add -b "$BRANCH_NAME" "$WORKTREE_PATH" origin/dev
```

## Merging Strategy / 合并策略

### Strategy Selection

| Strategy | When to Use | Pros | Cons |
|----------|-------------|------|------|
| **Squash merge** | Most PRs; clean history desired | Clean single commit, easy revert | Loses granular history |
| **Merge commit** | Release branches; need full history | Preserves all commits, clear merge point | Cluttered history |
| **Rebase** | Linear history desired; small PRs | Clean linear history, no merge commits | Rewrites history, complex conflicts |

### Default: Squash Merge

```bash
# Preferred for most PRs
gh pr merge "$PR_NUMBER" --squash --admin

# This creates one clean commit on target branch
# Commit message = PR title + description
# Author = PR author
```

### When to Use Merge Commit

- Release branch merges (need to see all feature commits)
- Long-running features with meaningful commit history
- When bisecting by commit is important

```bash
# Merge commit preserves full history
gh pr merge "$PR_NUMBER" --merge
```

### When to Rebase

- Small, focused PRs (1-3 commits)
- When linear history is required by project convention
- NEVER rebase shared branches

```bash
# Rebase before creating PR for clean history
cd "$WORKTREE_PATH"
git rebase origin/dev
git push --force-with-lease  # Only if PR not yet reviewed
```

## Cleanup / 清理工作树

### Standard Cleanup After Merge

```bash
# Step 1: Verify merge completed
gh pr view "$PR_NUMBER" --json state -q .state
# Expected output: MERGED

# Step 2: Remove worktree (safe — checks for uncommitted changes)
git worktree remove "$WORKTREE_PATH"

# Step 3: Delete remote branch
git push origin --delete "$BRANCH_NAME"

# Step 4: Delete local branch
git branch -d "$BRANCH_NAME"

# Step 5: Prune stale worktree references
git worktree prune

# Step 6: Update main repo
cd "$MAIN_REPO"
git fetch origin --prune
git checkout dev
git pull origin dev
```

### Cleanup Safety Guards

```bash
# Guard 1: Never remove worktree with uncommitted changes
# Check for uncommitted changes before removing
if [ -n "$(cd "$WORKTREE_PATH" && git status --porcelain)" ]; then
    echo "WARNING: Uncommitted changes in worktree. Aborting cleanup."
    echo "Changes:"
    cd "$WORKTREE_PATH" && git status --short
    exit 1
fi

# Guard 2: Never remove worktree that hasn't been merged
PR_STATE=$(gh pr view "$PR_NUMBER" --json state -q .state 2>/dev/null || echo "UNKNOWN")
if [ "$PR_STATE" != "MERGED" ]; then
    echo "WARNING: PR #${PR_NUMBER} is ${PR_STATE}, not MERGED. Aborting cleanup."
    exit 1
fi

# Guard 3: Verify worktree path is not root or home directory
if [ -z "$WORKTREE_PATH" ] || [ "$WORKTREE_PATH" = "/" ] || [ "$WORKTREE_PATH" = "$HOME" ]; then
    echo "FATAL: Invalid worktree path '${WORKTREE_PATH}'. Aborting."
    exit 1
fi

# Guard 4: Only remove directories we created (match naming pattern)
case "$WORKTREE_PATH" in
    *-wt/*) ;;  # Our naming pattern — safe
    *) echo "FATAL: Path '${WORKTREE_PATH}' doesn't match worktree pattern. Aborting."; exit 1 ;;
esac

# Guard 5: Double-check with git worktree list
git worktree list | grep -q "$WORKTREE_PATH" || {
    echo "WARNING: '${WORKTREE_PATH}' not in worktree list. May already be removed."
}
```

### Force Cleanup (Emergency Only)

```bash
# Only if worktree is corrupted or cannot be removed normally
# Step 1: Force remove directory
# WARNING: This bypasses safety checks. Use with extreme caution.
if [ -n "$WORKTREE_PATH" ] && [ "$WORKTREE_PATH" != "/" ]; then
    rm -rf "$WORKTREE_PATH"
fi

# Step 2: Clean up git references
git worktree prune

# Step 3: Verify clean state
git worktree list
```

## Troubleshooting / 故障排除

### Worktree Locked

```bash
# Error: cannot lock ref 'refs/heads/feature/xxx'
# Fix: prune stale references
git worktree prune
git update-ref -d "refs/heads/${BRANCH_NAME}" 2>/dev/null || true
```

### Stale Worktree References

```bash
# List and clean
git worktree list           # Show current
git worktree prune          # Remove stale refs
git worktree list           # Verify cleanup
```

### Branch Already Exists

```bash
# If branch name conflicts:
git branch -D "$BRANCH_NAME"  # Delete local branch if no worktree uses it

# Or use different branch name:
BRANCH_NAME="feat/auth-v2-$(date +%Y%m%d)"
```