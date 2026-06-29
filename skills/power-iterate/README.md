# 强力迭代器

## 状态：Beta

## 用途
全自主持续迭代技能，自动理解需求、设计评估方案、规划迭代路径并自主执行直到时间或 Token 预算耗尽。无需用户确认即可完成从需求到交付的全流程开发。

## 快速命令
| 命令 | 说明 |
|------|------|
| `/强力迭代 <任务> [预算]` | 启动全自主强力迭代 |
| `/power-iterate <task> [budget]` | 启动强力迭代（英文） |

## 适用场景
- 需要全自主开发、不需要用户干预的长任务
- 明确时间或 Token 预算约束的迭代工作
- 从一句话需求到完整交付的端到端开发
- 多轮迭代的代码质量提升

## 依赖
- 依赖 _shared/core/safety-rules.md

## 参见
- `/修仙` from **sleepless** — 不眠不休长时间迭代执行
- `/自控` from **zi-kong** — 跨会话记忆的长周期迭代
- `/iterate` from **iteration-manager** — 迭代中的质量指标追踪

## 文件结构
```
skills/power-iterate/
├── README.md
├── SKILL.md
└── rules/
    ├── task-decomposition.md
    ├── autonomous-loop.md
    ├── budget-manager.md
    └── anti-aigc.md
```
