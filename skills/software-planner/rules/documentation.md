# Documentation Requirements

## README.md Structure (English)

Each section must be **200+ words**.

### 1. Project Background

```markdown
## Project Background

The development of [Software Name] arises from the critical need to address 
[specific problem] in the domain of [field]. Traditional approaches to this 
challenge have been limited by [limitation 1] and [limitation 2], which has 
created a significant gap between theoretical advances and practical 
applications. 

Recent research by [Author et al., Year] has demonstrated that [key finding], 
providing new opportunities for automated solutions. However, existing tools 
either lack [missing feature 1] or suffer from [issue 2], making them 
unsuitable for [specific use case]. 

[Software Name] bridges this gap by implementing [core approach] with a 
focus on [key advantage]. The software integrates [technology 1] and 
[technology 2] to provide a comprehensive solution that is both [quality 1] 
and [quality 2]. This project contributes to the field by [contribution].

The name "[Software Name]" reflects [meaning/significance], symbolizing 
the software's purpose of [purpose]. By making this tool publicly available 
under an open-source license, we aim to [goal] and facilitate [outcome].
```

### 2. Application Scenarios

```markdown
## Application Scenarios

[Software Name] is designed to serve multiple application scenarios across 
[domain]. The primary use case involves [scenario 1], where users need to 
[task]. In this context, the software enables [capability] while maintaining 
[quality].

A second major application scenario is [scenario 2]. Researchers and 
practitioners in [field] often face challenges with [problem], and 
[Software Name] addresses this by providing [solution]. The software's 
ability to [feature] makes it particularly valuable for [specific users].

The software also supports [scenario 3], where [description]. This is 
especially relevant for [context], as demonstrated by [example]. Users 
can leverage the [feature] to achieve [outcome].

Educational institutions can utilize [Software Name] for [educational use 
case], helping students understand [concept]. The intuitive interface and 
comprehensive documentation make it accessible to users with varying levels 
of technical expertise.
```

### 3. Hardware Compatibility

```markdown
## Hardware Compatibility

[Software Name] is designed to run efficiently on a wide range of hardware 
configurations, ensuring accessibility for users with different computing 
resources.

**Minimum Requirements:**
The software requires a processor with [CPU specification] or equivalent, 
[RAM amount] of system memory, and [storage amount] of available disk space. 
These minimal specifications allow the software to run on most modern laptops 
and desktop computers.

**Recommended Configuration:**
For optimal performance, especially when processing [large datasets/complex 
calculations], we recommend a system with [better CPU], [more RAM], and 
[storage type]. Users working with [specific workload] will benefit from 
[specific hardware feature].

**GPU Acceleration:**
While the core functionality operates on CPU-only systems, [Software Name] 
optionally supports GPU acceleration through [technology]. This can improve 
performance by [percentage] for [specific operations]. Compatible GPUs 
include [list].

**Special Considerations:**
The software does not require [unusual hardware], making it deployable in 
standard computing environments. Network connectivity is only required for 
[specific feature], allowing offline operation for core functionality.
```

### 4. Operating Systems

```markdown
## Operating Systems

[Software Name] is developed with cross-platform compatibility as a core 
design principle, ensuring consistent functionality across major operating 
systems.

**Windows:**
The software is fully compatible with Windows 10 and Windows 11. Installation 
on Windows is straightforward using [method], and all features have been 
thoroughly tested on both x64 and ARM64 architectures. Users should ensure 
that [requirement] is installed before running the software.

**macOS:**
macOS users running version 10.15 (Catalina) or later can run [Software Name] 
without issues. The software has been validated on Intel-based Macs and Apple 
Silicon (M1/M2/M3) processors. Native performance on Apple Silicon is 
achieved through [mechanism].

**Linux:**
The software supports major Linux distributions including Ubuntu 20.04+, 
Debian 11+, Fedora 35+, and Arch Linux. Users can install via [method] or 
run from source with [requirements]. The CLI and Web interfaces are 
particularly well-suited for server deployments on Linux.

**Platform-Specific Notes:**
- On Windows, [specific note]
- On macOS, [specific note]
- On Linux, [specific note]

The software does not rely on platform-specific dependencies, ensuring 
consistent behavior across all supported operating systems.
```

### 5. Dependencies

```markdown
## Dependencies

[Software Name] requires Python 3.10 or higher and several external packages 
to provide its full range of functionality.

**Core Dependencies:**
The essential packages required for basic operation include:

- `PySide6` (≥6.5.0): Provides the graphical user interface framework. This 
  Qt-based library enables cross-platform GUI development with native look 
  and feel.

- `pyqtgraph` (≥0.13.0): Handles scientific visualization and plotting. This 
  high-performance library is optimized for real-time data display.

- `Flask` (≥3.0.0): Powers the web interface and REST API. This lightweight 
  framework allows flexible web application development.

- `numpy` (≥1.24.0): Provides numerical computing capabilities. Essential 
  for [specific functionality].

- `pandas` (≥2.0.0): Handles data manipulation and analysis. Used for 
  [specific functionality].

**Optional Dependencies:**
Additional packages enhance specific features:

- `scipy` (≥1.10.0): Provides advanced scientific algorithms for [feature].
- `matplotlib` (≥3.7.0): Alternative plotting backend for publication-quality 
  figures.

**Development Dependencies:**
For contributors, additional packages are required:

- `pytest` (≥7.0.0): Testing framework
- `black` (≥23.0.0): Code formatting
- `mypy` (≥1.0.0): Static type checking

All dependencies are specified in `requirements.txt` and `pyproject.toml` 
for easy installation.
```

