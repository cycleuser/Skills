#!/usr/bin/env python3
"""布阵 (bu-zhen) preset manager.

Switches the model/temperature of the bu-zhen specialist agents by rewriting
their markdown frontmatter, and installs them into opencode's global agent dir.

Usage:
    python3 apply_preset.py list                 # list available presets
    python3 apply_preset.py status               # show current agent models
    python3 apply_preset.py <preset>             # apply preset to repo agents/
    python3 apply_preset.py <preset> --install   # apply + install to ~/.config/opencode/agents/
    python3 apply_preset.py --install            # install current agents/ as-is
    python3 apply_preset.py check                # verify agent frontmatter is valid

Presets live in ../presets/*.jsonc. Agent definitions live in ../agents/*.md.
No third-party dependencies.
"""

from __future__ import annotations

import json
import re
import shutil
import sys
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parent.parent
AGENTS_DIR = SKILL_ROOT / "agents"
PRESETS_DIR = SKILL_ROOT / "presets"
INSTALL_DIR = Path.home() / ".config" / "opencode" / "agents"

FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)
MODEL_RE = re.compile(r"^model:\s*.*$", re.MULTILINE)
TEMP_RE = re.compile(r"^temperature:\s*.*$", re.MULTILINE)


def strip_jsonc(text: str) -> str:
    """Strip // and /* */ comments plus trailing commas from JSONC."""
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.DOTALL)
    text = re.sub(r"(^|[^:])//[^\n]*", lambda m: m.group(1), text)
    text = re.sub(r",(\s*[}\]])", r"\1", text)
    return text


def load_preset(name: str) -> dict:
    path = PRESETS_DIR / f"{name}.jsonc"
    if not path.exists():
        available = ", ".join(sorted(p.stem for p in PRESETS_DIR.glob("*.jsonc")))
        raise SystemExit(f"preset '{name}' not found. available: {available}")
    data = json.loads(strip_jsonc(path.read_text(encoding="utf-8")))
    return data.get("agents", {})


def rewrite_agent(path: Path, model: str, temperature: float | None) -> bool:
    text = path.read_text(encoding="utf-8")
    m = FRONTMATTER_RE.match(text)
    if not m:
        print(f"  SKIP {path.name}: no frontmatter")
        return False
    fm = m.group(1)
    if not MODEL_RE.search(fm):
        print(f"  SKIP {path.name}: no model: line in frontmatter")
        return False
    new_fm = MODEL_RE.sub(f"model: {model}", fm, count=1)
    if temperature is not None:
        temp_line = f"temperature: {temperature}"
        if TEMP_RE.search(new_fm):
            new_fm = TEMP_RE.sub(temp_line, new_fm, count=1)
        else:
            new_fm = new_fm.rstrip("\n") + "\n" + temp_line
    text = text[: m.start(1)] + new_fm + text[m.end(1):]
    path.write_text(text, encoding="utf-8")
    return True


def apply_preset(name: str, install: bool) -> None:
    mapping = load_preset(name)
    if not mapping:
        raise SystemExit(f"preset '{name}' has no agents mapping")
    print(f"applying preset '{name}':")
    for agent_file in sorted(AGENTS_DIR.glob("bz-*.md")):
        stem = agent_file.stem
        if stem not in mapping:
            print(f"  SKIP {stem}: not in preset")
            continue
        entry = mapping[stem]
        ok = rewrite_agent(agent_file, entry["model"], entry.get("temperature"))
        if ok:
            print(f"  {stem} -> {entry['model']}")
    if install:
        install_agents()


def install_agents() -> None:
    INSTALL_DIR.mkdir(parents=True, exist_ok=True)
    installed = []
    for agent_file in sorted(AGENTS_DIR.glob("bz-*.md")):
        dest = INSTALL_DIR / agent_file.name
        shutil.copy(agent_file, dest)
        installed.append(dest.name)
    print(f"installed {len(installed)} agents to {INSTALL_DIR}")
    for name in installed:
        print(f"  {name}")


def list_presets() -> None:
    print("available presets:")
    for p in sorted(PRESETS_DIR.glob("*.jsonc")):
        try:
            data = json.loads(strip_jsonc(p.read_text(encoding="utf-8")))
            comment = data.get("$comment", "")
            print(f"  {p.stem:16s} {comment}")
        except json.JSONDecodeError as exc:
            print(f"  {p.stem:16s} INVALID JSON: {exc}")


def status() -> None:
    print(f"agent source: {AGENTS_DIR}")
    for agent_file in sorted(AGENTS_DIR.glob("bz-*.md")):
        text = agent_file.read_text(encoding="utf-8")
        m = FRONTMATTER_RE.match(text)
        fm = m.group(1) if m else ""
        model = re.search(r"^model:\s*(.+)$", fm, re.MULTILINE)
        temp = re.search(r"^temperature:\s*(.+)$", fm, re.MULTILINE)
        installed = " (installed)" if (INSTALL_DIR / agent_file.name).exists() else ""
        print(f"  {agent_file.stem:16s} {model.group(1) if model else '?':42s} t={temp.group(1) if temp else '?'}{installed}")


def check() -> int:
    errors = 0
    for agent_file in sorted(AGENTS_DIR.glob("bz-*.md")):
        text = agent_file.read_text(encoding="utf-8")
        m = FRONTMATTER_RE.match(text)
        if not m:
            print(f"  FAIL {agent_file.name}: missing frontmatter")
            errors += 1
            continue
        fm = m.group(1)
        for field in ("description:", "mode:", "model:"):
            if field not in fm:
                print(f"  FAIL {agent_file.name}: missing {field}")
                errors += 1
        if "permission:" not in fm:
            print(f"  WARN {agent_file.name}: no permission block")
    if errors:
        print(f"{errors} error(s)")
        return 1
    print(f"all {len(list(AGENTS_DIR.glob('bz-*.md')))} agents OK")
    return 0


def main() -> int:
    args = [a for a in sys.argv[1:] if a != "--install"]
    install = "--install" in sys.argv
    if not args:
        if install:
            install_agents()
            return 0
        list_presets()
        return 0
    cmd = args[0]
    if cmd == "list":
        list_presets()
    elif cmd == "status":
        status()
    elif cmd == "check":
        return check()
    elif cmd in ("-h", "--help"):
        print(__doc__)
    else:
        apply_preset(cmd, install)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
