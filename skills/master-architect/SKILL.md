---
name: master-architect
version: "1.1.0"
description: |
  Top-tier software architect agent for complex multi-stage project development with strict quality gates and iterative refinement.

  Triggers when: Designing architecture for a complex multi-stage project, decomposing requirements into modules, or establishing quality gates for development phases.

  Commands:
  - /architect design <task> - Full architecture design for a task
  - /architect phase <n> - Execute specific phase
  - /architect iterate <module> - Iterate on a specific module
  - /architect status - Show current architecture status
  - /architect review - Review and validate architecture

  Capabilities: Six-phase architecture with quality gates, requirement analysis, architecture design, task decomposition, iterative development, integration and validation, documentation generation
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

## Quick Commands

| Command | Description |
|---------|-------------|
| `/architect design <task>` | Full architecture design for a task |
| `/architect phase <n>` | Execute specific phase (1-6) |
| `/architect iterate <module>` | Iterate on a specific module |
| `/architect status` | Show current architecture status |
| `/architect review` | Review and validate architecture |

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

Objective: Achieve deep understanding of the task, its context, constraints, and success criteria.

Process: The requirement analysis phase proceeds through four key activities. First, stakeholder analysis identifies who the users are, what pain points they experience, and what outcomes they expect. Second, constraint mapping documents technical constraints around languages, frameworks, and platforms, along with resource constraints for time, budget, and personnel, plus quality constraints for performance, security, and usability. Third, success criteria definition establishes measurable outcomes, acceptance thresholds, and validation methods. Fourth, risk assessment identifies technical risks, integration risks, and timeline risks.

Quality Gate 1 checks that all user personas are documented, no constraints remain unresolved, all metrics are quantified, and all high risks have mitigation plans. Exit condition: All gate criteria passed. Architecture review approved.

## Phase 2: Architecture Design

Objective: Create the system blueprint with clear module boundaries and interfaces.

Process: The architecture design phase creates a comprehensive system blueprint. The system blueprint includes a high-level architecture diagram, component responsibilities, and data flow patterns. Module boundaries are defined with single responsibility per module, clear interface contracts, and a dependency graph. Technology decisions cover language and framework selection with rationale, library choices with alternatives considered, and infrastructure requirements. Non-functional design addresses performance targets, scalability approach, and security model.

### Architecture Documentation Template

The architecture document should follow a standard structure. Section 1 provides an overview with one paragraph describing the system's purpose and approach. Section 2 presents the high-level design with an architecture diagram. Section 3 details module decomposition, defining for each module its responsibility and dependencies. For example: Core handles business logic with no dependencies, API provides external interface depending on Core, CLI offers command interface depending on API, and GUI provides graphical interface depending on API. Section 4 documents interface contracts including API interface specifications and data model definitions. Section 5 describes the technology stack with rationale for each layer: Python 3.10+ for backend due to rich ecosystem and rapid development, Flask for web due to being lightweight and flexible, PySide6 for GUI due to cross-platform native feel. Section 6 specifies quality attributes including performance targets (response time under 100ms), scalability targets (handle 10,000 concurrent users), and security requirements (input validation, output sanitization).

Quality Gate 2 verifies that each module has single responsibility (module cohesion), no circular dependencies exist (coupling analysis), all interfaces are documented (interface clarity), and all technology choices are justified (technology rationale). Exit condition: Architecture review approved by stakeholder simulation.

## Phase 3: Task Decomposition

Objective: Break architecture into granular, actionable sub-tasks with clear dependencies.

Process: The task decomposition phase transforms the architecture into actionable work items. Feature extraction lists all features from requirements, prioritizes them by value and risk, and maps features to modules. Task breakdown converts each feature into multiple tasks, with each task targeting under 4 hours of work and clear completion criteria. Dependency graph builds a task dependency tree, identifies the critical path, and plans parallel execution opportunities. Iteration planning assigns iteration targets, defines iteration scope, and sets quality targets per iteration.

Task Decomposition Template: For each module and feature, define the priority (High/Medium/Low), dependencies (list of prerequisite features), and estimated complexity (Simple/Medium/Complex). Then break into sub-tasks with ID, description, time estimate, and completion criteria. Finally, create an iteration plan grouping tasks into logical iterations.

Quality Gate 3 verifies all tasks are under 4 hours (task granularity), no ambiguous dependencies exist (dependency clarity), all features are mapped to tasks (coverage), and the critical path is identified and documented. Exit condition: Task breakdown reviewed and approved.

## Phase 4: Iterative Development

Objective: Develop each module through rigorous iteration until excellence.

Iteration Cycle:

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

Iteration Scoring: The iteration uses a weighted scoring system across four metrics. Test coverage carries 30% weight with a target of 80% or higher. Code quality carries 25% weight targeting a lint score of zero. Functionality carries 25% weight requiring all tests to pass. Documentation carries 20% weight requiring completeness. Minimum score to proceed: 90/100.

Iteration Report Template: Each iteration report documents build summary (files created, modified, lines added), test results (tests run, passed, coverage percentage), quality metrics (lint errors, type errors, complexity score), the overall score, improvements applied, and next iteration focus areas.

