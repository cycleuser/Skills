# Review Roles / 审查角色

Five parallel review perspectives for holistic code review. Each role has specific focus areas and checklists.

## Role 1: Architect / 架构师

**Focus**: Design decisions, API contracts, data flow, system structure.

### Checklist

- [ ] **API contract stability**: Are public interfaces backward-compatible? Breaking changes justified?
- [ ] **Dependency direction**: Do dependencies point inward (stable depends on volatile, not reverse)?
- [ ] **Module boundaries**: Are responsibilities clearly separated? No god modules?
- [ ] **Data flow clarity**: Can you trace data from input to output without jumps across 5+ files?
- [ ] **Error propagation**: Do errors bubble up to the right handler, not get swallowed mid-chain?
- [ ] **Scalability impact**: Does this change impose new bottlenecks? O(n²) where before O(n)?
- [ ] **Configuration design**: Are new configs scoped correctly? No global state hiding in module-level vars?
- [ ] **Extensibility**: Can the next feature be added without modifying this code (open-closed principle)?

### Red Flags

- Circular dependencies between modules
- God class/function (>200 lines or >8 responsibilities)
- New global mutable state
- Mixed abstraction levels in same module
- Feature envy: method uses more data from another class than its own

### Assessment Format

```markdown
### Architecture Review

**Pattern compliance**: {consistent|inconsistent} — {detail}
**Cohesion score**: {high|medium|low} — {explanation}
**Coupling score**: {low|medium|high} — {explanation}

**Decisions**:
- ✅ {good decision with permalink}
- ❌ {problematic decision with permalink}
- ⚠️ {questionable decision with permalink}

**Recommendation**: {pass|improve|reject}
```

## Role 2: Developer / 开发者

**Focus**: Code quality, patterns, error handling, readability, maintainability.

### Checklist

- [ ] **Naming clarity**: Do names reveal intent without comments? No `data`, `info`, `result` abstractions
- [ ] **Function length**: Functions <30 lines. If longer, can it be decomposed?
- [ ] **DRY**: No duplicated logic within 3+ locations. Extracted to shared utility if duplicated
- [ ] **Error handling**: Every external call wrapped in try/except. Errors include context, not bare messages
- [ ] **Magic numbers**: No unexplained literals. Named constants or config values
- [ ] **Type safety**: Type hints on all function signatures. No `Any` without justification
- [ ] **Null/None handling**: Explicit None checks, no silent None propagation
- [ ] **Code comments**: Comments explain "why", not "what". No commented-out code blocks
- [ ] **Immutability**: Prefer immutable data where possible, avoid unnecessary mutation

### Code Smell Detection

| Smell | Detection | Action |
|-------|-----------|--------|
| Long method | >30 lines | Extract method |
| Deep nesting | >3 levels | Guard clauses, early return |
| Feature envy | Uses more data from other class than own | Move method |
| Shotgun surgery | One change touches 5+ files | Consolidate into module |
| Primitive obsession | Overuse of raw types | Introduce small class/dataclass |
| Dead code | Unreachable paths or unused exports | Remove |

### Assessment Format

```markdown
### Developer Review

**Readability**: {excellent|good|needs-work}
**Complexity**: {low|medium|high} — cyclomatic {number}
**Technical debt**: {none|minor|moderate|significant}

**Issues found**:
1. [{severity}] {file}:{line} — {description} [evidence permalink]
2. ...

**Recommendation**: {pass|pass-with-notes|improve|reject}
```

## Role 3: Tester / 测试员

**Focus**: Test coverage, edge cases, failure modes, observability, testability.

### Checklist

- [ ] **New code has tests**: Every new function/class has corresponding test case
- [ ] **Edge cases covered**: Empty input, None/null, overflow, off-by-one, concurrent access
- [ ] **Error paths tested**: Exception handling tested, not just happy path
- [ ] **Integration coverage**: Cross-module interactions tested, not just unit isolation
- [ ] **Test independence**: Tests don't depend on execution order, external state, or timing
- [ ] **Observability**: Can failures be diagnosed from logs/error messages alone?
- [ ] **Test naming**: `test_{scenario}_{expected_outcome}` pattern, not `test_function_works`
- [ ] **Coverage regression**: New code doesn't lower overall coverage percentage

### Test Gap Analysis

```markdown
### Test Coverage Matrix

| Module | Lines Changed | Tests Added | Coverage | Gap |
|--------|--------------|-------------|----------|-----|
| auth | +120 | 8 tests | 78% | Missing: token expiry, invalid format |
| api | +45 | 3 tests | 85% | Missing: rate limit edge case |
| config | +10 | 1 test | 92% | Adequate |
```

### Failure Mode Analysis

For each new failure path introduced:

