# Evidence Collection / 证据收集

Rules for extracting, linking, and presenting evidence from GitHub with permalinks.

## Core Evidence Principle / 核心证据原则

**Every factual claim must be backed by a GitHub permalink.** No assertion without proof.

Pattern: `Claim → Evidence Link → Impact Assessment`

## Permalink Format / 永久链接格式

### Standard GitHub Permalink

```
https://github.com/{owner}/{repo}/blob/{commit_sha}/{path}#L{start}-L{end}
```

**Always use commit SHA, never branch name.** Branch names change; commit SHAs are permanent.

### Getting Permalinks

```bash
# Get current HEAD commit SHA
CURRENT_SHA=$(git rev-parse HEAD)

# Get SHA for a specific tag/version
TAG_SHA=$(git rev-parse v1.2.0^{commit})

# Get SHA for a specific file at a specific commit
FILE_SHA=$(git log -1 --format="%H" -- path/to/file.py)

# Construct permalink
echo "https://github.com/${OWNER}/${REPO}/blob/${FILE_SHA}/src/module/auth.py#L45-L50"
```

### From GitHub Web UI

1. Navigate to file
2. Press `Y` to permalink (canonical URL with commit SHA)
3. Select line range (click line number, shift-click end range)
4. Copy URL — this is your permalink

### From GitHub API

```bash
# Get file content with line numbers at specific commit
gh api "repos/{owner}/{repo}/contents/{path}?ref={sha}" \
  --jq '.content' | base64 -d | cat -n | sed -n '45,50p'

# Get blame for specific lines (who wrote this code)
gh api "repos/{owner}/{repo}/blame?path={path}&sha={sha}" \
  --jq '.ranges[] | select(.start_line <= 50 and .end_line >= 45)'

# Get commit that introduced specific lines
git log -L '45,50:path/to/file.py' --format="%H %s" | head -1
```

## Evidence Collection Workflow / 证据收集工作流

### For Issues

```bash
# Step 1: Get issue metadata
gh issue view "$ISSUE_NUMBER" \
  --repo "{owner}/{repo}" \
  --json title,body,labels,createdAt,author,assignees,comments

# Step 2: Extract code references from issue body
# Look for: file paths, line numbers, stack traces, error messages
echo "$ISSUE_BODY" | grep -oE 'src/[a-zA-Z0-9_./-]+\.[a-z]+:[0-9]+'
echo "$ISSUE_BODY" | grep -oE 'File "[^"]+", line [0-9]+'

# Step 3: Locate relevant code at the commit where issue was reported
# Use issue creation date to find relevant commit
ISSUE_DATE=$(gh issue view "$ISSUE_NUMBER" --repo "{owner}/{repo}" --json createdAt -q .createdAt)
COMMIT_SHA=$(git log --before="${ISSUE_DATE}" -1 --format="%H")

# Step 4: Build permalinks for referenced code
for ref in $CODE_REFS; do
    file=$(echo "$ref" | cut -d: -f1)
    line=$(echo "$ref" | cut -d: -f2)
    echo "https://github.com/{owner}/{repo}/blob/${COMMIT_SHA}/${file}#L${line}"
done
```

### For Pull Requests

```bash
# Step 1: Get PR metadata
gh pr view "$PR_NUMBER" \
  --repo "{owner}/{repo}" \
  --json title,body,files,additions,deletions,changedFiles,commits,reviews

# Step 2: Get changed files with diff
gh pr diff "$PR_NUMBER" --repo "{owner}/{repo}" > /tmp/pr-diff.txt

# Step 3: Build evidence for each changed file
gh pr view "$PR_NUMBER" --repo "{owner}/{repo}" --json files \
  --jq '.files[] | .path'

# Step 4: For each file, get the PR's head commit
PR_SHA=$(gh pr view "$PR_NUMBER" --repo "{owner}/{repo}" --json headRefOid -q .headRefOid)

# Step 5: Build permalinks
for file in $CHANGED_FILES; do
    echo "https://github.com/{owner}/{repo}/blob/${PR_SHA}/${file}"
done
```

## Building Evidence Chains / 构建证据链

### Structure

Every claim follows this pattern:

```markdown
**Claim**: {what you assert}

**Evidence**: [{description}]({permalink})

**Impact**: {why this matters, what could happen}
```

