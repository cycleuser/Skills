# Skills Repository

A collection of specialized skills for AI coding agents. These skills provide structured workflows, templates, and guidelines for various software development tasks.

## Features

- **20 Production-Ready Skills** - Covering architecture, development, testing, writing, patents, official documents, text humanization, literary style imitation, blog style writing, skill refinement, project rebuilding, GitHub triage, review, PR workflow, security review, autonomous iteration, and more
- **30 Commands** - English and Chinese commands supported
- **OpenCode Compatible** - Native support for OpenCode's skill system
- **Auto-Discovery** - Skills are automatically loaded based on context
- **Modular Design** - Each skill is self-contained with rules and templates
- **Cross-Platform** - Works on macOS, Linux, and Windows

## Skills Overview

| Skill | Description | Use Case |
|-------|-------------|----------|
| **skill-manager** | Central skill registry and management | Auto-loaded |
| **master-architect** | Top-tier software architect agent | Architecture design |
| **python-project-developer** | Python CLI/GUI development | Python projects |
| **software-planner** | Multi-interface software planning | Project planning |
| **coding-agent-patterns** | AI coding agent patterns | Development patterns |
| **iteration-manager** | Iterative testing and improvement | Quality assurance |
| **academic-writer** | Academic paper writing | Research writing |
| **patent-writer** | Patent writing assistant | Patent applications |
| **official-document-writer** | Official document writing (GB/T 9704-2012) | Official documents |
| **humanizer** | AI text humanization | Natural language processing |
| **literary-ghostwriter** | Literary style imitation (7 masters) | Literary writing |
| **brief-write** | User blog style imitation | Blog & technical writing |
| **skill-refiner** | Skill refinement and polishing | Skill improvement |
| **project-rebuilder** | Reference project rebuilding | Project migration |
| **shen-shi** | GitHub triage (read-only) | Issue analysis |
| **ba-guan** | Pre-publish 3-layer review | Quality review |
| **he-bing** | Complete PR workflow | Pull requests |
| **an-jian** | Skill security review | Security analysis |
| **zi-kong** | Autonomous iteration | Self-controlling work |
| **power-iterate** | Autonomous continuous iteration | Time/token budget work |

## Installation

### Quick Install for OpenCode (Recommended)

```bash
# One-line installation
curl -sSL https://raw.githubusercontent.com/cycleuser/Skills/main/quick-install-opencode.sh | bash
```

### Python Installer

```bash
# Install from GitHub
curl -sSL https://raw.githubusercontent.com/cycleuser/Skills/main/install-opencode.py | python3 install

# Or clone and install locally
git clone https://github.com/cycleuser/Skills.git
cd Skills
python3 install-opencode.py install --source .
```

### Platform-Specific Commands

**macOS / Linux:**
```bash
curl -fsSL https://raw.githubusercontent.com/cycleuser/Skills/main/quick-install-opencode.sh | bash
```

**Windows (PowerShell):**
```powershell
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/cycleuser/Skills/main/install-opencode.py" -OutFile "install-opencode.py"
python install-opencode.py install
```

**Windows (WSL):**
```bash
curl -fsSL https://raw.githubusercontent.com/cycleuser/Skills/main/quick-install-opencode.sh | bash
```

## Verification

```bash
# List installed skills
python3 install-opencode.py list

# Show skill details
python3 install-opencode.py info --skills master-architect

# Check installation directory
ls ~/.config/opencode/skills/
```

## Quick Commands

After installation, use these commands in OpenCode:

| Command | Description |
|---------|-------------|
| `/architect <task>` | Design system architecture |
| `/python-dev <task>` | Python project development |
| `/plan <task>` | Software planning |
| `/iterate <task>` | Iterative testing |
| `/power-iterate <task> [budget]` | Autonomous iteration until budget exhausted |
| `/academic <task>` | Academic writing |
| `/patent <task>` | Patent writing |
| `/gongwen <task>` | Official document writing |
| `/humanize <text>` | Humanize AI-generated text |
| `/literary <author> <topic>` | Literary style writing |
| `/write <topic>` | Blog style writing |
| `/refine <skill>` | Skill refinement |
| `/rebuild <project>` | Project rebuilding |
| `/analyze <repo>` | GitHub triage |
| `/review <text>` | Pre-publish review |
| `/pr` | PR workflow |
| `/security <skill>` | Security review |
| `/auto <task>` | Autonomous iteration |
| `/skills` | List all skills |

### Command Examples

