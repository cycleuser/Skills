# Python项目开发器

## 状态：Beta

## 用途
完整的Python多项目开发规范，涵盖CLI/GUI工具的统一API设计、OpenAI函数调用集成和PyPI发布全流程。

## 快速命令
| 命令 | 说明 |
|------|------|
| `/python-project init <name>` | 初始化新Python项目 |
| `/python-project structure` | 生成项目结构 |
| `/python-project api` | 实现ToolResult API模式 |
| `/python-project cli` | 添加CLI统一标志 |
| `/python-project test` | 生成测试套件 |
| `/python-project publish` | 配置PyPI发布 |

## 适用场景
- 新建Python CLI/GUI工具项目
- 建立ToolResult dataclass统一API
- 集成OpenAI函数调用（TOOLS + dispatch模式）
- 编写双语README和pytest测试

## 依赖
- 依赖 _shared/core/safety-rules.md

## 参见
- software-planner — 开发前期规划与研究
- coding-agent-patterns — ToolResult模式与代理集成
- iteration-manager — 迭代测试改进

## 文件结构
```
skills/python-project-developer/
├── README.md
├── SKILL.md
└── rules/
    ├── project-structure.md
    ├── cli-flags.md
    ├── api-pattern.md
    ├── tools-integration.md
    └── testing-guide.md
```
