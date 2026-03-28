---
name: iteration-manager
version: "1.0.0"
description: |
  Iterative testing, verification, and improvement supervisor.

  Triggers when: User requests iterative testing and improvement, code quality review and assurance is needed, automated testing and feedback loops are required, or multiple rounds of refinement are specified.

  Commands:
  - /iterate <n> - Run n iterations of test-improve cycle
  - /iterate stop - Stop current iteration loop
  - /iterate status - Show current iteration status
  - /iterate report - Generate iteration report

  Capabilities: Automated test execution and result analysis, quality metrics tracking across iterations, improvement suggestion generation, convergence detection, and detailed iteration reports.
author: system
license: MIT
---

# Iteration Manager

Supervises iterative testing, verification, and improvement of code.

## Quick Commands

The iteration manager provides four commands. The `/iterate <n>` command runs n iterations of the test-improve cycle. The `/iterate stop` command stops the current iteration loop. The `/iterate status` command shows current iteration status. The `/iterate report` command generates a comprehensive report.

## Iteration Workflow

```
┌─────────────────────────────────────────────────────────────┐
│                    ITERATION CYCLE                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌────────┐│
│  │  TEST    │───▶│ ANALYZE  │───▶│ SUGGEST  │───▶│ APPLY  ││
│  │          │    │          │    │          │    │        ││
│  └──────────┘    └──────────┘    └──────────┘    └────────┘│
│       │                                                   │ │
│       │              ┌──────────┐                         │ │
│       └──────────────│ VERIFY   │◀────────────────────────┘ │
│                      │          │                           │
│                      └──────────┘                           │
│                            │                                 │
│                      ┌─────▼─────┐                          │
│                      │ CONVERGE? │                          │
│                      └─────┬─────┘                          │
│                     YES    │    NO                           │
│                      ┌─────┴─────┐                          │
│                      ▼           ▼                          │
│                   [DONE]    [NEXT ITERATION]                │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Iteration Process

### Step 1: Execute Tests

```bash
# Run all tests
pytest tests/ -v --tb=short

# Run with coverage
pytest tests/ --cov=package --cov-report=term-missing

# Run specific test categories
pytest tests/ -m "not slow"  # Skip slow tests
```

### Step 2: Analyze Results

Collect and analyze:
- Test pass/fail rates
- Coverage percentages
- Error patterns
- Performance metrics

### Step 3: Generate Suggestions

Based on analysis, suggest improvements:
- Bug fixes for failing tests
- Code coverage improvements
- Performance optimizations
- Code style improvements

### Step 4: Apply Changes

Implement suggested improvements and verify.

### Step 5: Verify & Iterate

Compare with previous iteration and decide to continue or stop.

## Quality Metrics

### Primary Metrics

Primary metrics track the most important quality indicators. Test pass rate has a target of 100% with 40% weight. Code coverage has a target above 80% with 30% weight. Lint score has a target of 0 errors with 15% weight. Type check has a target of 0 errors with 15% weight.

### Secondary Metrics

Secondary metrics provide additional quality signals. Test duration target is under 60 seconds. Code complexity target is under 10. Documentation coverage target is above 50%.

## Iteration Report Format

```markdown
# Iteration Report - Run #N

## Summary

| Metric | Previous | Current | Change |
|--------|----------|---------|--------|
| Pass Rate | 85% | 92% | +7% |
| Coverage | 72% | 78% | +6% |
| Errors | 5 | 2 | -3 |

## Issues Found

### Critical
- [Issue 1]: Description

### Major
- [Issue 2]: Description

### Minor
- [Issue 3]: Description

## Improvements Applied

1. Fixed [bug] in module X
2. Added test for Y
3. Refactored Z

## Next Iteration Focus

- [ ] Address remaining coverage gaps
- [ ] Fix failing edge case tests
- [ ] Improve performance of slow tests

## Convergence Check

- Score: 92/100
- Trend: Improving
- Recommendation: Continue iteration
```

## Convergence Detection

Stop iteration when:
1. All tests pass AND coverage > 80%
2. No new issues detected for 2 consecutive iterations
3. Improvement rate < 1% for 3 consecutive iterations
4. User-specified iteration count reached

## Usage Examples

### Basic Iteration

```
User: Run 5 iterations on the current project

Agent: Starting iteration cycle...

Iteration 1/5:
- Tests: 45/50 passed (90%)
- Coverage: 68%
- Errors: 3
- Applying fixes...

Iteration 2/5:
- Tests: 48/50 passed (96%)
- Coverage: 74%
- Errors: 1
- Applying fixes...

Iteration 3/5:
- Tests: 50/50 passed (100%)
- Coverage: 82%
- Errors: 0
- Convergence detected!

Final Report:
- Total iterations: 3
- Time: 5 minutes
- Improvements: 12 fixes applied
```

### Focused Iteration

```
User: Iterate until test coverage reaches 90%

Agent: Starting coverage-focused iteration...

Iteration 1: Coverage 68% → 72%
Iteration 2: Coverage 72% → 78%
Iteration 3: Coverage 78% → 83%
Iteration 4: Coverage 83% → 88%
Iteration 5: Coverage 88% → 91%

Target reached! Coverage: 91%
```

### Stop and Resume

```
User: /iterate stop

Agent: Iteration stopped at #3
- Current state saved
- Resume with /iterate resume

User: /iterate resume

Agent: Resuming from iteration #3...
```

## Rules

- [rules/testing-protocol.md](rules/testing-protocol.md) - Testing execution protocol
- [rules/quality-metrics.md](rules/quality-metrics.md) - Quality scoring system
- [rules/iteration-workflow.md](rules/iteration-workflow.md) - Detailed workflow

## Integration with Other Skills

The iteration manager integrates with other skills. The python-project-developer skill uses test patterns and ToolResult. The software-planner skill validates documentation requirements. The commit skill auto-commits improvements.

## Best Practices

Five practices guide effective iteration. First, start with baseline by running initial tests to establish metrics. Second, focus on one area by prioritizing critical failures first. Third, track progress by comparing metrics across iterations. Fourth, know when to stop by avoiding over-optimization. Fifth, document changes by keeping track of what was improved.