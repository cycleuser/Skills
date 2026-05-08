# 预算管理/Budget Management

## 预算层级/Budget Tiers

```
┌────────────────────────────────────────────────────────────────┐
│  层级/Tier       时间/Time      Tokens      用途/Use Case      │
├────────────────────────────────────────────────────────────────┤
│  session         15 min         50K         快速修复、小改动      │
│  standard        1 hour         200K        常规功能开发          │
│  deep            4 hours        800K        大型重构、多模块       │
│  enlightenment   8 hours        2M          全项目重写、从零构建    │
└────────────────────────────────────────────────────────────────┘
```

### 默认预算分配/Default Budget Allocation

```json
{
  "session": {
    "time_sec": 900,
    "tokens": 50000,
    "max_loops": 10,
    "allocation": {
      "perceive": 0.10,
      "decide": 0.05,
      "execute": 0.55,
      "review": 0.15,
      "save": 0.05,
      "overhead": 0.10
    }
  },
  "standard": {
    "time_sec": 3600,
    "tokens": 200000,
    "max_loops": 50,
    "allocation": {
      "perceive": 0.10,
      "decide": 0.05,
      "execute": 0.55,
      "review": 0.15,
      "save": 0.05,
      "overhead": 0.10
    }
  },
  "deep": {
    "time_sec": 14400,
    "tokens": 800000,
    "max_loops": 200,
    "allocation": {
      "perceive": 0.08,
      "decide": 0.05,
      "execute": 0.57,
      "review": 0.15,
      "save": 0.05,
      "overhead": 0.10
    }
  },
  "enlightenment": {
    "time_sec": 28800,
    "tokens": 2000000,
    "max_loops": 500,
    "allocation": {
      "perceive": 0.08,
      "decide": 0.05,
      "execute": 0.57,
      "review": 0.17,
      "save": 0.05,
      "overhead": 0.08
    }
  }
}
```

## 预算管理器/Budget Manager

```python
class BudgetManager:
    def __init__(self, config: dict):
        self.tier = config.get("tier", "standard")
        self.time_budget = config.get("time_sec", TIERS[self.tier]["time_sec"])
        self.token_budget = config.get("tokens", TIERS[self.tier]["tokens"])
        self.max_loops = config.get("max_loops", TIERS[self.tier]["max_loops"])
        self.time_start = time.time()
        self.tokens_used = 0
        self.loops_used = 0

    def check(self, decision: dict) -> bool:
        """检查预算是否足够执行决策"""
        remaining_time = self.time_budget - (time.time() - self.time_start)
        remaining_tokens = self.token_budget - self.tokens_used

        est_time = decision.get("estimated_time", 5)
        est_tokens = decision.get("estimated_tokens", 5000)

        if remaining_time < est_time * 1.2:
            return False
        if remaining_tokens < est_tokens * 1.2:
            return False
        if self.loops_used >= self.max_loops:
            return False
        return True

    def get_status(self) -> str:
        """返回预算状态: OK|LOW|CRITICAL|EXHAUSTED"""
        time_pct = (time.time() - self.time_start) / self.time_budget
        token_pct = self.tokens_used / self.token_budget
        max_resource = max(time_pct, token_pct)

        if max_resource >= 0.95:
            return "EXHAUSTED"
        elif max_resource >= 0.80:
            return "CRITICAL"
        elif max_resource >= 0.60:
            return "LOW"
        return "OK"
```

## 自动修剪策略/Auto-Trimming When Approaching Limits

### 触发阈值

```
┌────────────────────────────────────────────────────────────────┐
│  状态/Status     时间/Time      Tokens      触发动作/Action     │
├────────────────────────────────────────────────────────────────┤
│  OK             < 60%          < 60%       正常运行             │
│  LOW            60-80%         60-80%      开始修剪非核心任务    │
│  CRITICAL       80-95%         80-95%      只执行 P0 任务        │
│  EXHAUSTED      >= 95%         >= 95%      立即收尾，保存状态    │
└────────────────────────────────────────────────────────────────┘
```

### LOW 阶段修剪规则

```python
def trim_low_priority(self, perception: dict) -> dict:
    """LOW 阶段：修剪非核心任务"""
    trimmed = {
        "skip_P2_tasks": True,        # 跳过 P2 优化任务
        "reduce_review_depth": True,    # 减少审查深度
        "compress_context": True,       # 压缩上下文
        "skip_optional_checks": True,   # 跳过可选检查
    }
    return trimmed
```

### CRITICAL 阶段修剪规则

```python
def trim_critical(self, perception: dict) -> dict:
    """CRITICAL 阶段：只执行 P0 任务"""
    trimmed = {
        "only_P0_tasks": True,         # 只执行 P0 任务
        "minimal_review": True,         # 最小审查
        "max_context_compression": True, # 最大压缩
        "skip_all_optional": True,      # 跳过所有可选步骤
        "prepare_wrap_up": True,        # 准备收尾
    }
    return trimmed
```

### EXHAUSTED 阶段处理

```python
def handle_exhausted(self) -> dict:
    """EXHAUSTED 阶段：立即收尾保存"""
    return {
        "action": "emergency_save",
        "save_state": True,
        "save_snapshot": True,
        "write_progress_report": True,
        "create_recovery_point": True,
        "message": "Budget exhausted. State saved for recovery."
    }
```

## 预算分配示例/Budget Allocation Examples

### 修复单个安全漏洞（session 层级）

```
总预算: 15min / 50K tokens / 10 轮

感知: 1.5min / 5K tokens    (10%) - 扫描问题
决策: 0.75min / 2.5K tokens (5%)  - 确定修复方案
执行: 8.25min / 27.5K tokens (55%) - 实施修复
审查: 2.25min / 7.5K tokens  (15%) - 验证修复
保存: 0.75min / 2.5K tokens  (5%)  - 保存状态
余量: 1.5min / 5K tokens    (10%)  - 应急
```

### 开发新功能（standard 层级）

```
总预算: 1h / 200K tokens / 50 轮

感知: 6min / 20K tokens    (10%) - 分析需求和环境
决策: 3min / 10K tokens    (5%)  - 规划实现路径
执行: 33min / 110K tokens   (55%) - 编写代码和测试
审查: 9min / 30K tokens     (15%) - 代码审查和测试
保存: 3min / 10K tokens     (5%)  - 保存进度
余量: 6min / 20K tokens     (10%) - 应急和意外
```

### 大型重构（deep 层级）

```
总预算: 4h / 800K tokens / 200 轮

前50%: 理解代码库、识别重构点、建立测试基线
中间30%: 逐模块重构、运行测试、修复问题
后20%: 集成测试、性能验证、文档更新
```