```bash
# Architecture design
/architect Build a text mining system with CLI and GUI

# Python development
/python-dev Create a CSV analyzer with JSON output

# Software planning
/plan Design a multi-platform application

# Iterative testing
/iterate Improve test coverage to 90%

# Power iterate - autonomous until budget exhausted
/power-iterate Build a complete REST API --time 60 --tokens 100000

# Academic writing
/academic Write a paper about deep learning for NLP

# Patent writing
/patent Write a disclosure document for an AI-based image recognition method

# Official document writing
/gongwen Write a notice about safety production

# Humanize AI text
/humanize 本文将全面介绍优化器的核心原理...

# Literary style writing
/literary luxun 如何面对困境

# Blog style writing
/write 如何搭建本地AI编程环境

# Skill refinement
/refine literary-ghostwriter

# GitHub triage
/analyze https://github.com/user/repo

# Pre-publish review
/review 这篇文章的内容需要把关

# Security review
/security oh-my-openagent

# Autonomous iteration
/auto Build a Python CLI tool

**Note:** Chinese commands are also available. See [README_CN.md](README_CN.md) for Chinese documentation.

## Usage Examples

### Example 1: Architecture Design

In OpenCode, describe your project:

```
I need to design a text mining system with CLI and GUI interfaces,
capable of processing large-scale text data and generating visual reports.
Please help me plan the complete architecture.
```

OpenCode will automatically load the `master-architect` skill and provide:
- Requirement analysis
- Architecture design
- Module decomposition
- Iterative development plan

### Example 2: Python Project Development

```
Create a Python CLI tool for analyzing CSV files and generating statistical reports.
It should support JSON output and verbose logging mode.
```

The skill provides:
- Project structure template
- CLI standardized flags
- ToolResult API pattern
- Test case templates

### Example 3: Iterative Improvement

```
Run the test suite, analyze coverage, and provide improvement suggestions.
Target is 90%+ code coverage.
```

### Example 4: Academic Writing

```
Help me write a paper about deep learning in natural language processing,
targeting AAAI 2024.
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

## CLI Management

```bash
# List all installed skills
python3 install-opencode.py list

# Show skill information
python3 install-opencode.py info --skills <skill-name>

# Install specific skills
python3 install-opencode.py install --skills master-architect python-project-developer

# Install to project directory (instead of global)
python3 install-opencode.py install --local

# Uninstall skills
python3 install-opencode.py uninstall --skills <skill-name>
```

## Skill Structure

Each skill follows a standard structure:

```
skill-name/
├── SKILL.md              # Main skill definition with frontmatter
└── rules/
    ├── rule1.md          # Detailed rules and patterns
    └── rule2.md
```

### SKILL.md Format

```yaml
---
name: skill-name
description: Brief description of the skill
license: MIT
compatibility: opencode
metadata:
  version: "1.0.0"
  author: cycleuser
---

# Skill Title

Detailed skill instructions and templates...
```

## Integration with AGENTS.md

Create an `AGENTS.md` file in your project root:

```markdown
# Project Instructions

This project uses cycleuser/Skills specifications.

## Development Standards
- Follow python-project-developer CLI flag standards
- Use ToolResult pattern for API return types
- Require 80%+ test coverage
```

## Creating Custom Skills

```bash
# Create skill directory
mkdir -p skills/my-skill/rules

# Create SKILL.md
cat > skills/my-skill/SKILL.md << 'EOF'
---
name: my-skill
description: Description of what this skill does
license: MIT
compatibility: opencode
---

# My Skill

Detailed instructions here.
EOF

# Add rules
echo "# Rule Title\n\nRule content..." > skills/my-skill/rules/my-rule.md

# Install the skill
python3 install-opencode.py install --source .
```

## Troubleshooting

### Skills Not Loading

1. Verify installation directory: `~/.config/opencode/skills/`
2. Check SKILL.md file exists
3. Validate frontmatter format

### Permission Denied

```bash
chmod +x quick-install-opencode.sh
```

### Reinstall

```bash
python3 install-opencode.py uninstall --skills <skill-name>
python3 install-opencode.py install
```

## Documentation

- [OpenCode Usage Guide](OPENCODE_USAGE.md) - Detailed usage examples
- [Skills Specification](skills.json) - Skill registry
- [OpenCode Docs](https://opencode.ai/docs/skills/) - Official documentation

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add your skill following the standard structure
4. Submit a pull request

## License

MIT License - See [LICENSE](LICENSE) for details.

## Links

- **GitHub**: https://github.com/cycleuser/Skills
- **Issues**: https://github.com/cycleuser/Skills/issues
- **Releases**: https://github.com/cycleuser/Skills/releases
- **OpenCode**: https://opencode.ai