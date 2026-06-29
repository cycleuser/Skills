#!/usr/bin/env python3
"""
Skills Installer

Install skills from the cycleuser/Skills repository to your local environment.
Supports installation from local directory or GitHub URL.
"""

import argparse
import json
import os
import shutil
import sys
import urllib.request
import zipfile
from pathlib import Path
from typing import Optional


REPO_URL = "https://github.com/cycleuser/Skills"
RAW_URL = "https://raw.githubusercontent.com/cycleuser/Skills/main"


def get_default_install_dir() -> Path:
    """Get default installation directory based on platform."""
    home = Path.home()
    
    # Check for existing .opencode directory
    opencode_dir = home / ".opencode" / "skills"
    if opencode_dir.exists():
        return opencode_dir
    
    # Default to .opencode
    return opencode_dir


def download_file(url: str, dest: Path) -> bool:
    """Download a file from URL."""
    try:
        urllib.request.urlretrieve(url, dest)
        return True
    except Exception as e:
        print(f"Error downloading {url}: {e}")
        return False


def download_skill_from_github(skill_name: str, install_dir: Path) -> bool:
    """Download a single skill from GitHub."""
    skill_dir = install_dir / skill_name
    
    # Create skill directory
    skill_dir.mkdir(parents=True, exist_ok=True)
    rules_dir = skill_dir / "rules"
    rules_dir.mkdir(exist_ok=True)
    
    # Download SKILL.md
    skill_url = f"{RAW_URL}/skills/{skill_name}/SKILL.md"
    skill_file = skill_dir / "SKILL.md"
    
    if not download_file(skill_url, skill_file):
        return False
    
    # Try to download rules
    # First, get the list of rules from a registry or try common names
    common_rules = [
        "registry.md",
        "testing-protocol.md",
        "quality-metrics.md",
        "iteration-workflow.md",
        "literature-search.md",
        "citation-format.md",
        "paper-structure.md",
        "writing-style.md",
        "pre-development.md",
        "interface-design.md",
        "documentation.md",
        "sample-data.md",
        "project-structure.md",
        "cli-flags.md",
        "api-pattern.md",
        "tools-integration.md",
        "context-management.md",
        "tool-safety.md",
        "multi-provider.md",
        "memory-systems.md",
        "requirement-analysis.md",
        "architecture-design.md",
        "task-decomposition.md",
    ]
    
    for rule in common_rules:
        rule_url = f"{RAW_URL}/skills/{skill_name}/rules/{rule}"
        rule_file = rules_dir / rule
        download_file(rule_url, rule_file)  # Ignore failures
    
    return True


def install_from_local(source_dir: Path, install_dir: Path, skills: Optional[list] = None) -> bool:
    """Install skills from local directory."""
    source_skills = source_dir / "skills"
    
    if not source_skills.exists():
        print(f"Error: Skills directory not found at {source_skills}")
        return False
    
    # Create install directory
    install_dir.mkdir(parents=True, exist_ok=True)
    
    # Install _shared/ directory if it exists
    shared_src = source_skills / "_shared"
    if shared_src.exists():
        shared_dest = install_dir / "_shared"
        if shared_dest.exists():
            shutil.rmtree(shared_dest)
        shutil.copytree(shared_src, shared_dest)
        print(f"  ✓ Installed: _shared/ (common resources)")
    
    # Get list of skills to install
    if skills:
        skill_list = skills
    else:
        skill_list = [d.name for d in source_skills.iterdir() if d.is_dir() and (d / "SKILL.md").exists() and d.name != "_shared"]
    
    installed = []
    failed = []
    
    for skill_name in skill_list:
        source_skill = source_skills / skill_name
        dest_skill = install_dir / skill_name
        
        if not source_skill.exists():
            print(f"  ⚠ Skill not found: {skill_name}")
            failed.append(skill_name)
            continue
        
        # Remove existing
        if dest_skill.exists():
            shutil.rmtree(dest_skill)
        
        # Copy skill
        shutil.copytree(source_skill, dest_skill)
        installed.append(skill_name)
        print(f"  ✓ Installed: {skill_name}")
    
    print(f"\nInstalled {len(installed)} skill(s)")
    if failed:
        print(f"Failed: {', '.join(failed)}")
    
    return len(installed) > 0


