# OpenCode Skills 使用指南

本指南介绍如何在 OpenCode 中安装和使用 cycleuser/Skills 仓库中的技能。

## 快速安装

### 方法 1: 一键安装 (推荐)

```bash
curl -sSL https://raw.githubusercontent.com/cycleuser/Skills/main/quick-install-opencode.sh | bash
```

### 方法 2: Python 安装器

```bash
curl -sSL https://raw.githubusercontent.com/cycleuser/Skills/main/install-opencode.py | python3 install
```

### 方法 3: 从本地安装

```bash
git clone https://github.com/cycleuser/Skills.git
cd Skills
python3 install-opencode.py install --source .
```

## 可用技能列表

| 技能名称 | 描述 | 适用场景 |
|---------|------|---------|
| `skill-manager` | 技能注册和管理系统 | 自动加载 |
| `master-architect` | 顶级软件架构师代理 | 复杂项目架构设计 |
| `python-project-developer` | Python CLI/GUI 开发规范 | Python 项目开发 |
| `software-planner` | 软件开发规划 | 项目规划阶段 |
| `coding-agent-patterns` | AI 编码代理模式 | 通用开发模式 |
| `iteration-manager` | 迭代测试和改进 | 测试和质量保证 |
| `academic-writer` | 学术论文写作助手 | 学术写作 |

## 使用示例

### 示例 1: 使用 master-architect 设计系统架构

在 OpenCode 中输入:

```
我需要设计一个文本挖掘系统，支持 CLI 和 GUI 界面，
能够处理大规模文本数据并生成可视化报告。
请帮我规划完整的架构。
```

OpenCode 会自动加载 `master-architect` 技能并提供:
- 需求分析
- 架构设计
- 模块分解
- 迭代开发计划

### 示例 2: 使用 python-project-developer 开发 Python 项目

```
创建一个 Python 命令行工具，用于分析 CSV 文件并生成统计报告。
需要支持 JSON 输出和详细日志模式。
```

技能将提供:
- 项目结构模板
- CLI 标准化参数
- ToolResult API 模式
- 测试用例模板

### 示例 3: 使用 iteration-manager 进行迭代改进

```
运行测试套件，分析覆盖率，并提出改进建议。
目标是达到 90% 以上的代码覆盖率。
```

### 示例 4: 使用 academic-writer 撰写论文

```
帮我撰写一篇关于深度学习在自然语言处理中应用的论文，
目标会议是 AAAI 2024。
```

## 技能触发条件

各技能会在以下情况下被自动加载:

| 技能 | 触发关键词 |
|-----|-----------|
| master-architect | 架构设计, 系统设计, 模块分解, 项目规划 |
| python-project-developer | Python 项目, CLI 工具, GUI 应用, PyPI 发布 |
| software-planner | 开发计划, 项目规划, 接口设计 |
| iteration-manager | 迭代测试, 质量改进, 覆盖率, 测试套件 |
| academic-writer | 论文, 学术, AAAI, IEEE, 文献 |

## 手动加载技能

在 OpenCode 中，技能会自动加载。你也可以通过描述来触发:

```
使用 python-project-developer 规范创建一个新的 Python 项目
```

## 技能输出规范

每个技能遵循特定的输出格式:

### master-architect 输出

```markdown
# 系统架构文档

## 1. 概述
[系统描述]

## 2. 高层设计
[架构图]

## 3. 模块分解
| 模块 | 职责 | 依赖 |
|-----|------|-----|

## 4. 接口契约
[API 定义]

## 5. 技术栈
| 层 | 技术 | 理由 |
|---|-----|-----|
```

### python-project-developer 输出

```python
# 项目结构
project/
├── package_name/
│   ├── __init__.py
│   ├── core.py
│   ├── cli.py
│   └── api.py
├── tests/
├── pyproject.toml
└── README.md

# API 模式
@dataclass
class ToolResult:
    success: bool
    data: Any = None
    error: Optional[str] = None
    metadata: dict = field(default_factory=dict)
```

## 命令行管理

### 列出已安装技能

```bash
python3 install-opencode.py list
```

### 查看技能详情

```bash
python3 install-opencode.py info master-architect
```

### 卸载技能

```bash
python3 install-opencode.py uninstall skill-name
```

### 安装特定技能

```bash
python3 install-opencode.py install --skills master-architect python-project-developer
```

## 项目级安装

如果只想在当前项目使用技能:

```bash
python3 install-opencode.py install --local
```

这会将技能安装到 `.opencode/skills/` 目录。

## 与其他工具集成

### 与 AGENTS.md 配合

在项目根目录创建 `AGENTS.md`:

```markdown
# Project Instructions

本项目使用 cycleuser/Skills 规范进行开发。

## 开发规范
- 遵循 python-project-developer 的 CLI 参数标准
- 使用 ToolResult 模式作为 API 返回类型
- 测试覆盖率要求 80% 以上
```

### CI/CD 集成

```yaml
# .github/workflows/skills.yml
name: Install Skills
on: [push]
jobs:
  install:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Install Skills
        run: |
          curl -sSL https://raw.githubusercontent.com/cycleuser/Skills/main/quick-install-opencode.sh | bash
```

## 故障排除

### 技能未加载

1. 确认安装目录正确: `~/.config/opencode/skills/`
2. 检查 SKILL.md 文件存在
3. 验证 frontmatter 格式正确

### 权限问题

```bash
chmod +x quick-install-opencode.sh
```

### 重新安装

```bash
python3 install-opencode.py uninstall --skills all
python3 install-opencode.py install
```

## 更多资源

- [GitHub 仓库](https://github.com/cycleuser/Skills)
- [OpenCode 文档](https://opencode.ai/docs/skills/)
- [问题反馈](https://github.com/cycleuser/Skills/issues)