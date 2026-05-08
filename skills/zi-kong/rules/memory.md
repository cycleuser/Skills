# 跨会话记忆管理/Cross-Session Memory Management

## 状态文件格式/State File Format

### 文件路径

```
.zikong/state.json          # 当前状态
.zikong/snapshots/          # 快照目录
.zikong/decisions/          # 决策日志
.zikong/context/            # 压缩上下文
```

### state.json 完整结构

```json
{
  "version": "1.0",
  "goal": "string",
  "status": "INITIAL|RUNNING|PAUSED|DONE|ERROR|STOPPING",
  "loop_count": 0,
  "started_at": "ISO8601",
  "updated_at": "ISO8601",
  "progress": {
    "total_tasks": 0,
    "completed_tasks": 0,
    "completion_pct": 0.0,
    "current_task": "string|null"
  },
  "budget": {
    "time_remaining_sec": 0,
    "tokens_remaining": 0,
    "tier": "session|standard|deep|enlightenment"
  },
  "context_window": {
    "used_tokens": 0,
    "max_tokens": 0,
    "compression_count": 0
  },
  "perception": {},
  "decision": {},
  "result": {},
  "review": {},
  "errors": [],
  "checkpoints": []
}
```

## 检查点命名规范/Checkpoint Naming

### 命名格式

```
checkpoint_{loop_number}_{status}_{timestamp}.json
```

### 示例

```
checkpoint_001_initial_20260509T143000.json
checkpoint_005_fix_security_20260509T150000.json
checkpoint_010_refactor_api_20260509T163000.json
checkpoint_015_complete_20260509T180000.json
```

### 快照命名规范

```
snapshot_loop_{n}.json       # 每 5 轮自动快照
snapshot_pre_refactor.json   # 重构前快照
snapshot_pre_delete.json      # 删除前快照
snapshot_rollback_{n}.json   # 回滚点快照
```

### 检查点内容

```json
{
  "checkpoint_id": "chk_001",
  "loop_number": 5,
  "timestamp": "ISO8601",
  "status": "before_refactor",
  "files_state": {
    "created": ["file1.py"],
    "modified": ["file2.py"],
    "deleted": []
  },
  "git_state": {
    "branch": "string",
    "last_commit": "string",
    "uncommitted_changes": ["string"]
  },
  "test_state": {
    "passed": 0,
    "failed": 0,
    "coverage_pct": 0.0
  }
}
```

## 上下文压缩策略/Context Compression

### 触发条件

```
当 context_window.used_tokens > 70% * max_tokens 时触发压缩
```

### 压缩层次

```
┌────────────────────────────────────────────────────────────┐
│  Level 1: 摘要压缩                                         │
│  将对话历史压缩为摘要，保留关键决策和结果                      │
│  压缩比: ~5:1                                              │
│                                                            │
│  Level 2: 结构化压缩                                       │
│  只保留决策树、结果、关键文件变更摘要                          │
│  压缩比: ~10:1                                             │
│                                                            │
│  Level 3: 最小压缩                                         │
│  只保留目标、最终状态、未完成任务列表                          │
│  压缩比: ~20:1                                             │
└────────────────────────────────────────────────────────────┘
```

### Level 1 摘要压缩模板

```json
{
  "compression_level": 1,
  "compressed_at": "ISO8601",
  "original_loops": [1, 2, 3],
  "summary": "修复了3个安全漏洞（ANJ-001至ANJ-003），重构了API模块，测试覆盖率从65%提升到82%",
  "key_decisions": [
    {"loop": 1, "decision": "fix", "reason": "critical security issue"},
    {"loop": 2, "decision": "refactor", "reason": "API module coupling"}
  ],
  "key_results": [
    {"loop": 1, "result": "security fixes applied"},
    {"loop": 3, "result": "coverage improved to 82%"}
  ],
  "errors_encountered": ["loop 2: refactor conflict, resolved by rollback"]
}
```

### Level 2 结构化压缩模板

```json
{
  "compression_level": 2,
  "compressed_at": "ISO8601",
  "goal": "string",
  "progress": "82% complete",
  "decision_tree": {
    "loop_1": {"action": "fix", "target": "security", "result": "success"},
    "loop_3": {"action": "refactor", "target": "API", "result": "success"}
  },
  "pending_tasks": ["optimize database queries", "add integration tests"],
  "blocked_tasks": [],
  "current_state": {"files_changed": 5, "tests_passing": 42}
}
```

### Level 3 最小压缩模板

```json
{
  "compression_level": 3,
  "compressed_at": "ISO8601",
  "goal": "string",
  "status": "RUNNING",
  "progress_pct": 82,
  "last_completed": "refactor API module",
  "next_task": "optimize database queries",
  "budget_remaining": {"time_pct": 45, "tokens_pct": 35}
}
```

## 记忆修剪策略/Memory Pruning Strategies

### 修剪规则

```
规则1: 成功完成的低优先级任务，1轮后可修剪
规则2: 成功完成的高优先级任务，3轮后压缩为摘要
规则3: 失败的任务保留完整记录直到修复成功
规则4: 错误日志保留最近5条，更早的压缩为统计
规则5: 感知数据在决策后立即修剪，只保留决策相关的
```

### 修剪优先级

```
P0 保留: 当前任务上下文、未完成目标、活跃决策树
P1 保留: 最近5轮完整记录、关键错误日志
P2 压缩: 5-10轮压缩为摘要、普通错误压缩为统计
P3 丢弃: 10轮以上非关键感知数据、重复的中间状态
```

### 文件状态增量记录

```json
{
  "file_changes": {
    "created_this_session": ["src/api.py"],
    "modified_this_session": ["src/config.py", "tests/test_api.py"],
    "deleted_this_session": [],
    "rollback_available": true,
    "snapshot_every_n_loops": 5
  }
}
```

## 跨会话恢复/Cross-Session Recovery

### 恢复流程

```
1. 读取 state.json，恢复状态和进度
2. 读取最近快照，恢复文件变更记录
3. 读取决策日志，理解已完成决策
4. 读取压缩上下文，恢复关键信息
5. 基于恢复的状态继续迭代
```

### 恢复检查清单

```json
{
  "recovery_checks": [
    "state.json exists and valid",
    "goal matches previous session",
    "budget has remaining allocation",
    "no unresolved conflicts in workspace",
    "tests passing from last checkpoint"
  ]
}
```