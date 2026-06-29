# 自控 (Self-Controlled Iteration)

## 状态：Beta

## 用途
真正的自主迭代技能，控制 opencode 自身实现持续自我改进。支持感知-决策-执行-审查的自主循环、跨会话记忆恢复、预算控制、回滚机制，适用于长期自主任务。

## 快速命令
| 命令 | 说明 |
|------|------|
| `/自控 <目标>` | 启动自主迭代 |
| `/自控 status` | 查看迭代状态 |
| `/自控 pause` | 暂停迭代 |
| `/自控 resume` | 恢复迭代 |
| `/自控 log` | 查看迭代日志 |
| `/auto <goal>` | 英文版自主迭代 |

## 适用场景
- opencode 自身技能持续改进
- 长期任务的跨会话自主执行
- 多技能并行迭代优化
- 带安全回滚的自主代码修改

## 依赖
- 依赖 `_shared/core/safety-rules.md` 共享安全规则

## 参见
- [sleepless](../sleepless) — 不眠不休执行，适用于扩展的自控会话
- [power-iterate](../power-iterate) — 预算管理的迭代框架
- [skill-refiner](../skill-refiner) — 将自控改进能力应用于其他技能

## 文件结构
```
skills/zi-kong/
├── README.md
├── SKILL.md
└── rules/
    ├── autonomous-loop.md
    ├── memory.md
    ├── budget.md
    ├── safety.md
    ├── self-review.md
    └── anti-aigc.md
```
