# Classification Taxonomy / 分类体系

Rules for classifying GitHub Issues and PRs by type, priority, scope, and effort.

## Type Classification / 类型分类

### Decision Framework

```
Is the report about something not working as documented?
├── YES → bug
│   └── Is it a security vulnerability?
│       ├── YES → bug (security)
│       └── NO → bug
└── NO → Is it requesting something new that doesn't exist?
    ├── YES → Is it a small improvement to existing feature?
    │   ├── YES → enhancement
    │   └── NO → feature
    └── NO → What is it primarily about?
        ├── Code structure/quality → refactor
        ├── Test coverage → test
        ├── Documentation → docs
        ├── Build/CI/dependencies → chore
        └── Performance → perf
```

### Type Definitions

| Type | Definition | Indicators | Examples |
|------|-----------|------------|----------|
| **bug** | Behavior differs from specification | Error messages, unexpected output, crashes | App crashes on login, API returns 500 |
| **feature** | New capability not currently available | "Add", "Support", "Enable" in title | Add dark mode, Support PDF export |
| **enhancement** | Improvement to existing feature | "Improve", "Better", "Faster" in title | Improve search speed, Better error messages |
| **docs** | Documentation issue or request | "Document", "README", "Missing docs" | Missing API docs, Typo in guide |
| **refactor** | Code quality without behavior change | "Clean up", "Simplify", "Reorganize" | Extract utility function, Remove dead code |
| **test** | Test coverage issue or request | "Test", "Coverage", "Flaky" in title | Add tests for auth, Flaky CI test |
| **chore** | Maintenance, no user-facing change | "Update", "Bump", "Configure" | Update dependencies, Fix CI config |
| **perf** | Performance issue or improvement | "Slow", "Fast", "Latency", "Memory" | Page loads in 5s, Reduce memory usage |
| **question** | User asking for help, not a defect | "How to", "Can I", "Question" | How to configure X? Can Y do Z? |

### Bug Subclassification

| Subtype | Criteria | Response Priority |
|---------|----------|------------------|
| **security** | Vulnerability, data exposure, auth bypass | P0 — Immediate |
| **regression** | Worked in previous version | P0-P1 — High |
| **crash** | Application terminates unexpectedly | P1 — High |
| **data loss** | User data is lost or corrupted | P0 — Critical |
| **incorrect** | Wrong result without crash | P2 — Medium |
| **ux** | Confusing behavior, not technically wrong | P3 — Low |
| **cosmetic** | Visual glitch, no functional impact | P3 — Low |

## Priority Classification / 优先级分类

### P0 — Blocker (必须立即修复)

Definition: System is unusable, data is at risk, or security is compromised.

Criteria (any one suffices):
- Production system is down or unreachable
- Data corruption or data loss is occurring
- Security vulnerability being actively exploited
- All users are blocked from core functionality
- CI/CD pipeline completely broken

Decision check:
```
Are users completely unable to use the product?
├── YES → P0
└── NO → Is there a security vulnerability?
    ├── YES → P0
    └── NO → Is data loss occurring?
        ├── YES → P0
        └── NO → Not P0
```

### P1 — Critical (尽快修复)

Definition: Major feature broken, no workaround, or significant user impact.

Criteria (any one suffices):
- Core feature broken with no workaround
- Significant performance degradation (>5x slower)
- Affects large number of users (>25%)
- Only workaround is highly inconvenient
- Security vulnerability (not actively exploited)

Decision check:
```
Is a core feature completely non-functional?
├── YES → Is there a reasonable workaround?
│   ├── NO → P1
│   └── YES → P2
└── NO → Does it affect >25% of users?
    ├── YES → P1
    └── NO → P2 or lower
```

### P2 — Important (计划修复)

Definition: Feature partially broken, reasonable workaround exists, or affects subset of users.

Criteria (any one suffices):
- Feature works but with significant limitations
- Workaround exists but is inconvenient
- Affects moderate number of users (5-25%)
- Performance degradation noticeable but not blocking
- Error logging or monitoring gaps

