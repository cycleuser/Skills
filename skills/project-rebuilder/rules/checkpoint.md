# Checkpoint 保存与恢复

## Checkpoint 目录结构

```
.project-rebuilder/
├── checkpoints/
│   ├── session_001/
│   │   ├── checkpoint_001.json
│   │   ├── checkpoint_002.json
│   │   └── ...
│   └── session_002/
│       └── ...
├── reviews/
│   ├── review_001.md
│   └── ...
└── reports/
    ├── analysis_report.md
    └── progress_report.md
```

## 保存策略

### 自动保存

| 触发条件 | 保存内容 |
|---------|---------|
| 每 30 分钟 | 完整 Checkpoint |
| 完成任务后 | 进度更新 |
| 会话结束前 | 完整 Checkpoint |

### 手动保存

```
/rebuild checkpoint [名称]

示例:
/rebuild checkpoint after_core_module
```

## Checkpoint 内容

```json
{
  "meta": {
    "id": "ckpt_001",
    "session": "session_001",
    "created_at": "2024-01-01T12:00:00Z",
    "version": "1.0"
  },
  "project": {
    "name": "项目名称",
    "reference": "参考项目 URL",
    "goal": "重建目标"
  },
  "state": {
    "phase": "analysis/planning/review/execution",
    "iteration": 1,
    "completed": [],
    "in_progress": null,
    "pending": [],
    "skipped": []
  },
  "context": {
    "assumptions": [],
    "decisions": [],
    "issues": [],
    "files_created": [],
    "files_modified": []
  },
  "next_action": "下一步行动描述"
}
```

## 恢复命令

```
/rebuild restore [checkpoint_id]

示例:
/rebuild restore ckpt_003
/rebuild restore latest  # 恢复最新 Checkpoint
```

## 恢复确认

恢复前显示摘要：

```markdown
## 恢复确认

**Checkpoint**: ckpt_003
**创建时间**: 2024-01-01 15:30
**会话**: session_001

### 进度摘要
- 已完成：5/15 任务
- 进行中：任务 0.3 (50%)
- 待执行：10 任务

### 待解决问题
- [ ] 问题 A：描述
- [ ] 问题 B：描述

### 下一步行动
1. 完成任务 0.3
2. 开始任务 0.4
3. 运行测试

确认恢复？[Y/n]
```

## 状态迁移

```
INITIAL → ANALYZING → PLANNING → REVIEWING → EXECUTING → COMPLETED
    ↓          ↓           ↓           ↓           ↓          ↓
  save     save       save       save       save      save
```

## 过期清理

```bash
# 清理 7 天前的 Checkpoint
find .project-rebuilder/checkpoints -mtime +7 -delete

# 保留最近 3 个 Checkpoint 每会话
ls -t session_*/checkpoint_*.json | tail -n +4 | xargs rm
```