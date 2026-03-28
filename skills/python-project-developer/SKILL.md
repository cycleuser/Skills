---
name: python-project-developer
version: "1.0.0"
description: |
  Complete Python multi-project development specification for CLI/GUI tools.

  Triggers when: Creating a new Python project with CLI and GUI support, setting up pyproject.toml with README and PyPI publishing, implementing unified API with ToolResult pattern, adding OpenAI function-calling tools integration, or writing standardized tests and documentation.

  Capabilities: Project structure guidance from single-file to package migration, CLI unified flags (-V, -v, -o, --json, -q), Python API with ToolResult dataclass pattern, function-calling with TOOLS + dispatch pattern, bilingual README documentation with auto-screenshots, and pytest testing with unified test structure.
author: cycleuser
license: MIT
---

# Python Multi-Project Development Specification

Complete development workflow for Python CLI/GUI tools with PyPI publishing, unified APIs, and OpenAI function-calling integration.

## Project Structure

### Single File vs Package

Single file structure is appropriate when the total code is under 1500 lines. Package structure is required when code exceeds 1500 lines, with each module kept under 800 lines.

### Standard Package Modules

The package structure follows a convention where each file has a specific responsibility. The `__init__.py` file handles package initialization and public API exports. The `core.py` file contains core business logic including dataclasses, engines, and algorithms. The `cli.py` file implements the command-line interface using argparse with the run_cli entry point. The `gui.py` file provides GUI functionality using tkinter, PySide6, or PyQt. The `api.py` file implements the unified Python API with the ToolResult wrapper. The `tools.py` file defines OpenAI function-calling tools. The `__main__.py` file provides the `python -m` entry point.

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

The CLI follows a unified flag convention with five flags in a specific order. First, the version flag `-V` or `--version` uses argparse version action. Second, the verbose flag `-v` or `--verbose` enables verbose output. Third, the output path flag `-o` or `--output` specifies the output path. Fourth, the JSON output flag `--json` enables JSON output format. Fifth, the quiet mode flag `-q` or `--quiet` suppresses non-essential output.

### Exit Codes

Exit code 0 indicates success. Exit code 1 indicates a runtime error. Exit code 2 indicates invalid arguments, which argparse handles automatically.

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

The test suite requires six test classes covering different aspects of the project. TestToolResult verifies ToolResult behavior. TestXxxAPI covers API function tests. TestToolsSchema validates the TOOLS schema. TestToolsDispatch tests the dispatch function. TestCLIFlags handles CLI integration tests. TestPackageExports verifies `__init__.py` exports.

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

The README follows a specific chapter order to ensure consistent documentation across projects. Chapter 1 is the project name with a one-line description. Chapter 2 covers features in both English and Chinese. Chapter 3 details requirements in both languages. Chapter 4 provides installation instructions. Chapter 5 offers quick start guidance. Chapter 6 explains usage. Chapter 7 documents the Python API. Chapter 8 covers agent integration with OpenAI function calling. Chapter 9 includes a CLI help screenshot. Chapter 10 discusses development. Chapter 11 provides license information.

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

Before considering a project complete, verify the following items. The editable install should succeed with `pip install -e .`. The version flag should output the correct version with `toolname -V`. The help command should show unified flags with `toolname --help`. The ToolResult import should work with `from projectname import ToolResult`. The TOOLS import should work with `from projectname.tools import TOOLS`. The test suite should pass with `pytest tests/test_unified_api.py -v`. The README should contain both Python API and Agent sections. Screenshots should be generated in the `images/` directory.