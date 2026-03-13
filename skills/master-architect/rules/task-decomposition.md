# Task Decomposition Protocol

## Decomposition Principles

### 1. SMART Tasks

Each task should be:
- **Specific**: Clear, unambiguous description
- **Measurable**: Has completion criteria
- **Achievable**: Can be completed in one iteration
- **Relevant**: Contributes to project goals
- **Time-bound**: Has estimated duration

### 2. Granularity Rule

```
Optimal task size: 1-4 hours
Maximum task size: 8 hours
Minimum task size: 30 minutes
```

### 3. Dependency Graph

```
Task A (no dependencies)
    │
    ├── Task B (depends on A)
    │       │
    │       └── Task D (depends on B)
    │
    └── Task C (depends on A)
            │
            └── Task E (depends on C)
                    │
                    └── Task F (depends on D, E)
```

## Task Breakdown Process

### Step 1: Feature Extraction

```markdown
## Feature List

| ID | Feature | Priority | Module |
|----|---------|----------|--------|
| F-001 | User authentication | High | Auth |
| F-002 | Data import | High | Core |
| F-003 | Report generation | Medium | Reports |
```

### Step 2: Feature to Task Mapping

```markdown
## Feature: F-001 User Authentication

### Tasks

| ID | Task | Estimate | Dependencies |
|----|------|----------|--------------|
| T-001 | Design auth schema | 2h | None |
| T-002 | Implement password hashing | 1h | T-001 |
| T-003 | Create login API | 3h | T-002 |
| T-004 | Build login UI | 4h | T-003 |
| T-005 | Add session management | 2h | T-003 |
| T-006 | Write auth tests | 3h | T-004, T-005 |

Total: 15 hours
Critical Path: T-001 → T-002 → T-003 → T-004 → T-006
```

### Step 3: Iteration Planning

```markdown
## Iteration Plan

### Iteration 1: Foundation
- T-001: Design auth schema
- T-002: Implement password hashing

### Iteration 2: Core
- T-003: Create login API
- T-005: Add session management

### Iteration 3: Integration
- T-004: Build login UI
- T-006: Write auth tests
```

## Task Template

```markdown
# Task: [T-NNN] [Task Name]

## Description
[One paragraph describing what needs to be done]

## Acceptance Criteria
- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Criterion 3

## Technical Notes
[Any technical considerations or constraints]

## Dependencies
- Requires: [List of prerequisite tasks]
- Blocks: [List of tasks that depend on this]

## Estimate
- Time: X hours
- Complexity: Simple | Medium | Complex

## Files to Modify
- [ ] file1.py
- [ ] file2.py

## Testing Requirements
- [ ] Unit tests
- [ ] Integration tests
- [ ] Manual testing
```

## Dependency Management

### Types of Dependencies

| Type | Description | Example |
|------|-------------|---------|
| Hard | Must complete before | API must exist before UI |
| Soft | Should complete before | Tests preferred before deployment |
| External | Outside the project | Third-party API availability |

### Dependency Graph Construction

```python
def build_dependency_graph(tasks: list) -> dict:
    """
    Build dependency graph from task list.
    
    Returns:
        {
            "T-001": {"dependencies": [], "dependents": ["T-002", "T-003"]},
            "T-002": {"dependencies": ["T-001"], "dependents": ["T-004"]},
        }
    """
    graph = {}
    for task in tasks:
        graph[task["id"]] = {
            "dependencies": task.get("dependencies", []),
            "dependents": []
        }
    
    # Build reverse dependencies
    for task_id, info in graph.items():
        for dep in info["dependencies"]:
            graph[dep]["dependents"].append(task_id)
    
    return graph


def find_critical_path(graph: dict) -> list:
    """Find the longest path through the graph."""
    # Use topological sort and dynamic programming
    pass
```

## Progress Tracking

### Task Status

| Status | Description |
|--------|-------------|
| Pending | Not started |
| In Progress | Currently working |
| Blocked | Cannot proceed |
| Review | Awaiting review |
| Complete | Done and verified |

### Burndown Chart

```
Tasks Remaining
│
│ ████
│ ██████
│ ████████
│ ██████████
│ ████████████
│ ██████████████
└─────────────────── Iterations
  I1   I2   I3   I4
```

## Task Prioritization

### MoSCoW Method

| Priority | Description |
|----------|-------------|
| Must Have | Critical for success |
| Should Have | Important but not critical |
| Could Have | Nice to have |
| Won't Have | Explicitly out of scope |

### Value vs. Effort Matrix

```
High Value │  Do First    │  Schedule
           │              │
───────────┼──────────────┼──────────
Low Value  │  Consider    │  Avoid
           │              │
           ────────────────────────────
              Low Effort   High Effort
```