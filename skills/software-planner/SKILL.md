---
name: software-planner
version: "1.0.0"
description: |
  Comprehensive software development planning and implementation skill.

  **Triggers when:**
  - Creating new Python software with CLI/GUI/Web interfaces
  - Planning software architecture and modules
  - Designing scientific or engineering applications
  - Setting up bilingual documentation and PyPI publishing
  - Need academic research-based feature design

  **Capabilities:**
  - Pre-development planning and research
  - Multi-interface design (CLI + PySide6 GUI + Flask Web)
  - Scientific visualization with pyqtgraph
  - Academic literature-based feature design
  - Sample data and test documentation generation
  - Bilingual README with structured sections
  - GPLv3 licensing and PyPI publishing setup
author: cycleuser
license: MIT
---

# Software Development Planner

Complete workflow for planning and implementing Python software with CLI, GUI, and Web interfaces, following established project patterns from GangDan, Chou, Huan, LaPian, and NuoYi.

## Pre-Development Planning

### Step 1: Domain Research

Before writing any code, conduct thorough research:

1. **Academic Literature Search**
   - Search Google Scholar, CNKI, IEEE, ACM for relevant papers
   - Download key PDFs to `pdf/` directory in project root
   - Extract core concepts and methodologies
   - Identify evaluation criteria and metrics

2. **Existing Solutions Analysis**
   - Search GitHub for similar projects
   - Identify feature gaps and improvement opportunities
   - Note UI/UX patterns and architectural decisions

3. **Requirements Synthesis**
   - Combine academic findings with practical needs
   - Define functional requirements with citations
   - Establish non-functional requirements (performance, usability)

### Step 2: Architecture Design

Design the system before implementation:

```
Software Name (v1.0)
├── Core Features (from research)
│   ├── Feature 1: [description with citation]
│   ├── Feature 2: [description with citation]
│   └── Feature 3: [description with citation]
├── Data Models
│   ├── Model 1: fields, relationships
│   └── Model 2: fields, relationships
├── Algorithms
│   ├── Algorithm 1: input, output, complexity
│   └── Algorithm 2: input, output, complexity
└── User Interfaces
    ├── CLI: commands, flags, arguments
    ├── GUI: windows, panels, controls
    └── Web: routes, templates, API endpoints
```

### Step 3: Module Specification

Define each module with clear responsibilities:

| Module | Responsibility | Size Target |
|--------|---------------|-------------|
| `cli.py` | Command-line argument parsing, routing | ~100 lines |
| `gui.py` | PySide6 window, controls, event handlers | ~200 lines |
| `app.py` | Flask routes, API endpoints | ~100 lines |
| `core.py` | Business logic, algorithms, data models | ~200 lines |
| `api.py` | Unified Python API with ToolResult | ~100 lines |

**Total: 500+ lines required**

## Interface Requirements

### CLI (Command-Line Interface)

Follow unified flag conventions from GangDan:

```python
import argparse

def main():
    parser = argparse.ArgumentParser(
        prog="softwarename",
        description="Software description",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    
    # Unified flags (required)
    parser.add_argument("-V", "--version", action="version", version=f"softwarename {__version__}")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    parser.add_argument("-o", "--output", help="Output path")
    parser.add_argument("--json", action="store_true", dest="json_output", help="Output as JSON")
    parser.add_argument("-q", "--quiet", action="store_true", help="Suppress output")
    
    # Mode selection
    subparsers = parser.add_subparsers(dest="mode")
    
    # GUI mode
    gui_parser = subparsers.add_parser("gui", help="Launch GUI")
    gui_parser.add_argument("--no-web", action="store_true", help="Disable embedded web server")
    
    # Web mode
    web_parser = subparsers.add_parser("web", help="Launch web server")
    web_parser.add_argument("--host", default="127.0.0.1")
    web_parser.add_argument("--port", type=int, default=5000)
    
    # CLI operations
    cli_parser = subparsers.add_parser("cli", help="CLI mode")
    cli_parser.add_argument("input", help="Input file or data")
```

**Entry Points (following GangDan pattern):**

