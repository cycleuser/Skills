# 预算管理规则

## 预算类型

### 时间预算

| 级别 | 分钟数 | 适用场景 |
|-----|-------|---------|
| `tiny` | 10 | 快速验证、最小可用版本 |
| `small` | 30 | 小功能、单一模块 |
| `medium` | 60 | 中等项目、一个完整功能 |
| `large` | 120 | 大项目、多个功能 |
| `xlarge` | 240 | 超大项目、完整系统 |

### Token预算

| 级别 | Token数 | 适用场景 |
|-----|--------|---------|
| `tiny` | 20,000 | 简单任务 |
| `small` | 50,000 | 标准任务 |
| `medium` | 100,000 | 中等复杂度 |
| `large` | 200,000 | 复杂项目 |
| `xlarge` | 500,000 | 超大项目 |

### 综合预算

```yaml
budget_levels:
  tiny:   {time: 10,  tokens: 20000}
  small:  {time: 30,  tokens: 50000}
  medium: {time: 60,  tokens: 100000}
  large:  {time: 120, tokens: 200000}
  xlarge: {time: 240, tokens: 500000}
```

## 预算追踪

### 初始化

```python
class BudgetTracker:
    def __init__(self, time_limit=None, token_limit=None, budget_level=None):
        self.time_limit = time_limit or 60  # minutes
        self.token_limit = token_limit or 100000
        self.time_consumed = 0
        self.tokens_consumed = 0
        self.start_time = now()
        self.checkpoints = []
```

### 更新消耗

```python
def update(self, time_delta, tokens_delta):
    self.time_consumed += time_delta
    self.tokens_consumed += tokens_delta
    self.checkpoints.append({
        "time": self.time_consumed,
        "tokens": self.tokens_consumed,
        "timestamp": now()
    })
```

### 状态查询

```python
def status(self):
    time_pct = self.time_consumed / self.time_limit * 100
    token_pct = self.tokens_consumed / self.token_limit * 100
    time_remaining = self.time_limit - self.time_consumed
    token_remaining = self.token_limit - self.tokens_consumed
    
    return {
        "time": {
            "consumed": self.time_consumed,
            "limit": self.time_limit,
            "remaining": time_remaining,
            "percent": time_pct
        },
        "tokens": {
            "consumed": self.tokens_consumed,
            "limit": self.token_limit,
            "remaining": token_remaining,
            "percent": token_pct
        },
        "healthy": time_pct < 80 and token_pct < 85,
        "warning": time_pct >= 80 or token_pct >= 85,
        "critical": time_pct >= 95 or token_pct >= 90
    }
```

## 决策阈值

### 阈值表

| 状态 | 时间% | Token% | 行为 |
|-----|-------|--------|-----|
| `HEALTHY` | < 70% | < 75% | 全速执行 |
| `NORMAL` | 70-85% | 75-85% | 正常执行 |
| `WARNING` | 85-95% | 85-95% | 减速，检查质量 |
| `CRITICAL` | > 95% | > 95% | 立即终止 |
| `TOKEN_WARNING` | any | > 85% | Token优先控制 |

### 行为响应

**HEALTHY**:
- 全速执行任务
- 每5个任务检查一次
- 正常日志级别

**NORMAL**:
- 正常执行
- 每3个任务检查一次
- 详细日志

**WARNING**:
- 减速执行
- 每个任务后检查
- 评估是否继续P1/P2
- 准备终止报告

**CRITICAL**:
- 立即停止新任务
- 完成当前验证
- 保存所有进度
- 生成最终报告

**TOKEN_WARNING**:
- 减少冗余输出
- 合并多个小任务
- 跳过不必要的文档

## 预算节省策略

### 时间节省

1. 跳过重复验证
2. 减少日志输出
3. 批量处理小任务
4. 跳过非关键文档

### Token节省

1. 简洁的代码风格
2. 最小化注释
3. 合并文件操作
4. 跳过详细解释

### 节省级别

| 级别 | 触发条件 | 节省策略 |
|-----|---------|---------|
| `NORMAL` | - | 默认策略 |
| `LIGHT` | 时间>80% | 减少日志 |
| `MODERATE` | 时间>90% | 跳过文档 |
| `AGGRESSIVE` | Token>90% | 最小化输出 |

## 终止处理

### 终止检查清单

- [ ] 停止接受新任务
- [ ] 完成当前任务验证
- [ ] 保存所有修改文件
- [ ] 生成进度报告
- [ ] 生成待办清单
- [ ] 计算效率评分

### 效率评分

```python
def efficiency_score(completed, total, time_pct, token_pct):
    completion_rate = completed / total * 100
    time_efficiency = 100 - time_pct
    token_efficiency = 100 - token_pct
    
    # 加权平均
    score = (
        completion_rate * 0.5 +
        time_efficiency * 0.25 +
        token_efficiency * 0.25
    )
    
    return min(100, score)
```

### 评分等级

| 等级 | 分数 | 说明 |
|-----|-----|-----|
| `S` | 95+ | 卓越，超额完成 |
| `A` | 85-94 | 优秀，高效完成 |
| `B` | 70-84 | 良好，完成大部分 |
| `C` | 50-69 | 一般，完成一半 |
| `D` | < 50 | 未达标，需改进 |

## 报告生成

### 实时报告模板

```markdown
## 强力迭代进度报告

**时间**: {current_time} / {limit_time} ({time_pct}%)
**Token**: {current_tokens:,} / {limit_tokens:,} ({token_pct}%)
**进度**: {progress_bar} {completed}/{total} ({completion_pct}%)

### 状态: {status}

### 已完成
{completed_list}

### 进行中
{current_task}

### 待处理
{pending_list}

### 预算健康度: {health_status}
```

### 最终报告模板

```markdown
## 强力迭代最终报告

**会话ID**: {session_id}
**开始时间**: {start_time}
**结束时间**: {end_time}
**总耗时**: {total_time}分钟
**总Token**: {total_tokens:,}

### 完成度: {completion_rate}%

**已完成**: {completed_count}个任务
**跳过**: {skipped_count}个任务
**失败**: {failed_count}个任务

### 效率评分: {score} ({grade})

### 已产出文件
{file_list}

### 未完成任务
{unfinished_list}

### 下一步建议
{recommendations}
```
