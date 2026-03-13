# Skill Registry

Complete registry of all available skills in the workspace.

## Registry Format

Each skill entry contains:
- `name`: Skill identifier for invocation
- `version`: Semantic version
- `location`: File path to SKILL.md
- `description`: Brief description
- `triggers`: Conditions that activate the skill
- `invoke`: Command to load the skill

---

## Core Skills (Auto-loaded)

### skill-manager

```yaml
name: skill-manager
version: "1.0.0"
location: skills/skill-manager/SKILL.md
invoke: /skill skill-manager
description: |
  Central skill registry and management system. Auto-loaded on every session.
auto_load: true
priority: 0
commands:
  - /skills - List all skills
  - /skill <name> - Load skill
  - /skill reload - Refresh registry
  - /skill help <name> - Show details
```

---

## Architecture & Planning

### master-architect

```yaml
name: master-architect
version: "1.0.0"
location: skills/master-architect/SKILL.md
invoke: /skill master-architect
description: |
  Top-tier software architect agent for complex multi-stage project development.
  Decomposes tasks into sub-modules, iterates each until excellence.
priority: 100
commands:
  - /architect design <task> - Full architecture design
  - /architect phase <n> - Execute specific phase
  - /architect iterate <module> - Iterate on module
  - /architect status - Show status
  - /architect review - Review architecture
rules:
  - requirement-analysis.md
  - architecture-design.md
  - task-decomposition.md
  - iteration-protocol.md
  - quality-gates.md
```

---

## Development Skills

### python-project-developer

```yaml
name: python-project-developer
version: "1.0.0"
location: .opencode/skills/python-project-developer/SKILL.md
invoke: /skill python-project-developer
description: |
  Complete Python multi-project development specification for CLI/GUI tools.
triggers:
  - Creating a new Python project with CLI and GUI support
  - Setting up pyproject.toml, README, and PyPI publishing
  - Implementing unified API with ToolResult pattern
  - Adding OpenAI function-calling tools integration
rules:
  - project-structure.md
  - cli-flags.md
  - api-pattern.md
  - tools-integration.md
  - testing-guide.md
```

### software-planner

```yaml
name: software-planner
version: "1.0.0"
location: .opencode/skills/software-planner/SKILL.md
invoke: /skill software-planner
description: |
  Comprehensive software development planning for Python projects with CLI, GUI, Web interfaces.
triggers:
  - Creating new Python software with multiple interfaces
  - Planning software architecture from academic research
  - Designing scientific or engineering applications
  - Setting up bilingual documentation and PyPI publishing
rules:
  - pre-development.md
  - interface-design.md
  - documentation.md
  - sample-data.md
```

### coding-agent-patterns

```yaml
name: coding-agent-patterns
version: "1.0.0"
location: .opencode/skills/coding-agent-patterns/SKILL.md
invoke: /skill coding-agent-patterns
description: |
  Core patterns for AI coding agents based on Claude Code, Codex, Cline, Aider, OpenCode.
triggers:
  - Building AI coding agents
  - Implementing tool-calling loops
  - Managing context windows
  - Setting up agent memory systems
rules:
  - context-management.md
  - tool-safety.md
  - multi-provider.md
  - memory-systems.md
```

### iteration-manager

```yaml
name: iteration-manager
version: "1.0.0"
location: .opencode/skills/iteration-manager/SKILL.md
invoke: /skill iteration-manager
description: |
  Iterative testing, verification, and improvement supervisor.
triggers:
  - Need iterative testing and improvement
  - Code review and quality assurance
  - Automated testing workflows
commands:
  - /iterate <n> - Run n iterations
  - /iterate stop - Stop iteration
  - /iterate status - Show status
  - /iterate report - Generate report
rules:
  - testing-protocol.md
  - quality-metrics.md
  - iteration-workflow.md
```

### academic-writer

```yaml
name: academic-writer
version: "1.0.0"
location: .opencode/skills/academic-writer/SKILL.md
invoke: /skill academic-writer
description: |
  Academic paper writing assistant for top-tier conferences (AAAI, IJCAI, IEEE).
triggers:
  - Writing academic papers or articles
  - Need literature search and citation formatting
  - Preparing manuscripts for conference submission
commands:
  - /paper new <topic> - Start new paper
  - /paper search <keywords> - Search literature
  - /paper cite - Format citations
  - /paper structure - Generate outline
  - /paper review - Review and polish
rules:
  - literature-search.md
  - citation-format.md
  - paper-structure.md
  - writing-style.md
```

