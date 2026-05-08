# Self-Review for Autonomous Iteration

Autonomous agents must self-assess their own output quality. This document defines the review dimensions, scoring rubric, and decision tree for autonomous iteration.

## Review Dimensions

Four quality dimensions, each scored 0-10:

### Code Quality (Weight: 30%)
- Syntax and style consistency
- Error handling coverage
- No duplicated logic
- Appropriate abstractions (not over-engineered)

### Functionality (Weight: 35%)
- All requirements implemented
- Edge cases handled
- Expected outputs produced
- No regressions introduced

### Documentation (Weight: 15%)
- Inline comments where logic is non-obvious
- Function/method docstrings
- No stale or misleading comments

### Security (Weight: 20%)
- No secrets hardcoded
- Input validation present
- No dangerous patterns (rm -rf, sudo, curl|bash)
- Safe defaults for configuration

## Scoring Rubric

| Score | Criteria |
|-------|----------|
| 9-10 | Exceeds requirements. Robust, clean, well-tested. |
| 7-8 | Meets requirements with minor cosmetic issues. |
| 5-6 | Meets basic requirements but has notable gaps. |
| 3-4 | Partially functional. Missing requirements or buggy. |
| 0-2 | Broken or does not work. |

**Composite Score**: Weighted average of all four dimensions.

## Decision Tree

After each iteration, run self-review and decide:

```
Composite Score ≥ 85 → Decision: COMPLETE
  → Report final status, deliver output
  → Exit autonomous loop gracefully

Composite Score 70-84 → Decision: CONTINUE
  → Identify specific improvements needed
  → Apply targeted fixes
  → Increment iteration counter, continue loop

Composite Score < 70 → Decision: REVISE
  → If iteration > 5: escalate to user for guidance
  → If iteration ≤ 5: attempt structural revision (not just patches)
  → Save current state before revision for rollback
```

## Iteration Limit

Maximum iterations: 10. If approaching limit:
- Iteration 8-9: focus ONLY on highest-weight deficiencies
- Iteration 10: deliver best-effort result regardless of score, with a quality note

## Self-Review Template

After each iteration, output:

```markdown
## Iteration {N} Self-Review

| Dimension | Score | Notes |
|-----------|-------|-------|
| Code Quality | {0-10} | {specific observations} |
| Functionality | {0-10} | {what works, what doesn't} |
| Documentation | {0-10} | {coverage gaps} |
| Security | {0-10} | {risk assessment} |

**Composite**: {weighted_score}/100
**Decision**: {COMPLETE|CONTINUE|REVISE}
**Next Actions**: {specific improvements for next iteration}
```