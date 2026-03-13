# Project Structure Decisions

## Single File vs Package

### When to Use Single File

- Total lines < 1500
- Simple, focused functionality
- Quick prototype or utility

### When to Split to Package

- File exceeds 1500 lines
- Multiple distinct responsibilities
- Need separate CLI/GUI/API
- Planning for growth

## Package Module Responsibilities

| Module | Lines Max | Responsibility |
|--------|-----------|----------------|
| `__init__.py` | 50 | Exports, version, lazy loading |
| `core.py` | 800 | Business logic, data models |
| `cli.py` | 500 | Argument parsing, entry point |
| `gui.py` | 800 | UI components, event handlers |
| `api.py` | 300 | ToolResult wrapper functions |
| `tools.py` | 200 | OpenAI tool definitions |

## pyproject.toml Essentials

```toml
[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[project]
name = "package-name"
version = "1.0.0"
requires-python = ">=3.8"

[project.scripts]
toolname = "package_name.cli:main"

[project.optional-dependencies]
dev = ["pytest", "black", "ruff", "mypy"]
gui = ["PySide6"]
```

## Version Management

Define version in ONE place only:

```python
# package_name/__init__.py or __version__.py
__version__ = "1.0.0"
```

Reference in pyproject.toml:

```toml
[tool.setuptools.dynamic]
version = {attr = "package_name.__version__"}
```

## Lazy Loading Pattern

For heavy dependencies, use `__getattr__` in `__init__.py`:

```python
def __getattr__(name: str):
    if name == "HeavyClass":
        from .core import HeavyClass
        return HeavyClass
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
```

This reduces import time for CLI usage.