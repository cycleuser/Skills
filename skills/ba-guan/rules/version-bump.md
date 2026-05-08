# Version Bump Rules / 版本升级规则

Semantic versioning decisions based on change types. Determines whether to bump major, minor, or patch.

## SemVer Decision Framework / 语义版本决策框架

### Core Rule

```
Given a version MAJOR.MINOR.PATCH:

MAJOR → Breaking changes (incompatible API changes)
MINOR → New features (backward-compatible additions)
PATCH → Bug fixes (backward-compatible bug fixes)
```

### Decision Tree

```
Is there any breaking change?
├── YES → BUMP MAJOR (1.x.y → 2.0.0)
│   └── Even ONE breaking change = major bump
│       └── Document ALL breaking changes in changelog
└── NO → Is there any new feature?
    ├── YES → BUMP MINOR (1.2.y → 1.3.0)
    │   └── Even ONE new feature = minor bump
    │       └── Can also include patches in same release
    └── NO → Is there any bug fix?
        ├── YES → BUMP PATCH (1.2.3 → 1.2.4)
        │   └── Only if NO new features and NO breaking changes
        └── NO → No version bump needed
            └── Docs-only or cosmetic-only changes
```

## Breaking Change Detection / 破坏性变更检测

### Definite Breaking Changes → Major Bump

1. **Removed public API**: Function, class, method, or export removed
2. **Changed function signature**: Parameter removed or added without default, parameter order changed
3. **Changed return type**: Return type changed to incompatible type
4. **Changed error types**: Different exceptions raised, existing exceptions no longer raised
5. **Changed defaults**: Default value of existing option changed (changes behavior for existing users)
6. **Removed config options**: Previously supported option no longer exists
7. **Database schema change**: Column removed, type changed without migration
8. **Protocol change**: API endpoint removed, request/response format changed

Detection commands:

```bash
# Detect removed exports (JavaScript)
git diff "v${PUBLISHED}"..HEAD -S "export " -- '*.ts' '*.js' | grep "^-.*export"

# Detect removed public functions (Python)
git diff "v${PUBLISHED}"..HEAD -S "def " -- '*.py' | grep "^-.*def " | grep -v "^-.*def _"

# Detect changed function signatures
git diff "v${PUBLISHED}"..HEAD -- '*.py' | grep -A2 "^-.*def " | grep -v "^--"
```

### Possibly Breaking → Investigate Further

| Pattern | Why Possibly Breaking | How to Verify |
|---------|---------------------|---------------|
| New required parameter | Callers must provide it | Check if parameter has default value |
| Changed error message | Downstream code may parse messages | Check if anyone uses `str(exception)` |
| Changed logging format | Log parsers may break | Check monitoring/alerting dependencies |
| Dependency major bump | Transitive breaking change | Check dependency's changelog |
| Changed file structure | Import paths change | Check if re-exports maintained |

### Definite Non-Breaking → Minor or Patch

- Added new public function/class/method
- Added optional parameter with default value
- Added new field to response object (clients ignore unknown)
- Added new API endpoint
- Fixed bug that was returning wrong data
- Improved error messages (without changing exception types)
- Performance improvement
- Documentation update

## Version Detection / 版本检测

### npm Package

```bash
# Get all published versions
npm view package-name versions --json 2>/dev/null

# Get latest published version
PUBLISHED=$(npm view package-name version 2>/dev/null || echo "0.0.0")

# Get local version
LOCAL=$(node -p "require('./package.json').version" 2>/dev/null || echo "unknown")

# Check if version already published
npm view "package-name@${LOCAL}" version 2>/dev/null && echo "ALREADY PUBLISHED" || echo "NEW VERSION"
```

### Python Package

```bash
# Get all published versions from PyPI
pip index versions package-name 2>/dev/null | head -1

# Or via API
curl -s "https://pypi.org/pypi/package-name/json" 2>/dev/null | python3 -c "import sys,json; print(json.load(sys.stdin)['info']['version'])"

# Get local version
LOCAL=$(python3 -c "import configparser; c=configparser.ConfigParser(); c.read('pyproject.toml'); print(c['project']['version'])" 2>/dev/null || echo "unknown")

# Alternative: parse from __init__.py or _version.py
LOCAL=$(python3 -c "from package import __version__; print(__version__)")
```

### Git Tags

```bash
# List all version tags
git tag -l 'v*' --sort=-version:refname | head -20

# Get latest tag
LATEST_TAG=$(git describe --tags --abbrev=0 2>/dev/null || echo "v0.0.0")

# Commits since last tag
git log "${LATEST_TAG}..HEAD" --oneline
```

## Change Analysis → Version Recommendation / 变更分析到版本建议

### Step 1: Categorize All Changes

```bash
# Get commit messages since last release
git log "v${PUBLISHED}"..HEAD --pretty=format:"%s" | while read -r msg; do
    type=$(echo "$msg" | sed -n 's/^\(feat\|fix\|refactor\|docs\|chore\|perf\|test\|build\|ci\)(\(.*\)):.*$/\1/p')
    scope=$(echo "$msg" | sed -n 's/^\(feat\|fix\|refactor\|docs\|chore\|perf\|test\|build\|ci\)(\(.*\)):.*$/\2/p')
    echo "${type:-other}|${scope:-global}|${msg}"
done
```

### Step 2: Map to Version Impact

| Conventional Commit Type | Version Impact | Unless |
|-------------------------|---------------|--------|
| `feat!` or `feat!(` | MAJOR | — |
| `feat` | MINOR | — |
| `fix` | PATCH | — |
| `perf` | PATCH | — |
| `refactor` | NONE* | Unless it changes public API |
| `docs` | NONE | — |
| `test` | NONE | — |
| `chore` | NONE | — |
| `ci` | NONE | — |
| `build` | NONE | Unless dependency major bump |

*Merge to highest impact across all commits.

### Step 3: Generate Recommendation

```markdown
## Version Recommendation

**Current version**: {current}
**Recommended version**: {recommended}
**Bump type**: {major|minor|patch}

### Justification

**Breaking changes** ({count}):
- {description} [commit permalink]

**New features** ({count}):
- {description} [commit permalink]

**Bug fixes** ({count}):
- {description} [commit permalink]

### Pre-release Considerations

- [ ] All breaking changes documented in migration guide
- [ ] Deprecation warnings added in previous minor release (if applicable)
- [ ] Changelog entry prepared
- [ ] Package version updated in all manifest files
```

## Pre-release Checklist / 发布前清单

Before finalizing version bump:

1. **Version consistency**: Same version in `package.json`, `pyproject.toml`, `__init__.py`, `CHANGELOG.md`
2. **Changelog entry**: Added under `[Unreleased]` or new version heading
3. **No snapshot dependencies**: No `*` or `latest` version ranges in production deps
4. **Lock file updated**: `package-lock.json` or `poetry.lock` committed and matching
5. **Git tag ready**: Tag format matches existing convention (`v1.2.3` or `1.2.3`)