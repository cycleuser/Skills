#!/bin/bash
# Quick Install Script for cycleuser/Skills
# Usage: curl -sSL https://raw.githubusercontent.com/cycleuser/Skills/main/quick-install.sh | bash

set -e

REPO_URL="https://github.com/cycleuser/Skills"
INSTALL_DIR="${HOME}/.opencode/skills"

echo "========================================"
echo "  Skills Installer"
echo "========================================"
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is required but not installed."
    exit 1
fi

# Create installation directory
echo "Creating installation directory: $INSTALL_DIR"
mkdir -p "$INSTALL_DIR"

# Download and run Python installer
echo "Downloading installer..."
curl -sSL "$REPO_URL/raw/main/install.py" -o /tmp/skills_install.py

echo "Running installer..."
python3 /tmp/skills_install.py install

# Cleanup
rm -f /tmp/skills_install.py

echo ""
echo "========================================"
echo "  Installation Complete!"
echo "========================================"
echo ""
echo "Skills installed to: $INSTALL_DIR"
echo ""
echo "Quick Start:"
echo "  /skills              - List all skills"
echo "  /skill <name>        - Load a skill"
echo ""
echo "Available Skills:"
echo "  - skill-manager (auto-loaded)"
echo "  - master-architect"
echo "  - python-project-developer"
echo "  - software-planner"
echo "  - coding-agent-patterns"
echo "  - iteration-manager"
echo "  - academic-writer"
echo ""
echo "For more info: https://github.com/cycleuser/Skills"