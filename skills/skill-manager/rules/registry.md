# Skill Registry

Complete registry of all 22 available skills.

## Registry Format

Each entry contains: `name`, `version`, `location`, `description`, `commands`, `rules`.

---

## Core Skills (Auto-loaded)

### skill-manager

```yaml
name: skill-manager
version: "1.1.0"
location: skills/skill-manager/SKILL.md
description: |
  Central skill registry and management system. Auto-loaded on every session.
auto_load: true
priority: 0
commands:
  - /skills - List all skills
  - /skill <name> - Load skill
  - /skill reload - Refresh registry
  - /skill help <name> - Show details
rules:
  - registry.md
```

---

## Architecture & Planning

### master-architect

```yaml
name: master-architect
version: "1.0.0"
location: skills/master-architect/SKILL.md
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
location: skills/python-project-developer/SKILL.md
description: |
  Complete Python multi-project development specification for CLI/GUI tools.
triggers:
  - Creating Python projects with CLI/GUI support
  - Setting up pyproject.toml, README, and PyPI publishing
  - Implementing unified API with ToolResult pattern
commands:
  - /python-project init <name> - Initialize new project
  - /python-project structure - Generate project structure
  - /python-project api - Implement API pattern
  - /python-project cli - Add CLI with unified flags
  - /python-project test - Generate test suite
  - /python-project publish - Setup PyPI publishing
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
location: skills/software-planner/SKILL.md
description: |
  Comprehensive software development planning for Python projects with CLI, GUI, Web interfaces.
triggers:
  - Creating new Python software with multiple interfaces
  - Planning software architecture from academic research
  - Designing scientific or engineering applications
  - Setting up bilingual documentation and PyPI publishing
commands:
  - /planner research <topic> - Conduct domain research
  - /planner design <project> - Design system architecture
  - /planner modules - Generate module specifications
  - /planner docs - Create bilingual documentation
  - /planner verify - Run verification checklist
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
location: skills/coding-agent-patterns/SKILL.md
description: |
  Core patterns for AI coding agents based on Claude Code, Codex, Cline, Aider, OpenCode.
triggers:
  - Building AI coding agents
  - Implementing tool-calling loops
  - Managing context windows
  - Setting up agent memory systems
commands:
  - /agent-patterns loop - Core tool-calling loop
  - /agent-patterns context - Context management
  - /agent-patterns safety - Tool safety patterns
  - /agent-patterns memory - Memory system design
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
location: skills/iteration-manager/SKILL.md
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

### project-rebuilder

```yaml
name: project-rebuilder
version: "1.0.0"
location: skills/project-rebuilder/SKILL.md
description: |
  项目重建 - Rebuild projects from scratch referencing existing implementations.
  Uses team parallel review + ralph persistent execution mode.
triggers:
  - Rebuilding core features from reference projects
  - Deep refactoring of existing projects
  - Building similar products from scratch
commands:
  - /rebuild <project> <goal> - Start project rebuild
  - /rebuild analyze <project> - Analyze reference project
  - /rebuild team - Launch team review
  - /rebuild status - Check rebuild progress
rules:
  - project-analysis.md
  - team-review.md
  - ralph-execution.md
  - checkpoint.md
```

---

## Quality & Security

### an-jian

```yaml
name: an-jian
version: "1.0.0"
location: skills/an-jian/SKILL.md
description: |
  安检 - Security review for skills before installation.
  Detects dangerous commands, network leaks, file writes, credential exposure, resource exhaustion.
triggers:
  - Before installing new skills
  - Periodic security review of installed skills
  - Suspicion of compromised skill content
commands:
  - /安检 <skill-path> - Review skill security
  - /安检 scan <path> - Deep scan
  - /安检 list - List installed skill risks
  - /安检 fix <skill> - Fix security issues
  - /security <skill-path> - English command
rules:
  - dangerous-patterns.md
  - risk-assessment.md
  - fix-strategies.md
  - audit-format.md
