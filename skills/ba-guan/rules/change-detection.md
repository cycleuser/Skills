# Change Detection / 变更检测

Rules for detecting, parsing, and categorizing code changes before review.

## Git Diff Parsing / Git 差异解析

### Extracting Meaningful Changes

Filter out noise from diffs to focus on substantive changes:

```bash
# Get changed files with stats (ignores whitespace-only changes)
git diff --stat "v${PUBLISHED}"..HEAD -- . ':!*.lock' ':!package-lock.json' ':!yarn.lock'

# Get meaningful diff only (ignore whitespace moves)
git diff "v${PUBLISHED}"..HEAD -w --unified=3

# List files changed, excluding generated/lock files
git diff --name-only "v${PUBLISHED}"..HEAD | grep -v -E '\.(lock|map|min\.(js|css))$'
```

### Distinguishing Meaningful vs Cosmetic Changes

| Category | Examples | Action |
|----------|----------|--------|
| **Cosmetic** | Whitespace, trailing newlines, import reorder, formatting | Skip deep review |
| **Structural** | Renamed files, moved directories, split modules | Track but low priority |
| **Substantive** | Logic changes, new functions, API modifications | Full review required |
| **Critical** | Auth, permissions, data handling, external calls | Deep review + security |

Detection rules:
- **Whitespace-only**: `git diff -w` shows empty → cosmetic
- **Import reorder**: lines starting with `import` moved within import block → cosmetic
- **Comment-only**: only `//` or `/* */` lines changed → cosmetic unless docstrings
- **Lock file changes**: package-lock.json, yarn.lock → structural, skip review
- **Generated files**: `.map`, `.min.js`, `dist/` → skip

### Parsing Diff Hunk Headers

```
@@ -start,count +start,count @@
```

- `count=0`: lines were deleted entirely
- `count=1` with large `-count`: many lines replaced with one (likely refactored)
- Multiple `@@` blocks in same file: file has several independent changes → consider splitting

### Change Grouping Strategy

Group changes by **logical scope**, not file boundaries:

```python
# Group by module/directory, not individual files
groups = {}
for file in changed_files:
    module = file.split('/')[0]  # top-level directory as group key
    if module not in groups:
        groups[module] = []
    groups[module].append(file)

# Limit to max 10 groups; merge smallest groups if exceeded
if len(groups) > 10:
    sorted_groups = sorted(groups.items(), key=lambda x: len(x[1]))
    # Merge smallest groups into "misc" until under limit
    while len(groups) > 10:
        smallest = sorted_groups.pop(0)
        groups.setdefault('misc', []).extend(smallest[1])
        del groups[smallest[0]]
```

## Severity Classification / 严重度分类

### Decision Tree

```
Does the change modify exported/public API?
├── YES → Does it break existing callers?
│   ├── YES → CRITICAL
│   └── NO → Does it add new optional params/fields?
│       ├── YES → HIGH
│       └── NO → MEDIUM (API change, backward compatible)
└── NO → Does it change runtime behavior?
    ├── YES → Does it affect data flow or error handling?
    │   ├── YES → HIGH
    │   └── NO → MEDIUM
    └── NO → Is it test/docs/config only?
        ├── YES → LOW
        └── NO → MEDIUM (internal refactoring)
```

### Severity Levels

| Level | Criteria | Examples | Review Depth |
|-------|----------|----------|-------------|
| **Critical** | Breaking API changes, security-affecting changes | Removed public method, auth bypass fix, changed return type | Full review + security audit |
| **High** | New features, behavior changes, data flow changes | New endpoint, changed validation logic, new dependencies | Full review |
| **Medium** | Internal refactor, non-breaking enhancements, config changes | Extracted helper function, added logging, updated defaults | Standard review |
| **Low** | Docs, tests, formatting, dependency version bumps | README update, new test case, prettier formatting | Quick scan |

### Breaking Change Detection

A change is **breaking** if any of these hold:

1. **Removed or renamed export**: Previously accessible symbol no longer exported
2. **Changed function signature**: Parameters added without defaults, parameter order swapped
3. **Changed return type**: Return type narrows or changes incompatible type
4. **Changed error behavior**: New exceptions thrown, existing exceptions removed
5. **Changed default values**: Default behavior of existing config changes
6. **Removed config option**: Previously supported option no longer exists
7. **Schema change without migration**: Database/API schema that drops fields

Detection commands:

```bash
# Check if exported symbols changed
git diff "v${PUBLISHED}"..HEAD --grep="export\|module\.exports\|public" -- '*.ts' '*.js' '*.py'

# Check if function signatures changed (Python)
git diff "v${PUBLISHED}"..HEAD -S "def " -- '*.py'

# Check for dependency version changes
git diff "v${PUBLISHED}"..HEAD -- package.json pyproject.toml requirements.txt
```

### Backward-Compatible Changes

The following are **not** breaking:
- Adding new exported function/class
- Adding optional parameter with default value
- Adding new field to response (clients ignore unknown fields)
- Adding new enum variant (if clients use switch-default)
- Deprecating (without removing) a feature
- Internal implementation change with same external behavior

## Change Impact Analysis / 变更影响分析

For each change group, assess impact radius:

```markdown
## Change Group: {name}

**Files**: {file_count} files, +{added}/-{removed} lines
**Severity**: {critical|high|medium|low}
**Breaking**: {yes/no/uncertain}
**Affected modules**: {list modules touched}
**Risk areas**: {list areas that could be affected}

### Blast Radius
- Direct consumers: {who calls this code}
- Transitive effects: {what depends on direct consumers}
- Config/deploy impact: {does this need config/deploy changes}
```