### P3 — Nice-to-have (有空就修)

Definition: Minor inconvenience, cosmetic issue, or improvement request.

Criteria:
- Feature works correctly but could be better
- Cosmetic or visual issues
- Affects small number of users (<5%)
- Convenience improvement
- Documentation clarity improvement

### Priority Decision Matrix

| Impact \ Urgency | Immediate (users blocked now) | Soon (major impact) | When possible (minor impact) | Unplanned |
|-----------------|------------------------------|--------------------|-----------------------------|-----------|
| **All users** | P0 | P1 | P2 | P3 |
| **Many users** | P1 | P1 | P2 | P3 |
| **Some users** | P2 | P2 | P3 | P3 |
| **Few users** | P3 | P3 | P3 | Won't fix |

## Scope Classification / 范围分类

| Scope | Definition | Indicators | Example |
|-------|-----------|------------|---------|
| **single-file** | Change affects one file | Bug in isolated function, typo fix | Fix null check in auth.py |
| **module** | Change affects one module/directory | Feature addition to one subsystem | Add logging to auth module |
| **cross-cutting** | Change spans multiple modules | Touches 3+ directories, shared concerns | Add request tracing across services |
| **architecture** | Change affects system structure | New major component, data flow change | Switch from monolith to microservices |

### Scope Detection

```bash
# Count files changed by path prefix
gh pr diff "$PR_NUMBER" --name-only | \
  awk -F/ '{print $1}' | sort | uniq -c | sort -rn

# If only one prefix appears → single-module
# If 2-3 prefixes → cross-cutting
# If 4+ prefixes → architecture-level
```

## Effort Classification / 工作量分类

| Effort | Lines Changed | Time Estimate | Risk |
|--------|--------------|---------------|------|
| **trivial** | <10 | <30 min | Very low |
| **small** | 10-50 | 30 min - 2h | Low |
| **medium** | 50-200 | 2h - 1d | Medium |
| **large** | 200-500 | 1-3d | High |

### Effort Estimation Heuristics

```
Is it a typo or config change?
├── YES → trivial
└── NO → Does it only touch one file?
    ├── YES → Are there edge cases?
    │   ├── YES → small
    │   └── NO → trivial or small
    └── NO → Does it touch >3 modules?
        ├── YES → Does it change interfaces?
        │   ├── YES → large
        │   └── NO → medium
        └── NO → medium
```

### Adjustments

Add one level to effort for each:
- Requires new tests (not just modifying existing)
- Requires documentation updates
- Involves external dependencies or APIs
- Performance-sensitive code path
- Security-sensitive code path
- Cross-language or cross-platform concerns

## Combined Classification / 综合分类

### Issue Label Format

Use consistent labels following this pattern:

```
type:{type}          e.g., type:bug, type:feature
priority:{P0-P3}     e.g., priority:P1
scope:{scope}        e.g., scope:module
effort:{effort}      e.g., effort:medium
```

### Classification Output Format

```markdown
## Classification

**Type**: bug (security)
**Priority**: P0
**Scope**: module (auth)
**Effort**: medium (3-4 hours)

### Reasoning
- **Type**: Authentication bypass qualifies as security bug
- **Priority**: P0 because unauthenticated access to protected routes
- **Scope**: Only auth module affected, other modules untouched
- **Effort**: Medium — fix is localized but needs thorough testing across 15 endpoints

### Action Required
Immediate fix required. Suggested assignee: {developer with auth context}.
Estimated resolution: same business day.
```

### Bulk Classification Priority Order

When classifying many items at once, prioritize by:

1. **P0 first**: All blockers get immediate attention
2. **Bug over feature**: Bugs before enhancements
3. **Security first**: Vulnerabilities before other bugs
4. **High impact**: Many users affected before few
5. **Low effort first**: Quick wins before large efforts (within same priority)