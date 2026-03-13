---
name: skill-manager
version: "1.0.0"
auto_load: true
load_priority: 0
description: |
  Central skill registry and management system. Auto-loaded on every session.

  **Auto-loaded on startup** - This skill is automatically loaded to provide
  skill discovery and invocation capabilities.

  **Commands:**
  - `/skills` - List all available skills with descriptions
  - `/skill <name>` - Load and activate a specific skill
  - `/skill reload` - Refresh skill registry
  - `/skill help <name>` - Show detailed help for a skill

  **Capabilities:**
  - Auto-discovery of all skills in workspace
  - Unified skill invocation via /skill command
  - Skill registry with metadata and descriptions
  - Version tracking and dependency management
author: system
license: MIT
---

# Skill Manager

Central registry for all skills in the workspace. Auto-loaded on session start.

## Quick Commands

| Command | Description |
|---------|-------------|
| `/skills` | List all available skills |
| `/skill <name>` | Load a specific skill |
| `/skill help <name>` | Show skill details |
| `/skill reload` | Refresh registry |

## Available Skills

### Core Skills (Auto-loaded)

| Skill | Description | Invoke |
|-------|-------------|--------|
| **skill-manager** | Registry and management (auto-loaded) | Auto-loaded |

### Architecture & Planning

| Skill | Description | Invoke |
|-------|-------------|--------|
| **master-architect** | Top-tier software architect agent | `/skill master-architect` |
| **software-planner** | Multi-interface software planning | `/skill software-planner` |

### Development Skills

| Skill | Description | Invoke |
|-------|-------------|--------|
| **python-project-developer** | Python CLI/GUI development with ToolResult pattern | `/skill python-project-developer` |
| **software-planner** | Multi-interface software planning (CLI+GUI+Web) | `/skill software-planner` |
| **coding-agent-patterns** | AI coding agent patterns (Claude Code, Codex, etc.) | `/skill coding-agent-patterns` |
| **iteration-manager** | Iterative testing and improvement supervisor | `/skill iteration-manager` |
| **academic-writer** | Academic paper writing (AAAI/IJCAI/IEEE) | `/skill academic-writer` |

### Visualization Skills (manim-video-generator)

| Skill | Description | Invoke |
|-------|-------------|--------|
| **math-visualizer** | Mathematical equations, proofs, geometry | `/skill math-visualizer` |
| **visual-storyteller** | Narrative-driven educational animations | `/skill visual-storyteller` |
| **animation-composer** | Scene composition and orchestration | `/skill animation-composer` |
| **motion-graphics** | Kinetic typography, logo animations | `/skill motion-graphics` |

### Git Workflow Skills (symphony)

| Skill | Description | Invoke |
|-------|-------------|--------|
| **commit** | Well-formed git commits with context | `/skill commit` |
| **push** | Push branch and create/update PR | `/skill push` |
| **pull** | Merge origin/main with conflict resolution | `/skill pull` |
| **land** | PR merge workflow with CI monitoring | `/skill land` |
| **debug** | Investigate stuck runs and failures | `/skill debug` |
| **linear** | Linear GraphQL operations | `/skill linear` |

## Skill Registry

Full registry available at: [rules/registry.md](rules/registry.md)

## How Skills Work

### Skill Discovery

Skills are discovered from these locations:

```
.opencode/skills/           # Workspace-level skills (highest priority)
project/.opencode/skills/   # Project-level skills
project/.codex/skills/      # Codex-format skills
```

### Skill Loading

When you invoke `/skill <name>`:

1. Manager searches registry for matching skill
2. Loads the SKILL.md file
3. Activates all rules in the skill's rules/ directory
4. Returns skill context to the current session

### Skill Structure

```
skill-name/
├── SKILL.md              # Main skill definition
│   ├── frontmatter       # Metadata (name, version, triggers)
│   └── content           # Skill instructions
└── rules/
    ├── rule1.md          # Detailed rules
    └── rule2.md
```

## Creating New Skills

To create a new skill:

```bash
# Create skill directory
mkdir -p .opencode/skills/my-skill/rules

# Create SKILL.md with frontmatter
cat > .opencode/skills/my-skill/SKILL.md << 'EOF'
---
name: my-skill
version: "1.0.0"
description: |
  Brief description of what this skill does.
  
  **Triggers when:**
  - Condition 1
  - Condition 2
---

# My Skill

Detailed skill instructions here.
EOF

# Add rules
echo "# Rule Title\n\nRule content..." > .opencode/skills/my-skill/rules/my-rule.md
```

## Registry Update

To update the skill registry after adding new skills:

```
/skill reload
```

This will rescan all skill directories and update the registry.

## Installation

### From GitHub (Recommended)

```bash
# Quick install (Unix/macOS)
curl -sSL https://raw.githubusercontent.com/cycleuser/Skills/main/quick-install.sh | bash

# Quick install (Windows)
curl -sSL https://raw.githubusercontent.com/cycleuser/Skills/main/quick-install.bat | cmd

# Or use Python installer
curl -sSL https://raw.githubusercontent.com/cycleuser/Skills/main/install.py | python
```

### Manual Install

```bash
# Clone repository
git clone https://github.com/cycleuser/Skills.git

# Run installer
cd Skills && python install.py install

# Or copy directly
cp -r skills/* ~/.opencode/skills/
```

### Verify Installation

```bash
python install.py list
```

## Repository

- **GitHub**: https://github.com/cycleuser/Skills
- **Issues**: https://github.com/cycleuser/Skills/issues