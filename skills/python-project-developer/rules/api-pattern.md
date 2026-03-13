# API Design Patterns

## ToolResult Dataclass

The standard return type for all API functions:

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

## API Function Template

```python
def projectname_action_noun(
    *,
    required_param: str,
    optional_param: str = "default",
) -> ToolResult:
    """One-line description.

    Args:
        required_param: Description of required param.
        optional_param: Description of optional param.

    Returns:
        ToolResult with success status and data/error.
    """
    # Lazy imports - avoid startup overhead
    from pathlib import Path
    from .core import Processor

    try:
        # Validate inputs
        if not required_param:
            return ToolResult(
                success=False,
                error="required_param cannot be empty"
            )

        # Run core logic
        result = Processor.run(required_param, optional_param)

        return ToolResult(
            success=True,
            data=result,
            metadata={"version": __version__}
        )

    except Exception as e:
        return ToolResult(success=False, error=str(e))
```

## Key Principles

### 1. Keyword-Only Arguments

Use `*` to enforce keyword arguments:

```python
def api_function(*, arg1: str, arg2: int = 0) -> ToolResult:
    ...
```

This makes the API self-documenting and prevents positional confusion.

### 2. Path Type Flexibility

Accept both `str` and `Path`:

```python
def process_file(file_path: str | Path) -> ToolResult:
    path = Path(file_path)  # Normalize
    ...
```

### 3. Version in Metadata

Always include version for debugging:

```python
return ToolResult(
    success=True,
    data=result,
    metadata={"version": __version__}
)
```

### 4. Lazy Imports

Import heavy dependencies inside functions:

```python
def heavy_operation():
    # Good: imports only when function is called
    import torch
    import transformers

    # Bad: module-level import slows startup
```

### 5. Catch All Exceptions

API functions should never raise; return ToolResult:

```python
try:
    result = do_something()
    return ToolResult(success=True, data=result)
except Exception as e:
    return ToolResult(success=False, error=str(e))
```

## Naming Convention

Pattern: `{projectname}_{verb}_{noun}`

| Project | Example Function |
|---------|------------------|
| chou | `rename_papers` |
| gangdan | `chat` |
| huan | `archive_site` |
| liao | `list_windows` |
| nuoyi | `convert_file` |
| copytalker | `translate` |

## Async/Sync Pattern

Provide both versions when needed:

```python
async def fetch_data(url: str) -> ToolResult:
    import aiohttp
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.json()
    return ToolResult(success=True, data=data)

def fetch_data_sync(url: str) -> ToolResult:
    import asyncio
    return asyncio.run(fetch_data(url))
```

## __init__.py Exports

```python
from .__version__ import __version__
from .api import ToolResult, action_noun

__all__ = ["__version__", "ToolResult", "action_noun"]
```

For projects with `__getattr__` lazy loading:

```python
def __getattr__(name: str):
    if name == "ToolResult":
        from .api import ToolResult
        return ToolResult
    if name == "action_noun":
        from .api import action_noun
        return action_noun
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

__all__ = ["__version__", "ToolResult", "action_noun"]
```