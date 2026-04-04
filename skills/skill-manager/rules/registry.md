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

## Writing Skills

### humanizer

```yaml
name: humanizer
version: "1.4"
location: .opencode/skills/humanizer/SKILL.md
invoke: /skill humanizer
description: |
  AI文本人化处理技能：将AIGC生成的文本润色成自然的人类语言。
triggers:
  - 需要降低文本的AIGC检测率
  - 将AI生成内容改写为人话
  - 优化文本使其更像人类写作风格
commands:
  - /人话 <文本> - 对文本进行人化处理
  - /humanize <text> - Humanize AI-generated text
  - /detect <文本> - 检测文本AIGC特征
rules:
  - anti-detection.md
  - ai-patterns.md
  - humanization-strategies.md
```

### literary-ghostwriter

```yaml
name: literary-ghostwriter
version: "2.1"
location: .opencode/skills/literary-ghostwriter/SKILL.md
invoke: /skill literary-ghostwriter
description: |
  文豪技能：模仿7位文学大师写作风格，追求"神似"而非"形似"。
  支持Shakespeare、鲁迅、金庸、古龙、Calvino、老舍、茨威格。
triggers:
  - 需要模仿特定作家风格写作
  - 文学创作和风格化表达
commands:
  - /文豪 <作家> <主题> - 按指定作家风格创作
  - /literary <author> <topic> - Create in author's style
rules:
  - shakespeare-style.md
  - luxun-style.md
  - jinyong-style.md
  - gulong-style.md
  - calvino-style.md
  - laoshe-style.md
  - zweig-style.md
```

### brief-write

```yaml
name: brief-write
version: "1.0"
location: .opencode/skills/brief-write/SKILL.md
invoke: /skill brief-write
description: |
  简写技能：模仿用户博客写作风格，用简洁直接、口语化、真诚坦率的语言表达。
  支持中英双语命令，能识别并避免"一眼AI"的写作模式。
triggers:
  - 需要模仿用户写作风格
  - 简练表达
  - 撰写博客文章、技术文档
commands:
  - /简写 <主题或文本> - 按用户风格改写或创作
  - /write <topic/text> - Write in user's style
  - /风格检查 <文本> - 检查是否符合简写风格
rules:
  - user-style.md
  - ai-patterns-avoid.md
```

### bao-kao

```yaml
name: bao-kao
version: "1.0"
location: .opencode/skills/bao-kao/SKILL.md
invoke: /skill bao-kao
description: |
  报考技能：类似资深报考顾问风格的考研高考报考指导。
  从官网搜索所有公开数据（专业列表、历年报考指南、一分一段表、录取分数线），进行交叉对比分析，给出实用建议。
triggers:
  - 高考报考咨询
  - 考研报考咨询
  - 专业选择咨询
  - 学校选择咨询
commands:
  - /报考 <查询内容> - 搜索分析报考数据
  - /enroll <query> - Search and analyze enrollment data
  - /专业 <专业名> - 分析专业就业前景
  - /major <name> - Analyze major employment prospects
  - /学校 <学校名> - 分析学校录取情况
  - /school <name> - Analyze school admission data
rules:
  - data-sources.md
  - analysis-methods.md
  - consultant-style.md
  - taboo-list.md
```

### skill-refiner

```yaml
name: skill-refiner
version: "1.0"
location: .opencode/skills/skill-refiner/SKILL.md
invoke: /skill skill-refiner
description: |
  修炼技能：对任意技能进行反复打磨改进，直到达到最优状态。
triggers:
  - 需要改进现有技能
  - 润色技能文档
  - 优化技能规则
commands:
  - /修炼 <技能名> - 对指定技能进行修炼
  - /refine <skill> - Refine a specific skill
rules:
  - refinement-process.md
  - quality-criteria.md
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
| Architecture & Planning | 1 |
| Development | 5 |
| Visualization | 4 |
| Writing | 5 |
| Git Workflow | 6 |
| **Total** | **22** |

## Core Skills (Auto-loaded)

| Skill | Purpose |
|-------|---------|
| skill-manager | Registry and invocation |

## Writing Skills

| Skill | Purpose |
|-------|---------|
| humanizer | AI text humanization |
| literary-ghostwriter | Literary style imitation |
| brief-write | User blog style imitation |
| bao-kao | Enrollment consultation |
| skill-refiner | Skill refinement |

## Last Updated

2026-04-04

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