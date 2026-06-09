---
name: iteration-manager
version: "1.1.0"
description: |
  Iterative testing, verification, and improvement supervisor for code quality assurance.

  Triggers when: User requests iterative testing and improvement, code quality review and assurance is needed, automated testing and feedback loops are required, or multiple rounds of refinement are specified.

  Commands:
  - /iterate <n> - Run n iterations of test-improve cycle
  - /iterate stop - Stop current iteration loop
  - /iterate resume - Resume current iteration loop
  - /iterate status - Show current iteration status
  - /iterate report - Generate iteration report

  Capabilities: Automated test execution and result analysis, quality metrics tracking across iterations, improvement suggestion generation, convergence detection, and detailed iteration reports
author: cycleuser
license: MIT
---

## Safety Rules

**Critical**: Read and follow [global-rules/bash-safety.md](file:///Users/fred/.config/opencode/skills/global-rules/rules/bash-safety.md) for all bash/command execution.

Core rules:
1. **Always set explicit `timeout` on bash calls** — 30s for tests, 60s for installs, never default
2. **Never run unscoped full test suites** — use `-k` or file paths to limit scope
3. **Never use `rm -rf` without variable guards**, `curl|bash`, `sudo`, or `kill -9`
4. **Infinite loops must have hard timeout + budget limits** — no unbounded while(True)
5. **Redirect stdin** with `< /dev/null` for non-interactive commands

A bash timeout that triggers SIGKILL corrupts the terminal FD, crashes opencode's TUI, and forces a GUI restart.

# Iteration Manager

Supervises iterative testing, verification, and improvement of code.

## Quick Commands

| Command | Description |
|---------|-------------|
| `/iterate <n>` | Run n iterations of test-improve cycle |
| `/iterate stop` | Stop current iteration loop |
| `/iterate resume` | Resume current iteration loop |
| `/iterate status` | Show current iteration status |
| `/iterate report` | Generate iteration report |

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
- [rules/anti-aigc.md](rules/anti-aigc.md) - Iteration report anti-AIGC detection rules

## Integration with Other Skills

- Use `/paper new <topic>` and `/paper search <keywords>` from **academic-writer** to document iteration results and quality metrics as structured papers. After generating an `/iterate report`, feed it to `/paper` for formal documentation.
- Use `/人话 <text>` from **humanizer** to humanize generated iteration reports, removing AI-typical patterns from test analysis summaries. Pipe `/iterate report` output through `/人话` for natural-sounding documentation.
- Use `/python-project test` from **python-project-developer** to generate test suites before starting iteration. Scaffold tests with `/python-project test`, then run `/iterate <n>` to refine them against quality gates.

## Best Practices

Five practices guide effective iteration. First, start with baseline by running initial tests to establish metrics. Second, focus on one area by prioritizing critical failures first. Third, track progress by comparing metrics across iterations. Fourth, know when to stop by avoiding over-optimization. Fifth, document changes by keeping track of what was improved.

## Troubleshooting

### Quality metrics not converging
- **Symptom**: `/iterate status` shows metrics oscillating without improvement trend
- **Fix**: Increase iteration count `--convergence-window 5` for wider sample; check if test suite is non-deterministic; add `--metric-weight` to prioritize stable metrics

### Test suite too slow for rapid iteration
- **Symptom**: Each iteration runs for hours, making iterative cycles impractical
- **Fix**: Run `/iterate <n> --fast` to execute only smoke tests per iteration; run full suite every Nth iteration with `--full-suite-every 5`

### Iteration consumes too much budget without results
- **Symptom**: Many iterations run but improvement delta is below 1%
- **Fix**: Check if early stopping threshold is too low; use `/iterate stop` to manually terminate; review iteration strategy with `--strategy review`

## Edge Cases

- **Flaky tests**: Non-deterministic test results cause false convergence — tag flaky tests with `@flaky`; exclude from quality metrics calculation
- **Performance benchmarks**: Benchmark tests need warm-up iterations — set `--warmup 3` to exclude first 3 runs from metrics
- **Cross-branch iteration**: Testing changes across multiple git branches — use `--branch <branch>` to target specific branch
- **Generated code validation**: Iteratively improving AI-generated code — use `--validate-output` to add output correctness checks beyond unit tests
- **Zero-change iterations**: If change delta is literally zero, auto-detected as "stuck" and iteration is terminated

## AIGC-Aware Output

Iteration reports must include specific metrics with before/after numbers, not vague "improvement observed". Every finding must be specific: "SQL injection in /auth/login line 47" not "security issues found". Fix suggestions must be actionable: "change X to Y" not "consider improving". See `rules/anti-aigc.md` for complete anti-AIGC detection rules.

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-04-01 | Initial version, convergence detection, quality metrics |
| 1.1.0 | 2026-05-09 | Added safety rules, integration, troubleshooting, edge cases |

## See Also

- `/python-project test` from **python-project-developer** — Generate test suites for iteration
- `/architect phase` from **master-architect** — Quality gates during phased development
- `/把关 check` from **ba-guan** — Pre-publish quality validation