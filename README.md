# Skills Repository

A collection of specialized skills for AI coding agents. These skills provide structured workflows, templates, and guidelines for various software development tasks.

## Skills Overview

| Skill | Description | Install Command |
|-------|-------------|-----------------|
| **skill-manager** | Central skill registry and management | Auto-loaded |
| **master-architect** | Top-tier software architect agent | `/skill master-architect` |
| **python-project-developer** | Python CLI/GUI development | `/skill python-project-developer` |
| **software-planner** | Multi-interface software planning | `/skill software-planner` |
| **coding-agent-patterns** | AI coding agent patterns | `/skill coding-agent-patterns` |
| **iteration-manager** | Iterative testing and improvement | `/skill iteration-manager` |
| **academic-writer** | Academic paper writing | `/skill academic-writer` |

## Installation

### Method 1: Clone and Install (Recommended)

```bash
# Clone the repository
git clone https://github.com/cycleuser/Skills.git
cd Skills

# Run the installation script
python install.py
```

### Method 2: Direct URL Install

```bash
# Download and run installer in one command
curl -sSL https://raw.githubusercontent.com/cycleuser/Skills/main/install.py | python
```

### Method 3: Manual Install

```bash
# Clone to your workspace
git clone https://github.com/cycleuser/Skills.git ~/.opencode/skills

# Or copy specific skills
cp -r Skills/skills/skill-manager ~/.opencode/skills/
```

### Method 4: pip Install (Coming Soon)

```bash
pip install cycleuser-skills
```

## Skill Categories

### Core Skills (Auto-loaded)

| Skill | Purpose |
|-------|---------|
| skill-manager | Registry, discovery, and invocation of all skills |

### Architecture & Planning

| Skill | Purpose |
|-------|---------|
| master-architect | Top-tier architecture design and iterative development |
| software-planner | Multi-interface project planning (CLI+GUI+Web) |

### Development

| Skill | Purpose |
|-------|---------|
| python-project-developer | Python CLI/GUI development with ToolResult pattern |
| coding-agent-patterns | AI agent patterns (Claude Code, Codex, etc.) |
| iteration-manager | Iterative testing and quality improvement |

### Documentation

| Skill | Purpose |
|-------|---------|
| academic-writer | Academic paper writing (AAAI/IJCAI/IEEE) |

## Quick Start

```bash
# List all available skills
/skills

# Load a specific skill
/skill python-project-developer

# Get help for a skill
/skill help master-architect

# Start architecture design
/architect design "Build a text mining system"

# Run iterative development
/iterate 5
```

## Skill Structure

Each skill follows a standard structure:

```
skill-name/
├── SKILL.md              # Main skill definition
│   ├── frontmatter       # Metadata (name, version, triggers)
│   └── content           # Skill instructions and templates
└── rules/
    ├── rule1.md          # Detailed rules and patterns
    └── rule2.md
```

## Creating Custom Skills

To create a new skill:

```bash
# Create skill directory
mkdir -p skills/my-skill/rules

# Create SKILL.md
cat > skills/my-skill/SKILL.md << 'EOF'
---
name: my-skill
version: "1.0.0"
description: |
  Description of what this skill does.
  
  **Triggers when:**
  - Condition 1
  - Condition 2
---

# My Skill

Detailed instructions here.
EOF
```

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add your skill following the standard structure
4. Submit a pull request

## License

MIT License - See [LICENSE](LICENSE) for details.

## Repository

- **GitHub**: https://github.com/cycleuser/Skills
- **Issues**: https://github.com/cycleuser/Skills/issues
- **Releases**: https://github.com/cycleuser/Skills/releases