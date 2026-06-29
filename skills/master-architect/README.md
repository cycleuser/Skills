# 主架构师

## 状态：Beta

## 用途
顶级软件架构代理，为复杂多阶段项目提供六阶段开发工作流，包含严格的质量门控和迭代精炼机制。

## 快速命令
| 命令 | 说明 |
|------|------|
| `/architect design <task>` | 完整架构设计 |
| `/architect phase <n>` | 执行指定阶段 (1-6) |
| `/architect iterate <module>` | 迭代开发指定模块 |
| `/architect status` | 查看当前架构状态 |
| `/architect review` | 审查和验证架构 |

## 适用场景
- 复杂多阶段项目的架构设计
- 需求分析与模块分解
- 建立质量门控确保交付标准
- 跨模块迭代开发与集成验证

## 依赖
- 依赖 _shared/core/safety-rules.md

## 参见
- python-project-developer — 架构完成后脚手架搭建
- iteration-manager — 模块质量迭代测试
- ba-guan — 发布前多层审查

## 文件结构
```
skills/master-architect/
├── README.md
├── SKILL.md
└── rules/
    ├── requirement-analysis.md
    ├── architecture-design.md
    ├── task-decomposition.md
    ├── iteration-protocol.md
    └── quality-gates.md
```
