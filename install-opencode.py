#!/usr/bin/env python3
"""
OpenCode Skills Installer

Install skills from the cycleuser/Skills repository to OpenCode's skill directory.
Converts SKILL.md files to OpenCode-compatible format.
"""

import argparse
import json
import os
import re
import shutil
import sys
import urllib.request
from pathlib import Path
from typing import Optional


REPO_URL = "https://github.com/cycleuser/Skills"
RAW_URL = "https://raw.githubusercontent.com/cycleuser/Skills/main"

OPENCODE_GLOBAL_DIR = Path.home() / ".config" / "opencode" / "skills"
OPENCODE_PROJECT_DIR = Path(".opencode") / "skills"
OPENCODE_COMMANDS_GLOBAL_DIR = Path.home() / ".config" / "opencode" / "commands"
OPENCODE_COMMANDS_PROJECT_DIR = Path(".opencode") / "commands"


SKILLS = [
    "skill-manager",
    "master-architect",
    "python-project-developer",
    "software-planner",
    "coding-agent-patterns",
    "iteration-manager",
    "academic-writer",
    "patent-writer",
]

COMMANDS = [
    "architect",
    "python-dev",
    "plan",
    "iterate",
    "academic",
    "patent",
    "skills",
]


def convert_skill_to_opencode(content: str) -> str:
    """Convert SKILL.md content to OpenCode-compatible format."""
    if not content.startswith("---"):
        return content
    
    parts = content.split("---", 2)
    if len(parts) < 3:
        return content
    
    frontmatter = parts[1].strip()
    body = parts[2]
    
    lines = frontmatter.split("\n")
    new_frontmatter = []
    name = None
    description_lines = []
    in_description = False
    license_val = "MIT"
    metadata = {}
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        if line.startswith("name:"):
            name = line.split(":", 1)[1].strip().strip('"')
            new_frontmatter.append(f'name: {name}')
        
        elif line.startswith("description:"):
            desc_val = line.split(":", 1)[1].strip()
            if desc_val.startswith("|"):
                in_description = True
            else:
                description_lines.append(desc_val)
        
        elif in_description:
            if line and not line[0].isspace() and ":" in line:
                in_description = False
                i -= 1
            elif line.strip():
                description_lines.append(line.strip())
        
        elif line.startswith("license:"):
            license_val = line.split(":", 1)[1].strip().strip('"')
        
        elif line.startswith("version:"):
            metadata["version"] = line.split(":", 1)[1].strip().strip('"')
        
        elif line.startswith("author:"):
            metadata["author"] = line.split(":", 1)[1].strip().strip('"')
        
        elif line.startswith("priority:"):
            metadata["priority"] = line.split(":", 1)[1].strip()
        
        elif line.startswith("auto_load:"):
            metadata["auto_load"] = line.split(":", 1)[1].strip()
        
        i += 1
    
    description = " ".join(description_lines)
    if len(description) > 1024:
        description = description[:1021] + "..."
    
    new_frontmatter.append(f'description: {description}')
    new_frontmatter.append(f'license: {license_val}')
    new_frontmatter.append('compatibility: opencode')
    
    if metadata:
        new_frontmatter.append('metadata:')
        for key, value in metadata.items():
            new_frontmatter.append(f'  {key}: {value}')
    
    return "---\n" + "\n".join(new_frontmatter) + "\n---" + body


def get_default_install_dir(global_install: bool = True) -> Path:
    """Get default installation directory."""
    if global_install:
        return OPENCODE_GLOBAL_DIR
    return OPENCODE_PROJECT_DIR


def get_default_commands_dir(global_install: bool = True) -> Path:
    """Get default commands directory."""
    if global_install:
        return OPENCODE_COMMANDS_GLOBAL_DIR
    return OPENCODE_COMMANDS_PROJECT_DIR


def download_file(url: str, dest: Path) -> bool:
    """Download a file from URL."""
    try:
        urllib.request.urlretrieve(url, dest)
        return True
    except Exception as e:
        print(f"Error downloading {url}: {e}")
        return False


def install_from_local(source_dir: Path, install_dir: Path, skills: Optional[list] = None) -> bool:
    """Install skills from local directory."""
    source_skills = source_dir / "skills"
    
    if not source_skills.exists():
        print(f"Error: Skills directory not found at {source_skills}")
        return False
    
    install_dir.mkdir(parents=True, exist_ok=True)
    
    if skills:
        skill_list = skills
    else:
        skill_list = [d.name for d in source_skills.iterdir() if d.is_dir() and (d / "SKILL.md").exists()]
    
    installed = []
    failed = []
    
    for skill_name in skill_list:
        source_skill = source_skills / skill_name
        dest_skill = install_dir / skill_name
        
        if not source_skill.exists():
            print(f"  ⚠ Skill not found: {skill_name}")
            failed.append(skill_name)
            continue
        
        skill_file = source_skill / "SKILL.md"
        if not skill_file.exists():
            print(f"  ⚠ SKILL.md not found: {skill_name}")
            failed.append(skill_name)
            continue
        
        if dest_skill.exists():
            shutil.rmtree(dest_skill)
        
        dest_skill.mkdir(parents=True, exist_ok=True)
        
        content = skill_file.read_text()
        converted = convert_skill_to_opencode(content)
        (dest_skill / "SKILL.md").write_text(converted)
        
        rules_src = source_skill / "rules"
        if rules_src.exists():
            rules_dest = dest_skill / "rules"
            rules_dest.mkdir(exist_ok=True)
            for rule_file in rules_src.glob("*.md"):
                shutil.copy(rule_file, rules_dest / rule_file.name)
        
        installed.append(skill_name)
        print(f"  ✓ Installed: {skill_name}")
    
    print(f"\nInstalled {len(installed)} skill(s) to {install_dir}")
    if failed:
        print(f"Failed: {', '.join(failed)}")
    
    return len(installed) > 0


