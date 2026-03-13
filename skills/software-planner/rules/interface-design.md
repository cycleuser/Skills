# Interface Design Patterns

## CLI (Command-Line Interface)

### Unified Flag Conventions

All projects MUST include these standard flags:

```python
import argparse

parser = argparse.ArgumentParser(
    prog="softwarename",
    description="Software description",
    formatter_class=argparse.RawDescriptionHelpFormatter,
    epilog="""
Examples:
  softwarename                    # Launch GUI (default)
  softwarename web --port 8080    # Web server on port 8080
  softwarename cli input.json     # CLI mode with input file
  softwarename -V                 # Show version
"""
)

# Required unified flags
parser.add_argument("-V", "--version", action="version", 
                    version=f"softwarename {__version__}")
parser.add_argument("-v", "--verbose", action="store_true", 
                    help="Verbose output")
parser.add_argument("-o", "--output", help="Output path")
parser.add_argument("--json", action="store_true", dest="json_output",
                    help="Output results as JSON")
parser.add_argument("-q", "--quiet", action="store_true",
                    help="Suppress non-essential output")
```

### Subcommand Structure (GangDan Pattern)

```python
def main():
    # Check for subcommands
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd in ("gui", "web", "cli"):
            # Route to subcommand handler
            return handle_subcommand(cmd, sys.argv[2:])
    
    # Default: launch GUI
    return launch_gui()

# Entry points
# softwarename          -> GUI
# softwarename gui      -> GUI (explicit)
# softwarename web      -> Web server
# softwarename cli      -> CLI mode
```

### Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Runtime error |
| 2 | Invalid arguments |

## GUI (PySide6 Interface)

### Default Styling Rules

**CRITICAL: Use ONLY default PySide6 styling**

```python
# CORRECT: Use default styling
widget = QWidget()
layout = QVBoxLayout(widget)
button = QPushButton("Run")

# WRONG: Custom colors
# button.setStyleSheet("background-color: #3498db;")  # NO!
# widget.setStyleSheet("font-family: Arial;")         # NO!
```

### Window Structure

```python
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QHBoxLayout, QGroupBox, QLabel, QLineEdit,
    QPushButton, QComboBox, QSpinBox, QDoubleSpinBox,
    QTableWidget, QTabWidget, QMessageBox, QFileDialog,
    QProgressBar, QStatusBar, QMenuBar, QToolBar,
)
import pyqtgraph as pg


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Window properties
        self.setWindowTitle("Software Name v1.0")
        self.setMinimumSize(1024, 768)
        
        # Create menu bar
        self.create_menu_bar()
        
        # Create central widget
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        
        # 1. Control panel (top)
        self.create_control_panel(main_layout)
        
        # 2. Main content area (middle)
        self.create_content_area(main_layout)
        
        # 3. Results area (bottom)
        self.create_results_area(main_layout)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
    
    def create_menu_bar(self):
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("&File")
        
        open_action = file_menu.addAction("&Open...")
        open_action.triggered.connect(self.open_file)
        
        save_action = file_menu.addAction("&Save Results...")
        save_action.triggered.connect(self.save_results)
        
        file_menu.addSeparator()
        exit_action = file_menu.addAction("E&xit")
        exit_action.triggered.connect(self.close)
        
        # Help menu
        help_menu = menubar.addMenu("&Help")
        about_action = help_menu.addAction("&About")
        about_action.triggered.connect(self.show_about)
    
    def create_control_panel(self, parent_layout):
        """Create control panel with input widgets."""
        group = QGroupBox("Parameters")
        layout = QHBoxLayout(group)
        
        # Parameter 1: Text input
        layout.addWidget(QLabel("Input:"))
        self.input_edit = QLineEdit()
        self.input_edit.setPlaceholderText("Enter input...")
        layout.addWidget(self.input_edit)
        
        # Parameter 2: Numeric input
        layout.addWidget(QLabel("Value:"))
        self.value_spin = QDoubleSpinBox()
        self.value_spin.setRange(0, 100)
        self.value_spin.setValue(50)
        layout.addWidget(self.value_spin)
        
        # Parameter 3: Selection
        layout.addWidget(QLabel("Type:"))
        self.type_combo = QComboBox()
        self.type_combo.addItems(["Type A", "Type B", "Type C"])
        layout.addWidget(self.type_combo)
        
        # Run button
        self.run_btn = QPushButton("Run Analysis")
        self.run_btn.clicked.connect(self.run_analysis)
        layout.addWidget(self.run_btn)
        
        parent_layout.addWidget(group)
    
    def create_content_area(self, parent_layout):
        """Create visualization area with pyqtgraph."""
        # Tab widget for multiple views
        tabs = QTabWidget()
        
        # Plot tab
        plot_tab = QWidget()
        plot_layout = QVBoxLayout(plot_tab)
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground('w')
        self.plot_widget.showGrid(x=True, y=True)
        self.plot_widget.setLabel('left', 'Value')
        self.plot_widget.setLabel('bottom', 'Index')
        plot_layout.addWidget(self.plot_widget)
        tabs.addTab(plot_tab, "Plot")
        
        # Data tab
        data_tab = QWidget()
        data_layout = QVBoxLayout(data_tab)
        self.data_table = QTableWidget()
        self.data_table.setColumnCount(4)
        self.data_table.setHorizontalHeaderLabels(["ID", "Name", "Value", "Status"])
        data_layout.addWidget(self.data_table)
        tabs.addTab(data_tab, "Data")
        
        parent_layout.addWidget(tabs, stretch=1)
    
    def create_results_area(self, parent_layout):
        """Create results display area."""
        group = QGroupBox("Results")
        layout = QVBoxLayout(group)
        
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(3)
        self.results_table.setHorizontalHeaderLabels(["Metric", "Value", "Unit"])
        layout.addWidget(self.results_table)
        
        parent_layout.addWidget(group)
```

