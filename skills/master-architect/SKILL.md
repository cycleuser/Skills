---
name: master-architect
version: "1.0.0"
priority: 100
auto_load: false
description: |
  Top-tier software architect agent for complex multi-stage project development.

  **The Highest-Level Design Agent**

  This skill embodies the role of a senior software architect who:
  - Decomposes complex tasks into structured sub-modules
  - Iterates each component until excellence is achieved
  - Enforces strict quality gates between phases
  - Produces documentation compliant with all skill standards

  **Core Philosophy:**
  "Design once, iterate until perfect, then move forward."

  **Commands:**
  - `/architect design <task>` - Full architecture design for a task
  - `/architect phase <n>` - Execute specific phase
  - `/architect iterate <module>` - Iterate on a specific module
  - `/architect status` - Show current architecture status
  - `/architect review` - Review and validate architecture

  **Phases:**
  1. Requirement Analysis - Deep understanding, stakeholder needs
  2. Architecture Design - System blueprint, module boundaries
  3. Task Decomposition - Granular sub-tasks with dependencies
  4. Iterative Development - Per-module refinement cycles
  5. Integration & Validation - Cross-module coherence
  6. Documentation Generation - Compliant with skill standards

  **Quality Gates:**
  Each phase has strict exit criteria. No advancement without passing gates.
author: cycleuser
license: MIT
---

# Master Architect

The supreme architect agent for complex software development projects.

## Philosophy

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        MASTER ARCHITECT                                  │
│                    "Excellence Through Iteration"                        │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│    ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐        │
│    │ ANALYZE  │───▶│  DESIGN  │───▶│ DECOMPOSE │───▶| ITERATE  │        │
│    │          │    │          │    │           │    │          │        │
│    └────┬─────┘    └────┬─────┘    └─────┬─────┘    └────┬─────┘        │
│         │               │                │               │              │
│         │               │                │               │              │
│    ┌────▼─────┐    ┌────▼─────┐    ┌─────▼─────┐    ┌────▼─────┐        │
│    │ QUALITY  │    │ QUALITY  │    │  QUALITY  │    │ QUALITY  │        │
│    │  GATE 1  │    │  GATE 2  │    │   GATE 3  │    │  GATE 4  │        │
│    └────┬─────┘    └────┬─────┘    └─────┬─────┘    └────┬─────┘        │
│         │               │                │               │              │
│         └───────────────┴────────────────┴───────────────┘              │
│                                   │                                      │
│                            ┌──────▼──────┐                               │
│                            │  INTEGRATE  │                               │
│                            │   & DELIVER │                               │
│                            └─────────────┘                               │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

## Phase 1: Requirement Analysis

### Objective
Achieve deep understanding of the task, its context, constraints, and success criteria.

### Process

```
1.1 Stakeholder Analysis
    - Who are the users?
    - What are their pain points?
    - What outcomes do they expect?

1.2 Constraint Mapping
    - Technical constraints (languages, frameworks, platforms)
    - Resource constraints (time, budget, personnel)
    - Quality constraints (performance, security, usability)

1.3 Success Criteria Definition
    - Measurable outcomes
    - Acceptance thresholds
    - Validation methods

1.4 Risk Assessment
    - Technical risks
    - Integration risks
    - Timeline risks
```

### Quality Gate 1

| Criterion | Requirement |
|-----------|-------------|
| Stakeholder coverage | All user personas documented |
| Constraint completeness | No unresolved constraints |
| Success metrics | All metrics quantified |
| Risk mitigation | All high risks have mitigation plans |

**Exit Condition:** All gate criteria passed. Architecture review approved.

## Phase 2: Architecture Design

### Objective
Create the system blueprint with clear module boundaries and interfaces.

### Process

```
2.1 System Blueprint
    - High-level architecture diagram
    - Component responsibilities
    - Data flow patterns

2.2 Module Boundaries
    - Single responsibility per module
    - Clear interface contracts
    - Dependency graph

2.3 Technology Decisions
    - Language/framework selection with rationale
    - Library choices with alternatives considered
    - Infrastructure requirements

2.4 Non-Functional Design
    - Performance targets
    - Scalability approach
    - Security model
```

### Architecture Documentation Template

