# Iteration Workflow

## Standard Iteration Cycle

### 1. Initialize

```python
def initialize_iteration(project_path: Path) -> dict:
    """Initialize iteration tracking."""
    return {
        "project_path": str(project_path),
        "start_time": datetime.now(),
        "iteration": 0,
        "history": [],
        "converged": False,
        "config": {
            "max_iterations": 10,
            "target_quality": 90,
            "target_coverage": 80,
            "target_pass_rate": 100,
        }
    }
```

### 2. Execute Tests

```python
def run_tests(state: dict) -> dict:
    """Execute all test phases."""
    results = {
        "syntax_check": run_syntax_check(),
        "lint_check": run_lint_check(),
        "type_check": run_type_check(),
        "unit_tests": run_unit_tests(),
        "coverage": run_coverage_analysis(),
    }
    return results
```

### 3. Analyze Results

```python
def analyze_results(test_results: dict) -> dict:
    """Analyze test results and identify issues."""
    analysis = {
        "failures": [],
        "coverage_gaps": [],
        "lint_issues": [],
        "type_issues": [],
        "quality_score": calculate_quality_score(test_results),
    }
    
    # Categorize failures
    for failure in test_results.get("failures", []):
        analysis["failures"].append({
            "test": failure["test"],
            "error": failure["error"],
            "priority": calculate_priority(failure),
            "suggested_fix": suggest_fix(failure),
        })
    
    return analysis
```

### 4. Generate Improvements

```python
def generate_improvements(analysis: dict) -> list[dict]:
    """Generate improvement suggestions."""
    improvements = []
    
    # Fix failing tests
    for failure in sorted(analysis["failures"], key=lambda x: -x["priority"]):
        improvements.append({
            "type": "fix_test",
            "priority": "high",
            "description": f"Fix {failure['test']}",
            "suggested_fix": failure["suggested_fix"],
        })
    
    # Improve coverage
    for gap in analysis["coverage_gaps"]:
        improvements.append({
            "type": "add_test",
            "priority": "medium",
            "description": f"Add test for {gap['file']}:{gap['line']}",
        })
    
    # Fix lint issues
    for issue in analysis["lint_issues"]:
        improvements.append({
            "type": "fix_lint",
            "priority": "low",
            "description": f"Fix {issue['code']} at {issue['file']}:{issue['line']}",
        })
    
    return improvements
```

### 5. Apply Improvements

```python
def apply_improvements(improvements: list[dict], state: dict) -> dict:
    """Apply top improvements and track changes."""
    applied = []
    
    for imp in improvements[:5]:  # Apply top 5
        result = apply_improvement(imp)
        applied.append({
            "improvement": imp,
            "result": result,
            "timestamp": datetime.now(),
        })
    
    return {"applied": applied, "count": len(applied)}
```

### 6. Verify Changes

```python
def verify_changes(state: dict) -> dict:
    """Verify that improvements didn't introduce regressions."""
    new_results = run_tests(state)
    
    return {
        "success": new_results["quality_score"] >= state["previous_quality"],
        "new_quality": new_results["quality_score"],
        "delta": new_results["quality_score"] - state["previous_quality"],
    }
```

### 7. Check Convergence

```python
def check_convergence(state: dict) -> tuple[bool, str]:
    """Check if iteration should stop."""
    current = state["history"][-1]
    config = state["config"]
    
    # Target reached
    if current["quality_score"] >= config["target_quality"]:
        return True, "target_reached"
    
    # All tests pass
    if current["pass_rate"] == config["target_pass_rate"]:
        if current["coverage"] >= config["target_coverage"]:
            return True, "quality_threshold_met"
    
    # Max iterations
    if state["iteration"] >= config["max_iterations"]:
        return True, "max_iterations_reached"
    
    # Diminishing returns
    if len(state["history"]) >= 3:
        recent = [h["quality_score"] for h in state["history"][-3:]]
        deltas = [recent[i+1] - recent[i] for i in range(2)]
        if all(d < 1 for d in deltas):
            return True, "diminishing_returns"
    
    return False, "continue"
```

## Full Iteration Loop

```python
def run_iteration_cycle(state: dict) -> dict:
    """Execute complete iteration cycle."""
    while not state["converged"]:
        state["iteration"] += 1
        
        # 1. Run tests
        test_results = run_tests(state)
        
        # 2. Analyze
        analysis = analyze_results(test_results)
        
        # 3. Record progress
        state["history"].append({
            "iteration": state["iteration"],
            "timestamp": datetime.now(),
            "quality_score": analysis["quality_score"],
            "pass_rate": test_results["pass_rate"],
            "coverage": test_results["coverage"],
            "lint_errors": len(test_results["lint_issues"]),
            "type_errors": len(test_results["type_issues"]),
        })
        
        # 4. Check convergence
        converged, reason = check_convergence(state)
        if converged:
            state["converged"] = True
            state["convergence_reason"] = reason
            break
        
        # 5. Generate improvements
        improvements = generate_improvements(analysis)
        
        # 6. Apply improvements
        apply_results = apply_improvements(improvements, state)
        
        # 7. Verify
        verification = verify_changes(state)
        
        if not verification["success"]:
            # Rollback if regression
            rollback_changes(state)
        
        state["previous_quality"] = analysis["quality_score"]
    
    return generate_final_report(state)
```

## User Interaction Points

### Progress Display

```
Iteration 3/10
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Quality Score: ████████░░ 82/100 (+5)

Tests:    ██████████ 100% (50/50)
Coverage: ████████░░ 78% (+6%)
Lint:     ██████████ 0 errors
Types:    ██████████ 0 errors

Focus: Improving coverage in core.py
Next: Adding tests for lines 45-67
```

### Interactive Mode

```
Iteration 5 - 2 issues found:

1. [HIGH] test_auth failing - AssertionError
   Fix: Update token validation logic
   Apply? [y/n/skip]

2. [MED] Coverage gap in api.py
   Add test for error handling?
   Apply? [y/n/skip]

> y y

Applying fixes...
```

## Output Artifacts

### Iteration Log

```
logs/
└── iteration_YYYYMMDD_HHMMSS.log
```

### Quality Report

```
reports/
├── iteration_N_summary.md
├── iteration_N_detailed.md
└── iteration_N_metrics.json
```

### Coverage Reports

```
htmlcov/
└── index.html
```