Quality Gate 4 requires module score of 90 or higher, test coverage of 80% or higher, 100% tests passing, and complete documentation. Exit condition: Module achieves excellence score. Proceed to next module.

## Phase 5: Integration & Validation

Objective: Ensure all modules work together coherently.

Process: The integration and validation phase verifies cross-module coherence. Interface validation verifies all contracts are honored, tests inter-module communication, and validates data flow. Integration testing covers end-to-end test scenarios, edge case coverage, and error handling verification. Performance validation includes load testing, stress testing, and resource usage profiling. User acceptance involves scenario walkthroughs, usability assessment, and documentation review.

Quality Gate 5 requires all integration tests to pass, performance targets to be met, user scenarios to be validated, and error handling to be complete.

## Phase 6: Documentation Generation

Objective: Produce documentation compliant with all skill standards.

Documentation Checklist: Code-level documentation includes README.md in English, README_CN.md in Chinese, API documentation, code comments, and type hints. Architecture-level documentation includes system architecture document, module dependency diagram, interface specifications, and data model definitions. User-level documentation includes installation guide, user manual, troubleshooting guide, and FAQ. Development-level documentation includes CONTRIBUTING.md, development setup guide, testing guide, and release notes template.

Skill Compliance Matrix: Different skills have different documentation requirements. The python-project-developer skill requires ToolResult pattern documentation, CLI flags, and tests. The software-planner skill requires README sections and sample data. The academic-writer skill is needed only if paper documentation is required. |

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

- Use `/python-project` from **python-project-developer** to scaffold the project structure after architecture design is complete. Run `/python-project init <name>` then `/python-project structure` to generate the skeleton.
- Use `/iterate <n>` from **iteration-manager** to iteratively test each module against quality gates. Start with `/iterate 5` after each module implementation to verify the 90/100 score threshold.
- Use `/把关` from **ba-guan** for pre-publish review after architecture implementation. Run `/把关 check` to detect unpublished changes, then `/把关` for the full three-layer review.
- Use `/合并 <task>` from **he-bing** to manage the PR workflow for architectural changes. Use `/合并 create` to open a PR and `/合并 check` to verify CI and review status.
- Use `/安检` from **an-jian** to security-review the architecture. Run `/安检 scan` on the architecture documents and implementation to catch dangerous patterns, credential leaks, and privilege escalation risks.

## Best Practices

Five principles guide the architecture process. First, never skip phases because each phase builds on the previous one. Second, quality gates are mandatory with no exceptions. Third, iterate until excellence and settle for nothing less than 90%. Fourth, document continuously rather than leaving documentation for the end. Fifth, validate assumptions by testing early and testing often.

## Usage Examples

### Full Architecture Design
```
/architect design "E-commerce platform with microservices"
/architect phase 1  # Requirement Analysis
/architect phase 2  # Architecture Design
/architect iterate payment-service  # Iterate on payment module until quality gate passes
/architect phase 3  # Task Decomposition
```

### Iterative Module Development
```
/architect iterate auth-service --max-iterations 5 --quality-gate score>85
/architect iterate auth-service --focus security --review
```

## Troubleshooting

### Quality gate never passes
- **Symptom**: Module iteration loops indefinitely without meeting quality threshold
- **Fix**: Lower quality gate temporarily to `--quality-gate score>60`; identify specific failing sub-criteria; adjust iteration strategy with `--strategy targeted`

### Phase exit criteria unclear
- **Symptom**: Unclear when a phase is done and ready for next phase
- **Fix**: Run `/architect review` which checks all exit criteria explicitly; use `--exit-checklist` to see remaining items per phase

### Architecture design too abstract
- **Symptom**: Design phase produces high-level diagrams but no actionable module specs
- **Fix**: Use `/architect design <task> --detail full` for API-level decomposition; add `--implementation-notes` to generate pseudo-code for each module

## Edge Cases

- **Legacy system integration**: Existing system with no docs — use `/architect design --reverse-engineer` to infer architecture from code
- **Regulatory compliance**: Systems with SOC2/HIPAA/GDPR — add compliance requirements in Phase 1; each quality gate includes compliance check
- **Multi-team parallel development**: Use `/architect phase 3 --team-size 4` to generate parallel-safe task decomposition with clear module boundaries
- **Architecture migration**: Greenfield vs brownfield — use `--mode migration` to generate transition architecture with intermediate states
- **Real-time constraints**: Systems with latency SLOs — Phase 2 includes latency budget allocation per component

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-04-01 | Initial version, 6-phase workflow, quality gates, task decomposition |
| 1.1.0 | 2026-05-09 | Added safety rules, integration, examples, troubleshooting, edge cases |

## See Also

- `/agent-patterns` from **coding-agent-patterns** — Agent architecture patterns for complex systems
- `/python-project` from **python-project-developer** — Scaffold implementation after architecture design
- `/把关` from **ba-guan** — Pre-publish multi-layer review
- `/合并` from **he-bing** — PR workflow for phased delivery of architecture components