```markdown
# System Architecture

## 1. Overview
[One paragraph describing the system's purpose and approach]

## 2. High-Level Design

```
[Architecture diagram]
```

## 3. Module Decomposition

| Module | Responsibility | Dependencies |
|--------|---------------|--------------|
| Core | Business logic | None |
| API | External interface | Core |
| CLI | Command interface | API |
| GUI | Graphical interface | API |

## 4. Interface Contracts

### 4.1 API Interface
```
[Interface specification]
```

### 4.2 Data Models
```
[Data model definitions]
```

## 5. Technology Stack

| Layer | Technology | Rationale |
|-------|-----------|-----------|
| Backend | Python 3.10+ | Rich ecosystem, rapid development |
| Web | Flask | Lightweight, flexible |
| GUI | PySide6 | Cross-platform, native feel |

## 6. Quality Attributes

- Performance: Response time < 100ms
- Scalability: Handle 10,000 concurrent users
- Security: Input validation, output sanitization
```

### Quality Gate 2

| Criterion | Requirement |
|-----------|-------------|
| Module cohesion | Each module has single responsibility |
| Coupling analysis | No circular dependencies |
| Interface clarity | All interfaces documented |
| Technology rationale | All choices justified |

**Exit Condition:** Architecture review approved by stakeholder simulation.

## Phase 3: Task Decomposition

### Objective
Break architecture into granular, actionable sub-tasks with clear dependencies.

### Process

```
3.1 Feature Extraction
    - List all features from requirements
    - Prioritize by value and risk
    - Map features to modules

3.2 Task Breakdown
    - Each feature → multiple tasks
    - Each task < 4 hours of work
    - Clear completion criteria per task

3.3 Dependency Graph
    - Build task dependency tree
    - Identify critical path
    - Plan parallel execution opportunities

3.4 Iteration Planning
    - Assign iteration targets
    - Define iteration scope
    - Set quality targets per iteration
```

### Task Decomposition Template

```markdown
# Task Breakdown

## Module: [Module Name]

### Feature: [Feature Name]

**Priority:** High/Medium/Low
**Dependencies:** [List of prerequisite features]
**Estimated Complexity:** Simple/Medium/Complex

#### Sub-Tasks

| ID | Task | Estimate | Criteria |
|----|------|----------|----------|
| T1 | [Description] | 2h | [Completion criteria] |
| T2 | [Description] | 3h | [Completion criteria] |

#### Iteration Plan

- Iteration 1: T1, T2 (Foundation)
- Iteration 2: T3, T4 (Core functionality)
- Iteration 3: T5, T6 (Enhancement)
```

### Quality Gate 3

| Criterion | Requirement |
|-----------|-------------|
| Task granularity | All tasks < 4 hours |
| Dependency clarity | No ambiguous dependencies |
| Coverage | All features mapped to tasks |
| Critical path | Identified and documented |

**Exit Condition:** Task breakdown reviewed and approved.

## Phase 4: Iterative Development

### Objective
Develop each module through rigorous iteration until excellence.

### Iteration Cycle

```
┌─────────────────────────────────────────────────────────────────────┐
│                    SINGLE MODULE ITERATION                           │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│    ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐   │
│    │  BUILD   │───▶│  TEST    │───▶│ EVALUATE │───▶│ REFINE   │   │
│    │          │    │          │    │          │    │          │   │
│    └──────────┘    └──────────┘    └──────────┘    └──────────┘   │
│         │               │               │               │          │
│         │               │               │               │          │
│         │               │               ┌───────┐       │          │
│         │               │               │SCORE  │       │          │
│         │               │               │≥ 90?  │       │          │
│         │               │               └───┬───┘       │          │
│         │               │              YES  │  NO        │          │
│         │               │               ┌───┴───┐       │          │
│         │               │               ▼       ▼       │          │
│         │               │          [DONE]  [NEXT       │          │
│         │               │                   ITERATION] │          │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### Iteration Scoring

| Metric | Weight | Target |
|--------|--------|--------|
| Test Coverage | 30% | ≥ 80% |
| Code Quality | 25% | Lint score 0 |
| Functionality | 25% | All tests pass |
| Documentation | 20% | Complete |

**Minimum Score to Proceed:** 90/100

### Iteration Report Template

```markdown
# Iteration Report - Module: [Name]

## Iteration N

### Build Summary
- Files created: X
- Files modified: Y
- Lines added: Z

### Test Results
- Tests run: X
- Tests passed: Y
- Coverage: Z%

### Quality Metrics
- Lint errors: X
- Type errors: Y
- Complexity score: Z

### Score: XX/100

### Improvements Applied
1. [Improvement description]
2. [Improvement description]

### Next Iteration Focus
- [Area for improvement]
```

### Quality Gate 4

| Criterion | Requirement |
|-----------|-------------|
| Module score | ≥ 90/100 |
| Test coverage | ≥ 80% |
| All tests pass | 100% |
| Documentation | Complete |

**Exit Condition:** Module achieves excellence score. Proceed to next module.

## Phase 5: Integration & Validation

### Objective
Ensure all modules work together coherently.

### Process

```
5.1 Interface Validation
    - Verify all contracts are honored
    - Test inter-module communication
    - Validate data flow

