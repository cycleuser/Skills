---
name: software-planner
version: "1.0.0"
description: |
  Comprehensive software development planning and implementation skill.

  Triggers when: Creating new Python software with CLI/GUI/Web interfaces, planning software architecture and modules, designing scientific or engineering applications, setting up bilingual documentation and PyPI publishing, or needing academic research-based feature design.

  Capabilities: Pre-development planning and research, multi-interface design (CLI + PySide6 GUI + Flask Web), scientific visualization with pyqtgraph, academic literature-based feature design, sample data and test documentation generation, bilingual README with structured sections, GPLv3 licensing and PyPI publishing setup.
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

Define each module with clear responsibilities and size targets. The `cli.py` module handles command-line argument parsing and routing, targeting around 100 lines. The `gui.py` module provides PySide6 window, controls, and event handlers, targeting around 200 lines. The `app.py` module contains Flask routes and API endpoints, targeting around 100 lines. The `core.py` module implements business logic, algorithms, and data models, targeting around 200 lines. The `api.py` module provides the unified Python API with ToolResult, targeting around 100 lines. Total target is 500+ lines across all modules.

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

Entry Points (following GangDan pattern): The software supports multiple entry points. The default invocation launches GUI or web based on context. Explicit GUI mode uses `softwarename gui`. Web server mode uses `softwarename web`. CLI mode uses `softwarename cli <args>`. Module invocation uses `python -m packagename`.

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

GUI Design Principles: Three principles guide GUI implementation. First, use default styling only with system default colors, system default fonts, no custom backgrounds, and no custom stylesheets. Second, follow a consistent layout structure with the control panel with parameters at the top, visualization area with pyqtgraph in the middle, and results table or log output at the bottom. Third, select appropriate control types: `QLineEdit` for text input, `QSpinBox` or `QDoubleSpinBox` for numeric input, `QComboBox` for selections, `QCheckBox` for boolean options, and `QPushButton` for actions.

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

Required sections, each 200+ words: Section 1 covers project background including context, problem statement, and motivation. Section 2 describes application scenarios with use cases, target users, and workflows. Section 3 details hardware compatibility including CPU, GPU, and memory requirements. Section 4 specifies operating system support for Windows, macOS, and Linux. Section 5 lists dependencies including Python version and required packages. Section 6 provides installation instructions for pip install, from source, and configuration. Section 7 explains usage covering CLI commands, GUI operation, and Web interface. Section 8 includes screenshots with placeholders and descriptions. Section 9 covers license information with the GPLv3 statement.

### README_CN.md (Chinese)

Same structure as English, translated: Section 1 covers 项目背景 (project background). Section 2 covers 应用场景 (application scenarios). Section 3 covers 兼容硬件 (hardware compatibility). Section 4 covers 操作系统 (operating systems). Section 5 covers 依赖环境 (dependencies). Section 6 covers 安装过程 (installation). Section 7 covers 使用方法 (usage). Section 8 covers 运行截图 (screenshots). Section 9 covers 授权协议 (license).

### README Template

The README template provides a structured format for documentation. Each section should contain at least 200 words to ensure adequate detail. The Project Background section describes the context, problem, and motivation for the software, including academic context and practical need. The Application Scenarios section describes specific use cases, target users, and typical workflows. The Hardware Compatibility section describes CPU requirements, GPU needs if any, memory requirements, and storage needs. The Operating Systems section describes support for Windows, macOS, and Linux with specific version requirements. The Dependencies section lists Python version requirement, core dependencies with version constraints, and optional dependencies. The Installation section provides step-by-step installation instructions for pip, conda, and from-source methods. The Usage section provides CLI examples, GUI instructions, and Web interface usage. The Screenshots section displays GUI and Web interface images. The License section states GPLv3 and references the LICENSE file.

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

Before considering the project complete, verify the following items. Code should be 500+ lines total across all modules. CLI should have unified flags (-V, -v, -o, --json, -q). GUI should use default PySide6 styling without custom styling. Web interface should have a REST API. All functions should return ToolResult. Sample data files should exist in the data directory. Test cases should be defined. README.md should have all 9 sections with 200+ words each. README_CN.md should have all 9 sections with 200+ words each. Academic PDFs should be present in the `pdf/` directory. GPLv3 LICENSE file should exist. requirements.txt should exist. pyproject.toml should be configured correctly. PyPI upload scripts should exist.

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