#!/bin/bash
# Quick Install Script for OpenCode Skills
# Usage: curl -sSL https://raw.githubusercontent.com/cycleuser/Skills/main/quick-install-opencode.sh | bash

set -e

echo "========================================"
echo "  OpenCode Skills Installer"
echo "========================================"
echo ""

INSTALL_DIR="$HOME/.config/opencode/skills"

if command -v python3 &> /dev/null; then
    PYTHON="python3"
elif command -p python &> /dev/null; then
    PYTHON="python"
else
    echo "Error: Python not found. Please install Python 3."
    exit 1
fi

echo "Installing to: $INSTALL_DIR"
echo ""

mkdir -p "$INSTALL_DIR"

SKILLS=(
    "skill-manager"
    "master-architect"
    "python-project-developer"
    "software-planner"
    "coding-agent-patterns"
    "iteration-manager"
    "academic-writer"
)

RAW_URL="https://raw.githubusercontent.com/cycleuser/Skills/main"

for skill in "${SKILLS[@]}"; do
    echo "Installing: $skill"
    mkdir -p "$INSTALL_DIR/$skill"
    
    curl -sSL "$RAW_URL/skills/$skill/SKILL.md" -o "$INSTALL_DIR/$skill/SKILL.md.tmp" 2>/dev/null
    
    if [ -f "$INSTALL_DIR/$skill/SKILL.md.tmp" ]; then
        cat "$INSTALL_DIR/$skill/SKILL.md.tmp" | sed 's/^description: |/description: /' | sed '/^  /d' > "$INSTALL_DIR/$skill/SKILL.md"
        rm "$INSTALL_DIR/$skill/SKILL.md.tmp"
        echo "  ✓ $skill installed"
    else
        echo "  ✗ Failed to download $skill"
    fi
done

echo ""
echo "========================================"
echo "  Installation Complete!"
echo "========================================"
echo ""
echo "Installed ${#SKILLS[@]} skills to: $INSTALL_DIR"
echo ""
echo "Quick Start:"
echo "  1. Run 'opencode' in your project"
echo "  2. Type a request that matches a skill"
echo "  3. The skill will be loaded automatically"
echo ""
echo "Example:"
echo "  'Design an architecture for a text mining system'"
echo "  → loads master-architect skill"
echo ""