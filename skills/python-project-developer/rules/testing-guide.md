# Testing Best Practices

## Test File Structure

Location: `tests/test_unified_api.py`

### Required Test Classes

```python
class TestToolResult:
    """Test ToolResult dataclass behavior."""

class TestXxxAPI:
    """Test api.py functions."""

class TestToolsSchema:
    """Test TOOLS list schema validity."""

class TestToolsDispatch:
    """Test dispatch() function."""

class TestCLIFlags:
    """Test CLI unified flags."""

class TestPackageExports:
    """Test __init__.py exports."""
```

## TestToolResult

```python
class TestToolResult:
    def test_success_result(self):
        from projectname.api import ToolResult
        r = ToolResult(success=True, data={"key": "value"}, metadata={"v": "1"})
        assert r.success is True
        assert r.data == {"key": "value"}
        assert r.error is None

    def test_failure_result(self):
        from projectname.api import ToolResult
        r = ToolResult(success=False, error="something broke")
        assert r.success is False
        assert r.error == "something broke"
        assert r.data is None

    def test_to_dict(self):
        from projectname.api import ToolResult
        r = ToolResult(success=True, data=[1, 2], metadata={"x": 1})
        d = r.to_dict()
        assert set(d.keys()) == {"success", "data", "error", "metadata"}

    def test_default_metadata_isolation(self):
        """Verify each instance has independent metadata."""
        from projectname.api import ToolResult
        r1 = ToolResult(success=True)
        r2 = ToolResult(success=True)
        r1.metadata["a"] = 1
        assert "a" not in r2.metadata
```

## TestXxxAPI

Each API function needs at least 3 tests:

```python
import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path
import tempfile

class TestActionNounAPI:
    def test_invalid_input(self):
        """Test with invalid/missing input."""
        from projectname.api import action_noun
        result = action_noun(required_param="")
        assert result.success is False
        assert "empty" in result.error.lower()

    def test_valid_input(self):
        """Test with valid minimal input."""
        from projectname.api import action_noun
        with tempfile.TemporaryDirectory() as tmpdir:
            result = action_noun(required_param=tmpdir)
            assert result.success is True
            assert "version" in result.metadata

    def test_path_object_compatible(self):
        """Test that Path objects work."""
        from projectname.api import action_noun
        with tempfile.TemporaryDirectory() as tmpdir:
            result = action_noun(required_param=Path(tmpdir))
            assert result.success is True

    @patch("projectname.core.HeavyDependency")
    def test_with_mock(self, mock_dep):
        """Test with mocked external dependency."""
        mock_dep.return_value = MagicMock()
        from projectname.api import action_noun
        result = action_noun(required_param="test")
        assert result.success is True
```

### Mock Target Rules

**CRITICAL:** Mock the source module, not the API module.

```python
# CORRECT: Mock where the dependency is defined
@patch("projectname.core.HeavyDependency")
def test_correct(self, mock_dep):
    ...

# WRONG: Mock where it's used (lazy import doesn't have it)
@patch("projectname.api.HeavyDependency")  # AttributeError!
def test_wrong(self, mock_dep):
    ...
```

## TestToolsSchema

```python
class TestToolsSchema:
    def test_tools_is_list(self):
        from projectname.tools import TOOLS
        assert isinstance(TOOLS, list)
        assert len(TOOLS) >= 1

    def test_tool_names(self):
        from projectname.tools import TOOLS
        for tool in TOOLS:
            name = tool["function"]["name"]
            assert name.startswith("projectname_")

    def test_tool_structure(self):
        from projectname.tools import TOOLS
        for tool in TOOLS:
            assert tool["type"] == "function"
            func = tool["function"]
            assert "name" in func
            assert "description" in func
            assert "parameters" in func
            assert func["parameters"]["type"] == "object"
            assert "properties" in func["parameters"]
            assert "required" in func["parameters"]

    def test_required_fields_in_properties(self):
        from projectname.tools import TOOLS
        for tool in TOOLS:
            func = tool["function"]
            props = func["parameters"]["properties"]
            for req in func["parameters"]["required"]:
                assert req in props, f"Required '{req}' not in properties"
```

## TestToolsDispatch

```python
import json

class TestToolsDispatch:
    def test_dispatch_unknown_tool(self):
        from projectname.tools import dispatch
        with pytest.raises(ValueError, match="Unknown tool"):
            dispatch("nonexistent_tool", {})

    def test_dispatch_json_string_args(self):
        from projectname.tools import dispatch
        args = json.dumps({"required_param": "value"})
        result = dispatch("projectname_action_noun", args)
        assert isinstance(result, dict)
        assert "success" in result

    def test_dispatch_dict_args(self):
        from projectname.tools import dispatch
        result = dispatch("projectname_action_noun", {"required_param": "value"})
        assert "success" in result

    def test_dispatch_error_case(self):
        from projectname.tools import dispatch
        result = dispatch("projectname_action_noun", {"required_param": ""})
        assert result["success"] is False
```

## TestCLIFlags

```python
import subprocess
import sys

class TestCLIFlags:
    def _run_cli(self, *args):
        return subprocess.run(
            [sys.executable, "-m", "package_name"] + list(args),
            capture_output=True,
            text=True,
            timeout=15,
        )

    def test_version_flag(self):
        r = self._run_cli("-V")
        assert r.returncode == 0
        assert "package_name" in r.stdout.lower() or "projectname" in r.stdout.lower()

    def test_help_has_unified_flags(self):
        r = self._run_cli("--help")
        assert r.returncode == 0
        assert "--json" in r.stdout
        assert "--quiet" in r.stdout or "-q" in r.stdout
        assert "--verbose" in r.stdout or "-v" in r.stdout

    def test_quiet_suppresses_output(self):
        r_normal = self._run_cli("some_command")
        r_quiet = self._run_cli("some_command", "-q")
        # Quiet should have less output
        assert len(r_quiet.stdout) <= len(r_normal.stdout)
```

## TestPackageExports

```python
class TestPackageExports:
    def test_version(self):
        import projectname
        assert hasattr(projectname, "__version__")
        assert isinstance(projectname.__version__, str)

    def test_toolresult(self):
        from projectname import ToolResult
        assert callable(ToolResult)

    def test_api_function_exported(self):
        from projectname import action_noun
        assert callable(action_noun)

    def test_all_defined(self):
        import projectname
        assert hasattr(projectname, "__all__")
```

## Running Tests

```bash
# Single project
cd project_directory
pytest tests/test_unified_api.py -v

# Specific test class
pytest tests/test_unified_api.py::TestToolResult -v

# Specific test
pytest tests/test_unified_api.py::TestToolResult::test_success_result -v

# With coverage
pytest tests/test_unified_api.py --cov=projectname
```

## Testing Principles

1. **No network dependency** - Mock all external calls
2. **No external services** - Don't require Ollama, OpenAI, databases
3. **Use temp directories** - `tempfile.TemporaryDirectory()` for file tests
4. **Import inside tests** - Avoid module-level imports that might fail
5. **Precise assertions** - Use `is True` not truthy checks for booleans
6. **Verify error messages** - Check that errors contain expected strings