```bash
softwarename              # Default: launch GUI or web based on context
softwarename gui          # Explicit GUI mode
softwarename web          # Web server mode
softwarename cli <args>   # CLI mode
python -m packagename     # Module invocation
```

### GUI (PySide6 Interface)

Use default PySide6 styling - NO custom colors, fonts, or backgrounds:

```python
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, 
    QHBoxLayout, QPushButton, QLabel, QLineEdit, 
    QComboBox, QSpinBox, QDoubleSpinBox, QTableWidget,
    QTabWidget, QGroupBox, QFileDialog, QMessageBox,
)
from PySide6.QtCore import Qt
import pyqtgraph as pg

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Software Name v1.0")
        self.setMinimumSize(800, 600)
        
        # Central widget with default styling
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        
        # Controls in group box
        control_group = QGroupBox("Parameters")
        control_layout = QHBoxLayout(control_group)
        
        # Input controls
        self.input_edit = QLineEdit()
        self.input_edit.setPlaceholderText("Enter input...")
        control_layout.addWidget(QLabel("Input:"))
        control_layout.addWidget(self.input_edit)
        
        # Action buttons
        btn_run = QPushButton("Run")
        btn_run.clicked.connect(self.run_analysis)
        control_layout.addWidget(btn_run)
        
        layout.addWidget(control_group)
        
        # Visualization with pyqtgraph
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground('w')  # White background for plots
        self.plot_widget.showGrid(x=True, y=True)
        layout.addWidget(self.plot_widget)
        
        # Results table
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(4)
        self.results_table.setHorizontalHeaderLabels(["ID", "Name", "Value", "Score"])
        layout.addWidget(self.results_table)
```

**GUI Design Principles:**

1. **Default Styling Only**
   - Use system default colors
   - Use system default fonts
   - No custom backgrounds
   - No custom stylesheets

2. **Layout Structure**
   - Top: Control panel with parameters
   - Middle: Visualization area (pyqtgraph)
   - Bottom: Results table or log output

3. **Control Types**
   - `QLineEdit` for text input
   - `QSpinBox` / `QDoubleSpinBox` for numeric input
   - `QComboBox` for selections
   - `QCheckBox` for boolean options
   - `QPushButton` for actions

### Web (Flask Interface)

```python
from flask import Flask, render_template, jsonify, request

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/analyze", methods=["POST"])
def analyze():
    data = request.json
    result = perform_analysis(data)
    return jsonify(result.to_dict())

@app.route("/api/results/<id>")
def get_results(id):
    result = get_stored_result(id)
    return jsonify(result.to_dict())

def run_server(host="127.0.0.1", port=5000):
    print(f"Starting server at http://{host}:{port}")
    app.run(host=host, port=port, debug=False)
```

## ToolResult Pattern

All API functions must return ToolResult:

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

## Sample Data Requirements

Create sample data for testing and demonstration:

### Data File Structure

```
data/
├── sample_input.json      # Example input data
├── sample_results.json    # Expected output for testing
├── test_cases.json        # Test case definitions
└── reference_data.csv     # Reference/benchmark data
```

### Sample Data Template

```json
{
  "description": "Sample input for testing",
  "version": "1.0",
  "cases": [
    {
      "id": "case_001",
      "name": "Basic test case",
      "input": {
        "param1": "value1",
        "param2": 100
      },
      "expected_output": {
        "result": "expected_result",
        "score": 0.95
      }
    }
  ]
}
```

## Documentation Structure

### README.md (English)

Required sections, each 200+ words:

1. **Project Background** - Context, problem statement, motivation
2. **Application Scenarios** - Use cases, target users, workflows
3. **Hardware Compatibility** - CPU, GPU, memory requirements
4. **Operating Systems** - Windows, macOS, Linux support
5. **Dependencies** - Python version, required packages
6. **Installation** - pip install, from source, configuration
7. **Usage** - CLI commands, GUI operation, Web interface
8. **Screenshots** - Placeholders with descriptions
9. **License** - GPLv3 statement

### README_CN.md (Chinese)

Same structure as English, translated:

