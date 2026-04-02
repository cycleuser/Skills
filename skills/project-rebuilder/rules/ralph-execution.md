# 持久执行机制 (RALPH)

## RALPH 含义

**R**ecursive **A**utonomous **L**ong-term **P**ersistent **H**elper

递归自主长期持久助手

## 核心特性

### 1. 跨会话记忆

```json
{
  "session_id": "session_001",
  "project": "项目名称",
  "memory": {
    "completed": ["任务 1", "任务 2"],
    "in_progress": "任务 3",
    "pending": ["任务 4", "任务 5"],
    "context": {
      "assumptions": [...],
      "decisions": [...],
      "issues": [...]
    }
  }
}
```

### 2. Checkpoint 机制

```
执行 30 分钟 → 自动保存 Checkpoint → 继续执行 → 自动保存...

手动保存点：
- 完成重要任务后
- 遇到重大问题需要思考时
- 会话结束前
```

### 3. 状态恢复

```
新会话开始 → 检测 Checkpoint → 加载上下文 → 继续执行

恢复内容：
- 已完成任务清单
- 当前任务状态
- 假设与决策
- 问题与解决方案
- 下一步计划
```

## 执行循环

```
┌─────────────────────────────────────────────────────────────┐
│                    RALPH 执行循环                            │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌────────┐│
│  │ 获取任务  │───▶│ 执行任务  │───▶│ 验证结果 │───▶│ 保存   ││
│  │          │    │          │    │          │    │ 进度   ││
│  └──────────┘    └──────────┘    └──────────┘    └────┬───┘│
│       ▲                                               │    │
│       │              ┌──────────┐                     │    │
│       └──────────────│ 有新任务？│◀────────────────────┘    │
│                      └──────────┘                          │
│                           │                                 │
│                      YES  │  NO                            │
│                       ┌───┴───┐                            │
│                       ▼       ▼                            │
│                  [继续循环] [完成]                          │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## 执行规则

### 规则 1：自主决策

```
遇到选择时：

1. 有明确最佳实践？
   → 使用最佳实践

2. 有多种合理选择？
   → 选择最主流/最简单的，记录决策理由

3. 无法决定？
   → 选择最安全的，标注 [待确认]

4. 需要外部资源？
   → 先用 mock/placeholder，后续替换
```

### 规则 2：错误处理

```
遇到错误时：

1. 可自动修复？
   → 尝试修复（最多 2 次）

2. 需要用户决策？
   → 记录问题，继续其他任务

3. 阻塞后续任务？
   → 标记依赖任务为 [已跳过]
```

### 规则 3：进度报告

```
每 30 分钟报告一次：

## 进度报告

**时间**: {elapsed}/{budget}
**进度**: {completed}/{total}

**已完成**:
- ✅ {任务 1}
- ✅ {任务 2}

**进行中**:
- 🔄 {当前任务}

**待执行**:
- ⏳ {任务 3}

**问题**:
- ⚠️ {问题描述}
```

## Checkpoint 格式

```json
{
  "checkpoint_id": "ckpt_001",
  "timestamp": "2024-01-01T12:00:00Z",
  "session": "session_001",
  "project": {
    "name": "项目名称",
    "goal": "重建目标",
    "reference": "参考项目"
  },
  "progress": {
    "completed_tasks": [
      {"id": "0.1", "name": "任务名", "time": "30min"}
    ],
    "in_progress_task": {"id": "0.2", "name": "任务名", "progress": "50%"},
    "pending_tasks": [
      {"id": "0.3", "name": "任务名"}
    ],
    "skipped_tasks": [
      {"id": "1.1", "name": "任务名", "reason": "依赖失败"}
    ]
  },
  "context": {
    "assumptions": [
      {"id": 1, "content": "假设内容", "verified": true}
    ],
    "decisions": [
      {"id": 1, "content": "决策内容", "rationale": "理由"}
    ],
    "issues": [
      {"id": 1, "description": "问题", "solution": "方案", "status": "resolved"}
    ],
    "code_changes": [
      {"file": "path/to/file.py", "status": "created/modified"}
    ]
  },
  "next_steps": [
    "完成当前任务",
    "开始任务 0.3",
    "验证功能"
  ],
  "metrics": {
    "time_elapsed": "90min",
    "time_budget": "180min",
    "completion_rate": "60%"
  }
}
```

## 会话恢复

### 恢复流程

```
1. 检测 Checkpoint 文件
2. 加载 Checkpoint 内容
3. 显示恢复摘要
4. 确认恢复点
5. 继续执行
```

### 恢复摘要模板

```markdown
## 会话恢复

**找到 Checkpoint**: {checkpoint_id}
**创建时间**: {timestamp}
**项目**: {project_name}

### 上次进度

**已完成**: {completed_count}/{total_count}
**进行中**: {in_progress_task}

### 待执行任务

1. {pending_task_1}
2. {pending_task_2}

### 待解决问题

- [ ] {issue_1}
- [ ] {issue_2}

是否从此 Checkpoint 恢复？[Y/n]
```