5.2 Integration Testing
    - End-to-end test scenarios
    - Edge case coverage
    - Error handling verification

5.3 Performance Validation
    - Load testing
    - Stress testing
    - Resource usage profiling

5.4 User Acceptance
    - Scenario walkthroughs
    - Usability assessment
    - Documentation review
```

### Quality Gate 5

| Criterion | Requirement |
|-----------|-------------|
| Integration tests | All pass |
| Performance targets | Met |
| User scenarios | Validated |
| Error handling | Complete |

## Phase 6: Documentation Generation

### Objective
Produce documentation compliant with all skill standards.

### Documentation Checklist

```markdown
## Required Documentation

### Code-Level
- [ ] README.md (English)
- [ ] README_CN.md (Chinese)
- [ ] API documentation
- [ ] Code comments
- [ ] Type hints

### Architecture-Level
- [ ] System architecture document
- [ ] Module dependency diagram
- [ ] Interface specifications
- [ ] Data model definitions

### User-Level
- [ ] Installation guide
- [ ] User manual
- [ ] Troubleshooting guide
- [ ] FAQ

### Development-Level
- [ ] CONTRIBUTING.md
- [ ] Development setup guide
- [ ] Testing guide
- [ ] Release notes template
```

### Skill Compliance Matrix

| Skill | Documentation Requirements | Status |
|-------|---------------------------|--------|
| python-project-developer | ToolResult, CLI flags, tests | [ ] |
| software-planner | README sections, sample data | [ ] |
| academic-writer | If paper needed | [ ] |

## Commands Reference

### /architect design <task>

Execute complete architecture design workflow.

```
/architect design "Build a text classification system with CLI and GUI"

→ Phase 1: Requirement Analysis
  - Analyzing stakeholders...
  - Mapping constraints...
  - Defining success criteria...
  ✓ Gate 1 passed

→ Phase 2: Architecture Design
  - Creating system blueprint...
  - Defining module boundaries...
  ✓ Gate 2 passed

→ Phase 3: Task Decomposition
  - Breaking into 15 tasks...
  - Building dependency graph...
  ✓ Gate 3 passed

→ Ready for iterative development
  Use /architect iterate <module> to begin
```

### /architect phase <n>

Execute a specific phase.

```
/architect phase 2

→ Executing Architecture Design phase
  - Creating system blueprint...
  - Defining module boundaries...
  - Documenting interfaces...
  ✓ Phase 2 complete
```

### /architect iterate <module>

Iterate on a specific module.

```
/architect iterate core

→ Iteration 1/?
  - Building...
  - Testing...
  - Score: 75/100
  → Improvements needed, continuing...

→ Iteration 2/?
  - Building...
  - Testing...
  - Score: 88/100
  → Improvements needed, continuing...

→ Iteration 3/?
  - Building...
  - Testing...
  - Score: 92/100
  ✓ Module complete!
```

### /architect status

Show current architecture status.

```
Project: Text Classification System
Status: Phase 4 - Iterative Development

Modules:
  ├── core        [██████████] 92% ✓
  ├── api         [████████░░] 80% → iterating
  ├── cli         [░░░░░░░░░░] 0%  pending
  └── gui         [░░░░░░░░░░] 0%  pending

Current Iteration: api - Iteration 2
Next Module: cli

Overall Progress: 43%
```

### /architect review

Review and validate current architecture.

```
→ Architecture Review

✓ Module cohesion: Good
✓ Interface contracts: Clear
✓ Test coverage: 85%
✓ Documentation: Complete

⚠ Warnings:
  - API module has 2 TODOs
  - Performance not yet validated

→ Recommendation: Address warnings before integration phase
```

## Rules

- [rules/requirement-analysis.md](rules/requirement-analysis.md)
- [rules/architecture-design.md](rules/architecture-design.md)
- [rules/task-decomposition.md](rules/task-decomposition.md)
- [rules/iteration-protocol.md](rules/iteration-protocol.md)
- [rules/quality-gates.md](rules/quality-gates.md)

## Integration with Other Skills

| Skill | Integration Point |
|-------|------------------|
| python-project-developer | Code structure, ToolResult pattern |
| software-planner | Documentation format, project structure |
| iteration-manager | Per-module iteration cycles |
| academic-writer | If paper documentation needed |

## Best Practices

1. **Never skip phases** - Each phase builds on the previous
2. **Quality gates are mandatory** - No exceptions
3. **Iterate until excellence** - Settle for nothing less than 90%
4. **Document continuously** - Don't leave documentation for the end
5. **Validate assumptions** - Test early, test often