1. **项目背景** - 背景、问题陈述、动机
2. **应用场景** - 用例、目标用户、工作流程
3. **兼容硬件** - CPU、GPU、内存要求
4. **操作系统** - Windows、macOS、Linux 支持
5. **依赖环境** - Python 版本、依赖包
6. **安装过程** - pip 安装、源码安装、配置
7. **使用方法** - CLI 命令、GUI 操作、Web 界面
8. **运行截图** - 带描述的占位符
9. **授权协议** - GPLv3 声明

### README Template

```markdown
# Software Name

Brief one-line description.

## Project Background

[200+ words describing the context, problem, and motivation for this software. Include academic context and practical need.]

## Application Scenarios

[200+ words describing specific use cases, target users, and typical workflows.]

## Hardware Compatibility

[200+ words describing CPU requirements, GPU needs (if any), memory requirements, and storage needs.]

## Operating Systems

[200+ words describing support for Windows, macOS, Linux, with specific version requirements.]

## Dependencies

[200+ words listing Python version requirement, core dependencies with version constraints, and optional dependencies.]

## Installation

[200+ words with step-by-step installation instructions for pip, conda, and from-source methods.]

## Usage

[200+ words with CLI examples, GUI instructions, and Web interface usage.]

## Screenshots

| GUI Interface | Web Interface |
|:-------------:|:-------------:|
| ![GUI](images/gui.png) | ![Web](images/web.png) |

## License

GPLv3. See [LICENSE](LICENSE) for details.
```

## Project File Structure

```
project_name/
├── pyproject.toml          # Package configuration
├── requirements.txt        # Dependencies list
├── LICENSE                 # GPLv3 license
├── README.md               # English documentation
├── README_CN.md            # Chinese documentation
├── MANIFEST.in             # Package manifest
├── upload_pypi.sh          # PyPI upload script (Unix)
├── upload_pypi.bat         # PyPI upload script (Windows)
├── pdf/                    # Academic reference papers
│   ├── paper1.pdf
│   └── paper2.pdf
├── data/                   # Sample data
│   ├── sample_input.json
│   └── test_cases.json
├── images/                 # Screenshots
│   └── placeholder.png
├── tests/                  # Test suite
│   ├── __init__.py
│   ├── conftest.py
│   └── test_core.py
└── packagename/            # Main package
    ├── __init__.py         # Version and exports
    ├── __main__.py         # python -m entry
    ├── cli.py              # CLI implementation
    ├── gui.py              # GUI implementation
    ├── app.py              # Flask web app
    ├── core.py             # Business logic
    └── api.py              # Unified API
```

## Rules

- [rules/pre-development.md](rules/pre-development.md) - Research and planning phase
- [rules/interface-design.md](rules/interface-design.md) - CLI/GUI/Web patterns
- [rules/documentation.md](rules/documentation.md) - README requirements
- [rules/sample-data.md](rules/sample-data.md) - Test data creation

## Verification Checklist

Before considering the project complete:

- [ ] Code is 500+ lines total
- [ ] CLI has unified flags (-V, -v, -o, --json, -q)
- [ ] GUI uses default PySide6 styling
- [ ] Web interface has REST API
- [ ] All functions return ToolResult
- [ ] Sample data files exist
- [ ] Test cases defined
- [ ] README.md has all 9 sections (200+ words each)
- [ ] README_CN.md has all 9 sections (200+ words each)
- [ ] Academic PDFs in `pdf/` directory
- [ ] GPLv3 LICENSE file exists
- [ ] requirements.txt exists
- [ ] pyproject.toml configured correctly
- [ ] PyPI upload scripts exist

## Quick Start Template

```bash
# Create project structure
mkdir -p project_name/{pdf,data,images,tests,packagename}

# Create required files
touch project_name/{pyproject.toml,requirements.txt,LICENSE,README.md,README_CN.md}
touch project_name/upload_pypi.{sh,bat}

# Create package files
touch project_name/packagename/{__init__.py,__main__.py,cli.py,gui.py,app.py,core.py,api.py}

# Create test files
touch project_name/tests/{__init__.py,conftest.py,test_core.py}
```