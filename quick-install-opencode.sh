#!/bin/bash
# Quick Install Script for OpenCode Skills and Commands
# Usage: curl -sSL https://raw.githubusercontent.com/cycleuser/Skills/main/quick-install-opencode.sh | bash

set -e

echo "========================================"
echo "  OpenCode Skills & Commands Installer"
echo "========================================"
echo ""

SKILLS_DIR="$HOME/.config/opencode/skills"
COMMANDS_DIR="$HOME/.config/opencode/commands"

if command -v python3 &> /dev/null; then
    PYTHON="python3"
elif command -p python &> /dev/null; then
    PYTHON="python"
else
    echo "Error: Python not found. Please install Python 3."
    exit 1
fi

echo "Installing to:"
echo "  Skills: $SKILLS_DIR"
echo "  Commands: $COMMANDS_DIR"
echo ""

mkdir -p "$SKILLS_DIR"
mkdir -p "$COMMANDS_DIR"

SKILLS=(
    "skill-manager"
    "master-architect"
    "python-project-developer"
    "software-planner"
    "coding-agent-patterns"
    "iteration-manager"
    "academic-writer"
)

COMMANDS=(
    "architect"
    "python-dev"
    "plan"
    "iterate"
    "academic"
    "skills"
)

RAW_URL="https://raw.githubusercontent.com/cycleuser/Skills/main"

echo "========================================"
echo "  Installing Skills"
echo "========================================"

for skill in "${SKILLS[@]}"; do
    echo "Installing: $skill"
    mkdir -p "$SKILLS_DIR/$skill"
    
    curl -sSL "$RAW_URL/skills/$skill/SKILL.md" -o "$SKILLS_DIR/$skill/SKILL.md.tmp" 2>/dev/null
    
    if [ -f "$SKILLS_DIR/$skill/SKILL.md.tmp" ]; then
        cat "$SKILLS_DIR/$skill/SKILL.md.tmp" | sed 's/^description: |/description: /' | sed '/^  /d' > "$SKILLS_DIR/$skill/SKILL.md"
        rm "$SKILLS_DIR/$skill/SKILL.md.tmp"
        echo "  ✓ $skill installed"
    else
        echo "  ✗ Failed to download $skill"
    fi
done

echo ""
echo "========================================"
echo "  Installing Commands"
echo "========================================"

for cmd in "${COMMANDS[@]}"; do
    echo "Installing: /$cmd"
    
    curl -sSL "$RAW_URL/commands/$cmd.md" -o "$COMMANDS_DIR/$cmd.md" 2>/dev/null
    
    if [ -f "$COMMANDS_DIR/$cmd.md" ]; then
        echo "  ✓ /$cmd installed"
    else
        echo "  ✗ Failed to download /$cmd"
    fi
done

echo ""
echo "========================================"
echo "  Installation Complete!"
echo "========================================"
echo ""
echo "Installed ${#SKILLS[@]} skills and ${#COMMANDS[@]} commands"
echo ""
echo "Available Commands:"
echo "  /architect <task>  - Architecture design"
echo "  /python-dev <task> - Python development"
echo "  /plan <task>       - Software planning"
echo "  /iterate <task>    - Iterative testing"
echo "  /academic <task>   - Academic writing"
echo "  /skills            - List all skills"
echo ""
echo "Quick Start:"
echo "  1. Run 'opencode' in your project"
echo "  2. Type /architect to design an architecture"
echo "  3. Type /python-dev to start Python development"
echo ""