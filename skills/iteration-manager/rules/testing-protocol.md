# Testing Execution Protocol

## Test Execution Order

### Phase 1: Syntax and Import Checks

```bash
# Python syntax check
python -m py_compile **/*.py

# Import check
python -c "import package_name"

# Type check (if mypy configured)
mypy package_name
```

### Phase 2: Lint Checks

```bash
# Ruff (recommended)
ruff check .

# Or traditional
flake8 .
black --check .
isort --check .
```

### Phase 3: Unit Tests

```bash
# Run all unit tests
pytest tests/ -v --tb=short

# Run with markers
pytest tests/ -m "unit" -v
```

### Phase 4: Integration Tests

```bash
# Run integration tests
pytest tests/ -m "integration" -v

# Skip if no integration tests
pytest tests/ --ignore=tests/integration/
```

### Phase 5: Coverage Analysis

```bash
# Generate coverage report
pytest tests/ --cov=package --cov-report=term-missing --cov-report=html

# Minimum coverage threshold
pytest tests/ --cov=package --cov-fail-under=80
```

## Test Result Collection

### Result Format

```json
{
  "iteration": 1,
  "timestamp": "2024-01-01T12:00:00Z",
  "phase": "unit_tests",
  "results": {
    "total": 50,
    "passed": 45,
    "failed": 3,
    "skipped": 2,
    "duration_seconds": 12.5
  },
  "failures": [
    {
      "test": "test_function_name",
      "file": "tests/test_module.py",
      "error": "AssertionError: Expected True, got False",
      "line": 42
    }
  ],
  "coverage": {
    "percent": 78.5,
    "lines_covered": 1250,
    "lines_total": 1592,
    "missing_lines": [45, 67, 89]
  }
}
```

## Failure Analysis

### Categorize Failures

| Category | Pattern | Action |
|----------|---------|--------|
| Import Error | ModuleNotFoundError | Fix dependencies |
| Type Error | TypeError, AttributeError | Fix type handling |
| Logic Error | AssertionError | Fix logic |
| Config Error | FileNotFoundError | Fix configuration |
| Timeout | TimeoutError | Optimize or increase timeout |

### Priority Scoring

```python
def calculate_priority(failure: dict) -> int:
    """Calculate priority score (higher = more important)."""
    score = 0
    
    # Critical tests
    if failure.get("critical"):
        score += 100
    
    # Core functionality
    if "core" in failure["file"]:
        score += 50
    
    # New failures
    if not failure.get("known_issue"):
        score += 30
    
    # Multiple similar failures
    score += failure.get("similarity_count", 0) * 10
    
    return score
```

## Test Isolation

### Per-File Testing

```bash
# Test single file
pytest tests/test_specific.py -v

# Test single class
pytest tests/test_specific.py::TestClassName -v

# Test single method
pytest tests/test_specific.py::TestClassName::test_method -v
```

### Parallel Execution

```bash
# Run tests in parallel
pytest tests/ -n auto

# With coverage
pytest tests/ -n auto --cov=package
```

## Mock Strategy

### External Dependencies

```python
# Mock external APIs
@patch("requests.get")
def test_api_call(mock_get):
    mock_get.return_value.json.return_value = {"data": "test"}
    # test code

# Mock file system
@patch("builtins.open", mock_open(read_data="test"))
def test_file_read():
    # test code
```

### Database Mocking

```python
# Use in-memory database
@pytest.fixture
def db():
    from sqlalchemy import create_engine
    engine = create_engine("sqlite:///:memory:")
    # setup
    yield engine
    # cleanup
```

## Performance Testing

### Benchmarks

```python
import pytest
import time

@pytest.mark.benchmark
def test_performance():
    start = time.time()
    # operation
    duration = time.time() - start
    assert duration < 1.0, f"Too slow: {duration}s"
```

### Memory Profiling

```python
import tracemalloc

def test_memory_usage():
    tracemalloc.start()
    # operation
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    assert peak < 100 * 1024 * 1024  # 100MB limit
```

## Cleanup Protocol

After each test run:

1. Remove temporary files
2. Reset global state
3. Close connections
4. Clear caches

```python
@pytest.fixture(autouse=True)
def cleanup():
    yield
    # Cleanup code runs after each test
    import tempfile
    tempfile.tempdir = None
```