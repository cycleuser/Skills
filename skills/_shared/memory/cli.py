#!/usr/bin/env python3
"""
Shared Memory CLI — persistent key-value storage for all opencode skills.

Each skill gets a namespaced directory under _shared/memory/<skill>/
with atomic JSON reads/writes. Zero dependencies beyond Python stdlib.

Usage:
  python _shared/memory/cli.py get <skill> <key>
  echo '...' | python _shared/memory/cli.py set <skill> <key>
  python _shared/memory/cli.py set <skill> <key> --string "value"
  python _shared/memory/cli.py list <skill>
  python _shared/memory/cli.py delete <skill> <key>
  python _shared/memory/cli.py has <skill> <key>
  python _shared/memory/cli.py export <skill>
"""

import json
import os
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

_DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S"


def _resolve_memory_root() -> Path:
    return Path(__file__).resolve().parent


def _sanitize(name: str) -> str:
    safe = name.replace("/", "_").replace("\\", "_").replace("..", "_").strip("._")
    if not safe:
        raise ValueError(f"Invalid name: {name!r}")
    return safe


def _skill_dir(root: Path, skill: str) -> Path:
    return root / _sanitize(skill)


def _data_dir(root: Path, skill: str) -> Path:
    return _skill_dir(root, skill) / "data"


def _key_path(root: Path, skill: str, key: str) -> Path:
    return _data_dir(root, skill) / f"{_sanitize(key)}.json"


def _atomic_write(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(
        dir=str(path.parent), prefix="." + path.name, suffix=".tmp"
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        os.replace(tmp, path)
    except Exception:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def _read_json(path: Path) -> dict | None:
    if not path.exists():
        return None
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _now() -> str:
    ts = datetime.now(timezone.utc)
    return ts.strftime(_DATETIME_FORMAT)


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------


def cmd_get(root: Path, skill: str, key: str) -> None:
    data = _read_json(_key_path(root, skill, key))
    if data is None:
        sys.stdout.write("null\n")
    else:
        sys.stdout.write(json.dumps(data.get("value", data), indent=2, ensure_ascii=False) + "\n")


def cmd_set(root: Path, skill: str, key: str, value_json: str) -> None:
    try:
        value = json.loads(value_json)
    except json.JSONDecodeError as e:
        print(f"Error: invalid JSON — {e}", file=sys.stderr)
        sys.exit(1)
    path = _key_path(root, skill, key)
    record = {
        "_meta": {
            "skill": skill,
            "key": key,
            "updated": _now(),
        },
        "value": value,
    }
    # Preserve original creation time on updates
    existing = _read_json(path)
    if existing and "_meta" in existing:
        record["_meta"]["created"] = existing["_meta"].get("created", record["_meta"]["updated"])
    else:
        record["_meta"]["created"] = record["_meta"]["updated"]
    _atomic_write(path, record)
    print(f"ok  {skill}/{key}")


def cmd_list(root: Path, skill: str) -> None:
    data_dir = _data_dir(root, skill)
    if not data_dir.exists():
        print("[]")
        return
    keys = []
    for f in sorted(data_dir.glob("*.json")):
        data = _read_json(f)
        meta = data.get("_meta", {}) if data else {}
        keys.append(
            {
                "key": f.stem,
                "created": meta.get("created", ""),
                "updated": meta.get("updated", meta.get("created", "")),
            }
        )
    sys.stdout.write(json.dumps(keys, indent=2, ensure_ascii=False) + "\n")


def cmd_delete(root: Path, skill: str, key: str) -> None:
    path = _key_path(root, skill, key)
    if path.exists():
        path.unlink()
        print(f"ok  deleted {skill}/{key}")
    else:
        print(f"Error: key not found — {skill}/{key}", file=sys.stderr)
        sys.exit(1)


def cmd_has(root: Path, skill: str, key: str) -> None:
    exists = _key_path(root, skill, key).exists()
    sys.exit(0 if exists else 1)


def cmd_export(root: Path, skill: str) -> None:
    result: dict = {}
    data_dir = _data_dir(root, skill)
    if data_dir.exists():
        for f in sorted(data_dir.glob("*.json")):
            data = _read_json(f)
            if data:
                result[f.stem] = data.get("value", data)
    sys.stdout.write(json.dumps(result, indent=2, ensure_ascii=False) + "\n")


# ---------------------------------------------------------------------------
# CLI dispatch
# ---------------------------------------------------------------------------

USAGE = """\
Shared Memory CLI — persistent key-value storage for opencode skills.

Commands:
  get    <skill> <key>           Print value as JSON (or "null")
  set    <skill> <key>           Set value from stdin JSON
  set    <skill> <key> --string  Set a bare string value
  list   <skill>                 List all keys with timestamps
  delete <skill> <key>           Delete a key
  has    <skill> <key>           Exit 0 if exists, 1 if not
  export <skill>                 Export all data as flat JSON object

Examples:
  # Store a project reference
  echo '"长安雪"' | python _shared/memory/cli.py set literary-ghostwriter current_project

  # Store structured data
  echo '{"ch":15,"words":45000}' | python _shared/memory/cli.py set literary-ghostwriter progress

  # Simple string
  python _shared/memory/cli.py set brief-write tone --string casual

  # Read back
  python _shared/memory/cli.py get literary-ghostwriter current_project
  # => "长安雪"

  # Check existence (useful in shell conditionals)
  python _shared/memory/cli.py has literary-ghostwriter current_project && echo "yes"

  # List all keys
  python _shared/memory/cli.py list literary-ghostwriter

  # Export everything
  python _shared/memory/cli.py export literary-ghostwriter

Storage location: <skills>/_shared/memory/<skill>/data/<key>.json
All writes are atomic (temp-file + rename).
"""


def main(argv: list[str] | None = None) -> None:
    args = argv or sys.argv[1:]
    if not args:
        print(USAGE)
        sys.exit(1)

    cmd = args[0]
    root = _resolve_memory_root()

    if cmd == "get":
        if len(args) != 3:
            print(USAGE, file=sys.stderr)
            sys.exit(1)
        cmd_get(root, args[1], args[2])

    elif cmd == "set":
        if len(args) < 3:
            print(USAGE, file=sys.stderr)
            sys.exit(1)
        skill, key = args[1], args[2]

        if len(args) >= 5 and args[3] == "--string":
            value_json = json.dumps(args[4])
        elif len(args) >= 4:
            value_json = args[3]
        else:
            value_json = sys.stdin.read()
        cmd_set(root, skill, key, value_json)

    elif cmd == "list":
        if len(args) != 2:
            print(USAGE, file=sys.stderr)
            sys.exit(1)
        cmd_list(root, args[1])

    elif cmd == "delete":
        if len(args) != 3:
            print(USAGE, file=sys.stderr)
            sys.exit(1)
        cmd_delete(root, args[1], args[2])

    elif cmd == "has":
        if len(args) != 3:
            print(USAGE, file=sys.stderr)
            sys.exit(1)
        cmd_has(root, args[1], args[2])

    elif cmd == "export":
        if len(args) != 2:
            print(USAGE, file=sys.stderr)
            sys.exit(1)
        cmd_export(root, args[1])

    else:
        print(f"Unknown command: {cmd}", file=sys.stderr)
        print(USAGE, file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
