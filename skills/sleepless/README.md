# 修仙 (Sleepless)

## 状态：Beta

## 用途
不眠不休的自主执行技能。永不主动停止，直到任务 100% 完成。具备错误自愈、路径切换、降级兜底和跨会话持久化能力，适合长时间无人值守的 AI 开发任务。

## 快速命令
| 命令 | 说明 |
|------|------|
| `/修仙 <任务>` | 启动修仙执行 |
| `/修仙 <任务> --budget <级别>` | 指定预算级别启动 |
| `/修仙 status` | 查看修仙状态 |
| `/修仙 log` | 查看修仙日志 |
| `/sleepless <task>` | 启动英文版执行 |
| `/sleepless status` | 查看状态（英文） |

## 适用场景
- 长时间自主开发任务（通宵/周末/闭关）
- 无人值守的 AI 持续执行
- 需要强制交付的最低可行版本产出
- 跨会话的持久化任务推进
- 错误自愈、路径自动切换的容错场景

## 依赖
- 依赖 `_shared/core/safety-rules.md` 共享安全规则

## 参见
- [power-iterate](../power-iterate) — 带预算管理的持续迭代
- [zi-kong](../zi-kong) — 跨会话上下文持久化

## 文件结构
```
skills/sleepless/
├── README.md
├── SKILL.md
└── rules/
    ├── autonomous-loop.md
    ├── eternal-drive.md
    ├── task-omnipotence.md
    └── anti-aigc.md
```