### Example: Bug Report Evidence Chain

```markdown
**Claim**: Authentication bypass allows access without valid token

**Evidence**: [auth middleware skips validation for OPTIONS requests](https://github.com/owner/repo/blob/abc123/src/middleware/auth.py#L23-L28)

**Impact**: Any unauthenticated user can access protected endpoints by sending an OPTIONS request. This affects all routes using the auth middleware, estimated 15 endpoints.

**Reproduction**: Send `OPTIONS /api/admin/users` without Authorization header — receives 200 OK with data instead of 401.
```

### Example: Code Quality Evidence Chain

```markdown
**Claim**: Function `process_payment` has 8 responsibilities and should be decomposed

**Evidence**: [process_payment handles validation, calculation, API call, error mapping, logging, notification, DB update, and response formatting](https://github.com/owner/repo/blob/def456/src/services/payment.py#L112-L245)

**Impact**: High cognitive load for reviewers, difficult to test individual behaviors, any change to one concern risks breaking others.
```

## Cross-Referencing / 交叉引用

### Linking Related Items

```bash
# Find issues mentioned in a PR body
gh pr view "$PR_NUMBER" --json body -q .body | grep -oE '#[0-9]+'

# Find PRs that reference an issue
gh pr list --repo "{owner}/{repo}" --search "fixes #${ISSUE_NUMBER}" --json number,title

# Find issues with similar labels
gh issue list --repo "{owner}/{repo}" --label "bug" --json number,title

# Check if PR author also created related issues
gh issue list --repo "{owner}/{repo}" --author "$PR_AUTHOR" --json number,title
```

### Cross-Reference Table Format

```markdown
## Cross-References

| Issue | PRs | Code Area | Status |
|-------|-----|-----------|--------|
| #234 | #256 | [auth/login.py](https://github.com/owner/repo/blob/abc/src/auth/login.py#L10) | Open |
| #234 | #260 | [auth/middleware.py](https://github.com/owner/repo/blob/abc/src/auth/middleware.py#L5) | Merged |
| #189 | None | [api/routes.py](https://github.com/owner/repo/blob/abc/src/api/routes.py#L88) | Stale |
```

### Building Timeline

```bash
# When was related code last modified?
git log --follow --format="%H %ai %s" -- path/to/file.py | head -10

# What commits touched this area recently?
git log --since="2024-01-01" --oneline -- src/auth/

# Who has context on this code? (frequent contributors)
git shortlog -sn -- src/auth/ | head -5
```

## Evidence Quality / 证据质量

### Good Evidence

✅ Uses commit SHA, not branch name
✅ Points to specific line range (L10-L25), not entire file
✅ Directly supports the claim
✅ Comes from the relevant commit timeline (matches issue date or PR head)
✅ Includes surrounding context (not just one line)

### Bad Evidence

❌ `https://github.com/owner/repo/blob/main/src/file.py` — no commit SHA, no line numbers
❌ `src/file.py` — no URL at all
❌ Points to `main` branch which may have changed since issue was filed
❌ Generic link to repository root with no file specification
❌ Link to a 500-line file without line range

### Evidence Completeness

For each claim, check:
- [ ] **Specific**: Points to exact code, not vague areas
- [ ] **Current**: Uses commit SHA that existed when issue was filed
- [ ] **Relevant**: Directly supports the claim being made
- [ ] **Contextual**: Includes enough surrounding lines to understand the code
- [ ] **Verifiable**: Any person can click the link and see what you see

## Output Format / 输出格式

Each piece of evidence is written to individual analysis files:

```markdown
## Analysis: Issue #{number} — {title}

**Classification**: {bug/feature/enhancement/docs/refactor}
**Priority**: {P0/P1/P2/P3}
**Scope**: {single-file/module/cross-cutting/architecture}

### Summary
{2-3 sentence description of the issue}

### Evidence

**Claim 1**: {assertion}
- **Evidence**: [description](permalink)
- **Impact**: {consequence}

**Claim 2**: {assertion}
- **Evidence**: [description](permalink)
- **Impact**: {consequence}

### Cross-References
- Related: #{issue_numbers}
- Code: [file references](permalinks)

### Recommended Action
{specific next step with justification}
```