def install_commands_from_local(source_dir: Path, commands_dir: Path, commands: Optional[list] = None) -> bool:
    """Install commands from local directory."""
    source_commands = source_dir / "commands"
    
    if not source_commands.exists():
        print(f"  ⚠ Commands directory not found at {source_commands}")
        return False
    
    commands_dir.mkdir(parents=True, exist_ok=True)
    
    if commands:
        command_list = commands
    else:
        command_list = [f.stem for f in source_commands.glob("*.md")]
    
    installed = []
    failed = []
    
    for command_name in command_list:
        source_file = source_commands / f"{command_name}.md"
        dest_file = commands_dir / f"{command_name}.md"
        
        if not source_file.exists():
            print(f"  ⚠ Command not found: {command_name}")
            failed.append(command_name)
            continue
        
        shutil.copy(source_file, dest_file)
        installed.append(command_name)
        print(f"  ✓ Installed command: /{command_name}")
    
    print(f"\nInstalled {len(installed)} command(s) to {commands_dir}")
    if failed:
        print(f"Failed: {', '.join(failed)}")
    
    return len(installed) > 0


def install_commands_from_github(commands_dir: Path, commands: Optional[list] = None) -> bool:
    """Install commands from GitHub repository."""
    
    commands_dir.mkdir(parents=True, exist_ok=True)
    
    if not commands:
        commands = COMMANDS
    
    installed = []
    failed = []
    
    for command_name in commands:
        command_url = f"{RAW_URL}/commands/{command_name}.md"
        dest_file = commands_dir / f"{command_name}.md"
        
        if download_file(command_url, dest_file):
            installed.append(command_name)
            print(f"  ✓ Installed command: /{command_name}")
        else:
            failed.append(command_name)
            print(f"  ✗ Failed: /{command_name}")
    
    print(f"\nInstalled {len(installed)} command(s) to {commands_dir}")
    if failed:
        print(f"Failed: {', '.join(failed)}")
    
    return len(installed) > 0


def install_from_github(install_dir: Path, skills: Optional[list] = None) -> bool:
    """Install skills from GitHub repository."""
    print(f"Installing from {REPO_URL}")
    
    install_dir.mkdir(parents=True, exist_ok=True)
    
    if not skills:
        skills = SKILLS
    
    installed = []
    failed = []
    
    for skill_name in skills:
        print(f"  Installing {skill_name}...")
        
        skill_dir = install_dir / skill_name
        skill_dir.mkdir(parents=True, exist_ok=True)
        
        skill_url = f"{RAW_URL}/skills/{skill_name}/SKILL.md"
        temp_file = skill_dir / "SKILL.md.tmp"
        
        if not download_file(skill_url, temp_file):
            shutil.rmtree(skill_dir)
            failed.append(skill_name)
            print(f"  ✗ Failed: {skill_name}")
            continue
        
        content = temp_file.read_text()
        temp_file.unlink()
        
        converted = convert_skill_to_opencode(content)
        (skill_dir / "SKILL.md").write_text(converted)
        
        rules_dir = skill_dir / "rules"
        rules_dir.mkdir(exist_ok=True)
        
        common_rules = [
            "registry.md", "testing-protocol.md", "quality-metrics.md",
            "iteration-workflow.md", "literature-search.md", "citation-format.md",
            "paper-structure.md", "writing-style.md", "pre-development.md",
            "interface-design.md", "documentation.md", "sample-data.md",
            "project-structure.md", "cli-flags.md", "api-pattern.md",
            "tools-integration.md", "context-management.md", "tool-safety.md",
            "multi-provider.md", "memory-systems.md", "requirement-analysis.md",
            "architecture-design.md", "task-decomposition.md", "iteration-protocol.md",
            "quality-gates.md",
        ]
        
        for rule in common_rules:
            rule_url = f"{RAW_URL}/skills/{skill_name}/rules/{rule}"
            rule_file = rules_dir / rule
            download_file(rule_url, rule_file)
        
        installed.append(skill_name)
        print(f"  ✓ Installed: {skill_name}")
    
    print(f"\nInstalled {len(installed)} skill(s) to {install_dir}")
    if failed:
        print(f"Failed: {', '.join(failed)}")
    
    return len(installed) > 0