def install_from_github(install_dir: Path, skills: Optional[list] = None) -> bool:
    """Install skills from GitHub repository."""
    print(f"Installing from {REPO_URL}")
    
    # Create install directory
    install_dir.mkdir(parents=True, exist_ok=True)
    
    # Default skills to install
    if not skills:
        skills = [
            "skill-manager",
            "master-architect",
            "python-project-developer",
            "software-planner",
            "coding-agent-patterns",
            "iteration-manager",
            "academic-writer",
            "patent-writer",
            "official-document-writer",
            "power-iterate",
            "humanizer",
            "literary-ghostwriter",
            "skill-refiner",
            "brief-write",
            "bao-kao",
            "sleepless",
            "an-jian",
            "ba-guan",
            "he-bing",
            "shen-shi",
            "project-rebuilder",
            "zi-kong",
            "shuang-chong",
        ]
    
    installed = []
    failed = []
    
    for skill_name in skills:
        print(f"  Installing {skill_name}...")
        if download_skill_from_github(skill_name, install_dir):
            installed.append(skill_name)
            print(f"  ✓ Installed: {skill_name}")
        else:
            failed.append(skill_name)
            print(f"  ✗ Failed: {skill_name}")
    
    print(f"\nInstalled {len(installed)} skill(s)")
    if failed:
        print(f"Failed: {', '.join(failed)}")
    
    return len(installed) > 0


def list_installed_skills(install_dir: Path) -> list:
    """List installed skills."""
    skills = []
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
    
    # Parse frontmatter
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            frontmatter = parts[1].strip()
            info = {}
            for line in frontmatter.split("\n"):
                if ":" in line:
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
    print(f"Version: {info.get('version', 'unknown')}")
    print(f"Description: {info.get('description', 'No description')}")
    
    # List rules
    rules_dir = skill_path / "rules"
    if rules_dir.exists():
        rules = [r.stem for r in rules_dir.glob("*.md")]
        if rules:
            print(f"\nRules: {', '.join(rules)}")


def main():
    parser = argparse.ArgumentParser(
        description="Install and manage skills for AI coding agents"
    )
    
    parser.add_argument(
        "command",
        choices=["install", "list", "info", "uninstall", "update"],
        help="Command to execute"
    )
    
    parser.add_argument(
        "--source",
        type=str,
        default=None,
        help="Source directory or URL (default: GitHub)"
    )
    
    parser.add_argument(
        "--target",
        type=str,
        default=None,
        help="Target installation directory"
    )
    
    parser.add_argument(
        "--skills",
        type=str,
        nargs="+",
        default=None,
        help="Specific skills to install"
    )
    
    parser.add_argument(
        "--all",
        action="store_true",
        help="Install all available skills"
    )
    
    args = parser.parse_args()
    
    # Determine install directory
    if args.target:
        install_dir = Path(args.target)
    else:
        install_dir = get_default_install_dir()
    
    if args.command == "install":
        print(f"Installing skills to: {install_dir}")
        
        if args.source:
            source_path = Path(args.source)
            if source_path.exists():
                success = install_from_local(source_path, install_dir, args.skills)
            else:
                print(f"Source not found: {args.source}")
                sys.exit(1)
        else:
            success = install_from_github(install_dir, args.skills)
        
        if success:
            print("\nInstallation complete!")
            print(f"Use '/skills' to list installed skills")
        else:
            sys.exit(1)
    
    elif args.command == "list":
        print(f"Installed skills in: {install_dir}")
        skills = list_installed_skills(install_dir)
        if skills:
            for skill in skills:
                info = get_skill_info(install_dir / skill)
                desc = info.get("description", "").split("\n")[0][:60]
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
    
    elif args.command == "update":
        print("Updating skills...")
        if args.source:
            source_path = Path(args.source)
        else:
            source_path = Path(__file__).parent
        
        if source_path.exists():
            install_from_local(source_path, install_dir, args.skills)
        else:
            install_from_github(install_dir, args.skills)


if __name__ == "__main__":
    main()