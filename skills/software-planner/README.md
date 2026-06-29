# 软件规划器

## 状态：Beta

## 用途
综合软件开发规划与实施技能，支持CLI/PySide6 GUI/Flask Web多界面Python应用，集成学术研究驱动的功能设计。

## 快速命令
| 命令 | 说明 |
|------|------|
| `/planner research <topic>` | 领域研究与文献调研 |
| `/planner design <project>` | 系统架构设计 |
| `/planner modules` | 生成模块规格 |
| `/planner docs` | 创建双语文档 |
| `/planner verify` | 运行验证清单 |

## 适用场景
- 新建科学计算或工程类Python应用
- 需要学术文献支撑的功能设计
- 多界面（CLI+GUI+Web）统一规划
- 双语README及PyPI发布准备

## 依赖
- 依赖 _shared/core/safety-rules.md

## 参见
- python-project-developer — 将规划转为脚手架实现
- master-architect — 更细粒度的架构分解
- coding-agent-patterns — 多界面集成模式

## 文件结构
```
skills/software-planner/
├── README.md
├── SKILL.md
└── rules/
    ├── pre-development.md
    ├── interface-design.md
    ├── documentation.md
    └── sample-data.md
```
