# Quality Gates

## Gate Overview

Quality gates are strict checkpoints between phases. Each gate must be passed before proceeding.

```
Phase 1 ──▶ Gate 1 ──▶ Phase 2 ──▶ Gate 2 ──▶ Phase 3 ──▶ Gate 3 ──▶ ...
              │                     │                     │
              ▼                     ▼                     ▼
         [BLOCK]               [BLOCK]               [BLOCK]
         if failed             if failed             if failed
```

## Gate 1: Requirement Analysis

### Criteria

| Criterion | Requirement | Verification |
|-----------|-------------|--------------|
| Stakeholder Coverage | All personas documented | Checklist review |
| Requirement Completeness | No TBD or unclear items | Document review |
| Success Metrics | All quantified | Numeric check |
| Risk Assessment | All high risks mitigated | Risk matrix review |

### Gate Checklist

```markdown
## Gate 1 Checklist

- [ ] All stakeholders identified and documented
- [ ] All functional requirements listed with priority
- [ ] All non-functional requirements quantified
- [ ] All constraints documented
- [ ] All assumptions stated with risks
- [ ] Success criteria are measurable
- [ ] No conflicting requirements
- [ ] Out of scope items defined
- [ ] High risks have mitigation plans

Status: □ PASS  □ FAIL
Reviewer: ___________
Date: ___________
```

### Failure Actions

If gate fails:
1. Identify missing items
2. Return to requirement elicitation
3. Update documentation
4. Re-submit for gate review

## Gate 2: Architecture Design

### Criteria

| Criterion | Requirement | Verification |
|-----------|-------------|--------------|
| Module Cohesion | Single responsibility each | Design review |
| Coupling Analysis | No circular dependencies | Dependency graph |
| Interface Clarity | All interfaces documented | Document review |
| Technology Rationale | All choices justified | ADR review |
| Scalability Path | Growth plan defined | Architecture review |

### Gate Checklist

```markdown
## Gate 2 Checklist

- [ ] Architecture diagram complete
- [ ] All modules defined with responsibilities
- [ ] All interfaces documented
- [ ] No circular dependencies
- [ ] Technology choices justified
- [ ] Security model defined
- [ ] Performance targets set
- [ ] Error handling strategy defined
- [ ] Configuration management defined
- [ ] Scalability approach documented

Status: □ PASS  □ FAIL
Reviewer: ___________
Date: ___________
```

### Failure Actions

If gate fails:
1. Review architecture decisions
2. Address cohesion/coupling issues
3. Document missing interfaces
4. Re-submit for gate review

## Gate 3: Task Decomposition

### Criteria

| Criterion | Requirement | Verification |
|-----------|-------------|--------------|
| Task Granularity | All tasks < 4 hours | Estimate review |
| Dependency Clarity | All dependencies explicit | Graph review |
| Coverage | All features mapped | Matrix review |
| Critical Path | Identified and documented | Path analysis |

### Gate Checklist

```markdown
## Gate 3 Checklist

- [ ] All features decomposed into tasks
- [ ] All tasks under 4 hours estimate
- [ ] All dependencies identified
- [ ] No circular dependencies in tasks
- [ ] Critical path calculated
- [ ] Iteration plan defined
- [ ] Resource allocation done
- [ ] Risk buffer included in timeline

Status: □ PASS  □ FAIL
Reviewer: ___________
Date: ___________
```

### Failure Actions

If gate fails:
1. Break down large tasks
2. Clarify ambiguous dependencies
3. Map missing features
4. Re-submit for gate review

## Gate 4: Module Iteration

### Criteria

| Criterion | Requirement | Verification |
|-----------|-------------|--------------|
| Module Score | ≥ 90/100 | Automated calculation |
| Test Coverage | ≥ 80% | Coverage report |
| Test Pass Rate | 100% | Test results |
| Lint Errors | 0 | Lint report |
| Documentation | Complete | Document review |

### Gate Checklist

```markdown
## Gate 4 Checklist - Module: [Name]

- [ ] Module score ≥ 90/100 (Current: ___/100)
- [ ] All tests pass (___/___)
- [ ] Test coverage ≥ 80% (Current: ___%)
- [ ] Lint errors = 0 (Current: ___)
- [ ] Type errors = 0 (Current: ___)
- [ ] API documentation complete
- [ ] Code comments adequate
- [ ] README section written

Status: □ PASS  □ FAIL
Score: ___/100
Date: ___________
```

### Failure Actions

If gate fails:
1. Review failing tests
2. Add missing tests for coverage
3. Fix lint/type errors
4. Improve module score
5. Re-submit for gate review

## Gate 5: Integration

### Criteria

| Criterion | Requirement | Verification |
|-----------|-------------|--------------|
| Integration Tests | All pass | Test report |
| Interface Contracts | All honored | Integration test |
| Performance | Targets met | Benchmark results |
| Error Handling | Complete | Scenario testing |

### Gate Checklist

```markdown
## Gate 5 Checklist

- [ ] All integration tests pass
- [ ] All interfaces work correctly
- [ ] Data flows correctly between modules
- [ ] Error handling works across modules
- [ ] Performance targets met
- [ ] No memory leaks
- [ ] Resource cleanup verified
- [ ] Security requirements met

Status: □ PASS  □ FAIL
Reviewer: ___________
Date: ___________
```

### Failure Actions

If gate fails:
1. Debug integration failures
2. Fix interface mismatches
3. Optimize performance
4. Add missing error handling
5. Re-submit for gate review

## Gate 6: Documentation

### Criteria

| Criterion | Requirement | Verification |
|-----------|-------------|--------------|
| README | Complete per skill standard | Document review |
| API Docs | All functions documented | Coverage check |
| User Guide | All features explained | Review |
| Architecture | System design documented | Review |

### Gate Checklist

```markdown
## Gate 6 Checklist

- [ ] README.md complete (all required sections)
- [ ] README_CN.md complete (if applicable)
- [ ] API documentation complete
- [ ] Installation guide verified
- [ ] Usage examples provided
- [ ] Architecture documentation complete
- [ ] Contributing guide written
- [ ] License file present
- [ ] Changelog started

Status: □ PASS  □ FAIL
Reviewer: ___________
Date: ___________
```

## Gate Bypass Policy

### When Bypass is Allowed

- **Low-risk iterations**: Non-critical modules with < 2 hours work
- **Hotfixes**: Urgent production fixes (requires documentation)
- **Experiments**: Proof-of-concept work (clearly marked)

### Bypass Documentation

```markdown
## Gate Bypass Request

**Gate**: [Gate number]
**Reason**: [Justification]
**Risk**: [Risk assessment]
**Mitigation**: [How risks will be addressed]
**Approval**: [If required]

**Decision**: □ Approved  □ Denied
**Date**: ___________
```

## Quality Metrics Summary

| Gate | Key Metric | Target | Weight |
|------|-----------|--------|--------|
| Gate 1 | Requirement completeness | 100% | 10% |
| Gate 2 | Architecture coverage | 100% | 15% |
| Gate 3 | Task coverage | 100% | 10% |
| Gate 4 | Module score | ≥ 90 | 40% |
| Gate 5 | Integration pass | 100% | 15% |
| Gate 6 | Documentation | 100% | 10% |

**Overall Project Quality Score** = Weighted average of all gates