### pyqtgraph Usage

```python
import pyqtgraph as pg
import numpy as np

# Create plot
plot = pg.PlotWidget()
plot.setBackground('w')  # White background for print
plot.showGrid(x=True, y=True)
plot.setLabel('left', 'Y Axis')
plot.setLabel('bottom', 'X Axis')

# Plot data
x = np.linspace(0, 10, 100)
y = np.sin(x)
plot.plot(x, y, pen='b', name='Sine Wave')

# Multiple curves
plot.plot(x, np.cos(x), pen='r', name='Cosine Wave')
plot.addLegend()

# Scatter plot
scatter = pg.ScatterPlotItem(size=10, pen=pg.mkPen('b'), brush=pg.mkBrush('r'))
scatter.setData(x=np.random.rand(100)*10, y=np.random.rand(100))
plot.addItem(scatter)

# Bar chart equivalent
bar_item = pg.BarGraphItem(x=[1,2,3,4], height=[1,2,3,4], width=0.6, brush='b')
plot.addItem(bar_item)
```

## Web (Flask Interface)

### Application Structure

```python
from flask import Flask, render_template, jsonify, request, send_file
from dataclasses import dataclass
import json

app = Flask(__name__)


@app.route("/")
def index():
    """Main page."""
    return render_template("index.html")


@app.route("/api/analyze", methods=["POST"])
def analyze():
    """Run analysis via API."""
    try:
        data = request.json
        result = perform_analysis(data)
        return jsonify(result.to_dict())
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@app.route("/api/results/<result_id>")
def get_result(result_id):
    """Get stored result by ID."""
    result = load_result(result_id)
    if result:
        return jsonify(result.to_dict())
    return jsonify({"success": False, "error": "Not found"}), 404


@app.route("/api/export/<result_id>")
def export_result(result_id):
    """Export result as file."""
    filepath = generate_export(result_id)
    return send_file(filepath, as_attachment=True)


def run_server(host="127.0.0.1", port=5000, debug=False):
    """Start the Flask development server."""
    print(f"Starting server at http://{host}:{port}")
    print("Press Ctrl+C to stop")
    app.run(host=host, port=port, debug=debug, threaded=True)
```

### HTML Template Pattern

```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Software Name</title>
    <style>
        body { font-family: system-ui, sans-serif; margin: 20px; }
        .container { max-width: 1200px; margin: 0 auto; }
        .control-panel { background: #f5f5f5; padding: 15px; border-radius: 5px; }
        .results { margin-top: 20px; }
        table { width: 100%; border-collapse: collapse; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background: #f0f0f0; }
        button { padding: 10px 20px; cursor: pointer; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Software Name v1.0</h1>
        
        <div class="control-panel">
            <label>Input: <input type="text" id="input-data"></label>
            <label>Value: <input type="number" id="value" value="50"></label>
            <button onclick="runAnalysis()">Run Analysis</button>
        </div>
        
        <div class="results">
            <canvas id="chart"></canvas>
            <table id="results-table">
                <thead><tr><th>ID</th><th>Name</th><th>Value</th></tr></thead>
                <tbody></tbody>
            </table>
        </div>
    </div>
    
    <script>
        async function runAnalysis() {
            const input = document.getElementById('input-data').value;
            const value = document.getElementById('value').value;
            
            const response = await fetch('/api/analyze', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({input, value})
            });
            
            const result = await response.json();
            displayResults(result);
        }
        
        function displayResults(result) {
            // Update table
            const tbody = document.querySelector('#results-table tbody');
            tbody.innerHTML = result.data.map(row => 
                `<tr><td>${row.id}</td><td>${row.name}</td><td>${row.value}</td></tr>`
            ).join('');
        }
    </script>
</body>
</html>
```

## Mode Detection Pattern

Detect which interface to launch based on arguments and environment:

```python
def main():
    import sys
    
    # Check for explicit mode
    if len(sys.argv) > 1:
        mode = sys.argv[1]
        
        if mode == "web":
            from .app import run_server
            run_server()
            return
        
        if mode == "cli":
            run_cli(sys.argv[2:])
            return
        
        if mode == "gui":
            run_gui()
            return
    
    # Check if display available (for GUI)
    if has_display():
        run_gui()
    else:
        # Fall back to web or CLI
        print("No display available. Starting web server...")
        from .app import run_server
        run_server()


def has_display():
    """Check if graphical display is available."""
    import os
    return os.environ.get('DISPLAY') is not None or sys.platform == 'win32'
```