---

## Visualization Skills

### math-visualizer

```yaml
name: math-visualizer
version: "1.0.0"
location: Others/manim-video-generator/skills/math-visualizer/SKILL.md
invoke: /skill math-visualizer
description: |
  Mathematical visualization skill for equations, proofs, and geometric concepts.
triggers:
  - User mentions equations, formulas, or mathematical expressions
  - Request involves mathematical proofs or derivations
  - User mentions LaTeX, calculus, algebra, geometry
```

### visual-storyteller

```yaml
name: visual-storyteller
version: "1.0.0"
location: Others/manim-video-generator/skills/visual-storyteller/SKILL.md
invoke: /skill visual-storyteller
description: |
  Narrative-driven animation skill for explanatory content.
triggers:
  - User wants to explain a concept or process
  - Content is educational or tutorial-like
```

### animation-composer

```yaml
name: animation-composer
version: "1.0.0"
location: Others/manim-video-generator/skills/animation-composer/SKILL.md
invoke: /skill animation-composer
description: |
  Scene composition and orchestration for complex multi-part animations.
triggers:
  - User wants to compose multi-element scenes
  - Scene requires act-based structure
```

### motion-graphics

```yaml
name: motion-graphics
version: "1.0.0"
location: Others/manim-video-generator/skills/motion-graphics/SKILL.md
invoke: /skill motion-graphics
description: |
  Kinetic typography, logo animations, and stylized motion design.
triggers:
  - User wants text animations or kinetic typography
  - Request involves logo reveals or title sequences
```

---

## Git Workflow Skills

### commit

```yaml
name: commit
version: "1.0.0"
location: Others/symphony/.codex/skills/commit/SKILL.md
invoke: /skill commit
description: |
  Create well-formed git commits with session context.
triggers:
  - Asked to commit or prepare commit message
```

### push

```yaml
name: push
version: "1.0.0"
location: Others/symphony/.codex/skills/push/SKILL.md
invoke: /skill push
description: |
  Push branch changes and create/update pull request.
triggers:
  - Asked to push or publish updates
```

### pull

```yaml
name: pull
version: "1.0.0"
location: Others/symphony/.codex/skills/pull/SKILL.md
invoke: /skill pull
description: |
  Pull origin/main and resolve merge conflicts.
triggers:
  - Need to sync feature branch with origin
```

### land

```yaml
name: land
version: "1.0.0"
location: Others/symphony/.codex/skills/land/SKILL.md
invoke: /skill land
description: |
  Land a PR with conflict resolution and CI monitoring.
triggers:
  - Asked to land, merge, or shepherd a PR
```

### debug

```yaml
name: debug
version: "1.0.0"
location: Others/symphony/.codex/skills/debug/SKILL.md
invoke: /skill debug
description: |
  Investigate stuck runs and execution failures.
triggers:
  - Runs stall, retry repeatedly, or fail unexpectedly
```

### linear

```yaml
name: linear
version: "1.0.0"
location: Others/symphony/.codex/skills/linear/SKILL.md
invoke: /skill linear
description: |
  Linear GraphQL operations for issue management.
triggers:
  - Need to interact with Linear API
```

---

## Skill Statistics

| Category | Count |
|----------|-------|
| Core (Auto-loaded) | 1 |
| Architecture & Planning | 2 |
| Development | 4 |
| Visualization | 4 |
| Git Workflow | 6 |
| **Total** | **17** |

## Core Skills (Auto-loaded)

| Skill | Purpose |
|-------|---------|
| skill-manager | Registry and invocation |

## Last Updated

2025-03-14

## Installation

### From GitHub

```bash
# Quick install
curl -sSL https://raw.githubusercontent.com/cycleuser/Skills/main/install.py | python

# Or clone and install
git clone https://github.com/cycleuser/Skills.git
cd Skills && python install.py install
```

### List Installed Skills

```bash
python install.py list
```

## How to Update Registry

Run `/skill reload` to scan for new skills and update this registry.