```

### ba-guan

```yaml
name: ba-guan
version: "1.0.0"
location: skills/ba-guan/SKILL.md
description: |
  把关 - Pre-publish review with multi-layer deep analysis.
  Per-change review (up to 10 agents) → Holistic 5-role review → Synthesis.
triggers:
  - Preparing to publish npm packages
  - Pre-publish code review
  - Quality check of code changes
commands:
  - /把关 - Start pre-publish review
  - /把关 check - Check unpublished changes
  - /把关 version - Suggest version bump
  - /把关 report - Generate review report
  - /review - English command
rules:
  - change-detection.md
  - review-roles.md
  - version-bump.md
```

---

## Git Workflow

### he-bing

```yaml
name: he-bing
version: "1.0.0"
location: skills/he-bing/SKILL.md
description: |
  合并 - Complete PR lifecycle: worktree → implement → commits → PR → verify → merge.
  5-phase workflow with automatic verification loops and merge cleanup.
triggers:
  - Implementing features and submitting PRs
  - Fixing issues
  - Code review and merge workflows
commands:
  - /合并 <task> - Start full PR workflow
  - /合并 create <task> - Create PR
  - /合并 check - Check verification status
  - /合并 status - View PR status
  - /pr <task> - English command
rules:
  - worktree.md
  - commit-atomic.md
  - verification.md
```

---

## Writing Skills

### academic-writer

```yaml
name: academic-writer
version: "3.0.0"
location: skills/academic-writer/SKILL.md
description: |
  Academic paper writing assistant for top-tier conferences (AAAI, IJCAI, IEEE).
  Literature search, citation formatting, figure quality, reviewer response, opencode workflow.
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
  - /paper figures - Figure quality check
  - /paper rebuttal - Write reviewer response
rules:
  - literature-search.md
  - citation-format.md
  - paper-structure.md
  - writing-style.md
  - anti-ai-patterns.md
  - figure-quality.md
  - reviewer-response.md
  - opencode-experience.md
```

### humanizer

```yaml
name: humanizer
version: "1.4.0"
location: skills/humanizer/SKILL.md
description: |
  AI text humanizer that rewrites AI-generated content into natural human language
  using AIGC detection countermeasures.
triggers:
  - Reducing AIGC detection rates
  - Rewriting AI content into natural language
  - Humanization polish on AI text
commands:
  - /人话 <text> - Humanize text
  - /人话 --style formal <text> - Formal style
  - /人话 --style casual <text> - Casual style
  - /humanize <text> - Humanize (English)
  - /detect <text> - Detect AIGC features
  - /demo - Generate demo
rules:
  - ai-features.md
  - detection-methods.md
  - humanization.md
  - formal-humanization.md
  - iteration.md
  - examples.md
```

### literary-ghostwriter

```yaml
name: literary-ghostwriter
version: "2.1.0"
location: skills/literary-ghostwriter/SKILL.md
description: |
  文豪代笔 - Imitate writing styles of 7 literary masters.
  3 Western (Shakespeare, Zweig, Calvino) + 4 Chinese (Lu Xun, Lao She, Jin Yong, Gu Long).
triggers:
  - Creating works in specific author styles
  - Literary creation, script writing, novel writing
  - Style imitation practice
commands:
  - /文豪 <author> <topic> - Create in author style (CN)
  - /literary <author> <topic> - Create in author style (EN)
rules:
  - shakespeare-style.md
  - luxun-style.md
  - jinyong-style.md
  - gulong-style.md
  - calvino-style.md
  - laoshe-style.md
  - zweig-style.md
  - vocabulary.md
```

### brief-write

```yaml
name: brief-write
version: "1.0.0"
location: skills/brief-write/SKILL.md
description: |
  简写 - Mimic user's blog writing style: concise, direct, colloquial, honest.
  Bilingual CN/EN with anti-AI-pattern detection.
triggers:
  - Mimicking user writing style
  - Concise expression
  - Blog posts, technical documentation
commands:
  - /简写 <text> - Rewrite in user style
  - /write <text> - Write in user style (EN)
  - /风格检查 <text> - Check style compliance
  - /style-check <text> - Style check (EN)
rules:
  - user-style.md
  - ai-patterns-avoid.md
