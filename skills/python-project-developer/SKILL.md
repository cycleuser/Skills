---
name: python-project-developer
version: "1.0.0"
description: |
  Complete Python multi-project development specification for CLI/GUI tools.

  **Triggers when:**
  - Creating a new Python project with CLI and GUI support
  - Setting up pyproject.toml, README, and PyPI publishing
  - Implementing unified API with ToolResult pattern
  - Adding OpenAI function-calling tools integration
  - Writing standardized tests and documentation

  **Capabilities:**
  - Project structure: single-file to package migration
  - CLI unified flags: -V, -v, -o, --json, -q
  - Python API: ToolResult dataclass pattern
  - Function-calling: TOOLS + dispatch pattern
  - Documentation: bilingual README, auto-screenshots
  - Testing: pytest with unified test structure
author: cycleuser
license: MIT
---

# Python Multi-Project Development Specification

Complete development workflow for Python CLI/GUI tools with PyPI publishing, unified APIs, and OpenAI function-calling integration.

## Project Structure

### Single File vs Package

- **Single file**: Use when < 1500 lines
- **Package structure**: Required when > 1500 lines, each module < 800 lines

### Standard Package Modules

| File | Responsibility |
|------|----------------|
| `__init__.py` | Package init, public API exports |
| `core.py` | Core business logic (dataclasses, engines, algorithms) |
| `cli.py` | Command-line interface (argparse, run_cli entry) |
| `gui.py` | GUI (tkinter/PySide6/PyQt) |
| `api.py` | Unified Python API (ToolResult wrapper) |
| `tools.py` | OpenAI function-calling definitions |
| `__main__.py` | `python -m` entry point |

### Directory Convention

```
project/
├── package_name/
│   ├── __init__.py
│   ├── core.py
│   ├── cli.py
│   ├── gui.py
│   ├── api.py
│   └── tools.py
├── images/           # Screenshots for documentation
├── tests/
├── scripts/          # Helper scripts (screenshot generator)
├── pyproject.toml
├── README.md
└── README_CN.md
```

## CLI Unified Standards

### Required Flags (in order)

```python
import argparse

parser = argparse.ArgumentParser(
    formatter_class=argparse.RawDescriptionHelpFormatter,
    epilog="Examples:\n  toolname --input file.txt\n  toolname -o output.json"
)

# 1. Version
parser.add_argument("-V", "--version", action="version", version=f"toolname {__version__}")

# 2. Verbose
parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")

# 3. Output path
parser.add_argument("-o", "--output", help="Output path")

# 4. JSON output
parser.add_argument("--json", action="store_true", dest="json_output", help="Output as JSON")

# 5. Quiet mode
parser.add_argument("-q", "--quiet", action="store_true", help="Suppress non-essential output")
```

### Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Runtime error |
| 2 | Invalid arguments (argparse handles) |

### Logging by Mode

```python
if args.quiet:
    logging.getLogger().setLevel(logging.WARNING)
elif args.verbose:
    logging.getLogger().setLevel(logging.DEBUG)
```

## Python API Pattern

### ToolResult Dataclass

```python
from dataclasses import dataclass, field
from typing import Any, Optional

@dataclass
class ToolResult:
    success: bool
    data: Any = None
    error: Optional[str] = None
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "success": self.success,
            "data": self.data,
            "error": self.error,
            "metadata": self.metadata,
        }
```

### API Function Design

```python
def projectname_action_noun(
    *,
    input_path: str | Path,
    option: str = "default",
) -> ToolResult:
    """Action description.

    Args:
        input_path: Path to input file.
        option: Configuration option.

    Returns:
        ToolResult with success status and data.
    """
    # Lazy imports inside function
    from pathlib import Path
    from .core import Processor

    try:
        result = Processor.run(Path(input_path), option)
        return ToolResult(
            success=True,
            data=result,
            metadata={"version": __version__}
        )
    except Exception as e:
        return ToolResult(success=False, error=str(e))
```

### __init__.py Exports

```python
from .api import ToolResult, action_noun
from .__version__ import __version__

__all__ = ["ToolResult", "action_noun", "__version__"]
```

## OpenAI Function-Calling Tools

### TOOLS Definition

```python
TOOLS: list[dict] = [
    {
        "type": "function",
        "function": {
            "name": "projectname_action_noun",
            "description": "Clear description of what the tool does",
            "parameters": {
                "type": "object",
                "properties": {
                    "input_path": {
                        "type": "string",
                        "description": "Path to input file",
                    },
                    "option": {
                        "type": "string",
                        "description": "Configuration option",
                        "default": "default",
                    },
                },
                "required": ["input_path"],
            },
        },
    },
]
```

