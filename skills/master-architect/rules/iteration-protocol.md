# Iteration Protocol

## Iteration Lifecycle

```
┌────────────────────────────────────────────────────────────────┐
│                    ITERATION LIFECYCLE                          │
├────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐       │
│  │  BUILD  │──▶│  TEST   │──▶│ EVALUATE│──▶│ REFINE  │       │
│  └─────────┘   └─────────┘   └─────────┘   └─────────┘       │
│       │             │             │             │              │
│       │             │             ▼             │              │
│       │             │      ┌───────────┐       │              │
│       │             │      │   SCORE   │       │              │
│       │             │      │   ≥ 90?   │       │              │
│       │             │      └─────┬─────┘       │              │
│       │             │           │             │               │
│       │             │      ┌────┴────┐        │               │
│       │             │      │         │        │               │
│       │             │     YES       NO        │               │
│       │             │      │         │        │               │
│       │             │      ▼         └────────┘               │
│       │             │   [DONE]                                 │
│                                                                 │
└────────────────────────────────────────────────────────────────┘
```

## Phase 1: Build

### Build Checklist

- [ ] Code compiles without errors
- [ ] All imports resolve correctly
- [ ] No syntax errors
- [ ] Type hints are correct
- [ ] No hardcoded values

### Build Output

```markdown
## Build Report

### Files Modified
- src/core.py (45 lines added)
- src/api.py (23 lines added)
- tests/test_core.py (new file)

### Dependencies Added
- numpy>=1.24.0

### Build Status
✓ Success (no errors)
```

## Phase 2: Test

### Test Levels

| Level | Description | Coverage Target |
|-------|-------------|-----------------|
| Unit | Individual functions | 100% of new code |
| Integration | Module interactions | All interfaces |
| System | End-to-end | Critical paths |

### Test Execution

```bash
# Run unit tests
pytest tests/unit/ -v

# Run integration tests
pytest tests/integration/ -v

# Run with coverage
pytest tests/ --cov=module --cov-report=term-missing
```

### Test Report

```markdown
## Test Report

### Unit Tests
- Total: 25
- Passed: 24
- Failed: 1
- Skipped: 0

### Coverage
- Lines: 85%
- Branches: 78%
- Functions: 90%

### Failed Tests
1. test_process_invalid_input
   - Expected: ValueError
   - Actual: No exception raised
```

## Phase 3: Evaluate

### Scoring System

```python
def calculate_iteration_score(metrics: dict) -> float:
    """
    Calculate overall iteration score.
    
    Weights:
    - Test Pass Rate: 30%
    - Code Coverage: 25%
    - Lint Score: 20%
    - Type Check: 15%
    - Documentation: 10%
    """
    score = 0.0
    
    # Test pass rate (30%)
    score += (metrics["tests_passed"] / metrics["tests_total"]) * 30
    
    # Coverage (25%)
    score += (metrics["coverage"] / 100) * 25
    
    # Lint score (20%)
    lint_errors = metrics["lint_errors"]
    lint_score = max(0, 100 - lint_errors * 5)
    score += lint_score * 0.20
    
    # Type check (15%)
    type_errors = metrics["type_errors"]
    type_score = max(0, 100 - type_errors * 5)
    score += type_score * 0.15
    
    # Documentation (10%)
    doc_score = metrics.get("doc_coverage", 100)
    score += doc_score * 0.10
    
    return round(score, 2)
```

### Score Categories

| Score | Status | Action |
|-------|--------|--------|
| 90-100 | Excellent | Proceed to next module |
| 80-89 | Good | Minor refinements needed |
| 70-79 | Acceptable | Significant improvements needed |
| < 70 | Insufficient | Major rework required |

## Phase 4: Refine

### Improvement Generation

```python
def generate_improvements(evaluation: dict) -> list:
    """Generate prioritized improvement suggestions."""
    improvements = []
    
    # Fix failing tests
    for failure in evaluation["test_failures"]:
        improvements.append({
            "priority": "high",
            "type": "test_fix",
            "description": f"Fix {failure['test_name']}",
            "effort": failure.get("estimated_effort", "medium")
        })
    
    # Improve coverage
    for gap in evaluation["coverage_gaps"]:
        improvements.append({
            "priority": "medium",
            "type": "coverage",
            "description": f"Add test for {gap['file']}:{gap['line']}"
        })
    
    # Fix lint issues
    for issue in evaluation["lint_issues"]:
        improvements.append({
            "priority": "low",
            "type": "lint",
            "description": f"Fix {issue['code']} at {issue['file']}:{issue['line']}"
        })
    
    return sorted(improvements, key=lambda x: {"high": 0, "medium": 1, "low": 2}[x["priority"]])
```

### Refinement Log

```markdown
## Refinement Log - Iteration N

### Issues Identified
1. [HIGH] Test failure in test_process_data
2. [MEDIUM] Coverage gap in api.py:45-67
3. [LOW] Lint error E501 in core.py:120

### Improvements Applied
1. Fixed input validation in process_data()
2. Added test for edge case handling
3. Reformatted long line in core.py

### Results
- Tests: 25/25 passed (+1)
- Coverage: 87% (+2%)
- Lint: 0 errors (-1)
- Score: 92/100 (+7)
```

## Iteration Report Template

```markdown
# Iteration Report

## Module: [Name]
## Iteration: N
## Date: YYYY-MM-DD

### Summary

| Metric | Previous | Current | Delta |
|--------|----------|---------|-------|
| Score | 75 | 92 | +17 |
| Tests | 24/25 | 25/25 | +1 |
| Coverage | 78% | 87% | +9% |
| Lint | 1 error | 0 errors | -1 |

### Changes Made
1. [Description of change 1]
2. [Description of change 2]

### Issues Resolved
- [Issue 1]
- [Issue 2]

### Remaining Issues
- [Issue if any]

### Next Steps
- [If score < 90: what to improve]
- [If score >= 90: proceed to next module]

### Decision
□ Continue iteration
✓ Module complete, proceed to next
```

## Convergence Criteria

### Stop Conditions

1. **Target Reached**: Score ≥ 90
2. **Diminishing Returns**: < 2% improvement over 3 iterations
3. **Maximum Iterations**: 10 iterations reached
4. **All Tests Pass + Coverage ≥ 80%**

### Convergence Report

```markdown
## Convergence Analysis

### Iteration History
| Iteration | Score | Delta |
|-----------|-------|-------|
| 1 | 65 | - |
| 2 | 75 | +10 |
| 3 | 85 | +10 |
| 4 | 92 | +7 |

### Trend
- Improvement rate: Decreasing (expected)
- Convergence: Achieved at iteration 4
- Final score: 92/100

### Recommendation
Module meets quality standards. Proceed to integration.
```