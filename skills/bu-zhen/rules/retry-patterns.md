# Retry Patterns — 委派错误检测与修复提示

9 种常见 `task()` 委派错误及其检测模式与修复提示。orchestrator 委派失败时,按此表诊断并给 subagent 精确的修复指令。

## 9 种错误模式

| 错误类型 | 检测模式(错误消息含) | 修复提示 |
|---------|---------------------|---------|
| `missing_run_in_background` | `run_in_background` | 加 `run_in_background=true`(标准派发)或 `run_in_background=false`(短任务且结果门控下一调用) |
| `missing_load_skills` | `load_skills` | 加 `load_skills=[]` 参数(无技能用空数组)。注意:调 Skill 工具不会填充此参数。 |
| `mutual_exclusion` | `category OR subagent_type` | 仅提供其一:`category`(如 'general'、'quick')或 `subagent_type`(如 'oracle'、'explore') |
| `missing_category_or_agent` | `Must provide either category or subagent_type` | 加 `category='general'` 或 `subagent_type='explore'` |
| `unknown_category` | `Unknown category` | 用错误消息中 Available 列表里的合法 category |
| `empty_agent` | `Agent name cannot be empty` | 提供非空 `subagent_type` 值 |
| `unknown_agent` | `Unknown agent` | 用错误消息中 Available agents 列表里的合法 agent |
| `primary_agent` | `Cannot call primary agent` | 主 agent 不能用 task 调。用 subagent 如 'explore'、'oracle'、'librarian' |
| `unknown_skills` | `Skills not found` | 用错误消息中 Available 列表里的合法 skill 名 |

## 诊断流程

orchestrator 收到 `task()` 失败时:

1. 读错误输出
2. 按上表匹配模式(错误消息含检测模式字符串 → 命中错误类型)
3. 取对应修复提示
4. 用 `task_id` 恢复同会话,把修复提示作为新 prompt 的一部分:

```
task(
  task_id="ses_xyz",
  prompt="委派参数错误: {错误类型}。修复: {修复提示}。请按此调整后继续。"
)
```

## 重试指引构建

检测到错误后,构建重试指引含:

1. **修复提示**:上表对应行
2. **可用选项**:从错误消息的 Available 列表提取
3. **示例调用**:给出修正后的 `task()` 调用模板

示例(命中 `unknown_category`):

```
修复提示:用错误消息中 Available 列表里的合法 category
可用 category: general, quick, visual-engineering, ultrabrain
示例调用:
task(
  category="quick",
  load_skills=[],
  run_in_background=false,
  prompt="..."
)
```

## 为何用 task_id 重试而非新起

subagent 已读相关文件、知道试过什么。新起会话丢弃这些,多花约 3-4 倍 token。用 `task_id` 恢复保留上下文。

例外:subagent 在同一坏方法上循环(命中 doom-loop 检测)→ 起新 subagent,传失败尝试为上下文避免重复。

## 与安全硬化的关系

- 重试不绕过预算上限:重试仍计入 subagent 的 50k token / 10min 预算
- 重试不绕过 doom-loop:同参数重试 3 次仍触发暂停
- 重试不绕过路径白名单:修复后的调用仍经敏感目录与 PROJECT_ROOT 检查
- 错误检测本身不消耗 token(纯本地模式匹配)