### 6. Installation

```markdown
## Installation

Installing [Software Name] is straightforward using standard Python package 
management tools. Follow the instructions below for your preferred method.

**Method 1: Install from PyPI (Recommended)**

The simplest way to install [Software Name] is via pip:

```bash
pip install softwarename
```

This will automatically install all required dependencies. After installation, 
verify the installation:

```bash
softwarename -V
```

**Method 2: Install from Source**

For developers or users who want the latest features:

```bash
# Clone the repository
git clone https://github.com/user/softwarename.git
cd softwarename

# Create virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows

# Install in development mode
pip install -e .
```

**Method 3: Using conda**

```bash
conda create -n softwarename python=3.10
conda activate softwarename
pip install softwarename
```

**Post-Installation Setup:**

After installation, [Software Name] is ready to use immediately. No 
additional configuration is required for basic usage. Advanced users can 
customize settings by [method].

**Troubleshooting:**

If you encounter issues during installation:
- Ensure Python 3.10+ is installed: `python --version`
- Update pip: `pip install --upgrade pip`
- Check dependencies: `pip install -r requirements.txt`
```

### 7. Usage

```markdown
## Usage

[Software Name] provides three interfaces for maximum flexibility: a graphical 
user interface (GUI), a web interface, and a command-line interface (CLI).

**Graphical User Interface (GUI)**

Launch the GUI by running:

```bash
softwarename
# or explicitly:
softwarename gui
```

The GUI provides an intuitive interface for [task]. The main window consists 
of [description of GUI components]. Users can [primary workflow].

**Web Interface**

Start the web server:

```bash
softwarename web --port 5000
```

Then open http://localhost:5000 in your browser. The web interface mirrors 
the GUI functionality and is accessible from any device on the network.

**Command-Line Interface (CLI)**

For automation and scripting, use the CLI:

```bash
# Basic usage
softwarename cli input.json -o results.json

# With all options
softwarename cli input.json --verbose --output results.json --format json
```

**Common Workflows:**

1. **Workflow 1:** [Description]
   ```bash
   softwarename cli data.csv --method analysis
   ```

2. **Workflow 2:** [Description]
   ```bash
   softwarename web --port 8080
   # Open browser and use web interface
   ```

**Unified Flags:**
All interfaces support these common flags:
- `-V, --version`: Display version
- `-v, --verbose`: Enable verbose output
- `-o, --output`: Specify output path
- `--json`: Output in JSON format
- `-q, --quiet`: Suppress non-essential output
```

### 8. Screenshots

```markdown
## Screenshots

| Main Interface | Analysis Results |
|:--------------:|:----------------:|
| ![Main](images/main.png) | ![Results](images/results.png) |

| Settings Dialog | Export Options |
|:---------------:|:--------------:|
| ![Settings](images/settings.png) | ![Export](images/export.png) |

**Figure Descriptions:**

The main interface screenshot shows the primary workspace with [description]. 
Users can [action] through the control panel on the left side.

The analysis results view displays [description], with [features] highlighted 
for easy interpretation of results.

The settings dialog allows users to configure [options], including [specific 
settings]. Changes are persisted across sessions.

Export options provide flexibility in [description], supporting formats such 
as [list].
```

### 9. License

```markdown
## License

[Software Name] is released under the GNU General Public License version 3 
(GPLv3). This license ensures that the software remains free and open-source, 
allowing users to use, study, modify, and distribute the software.

**Key Rights Granted:**
- Freedom to use the software for any purpose
- Freedom to study how the software works and modify it
- Freedom to redistribute copies
- Freedom to distribute modified versions

**Requirements:**
- Any derivative work must be licensed under the same terms
- Source code must be made available when distributing the software
- License and copyright notices must be preserved

**Full License Text:**

```
GNU GENERAL PUBLIC LICENSE
Version 3, 29 June 2007

Copyright (C) [Year] [Author]

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
```

See the [LICENSE](LICENSE) file for the complete license text.
```

## README_CN.md Structure (Chinese)

Same structure as English, translated. Each section must be **200+ words**.

Sections:
1. 项目背景
2. 应用场景
3. 兼容硬件
4. 操作系统
5. 依赖环境
6. 安装过程
7. 使用方法
8. 运行截图
9. 授权协议