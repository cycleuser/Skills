---
name: skill-manager
version: "1.1.0"
description: |
  Central skill registry and management system, auto-loaded on session start for skill discovery and invocation.

  Triggers when: Listing available skills, loading or activating a specific skill, refreshing the skill registry, or viewing skill help information.

  Commands:
  - /skills - List all available skills with descriptions
  - /skill <name> - Load and activate a specific skill
  - /skill reload - Refresh skill registry
  - /skill help <name> - Show detailed help for a skill

  Capabilities: Auto-discovery of all skills in workspace, unified skill invocation via /skill command, skill registry with metadata and descriptions, version tracking and dependency management
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

# Skill Manager

Central registry for all skills in the workspace. Auto-loaded on session start.

## Quick Commands

| Command | Description |
|---------|-------------|
| `/skills` | List all available skills with descriptions |
| `/skill <name>` | Load and activate a specific skill |
| `/skill help <name>` | Show detailed help for a skill |
| `/skill reload` | Refresh skill registry |

## Available Skills

### Core Skills (Auto-loaded)

The skill-manager provides registry and management capabilities and is auto-loaded on session start.

### Architecture & Planning

Two skills support architecture and planning. The master-architect skill provides top-tier software architect agent capabilities. The software-planner skill supports multi-interface software planning.

### Development Skills

Five development skills are available. The python-project-developer skill supports Python CLI/GUI development with the ToolResult pattern. The software-planner skill supports multi-interface software planning with CLI, GUI, and Web interfaces. The coding-agent-patterns skill covers AI coding agent patterns from Claude Code, Codex, and similar tools. The iteration-manager skill supervises iterative testing and improvement. The academic-writer skill supports academic paper writing for AAAI, IJCAI, and IEEE conferences.

### Visualization Skills (manim-video-generator)

Four visualization skills are available. The math-visualizer skill handles mathematical equations, proofs, and geometry. The visual-storyteller skill creates narrative-driven educational animations. The animation-composer skill provides scene composition and orchestration. The motion-graphics skill handles kinetic typography and logo animations.

### Git Workflow Skills (symphony)

Six git workflow skills are available. The commit skill creates well-formed git commits with context. The push skill pushes branches and creates or updates PRs. The pull skill merges origin/main with conflict resolution. The land skill handles PR merge workflow with CI monitoring. The debug skill investigates stuck runs and failures. The linear skill handles Linear GraphQL operations.

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

A skill directory contains a SKILL.md file as the main skill definition with frontmatter for metadata (name, version, triggers) and content for skill instructions. The rules/ subdirectory contains detailed rules as separate markdown files.

## Creating New Skills

To create a new skill, first create the skill directory structure with `mkdir -p .opencode/skills/my-skill/rules`. Then create SKILL.md with proper frontmatter including name, version, and description fields. Add detailed rules as separate markdown files in the rules/ subdirectory. After creating new skills, use the `/skill reload` command to update the registry.

## Registry Update

To update the skill registry after adding new skills:

```
/skill reload
```

This will rescan all skill directories and update the registry.

## Installation

⚠️ **SAFETY NOTE**: The commands below follow safety rules — they download scripts for inspection before execution. Never pipe `curl` directly to `bash` without visual review. See [global-rules/bash-safety.md](file:///Users/fred/.config/opencode/skills/global-rules/rules/bash-safety.md).

### From GitHub (Recommended)

```bash
# Quick install (Unix/macOS) - Download and inspect first, then run
# ⚠️ WARNING: `curl|bash` is a security risk — always inspect scripts before executing
curl -sSL https://raw.githubusercontent.com/cycleuser/Skills/main/quick-install.sh -o /tmp/install_skills.sh && less /tmp/install_skills.sh && bash /tmp/install_skills.sh

# Quick install (Windows) - Download and inspect first
# ⚠️ WARNING: Always inspect scripts before executing
curl -sSL https://raw.githubusercontent.com/cycleuser/Skills/main/quick-install.bat -o %TEMP%\install_skills.bat && type %TEMP%\install_skills.bat && %TEMP%\install_skills.bat

# Or use Python installer - Download and inspect first
# ⚠️ WARNING: Always inspect scripts before executing
curl -sSL https://raw.githubusercontent.com/cycleuser/Skills/main/install.py -o /tmp/install_skills.py && less /tmp/install_skills.py && python /tmp/install_skills.py
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

## Integration with Other Skills

### Skill Discovery and Usage
The skill-manager works with all other skills. Use `/skills` to see the complete registry of available skills. Each skill can be loaded with `/skill <name>` and used independently or in combination with others.

### Common Skill Combinations
- **Development Projects**: Combine `python-project-developer`, `coding-agent-patterns`, and `academic-writer` for complete software development, documentation, and research workflows.
- **Research Projects**: Use `academic-writer` for paper writing, `literary-ghostwriter` for creative writing, and `patent-writer` for IP protection.
- **Code Quality**: Use `humanizer` to improve generated text, `an-jian` to audit skills before installation, and `iteration-manager` to improve code iteratively.
- **Project Management**: Combine `master-architect` for planning, `he-bing` for PR workflows, and `ba-guan` for pre-publish review.

## Troubleshooting

### Skill not found
- **Symptom**: `/skill <name>` returns "skill not found"
- **Fix**: Run `/skill reload` to rescan the skills directory; check that SKILL.md exists at `skills/<name>/SKILL.md`; verify the skill is listed in `/skills` output

### Registry mismatch
- **Symptom**: `/skills` shows different skills than what's actually in the directory
- **Fix**: Run `/skill reload` to regenerate the registry; if mismatch persists, manually update `rules/registry.md` or delete it and reload

### Cross-skill reference broken
- **Symptom**: Skill A references `/command` from Skill B, but command doesn't exist
- **Fix**: Run `/skills` to verify both skills are registered; check the referenced skill's Quick Commands table for correct command syntax

## Usage Examples

### Loading a Skill
```
/skills                    # List all available skills
/skill academic-writer     # Load the academic-writer skill
/skill help humanizer      # Show detailed help for humanizer
```

### Refreshing the Registry
```
/skill reload              # Rescan and update the skill registry
/skills                    # Verify the updated list
```

## Edge Cases

- **Skill directory name mismatch**: If a skill's directory name differs from its `name` field in frontmatter, the SKILL.md name takes priority for `/skill <name>`
- **Duplicate skill names**: If two skills share the same name, the first discovered by glob takes priority; manually rename to resolve
- **Corrupt SKILL.md**: If frontmatter is malformed, the skill is skipped in the registry with a warning to stderr
- **Missing rules/ directory**: Skills without a rules/ directory are still registered; missing rule file references are noted as warnings

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-04-01 | Initial version, skill discovery and loading |
| 1.1.0 | 2026-05-09 | Fixed registry (10 dead refs removed, 10 unregistered skills added, 5 rule filename mismatches corrected); added troubleshooting, version history |

## See Also

- `/修炼` from **skill-refiner** — Polish and improve skills in the registry
- `/agent-patterns memory` from **coding-agent-patterns** — Memory system patterns for skill loading