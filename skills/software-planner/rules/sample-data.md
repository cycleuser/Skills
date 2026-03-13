# Sample Data and Test Documentation

## Sample Data Requirements

### Directory Structure

```
data/
├── sample_input.json       # Example input for testing
├── sample_output.json      # Expected output for validation
├── test_cases.json         # Test case definitions
├── reference_data.csv      # Reference/benchmark data
└── sample_images/          # Sample images if needed
    ├── image1.png
    └── image2.png
```

### Sample Input Format

```json
{
  "description": "Sample input data for testing",
  "version": "1.0",
  "created": "2024-01-01",
  "parameters": {
    "param1": {
      "type": "string",
      "description": "Description of parameter 1",
      "default": "default_value"
    },
    "param2": {
      "type": "number",
      "description": "Description of parameter 2",
      "default": 100,
      "range": [0, 1000]
    }
  },
  "samples": [
    {
      "id": "sample_001",
      "param1": "test_value",
      "param2": 50
    },
    {
      "id": "sample_002",
      "param1": "another_value",
      "param2": 75
    }
  ]
}
```

### Sample Output Format

```json
{
  "description": "Expected output for sample_input.json",
  "version": "1.0",
  "results": [
    {
      "input_id": "sample_001",
      "success": true,
      "output": {
        "result1": "calculated_value",
        "result2": 123.45,
        "metrics": {
          "accuracy": 0.95,
          "confidence": 0.87
        }
      }
    },
    {
      "input_id": "sample_002",
      "success": true,
      "output": {
        "result1": "another_value",
        "result2": 234.56,
        "metrics": {
          "accuracy": 0.92,
          "confidence": 0.91
        }
      }
    }
  ]
}
```

### Test Cases Definition

```json
{
  "test_suite": "SoftwareName Test Suite",
  "version": "1.0",
  "test_cases": [
    {
      "id": "TC001",
      "name": "Basic functionality test",
      "description": "Test basic operation with valid input",
      "category": "functional",
      "priority": "high",
      "input": {
        "param1": "valid_input",
        "param2": 100
      },
      "expected_output": {
        "success": true,
        "result": "expected_result"
      },
      "validation": {
        "assertions": [
          "result.success == true",
          "result.data is not None"
        ]
      }
    },
    {
      "id": "TC002",
      "name": "Edge case: empty input",
      "description": "Test behavior with empty input",
      "category": "edge_case",
      "priority": "medium",
      "input": {
        "param1": "",
        "param2": 0
      },
      "expected_output": {
        "success": false,
        "error": "Input cannot be empty"
      }
    },
    {
      "id": "TC003",
      "name": "Error handling: invalid type",
      "description": "Test error handling for invalid input type",
      "category": "error_handling",
      "priority": "high",
      "input": {
        "param1": 123,
        "param2": "invalid"
      },
      "expected_output": {
        "success": false,
        "error": "Invalid input type"
      }
    }
  ]
}
```

### Reference Data Format (CSV)

```csv
id,name,value,category,benchmark_score
ref_001,Reference Item 1,100.5,A,0.95
ref_002,Reference Item 2,200.3,B,0.87
ref_003,Reference Item 3,150.8,A,0.92
```

## Test Documentation

### Test Plan Template

```markdown
# Test Plan

## 1. Introduction
- Purpose: Verify [Software Name] meets requirements
- Scope: All functional and non-functional requirements
- References: Requirements document, design document

## 2. Test Strategy
- Approach: Automated testing with pytest
- Levels: Unit, Integration, System
- Tools: pytest, pytest-qt, pytest-flask

## 3. Test Environment
- OS: Windows 10/11, macOS 12+, Ubuntu 22.04
- Python: 3.10, 3.11, 3.12
- Dependencies: As specified in requirements.txt

## 4. Test Cases
[Reference to test_cases.json]

## 5. Entry/Exit Criteria
- Entry: Software builds successfully
- Exit: All test cases pass, coverage > 80%

## 6. Deliverables
- Test cases (test_cases.json)
- Test results (test_results.json)
- Coverage report (coverage.xml)
```