def list_installed_skills(install_dir: Path) -> list:
    """List installed skills."""
    skills = []
    if not install_dir.exists():
        return skills
    for skill_dir in install_dir.iterdir():
        if skill_dir.is_dir() and (skill_dir / "SKILL.md").exists():
            skills.append(skill_dir.name)
    return sorted(skills)


def get_skill_info(skill_path: Path) -> dict:
    """Parse skill metadata from SKILL.md."""
    skill_file = skill_path / "SKILL.md"
    if not skill_file.exists():
        return {}
    
    content = skill_file.read_text()
    
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            frontmatter = parts[1].strip()
            info = {}
            for line in frontmatter.split("\n"):
                if ":" in line and not line.startswith(" "):
                    key, value = line.split(":", 1)
                    info[key.strip()] = value.strip()
            return info
    
    return {}


def show_skill_info(install_dir: Path, skill_name: str):
    """Show detailed information about a skill."""
    skill_path = install_dir / skill_name
    if not skill_path.exists():
        print(f"Skill not found: {skill_name}")
        return
    
    info = get_skill_info(skill_path)
    
    print(f"\n{skill_name}")
    print("=" * len(skill_name))
    print(f"Description: {info.get('description', 'No description')}")
    print(f"License: {info.get('license', 'unknown')}")
    
    rules_dir = skill_path / "rules"
    if rules_dir.exists():
        rules = [r.stem for r in rules_dir.glob("*.md")]
        if rules:
            print(f"\nRules: {', '.join(rules)}")


def main():
    parser = argparse.ArgumentParser(
        description="Install skills for OpenCode from cycleuser/Skills repository"
    )
    
    parser.add_argument(
        "command",
        choices=["install", "list", "info", "uninstall"],
        help="Command to execute"
    )
    
    parser.add_argument(
        "--source",
        type=str,
        default=None,
        help="Source directory (default: GitHub)"
    )
    
    parser.add_argument(
        "--target",
        type=str,
        default=None,
        help="Target installation directory"
    )
    
    parser.add_argument(
        "--global",
        dest="global_install",
        action="store_true",
        default=True,
        help="Install globally (default)"
    )
    
    parser.add_argument(
        "--local",
        dest="global_install",
        action="store_false",
        help="Install to project .opencode directory"
    )
    
    parser.add_argument(
        "--skills",
        type=str,
        nargs="+",
        default=None,
        help="Specific skills to install"
    )
    
    args = parser.parse_args()
    
    if args.target:
        install_dir = Path(args.target)
        commands_dir = Path(args.target).parent / "commands"
    else:
        install_dir = get_default_install_dir(args.global_install)
        commands_dir = get_default_commands_dir(args.global_install)
    
    if args.command == "install":
        print("=" * 60)
        print("  Installing Skills")
        print("=" * 60)
        print(f"Skills directory: {install_dir}")
        
        if args.source:
            source_path = Path(args.source)
            if source_path.exists():
                success = install_from_local(source_path, install_dir, args.skills)
                print()
                print("=" * 60)
                print("  Installing Commands")
                print("=" * 60)
                print(f"Commands directory: {commands_dir}")
                install_commands_from_local(source_path, commands_dir)
            else:
                print(f"Source not found: {args.source}")
                sys.exit(1)
        else:
            success = install_from_github(install_dir, args.skills)
            print()
            print("=" * 60)
            print("  Installing Commands")
            print("=" * 60)
            print(f"Commands directory: {commands_dir}")
            install_commands_from_github(commands_dir)
        
        if success:
            print()
            print("=" * 60)
            print("  Installation Complete!")
            print("=" * 60)
            print()
            print("Available commands:")
            print("  /architect <task>  - Architecture design")
            print("  /python-dev <task> - Python development")
            print("  /plan <task>       - Software planning")
            print("  /iterate <task>    - Iterative testing")
            print("  /academic <task>   - Academic writing")
            print("  /skills            - List all skills")
            print()
        else:
            sys.exit(1)
    
    elif args.command == "list":
        print(f"Installed skills in: {install_dir}")
        skills = list_installed_skills(install_dir)
        if skills:
            for skill in skills:
                info = get_skill_info(install_dir / skill)
                desc = info.get("description", "No description")[:60]
                print(f"  {skill:30} {desc}...")
        else:
            print("  No skills installed")
    
    elif args.command == "info":
        if not args.skills:
            print("Please specify skill name(s)")
            sys.exit(1)
        for skill_name in args.skills:
            show_skill_info(install_dir, skill_name)
    
    elif args.command == "uninstall":
        if not args.skills:
            print("Please specify skill name(s) to uninstall")
            sys.exit(1)
        for skill_name in args.skills:
            skill_path = install_dir / skill_name
            if skill_path.exists():
                shutil.rmtree(skill_path)
                print(f"✓ Uninstalled: {skill_name}")
            else:
                print(f"⚠ Not found: {skill_name}")


if __name__ == "__main__":
    main()