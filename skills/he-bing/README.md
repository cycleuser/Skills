# 合并 (PR Lifecycle)

## 状态：Beta

## 用途
完整的 PR 生命周期管理技能。从 worktree 创建、功能实现、原子提交、PR 创建、CI/审查/批准的验证循环，到最终合并和清理，覆盖 PR 全流程。

## 快速命令
| 命令 | 说明 |
|------|------|
| `/合并 <任务>` | 启动完整 PR 工作流 |
| `/合并 create <任务>` | 创建 PR |
| `/合并 check` | 检查验证状态 |
| `/合并 status` | 查看 PR 状态 |
| `/pr <task>` | 英文版 PR 工作流 |

## 适用场景
- 实现功能并提交 PR
- 修复 Issue 并完成合并
- Worktree 隔离开发与自动清理
- CI + Code Review + Bot 审批的验证门禁

## 依赖
- 依赖 `_shared/core/safety-rules.md` 共享安全规则

## 参见
- [ba-guan](../ba-guan) — 合并前的发布前审查
- [master-architect](../master-architect) — 按阶段架构验证
- [zi-kong](../zi-kong) — 带自我审查的自主 PR 迭代

## 文件结构
```
skills/he-bing/
├── README.md
├── SKILL.md
└── rules/
    ├── worktree.md
    ├── commit-atomic.md
    ├── verification.md
    └── anti-aigc.md
```