```

### official-document-writer

```yaml
name: official-document-writer
version: "1.0.0"
location: skills/official-document-writer/SKILL.md
description: |
  Official document writing assistant for Chinese government documents (公文).
  Based on GB/T 9704-2012 standard with 15 document types.
triggers:
  - Writing Chinese official documents (公文)
  - Formatting documents by national standards
  - Reviewing document compliance
commands:
  - /gongwen notice <topic> - Write notice (通知)
  - /gongwen report <topic> - Write report (报告)
  - /gongwen request <topic> - Write request (请示)
  - /gongwen reply <topic> - Write reply (批复)
  - /gongwen letter <topic> - Write letter (函)
  - /gongwen minutes <topic> - Write minutes (纪要)
  - /gongwen check <doc> - Check compliance
  - /gongwen format - Show formatting rules
rules:
  - document-types.md
  - formatting-rules.md
  - templates.md
  - writing-guidelines.md
```

---

## Patent & Legal

### patent-writer

```yaml
name: patent-writer
version: "2.0.0"
location: skills/patent-writer/SKILL.md
description: |
  Patent writing assistant for Chinese patents. Search, disclosure documents,
  filing strategy, blocking risk assessment, writing guidelines.
triggers:
  - Writing patent applications
  - Creating patent disclosure documents
  - Patent search and analysis
  - Planning patent strategy
commands:
  - /patent search <keywords> - Patent search
  - /patent disclosure <invention> - Write disclosure
  - /patent report <invention> - Self-search report
  - /patent workflow - Show workflow
  - /patent strategy - Filing strategy
  - /patent check - Quality checklist
  - /patent examples - Show examples
rules:
  - patent-search.md
  - disclosure-document.md
  - patent-workflow.md
  - writing-tips.md
```

---

## Consultation

### bao-kao

```yaml
name: bao-kao
version: "1.0.0"
location: skills/bao-kao/SKILL.md
description: |
  报考 - Enrollment consultation for college/graduate entrance exams.
  Searches official data sources, cross-compares admission data, practical advice.
triggers:
  - College entrance exam consultation (高考)
  - Graduate entrance exam consultation (考研)
  - Major selection consultation (专业选择)
  - School selection consultation (学校选择)
commands:
  - /报考 <query> - Search and analyze enrollment data
  - /enroll <query> - Search enrollment data (EN)
  - /专业 <major> - Analyze major prospects
  - /major <name> - Analyze major (EN)
  - /学校 <school> - Analyze school admission
  - /school <name> - Analyze school (EN)
rules:
  - data-sources.md
  - analysis-methods.md
  - consultant-style.md
  - taboo-list.md
  - search-methods.md
```

---

## Autonomous Execution

### sleepless

```yaml
name: sleepless
version: "1.0.0"
location: skills/sleepless/SKILL.md
description: |
  修仙 - Sleepless autonomous execution. No sleep, no ask, no pause — works until task is complete.
  Supports 8 task modes: Dev, Fix, Refactor, Test, Doc, Iterate, Integrate, Explore.
triggers:
  - Long-running autonomous work
  - Overnight execution of development tasks
  - Any task requiring "set it and forget it" execution
commands:
  - /修仙 <task> - Start sleepless execution
  - /修仙 <task> --budget <level> - With budget
  - /修仙 status - Check status
  - /修仙 log - View log
  - /sleepless <task> - English command
rules:
  - autonomous-loop.md
  - eternal-drive.md
  - task-omnipotence.md
```

### power-iterate

```yaml
name: power-iterate
version: "2.1.0"
location: skills/power-iterate/SKILL.md
description: |
  强力迭代 - Fully autonomous continuous iteration until time/token budget exhausted.
  Auto-understands requirements, designs evaluation plans, plans iteration paths.
triggers:
  - Requests for power iteration
  - Continuous development
  - Non-stop work with explicit time/token budget
commands:
  - /强力迭代 <task> [budget] - Start power iteration
  - /power-iterate <task> [budget] - English command
rules:
  - autonomous-loop.md
  - budget-manager.md
  - task-decomposition.md
