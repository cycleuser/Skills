# 项目重建 (Project Rebuilder)

## 状态：Beta

## 用途
参考现有开源项目从零重写核心功能的技能。采用 team 并行审查（架构师/开发者/测试员）和 ralph 跨会话持久执行两种工作模式，确保重建质量。

## 快速命令
| 命令 | 说明 |
|------|------|
| `/rebuild <参考项目> <目标>` | 启动项目重建 |
| `/rebuild analyze <项目>` | 分析参考项目 |
| `/rebuild team` | 启动团队并行审查 |
| `/rebuild ralph` | 启动跨会话持久执行 |
| `/rebuild checkpoint` | 查看或恢复检查点 |
| `/rebuild status` | 查看重建进度 |

## 适用场景
- 参考开源项目重写核心功能
- 从零构建类似产品
- 深层重构现有项目
- 多角色并行代码审查与质量保证

## 依赖
- 依赖 `_shared/core/safety-rules.md` 共享安全规则

## 参见
- [master-architect](../master-architect) — 参考项目架构分析
- [iteration-manager](../iteration-manager) — 重建组件迭代测试
- [python-project-developer](../python-project-developer) — 项目结构搭建

## 文件结构
```
skills/project-rebuilder/
├── README.md
├── SKILL.md
└── rules/
    ├── project-analysis.md
    ├── team-review.md
    ├── ralph-execution.md
    ├── checkpoint.md
    └── anti-aigc.md
```
