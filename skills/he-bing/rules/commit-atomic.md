# Atomic Commits / 原子提交

Principles and practices for creating small, focused, self-contained commits.

## Core Principle / 核心原则

**One logical change per commit.** Each commit should represent a single, coherent unit of work that:

1. Makes sense on its own — can be understood without other commits
2. Can be reverted independently — reverting doesn't break other changes
3. Passes tests on its own — every commit leaves the codebase in a working state
4. Has a clear purpose — the "why" is obvious from the commit message

## Conventional Commit Format / 提交信息格式

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Type Definitions

| Type | Meaning | Version Impact | Example |
|------|---------|---------------|---------|
| `feat` | New feature | minor | `feat(auth): add JWT token refresh` |
| `fix` | Bug fix | patch | `fix(api): handle null response body` |
| `refactor` | Code restructuring | none | `refactor(utils): extract date formatter` |
| `docs` | Documentation | none | `docs(api): update authentication guide` |
| `test` | Adding tests | none | `test(auth): cover token expiry edge case` |
| `perf` | Performance | none | `perf(query): add index on user_id` |
| `chore` | Maintenance | none | `chore(deps): update eslint to v9` |
| `ci` | CI/CD changes | none | `ci: add Node 22 to test matrix` |
| `build` | Build system | none | `build: configure webpack code splitting` |

### Breaking Changes

Append `!` after type, or add `BREAKING CHANGE:` in footer:

```
feat(api)!: change user endpoint response format

BREAKING CHANGE: /api/users now returns {data: [...]} instead of [...]
Migration: access response.data instead of response directly
```

### Scope Guidelines

- Use **module name** as scope: `auth`, `api`, `db`, `ui`, `config`
- Keep scope **short**: 1-2 words maximum
- Use **consistent naming**: same module always has same scope name

### Subject Rules

1. **Imperative mood**: "add feature" not "added feature" or "adds feature"
2. **No period**: Don't end with `.`
3. **Lowercase start**: Don't capitalize first letter
4. **Max 50 chars**: Keep it short; detail goes in body
5. **No ticket number**: Put issue references in footer, not subject

### Body Rules

1. **Explain why**, not what — the diff shows what changed
2. **Wrap at 72 chars**
3. **Separate from subject** with blank line
4. **Optional**: Only include if commit needs explanation beyond subject

### Footer Rules

1. **Reference issues**: `Closes #123` or `Fixes #456`
2. **Breaking changes**: `BREAKING CHANGE: description`
3. **Co-authors**: `Co-authored-by: Name <email>`
4. **One per line** for multiple references

## Splitting Large Changes / 拆分大型变更

### Strategy: Vertical Slice Ordering

When a feature requires changes across multiple concerns, split by **vertical slice** (each commit is a working increment):

```
Commit 1: feat(auth): add JWT token generation and validation
  - Add jwt.encode/decode utilities
  - Add token creation endpoint
  - Tests for token generation

Commit 2: feat(auth): add token refresh endpoint
  - Add refresh endpoint
  - Add refresh logic
  - Tests for refresh

Commit 3: feat(auth): add authentication middleware
  - Add middleware that validates tokens
  - Apply middleware to protected routes
  - Tests for middleware

Commit 4: docs(auth): update API documentation for auth endpoints
  - Document token creation, refresh, and middleware
```

### Strategy: Preparation → Implementation → Tests

For complex refactors, split into three phases:

```
Commit 1: refactor(utils): extract date formatting to separate module
  - Create new utils/date.py with extracted functions
  - Re-export from old location for compatibility
  - No behavior change

Commit 2: refactor(utils): migrate callers to new date module
  - Update all imports to use new module
  - Remove re-exports from old location
  - Existing tests still pass

Commit 3: test(utils): add comprehensive tests for date module
  - Unit tests for each format function
  - Edge cases: timezone, invalid input, overflow
```

### Strategy: Config First, Code Second

When adding a new feature that requires config changes:

```
Commit 1: feat(config): add auth configuration schema
  - Add auth config to config module
  - Add defaults
  - Add validation

Commit 2: feat(auth): implement JWT authentication
  - Use config from previous commit
  - Implement auth logic
  - Tests
```

### Pattern: What NOT to Split

Some changes should stay together in one commit:

- **Bug fix + regression test**: The fix and test prove each other
- **Rename + all references**: Splitting leaves broken references
- **Add field + all usages**: Half-implemented field is worse than whole feature
- **Security fix**: Don't separately commit the test that reveals the vulnerability

## Commit Message Do's and Don'ts / 提交信息规范

### Do

```
feat(auth): add password reset flow

Implement password reset with email verification.
Users request reset, receive email with time-limited token,
and can set new password within 30 minutes.

Closes #234
```

```
fix(api): prevent null pointer when user session expires

Session expiry during API call caused 500 error because
user object was None. Add explicit None check and return
401 Unauthorized instead.

Fixes #567
```

```
refactor(db): extract connection pooling to separate module

Connection pool management was spread across 3 files.
Extracted to db/pool.py with clear API. No behavior change.
External callers unchanged via re-exports.
```

### Don't

```
# DON'T: Vague subject
fix: fixed stuff

# DON'T: Past tense
fixed(api): handled null response

# DON'T: Ticket in subject
feat(#123): add login

# DON'T: Mega commit
feat: implement entire authentication system

# DON'T: Unrelated changes in one commit
feat(auth): add login and also fix typo in README

# DON'T: Empty or meaningless subject
chore: updates

# DON'T: Describing what instead of why
fix(api): added if statement to check for null

# DO: Explain WHY
fix(api): return 401 instead of 500 on session expiry
```

## Handling Edge Cases / 处理边缘情况

### Partial Staging

```bash
# Stage specific hunks from a file
git add -p src/auth/login.py

# Stage specific files only
git add src/auth/login.py src/auth/tests/test_login.py

# Stage everything except one file
git add .
git reset HEAD -- src/config/local.env
```

### Splitting an Already-Committed Change

```bash
# Soft reset to undo commit but keep changes staged
git reset --soft HEAD~1

# Unstage everything
git reset HEAD .

# Now re-stage in logical groups and commit each
git add src/auth/jwt.py
git commit -m "feat(auth): add JWT token generation"

git add src/auth/middleware.py
git commit -m "feat(auth): add authentication middleware"

git add src/auth/tests/
git commit -m "test(auth): cover JWT and middleware"
```

### Fixing the Last Commit

```bash
# Only if NOT yet pushed to remote
git add forgotten_file.py
git commit --amend -m "feat(auth): add JWT authentication"

# If already pushed, create a new fix commit instead
git add fix_file.py
git commit -m "fix(auth): add missing JWT import"
```

## Atomic Commit Verification / 原子提交验证

Before considering a commit atomic, verify:

- [ ] `git show --stat HEAD` shows coherent related files only
- [ ] `git checkout HEAD~1 && pytest -x && git checkout -` passes (previous commit works)
- [ ] Reverting this commit alone doesn't break the codebase
- [ ] Commit message explains the "why", not just the "what"
- [ ] No unrelated formatting, import, or config changes mixed in
- [ ] Tests are either in the same commit (for bug fixes) or a dedicated test commit