```

### zi-kong

```yaml
name: zi-kong
version: "1.0.0"
location: skills/zi-kong/SKILL.md
description: |
  自控 - Self-controlled autonomous iteration for opencode itself.
  Cross-session memory, self-review, budget control, parallel tasks, decision tree, rollback.
triggers:
  - opencode self-improvement
  - Continuous iteration of skills
  - Autonomous long-running tasks
commands:
  - /自控 <goal> - Start autonomous iteration
  - /自控 status - Check status
  - /自控 pause - Pause iteration
  - /自控 resume - Resume iteration
  - /自控 log - View log
  - /auto <goal> - English command
rules:
  - autonomous-loop.md
  - memory.md
  - budget.md
  - safety.md
  - self-review.md
```

---

## Skill Management

### skill-refiner

```yaml
name: skill-refiner
version: "1.0.0"
location: skills/skill-refiner/SKILL.md
description: |
  修炼 - Repeatedly polish and improve any skill until optimal state.
  Deep analysis → improvement plans → iterative optimization → validation.
triggers:
  - Improving existing skills
  - Polishing skill documentation
  - Optimizing skill rules
  - Fixing skill defects
commands:
  - /修炼 <skill> - Refine specified skill
  - /refine <skill> - Refine skill (EN)
rules:
  - diagnosis.md
  - improvement.md
  - templates.md
  - validation.md
```

---

## GitHub Tools

### shen-shi

```yaml
name: shen-shi
version: "1.0.0"
location: skills/shen-shi/SKILL.md
description: |
  审视 - Read-only GitHub triage for issues and PRs.
  Evidence-backed analysis, parallel processing, report generation — never modifies GitHub state.
triggers:
  - Analyzing GitHub Issues or PRs
  - Generating review reports
  - Classifying issues
commands:
  - /审视 analyze <repo> - Analyze all open issues/PRs
  - /审视 issues <repo> - Analyze issues only
  - /审视 prs <repo> - Analyze PRs only
  - /审视 <URL> - Analyze specific issue/PR
  - /analyze <repo> - English command
rules:
  - classification.md
  - evidence.md
  - report-format.md
```

---

## Skill Statistics

| Category | Count | Skills |
|----------|-------|--------|
| Core (Auto-loaded) | 1 | skill-manager |
| Architecture & Planning | 1 | master-architect |
| Development | 5 | python-project-developer, software-planner, coding-agent-patterns, iteration-manager, project-rebuilder |
| Quality & Security | 2 | an-jian, ba-guan |
| Git Workflow | 1 | he-bing |
| Writing | 5 | academic-writer, humanizer, literary-ghostwriter, brief-write, official-document-writer |
| Patent & Legal | 1 | patent-writer |
| Consultation | 1 | bao-kao |
| Autonomous Execution | 3 | sleepless, power-iterate, zi-kong |
| Skill Management | 1 | skill-refiner |
| GitHub Tools | 1 | shen-shi |
| **Total** | **22** | |

## Quick Reference Tables

### Core Skills (Auto-loaded)

| Skill | Purpose |
|-------|---------|
| skill-manager | Registry and invocation |

### Writing Skills

| Skill | Purpose |
|-------|---------|
| academic-writer | Academic paper writing for top conferences |
| humanizer | AI text humanization |
| literary-ghostwriter | Literary style imitation (7 masters) |
| brief-write | User blog style imitation |
| official-document-writer | Chinese government documents (GB/T 9704-2012) |

### Development Skills

| Skill | Purpose |
|-------|---------|
| python-project-developer | Python CLI/GUI project scaffolding |
| software-planner | Multi-interface software planning |
| coding-agent-patterns | AI coding agent architecture |
| iteration-manager | Iterative testing and improvement |
| project-rebuilder | Rebuild projects from scratch |

### Autonomous Execution

| Skill | Purpose |
|-------|---------|
| sleepless | Non-stop execution until complete |
| power-iterate | Continuous iteration with budget |
| zi-kong | Self-controlled iteration for opencode |

## Last Updated

2026-05-09