### Test Code Structure

```python
# tests/conftest.py
import pytest
import json
from pathlib import Path


@pytest.fixture
def sample_input():
    """Load sample input data."""
    data_file = Path(__file__).parent.parent / "data" / "sample_input.json"
    return json.loads(data_file.read_text())


@pytest.fixture
def expected_output():
    """Load expected output data."""
    data_file = Path(__file__).parent.parent / "data" / "sample_output.json"
    return json.loads(data_file.read_text())


@pytest.fixture
def test_cases():
    """Load test case definitions."""
    data_file = Path(__file__).parent.parent / "data" / "test_cases.json"
    return json.loads(data_file.read_text())


# tests/test_core.py
import pytest
from packagename.api import ToolResult, analyze


class TestToolResult:
    """Test ToolResult dataclass."""
    
    def test_success_result(self):
        result = ToolResult(success=True, data={"key": "value"})
        assert result.success is True
        assert result.data == {"key": "value"}
        assert result.error is None
    
    def test_failure_result(self):
        result = ToolResult(success=False, error="Error message")
        assert result.success is False
        assert result.error == "Error message"
    
    def test_to_dict(self):
        result = ToolResult(success=True, data=[1, 2, 3])
        d = result.to_dict()
        assert set(d.keys()) == {"success", "data", "error", "metadata"}


class TestAnalyze:
    """Test analyze function with sample data."""
    
    def test_analyze_valid_input(self, sample_input, expected_output):
        """Test with valid input from sample data."""
        for sample in sample_input["samples"]:
            result = analyze(param1=sample["param1"], param2=sample["param2"])
            assert result.success is True
    
    def test_analyze_empty_input(self):
        """Test with empty input."""
        result = analyze(param1="", param2=0)
        assert result.success is False
    
    def test_analyze_output_format(self, sample_input):
        """Test output format matches specification."""
        sample = sample_input["samples"][0]
        result = analyze(param1=sample["param1"], param2=sample["param2"])
        
        assert isinstance(result, ToolResult)
        assert "version" in result.metadata


class TestCasesFromJSON:
    """Run test cases from test_cases.json."""
    
    @pytest.mark.parametrize("test_case", [
        pytest.param(tc, id=tc["id"]) 
        for tc in json.loads(Path("data/test_cases.json").read_text())["test_cases"]
    ])
    def test_from_json(self, test_case):
        """Run each test case defined in JSON."""
        from packagename.api import analyze
        
        result = analyze(**test_case["input"])
        
        expected = test_case["expected_output"]
        assert result.success == expected["success"]
        
        if expected.get("error"):
            assert expected["error"] in result.error
```

### Test Results Format

```json
{
  "test_run": {
    "timestamp": "2024-01-01T12:00:00Z",
    "software_version": "1.0.0",
    "python_version": "3.10.0",
    "platform": "darwin"
  },
  "summary": {
    "total": 50,
    "passed": 48,
    "failed": 2,
    "skipped": 0,
    "coverage_percent": 85.5
  },
  "results": [
    {
      "test_id": "TC001",
      "status": "passed",
      "duration_ms": 15
    },
    {
      "test_id": "TC002",
      "status": "failed",
      "error": "AssertionError: Expected success to be False",
      "duration_ms": 10
    }
  ]
}
```

## Verification Checklist

- [ ] `data/sample_input.json` exists with valid JSON
- [ ] `data/sample_output.json` exists with expected results
- [ ] `data/test_cases.json` defines at least 5 test cases
- [ ] `data/reference_data.csv` contains benchmark data (if applicable)
- [ ] Tests pass with sample data
- [ ] Test coverage > 80%
- [ ] Test results documented