### Dispatch Function

```python
import json
from typing import Any

def dispatch(name: str, arguments: dict[str, Any] | str) -> dict:
    """Dispatch tool call to appropriate API function."""
    if isinstance(arguments, str):
        arguments = json.loads(arguments)

    if name == "projectname_action_noun":
        from .api import action_noun
        result = action_noun(**arguments)
        return result.to_dict()

    raise ValueError(f"Unknown tool: {name}")
```

## Testing Structure

### Required Test Classes

```
TestToolResult         # ToolResult behavior
TestXxxAPI            # API function tests
TestToolsSchema       # TOOLS schema validation
TestToolsDispatch     # dispatch() tests
TestCLIFlags          # CLI integration tests
TestPackageExports    # __init__.py exports
```

### Test Patterns

```python
import pytest
import subprocess
import sys

class TestToolResult:
    def test_success_result(self):
        from projectname.api import ToolResult
        r = ToolResult(success=True, data={"key": "value"})
        assert r.success is True
        assert r.error is None

    def test_failure_result(self):
        from projectname.api import ToolResult
        r = ToolResult(success=False, error="failed")
        assert r.success is False
        assert r.error == "failed"

    def test_to_dict(self):
        from projectname.api import ToolResult
        r = ToolResult(success=True, data=[1, 2])
        d = r.to_dict()
        assert set(d.keys()) == {"success", "data", "error", "metadata"}

    def test_default_metadata_isolation(self):
        from projectname.api import ToolResult
        r1 = ToolResult(success=True)
        r2 = ToolResult(success=True)
        r1.metadata["a"] = 1
        assert "a" not in r2.metadata


class TestToolsSchema:
    def test_tool_structure(self):
        from projectname.tools import TOOLS
        for tool in TOOLS:
            assert tool["type"] == "function"
            func = tool["function"]
            assert "name" in func
            assert "description" in func
            assert "parameters" in func

    def test_required_fields_in_properties(self):
        from projectname.tools import TOOLS
        for tool in TOOLS:
            func = tool["function"]
            props = func["parameters"]["properties"]
            for req in func["parameters"]["required"]:
                assert req in props


class TestCLIFlags:
    def _run_cli(self, *args):
        return subprocess.run(
            [sys.executable, "-m", "package_name"] + list(args),
            capture_output=True, text=True, timeout=15,
        )

    def test_version_flag(self):
        r = self._run_cli("-V")
        assert r.returncode == 0

    def test_help_has_unified_flags(self):
        r = self._run_cli("--help")
        assert "--json" in r.stdout
        assert "--quiet" in r.stdout or "-q" in r.stdout
```

## Documentation Structure

### README Chapters (in order)

```
## Project Name -- One-line description
## Features / 功能特性
## Requirements / 系统要求
## Installation / 安装
## Quick Start / 快速开始
## Usage / 使用方法
## Python API
## Agent Integration (OpenAI Function Calling) / Agent 集成
## CLI Help (screenshot)
## Development / 开发
## License / 许可证
```

### Python API Section Template

```markdown
## Python API

```python
from projectname import action_noun

result = action_noun(input_path="file.txt")
print(result.success)    # True / False
print(result.data)       # Return data
print(result.metadata)   # Metadata including version
```
```

## Rules

- [rules/project-structure.md](rules/project-structure.md) - Project structure decisions
- [rules/cli-flags.md](rules/cli-flags.md) - CLI implementation details
- [rules/api-pattern.md](rules/api-pattern.md) - API design patterns
- [rules/tools-integration.md](rules/tools-integration.md) - Function-calling patterns
- [rules/testing-guide.md](rules/testing-guide.md) - Testing best practices

## Pre-Commit Checklist

```bash
ruff format . && ruff check . && mypy . && pytest
```

## PyPI Publishing Scripts

### publish.sh

```bash
#!/bin/bash
rm -rf dist/
python -m build
twine upload dist/*
```

### publish.bat

```batch
@echo off
rmdir /s /q dist
python -m build
twine upload dist\*
```

## Verification Checklist

- [ ] `pip install -e .` succeeds
- [ ] `toolname -V` outputs correct version
- [ ] `toolname --help` shows unified flags
- [ ] `from projectname import ToolResult` works
- [ ] `from projectname.tools import TOOLS` works
- [ ] `pytest tests/test_unified_api.py -v` passes
- [ ] README contains Python API and Agent sections
- [ ] Screenshots generated in `images/`