1. **What fails?** — Specific code path
2. **How it manifests?** — Error message, exception type, log pattern
3. **Can it be detected?** — Monitoring metric, alert, or only user report
4. **Recovery path** — Auto-retry, fallback, or manual intervention

### Assessment Format

```markdown
### Test Review

**Overall coverage**: {percentage} (threshold: {config_threshold}%)
**New code coverage**: {percentage}
**Missing critical tests**: {list}

**Edge cases identified**:
1. {edge_case} — {tested/missing} [permalink]
2. ...

**Observability**: {adequate|needs-logging|needs-metrics}

**Recommendation**: {pass|needs-more-tests|reject}
```

## Role 4: Security / 安全专家

**Focus**: Input validation, auth/perm checks, secrets exposure, dependency risks, attack surface.

### Checklist

- [ ] **Input validation**: All external inputs validated (type, length, format, range)
- [ ] **Auth checks**: Every sensitive endpoint verifies authentication and authorization
- [ ] **Secrets handling**: No hardcoded credentials, API keys, tokens in source code
- [ ] **SQL injection**: All queries use parameterized statements, no string concatenation
- [ ] **XSS prevention**: All user-rendered content escaped, no `v-html` with untrusted data
- [ ] **Dependency audit**: New dependencies scanned for known CVEs
- [ ] **Least privilege**: New permissions are minimum required, no overly broad access
- [ ] **Data exposure**: Error messages don't leak internal details, stack traces, or env vars
- [ ] **Rate limiting**: New endpoints have rate limiting if externally exposed

### Secret Detection Patterns

```bash
# Scan for potential secrets
git diff "v${PUBLISHED}"..HEAD -S "API_KEY\|SECRET\|PASSWORD\|TOKEN\|PRIVATE_KEY" --unified=0

# Check for accidentally committed .env
git diff "v${PUBLISHED}"..HEAD -- '.env*' '*.pem' '*.key'

# Verify .gitignore covers sensitive patterns
git check-ignore .env .env.local secrets.json
```

### Dependency Risk Assessment

```markdown
### Dependency Changes

| Package | Version Change | Known CVEs | License | Risk |
|---------|---------------|------------|---------|------|
| express | 4.17→4.18 | None | MIT | Low |
| lodash | 4.17.20→4.17.21 | CVE-2021-23337 | MIT | Medium |
```

### Assessment Format

```markdown
### Security Review

**Risk level**: {low|medium|high|critical}
**Attack surface**: {shrunk|unchanged|expanded}

**Findings**:
- [{severity}] {description} [evidence permalink]
  - Impact: {what could happen}
  - Remediation: {how to fix}

**Recommendation**: {pass|pass-with-conditions|block}
```

## Role 5: Docs / 文档

**Focus**: README accuracy, API doc completeness, changelog, migration guides.

### Checklist

- [ ] **README updated**: New features documented, removed features noted, examples work
- [ ] **API docs complete**: All public methods/classes documented with parameters, returns, exceptions
- [ ] **Changelog entry**: Added under appropriate section (Breaking/Feature/Fix)
- [ ] **Migration guide**: For breaking changes, guide for upgrading from previous version
- [ ] **Type docs**: New types documented, removed types noted
- [ ] **Code examples**: New features have runnable examples in docs
- [ ] **Version references**: Version numbers in docs match actual version
- [ ] **Link integrity**: No broken links in documentation

### Doc Completeness Score

```markdown
### Doc Coverage

| Area | Status | Gap |
|------|--------|-----|
| README | ✅ Updated | — |
| API reference | ⚠️ Partial | Missing: `newFunction()`, `Config.new_option` |
| Changelog | ❌ Missing | No entry for this release |
| Migration guide | N/A | No breaking changes |
| Examples | ⚠️ Stale | Example for old API still present |
```

### Assessment Format

```markdown
### Docs Review

**Completeness**: {complete|mostly-complete|partial|incomplete}
**Accuracy**: {accurate|minor-errors|misleading}

**Required updates**:
1. {file}:{line} — {what needs updating} [permalink]
2. ...

**Recommendation**: {pass|needs-updates|block}
```

## Synthesis / 综合

After all 5 roles report, combine into final assessment:

```markdown
## Review Synthesis

| Role | Verdict | Critical Issues | Minor Issues |
|------|---------|----------------|-------------|
| Architect | {pass/improve/reject} | {n} | {n} |
| Developer | {pass/pass-with-notes/improve/reject} | {n} | {n} |
| Tester | {pass/needs-more-tests/reject} | {n} | {n} |
| Security | {pass/pass-with-conditions/block} | {n} | {n} |
| Docs | {pass/needs-updates/block} | {n} | {n} |

**Overall**: {ready/needs-fixes/not-ready}
**Blocking issues**: {count}
**Action items**: {sorted by severity}
```