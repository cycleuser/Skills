# Quality Metrics System

## Overall Quality Score

```python
def calculate_quality_score(metrics: dict) -> float:
    """
    Calculate overall quality score (0-100).
    
    Weights:
    - Test Pass Rate: 40%
    - Code Coverage: 30%
    - Lint Score: 15%
    - Type Check: 15%
    """
    score = 0.0
    
    # Test Pass Rate (40%)
    score += metrics.get("pass_rate", 0) * 0.40
    
    # Code Coverage (30%)
    score += metrics.get("coverage", 0) * 0.30
    
    # Lint Score (15%) - inverse of error count
    lint_errors = metrics.get("lint_errors", 0)
    lint_score = max(0, 100 - lint_errors * 10)
    score += lint_score * 0.15
    
    # Type Check (15%) - inverse of error count
    type_errors = metrics.get("type_errors", 0)
    type_score = max(0, 100 - type_errors * 10)
    score += type_score * 0.15
    
    return round(score, 2)
```

## Metric Definitions

### Test Pass Rate

```python
pass_rate = (tests_passed / tests_total) * 100

# Categories
# 95-100: Excellent
# 90-94: Good
# 80-89: Acceptable
# < 80: Needs Improvement
```

### Code Coverage

```python
coverage = (lines_covered / lines_total) * 100

# Categories
# 90-100: Excellent
# 80-89: Good
# 70-79: Acceptable
# < 70: Needs Improvement
```

### Lint Score

```python
lint_score = max(0, 100 - (errors * 10 + warnings * 2))

# Categories
# 95-100: Excellent
# 80-94: Good
# 60-79: Acceptable
# < 60: Needs Improvement
```

### Type Check Score

```python
type_score = max(0, 100 - errors * 10)

# Categories
# 100: Excellent (mypy strict)
# 90-99: Good
# 70-89: Acceptable
# < 70: Needs Improvement
```

## Iteration Progress Tracking

### Progress Metrics

```python
@dataclass
class IterationProgress:
    iteration: int
    timestamp: datetime
    quality_score: float
    pass_rate: float
    coverage: float
    lint_errors: int
    type_errors: int
    improvements: list[str]
    time_elapsed: float
```

### Trend Analysis

```python
def analyze_trend(progress_history: list[IterationProgress]) -> dict:
    """Analyze improvement trend across iterations."""
    if len(progress_history) < 2:
        return {"trend": "insufficient_data"}
    
    recent = progress_history[-1]
    previous = progress_history[-2]
    
    delta_quality = recent.quality_score - previous.quality_score
    delta_coverage = recent.coverage - previous.coverage
    delta_pass_rate = recent.pass_rate - previous.pass_rate
    
    return {
        "trend": "improving" if delta_quality > 0 else "declining" if delta_quality < 0 else "stable",
        "quality_delta": delta_quality,
        "coverage_delta": delta_coverage,
        "pass_rate_delta": delta_pass_rate,
        "improvement_rate": delta_quality / max(previous.quality_score, 1) * 100,
    }
```

## Convergence Criteria

### Automatic Convergence

Stop iteration when ALL of:

1. `quality_score >= 90`
2. `pass_rate == 100`
3. `coverage >= 80`
4. `lint_errors == 0`
5. `type_errors == 0`

### Diminishing Returns

Stop iteration when:

```python
# 3 consecutive iterations with < 1% improvement
if all(p.improvement_rate < 1 for p in last_3_iterations):
    return "converged_diminishing_returns"
```

### Regression Detection

Stop and alert when:

```python
# Quality score decreased by more than 5%
if current.quality_score < previous.quality_score - 5:
    return "regression_detected"
```

## Report Generation

### Summary Report

```markdown
# Quality Report - Iteration #N

## Overall Score: XX/100

## Metrics

| Metric | Value | Status |
|--------|-------|--------|
| Test Pass Rate | XX% | ✅/⚠️/❌ |
| Code Coverage | XX% | ✅/⚠️/❌ |
| Lint Errors | XX | ✅/⚠️/❌ |
| Type Errors | XX | ✅/⚠️/❌ |

## Trend

- Quality: ↑ +X.X (improving)
- Coverage: ↑ +X.X%
- Pass Rate: ↑ +X.X%

## Recommendations

1. [Priority recommendation]
2. [Secondary recommendation]
```

### Detailed Report

```markdown
# Detailed Quality Report

## Test Failures

| Test | Error | Priority |
|------|-------|----------|
| test_x | AssertionError | HIGH |
| test_y | TypeError | MEDIUM |

## Coverage Gaps

| File | Coverage | Missing Lines |
|------|----------|---------------|
| core.py | 65% | 45-67, 89-100 |
| api.py | 78% | 120-135 |

## Lint Issues

| File | Line | Code | Message |
|------|------|------|---------|
| core.py | 45 | E501 | Line too long |

## Type Errors

| File | Line | Error |
|------|------|-------|
| core.py | 45 | Incompatible types |
```

## Quality Gates

### CI Integration

```yaml
# .github/workflows/quality.yml
quality_gate:
  - pass_rate: 100%
  - coverage: 80%
  - lint_errors: 0
  - type_errors: 0
  - quality_score: 90
```

### Pre-commit Hook

```bash
#!/bin/bash
# Run quality checks before commit
pytest tests/ --cov=package --cov-fail-under=80 || exit 1
ruff check . || exit 1
mypy package || exit 1
```