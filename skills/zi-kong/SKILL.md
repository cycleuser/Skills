---
name: zi-kong
version: "1.0.0"
description: |
  Self-controlled autonomous iteration for opencode itself with cross-session memory and safe rollback.

  Triggers when: Needing opencode self-improvement, continuous skill iteration, or autonomous execution of long-running tasks.

  Commands:
  - /自控 <目标> - Start autonomous iteration
  - /自控 status - View iteration status
  - /自控 pause - Pause iteration
  - /自控 resume - Resume iteration
  - /自控 log - View iteration log
  - /auto <goal> - English command for autonomous iteration

  Capabilities: True autonomous while(true) loop, cross-session context persistence, self-review after each iteration, budget control with time/token management, parallel task handling, decision tree for autonomous choices, rollback mechanism for safe iteration
author: cycleuser
license: MIT
---

## Safety Rules

**Critical**: Read and follow [global-rules/bash-safety.md](file:///Users/fred/.config/opencode/skills/global-rules/rules/bash-safety.md) for all bash/command execution.

Core rules:
1. **Always set explicit `timeout` on bash calls** — 30s for tests, 60s for installs, never default
2. **Never run unscoped full test suites** — use `-k` or file paths to limit scope
3. **Never use `rm -rf` without variable guards**, `curl|bash`, `sudo`, or `kill -9`
4. **Infinite loops must have hard timeout + budget limits** — no unbounded while(True)
5. **Redirect stdin** with `< /dev/null` for non-interactive commands

A bash timeout that triggers SIGKILL corrupts the terminal FD, crashes opencode's TUI, and forces a GUI restart.

# 自控 (Self-Controlled Iteration)

真正的自主迭代技能。控制 opencode 自身，实现持续自我改进。
True autonomous iteration. Controls opencode itself for continuous self-improvement.

## Quick Commands

| 命令/Command | 功能/Function |
|-------------|--------------|
| `/自控 <目标>` | 启动自主迭代 |
| `/自控 status` | 查看迭代状态 |
| `/自控 pause` | 暂停迭代 |
| `/自控 resume` | 恢复迭代 |
| `/自控 log` | 查看迭代日志 |
| `/auto <goal>` | Start autonomous iteration |
| `/auto status` | Check iteration status |
| `/auto pause` | Pause iteration |
| `/auto resume` | Resume iteration |

## 核心架构/Core Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                    自控架构/Self-Control Architecture                │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                    自主循环/Autonomous Loop                    │  │
│  │  ┌────────┐   ┌────────┐   ┌────────┐   ┌────────┐          │  │
│  │  │ 感知   │──▶│ 决策   │──▶│ 执行   │──▶│ 审查   │──┐       │  │
│  │  │Perceive│   │Decide  │   │Execute │   │Review  │  │       │  │
│  │  └────────┘   └────────┘   └────────┘   └────────┘  │       │  │
│  │       ▲                                              │       │  │
│  │       └──────────────────────────────────────────────┘       │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                    持久化层/Persistence Layer                  │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐     │  │
│  │  │ 状态存储  │  │ 决策日志  │  │ 回滚快照  │  │ 预算追踪  │     │  │
│  │  │  State   │  │  Decision│  │ Snapshot │  │  Budget  │     │  │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘     │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                    安全层/Safety Layer                        │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐     │  │
│  │  │ 变更审查  │  │ 回滚机制  │  │ 预算限制  │  │ 用户确认  │     │  │
│  │  │  Review  │  │ Rollback │  │  Limit   │  │ Confirm  │     │  │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘     │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

## 自主循环/Autonomous Loop

### 循环状态机/Loop State Machine

```
┌─────────────────────────────────────────────────────────────────────┐
│                    状态机/State Machine                              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│     ┌─────────┐                                                     │
│     │ INITIAL │                                                     │
│     └────┬────┘                                                     │
│          │ start                                                    │
│          ▼                                                          │
│     ┌─────────┐                                                     │
│     │ RUNNING │◀────────────────────┐                               │
│     └────┬────┘                     │                               │
│          │                          │ loop                          │
│          │ decide                 ┌─┴─────┐                         │
│          ▼                        │       │                         │
│     ┌─────────┐                  YES      NO                        │
│     │PERCEIVE │                   │       │                         │
│     └────┬────┘                   │       │                         │
│          │                        │       │                         │
│          ▼                        │       │                         │
│     ┌─────────┐                  ┌┴───────▼────────┐               │
│     │ DECIDE  │                  │   CONTINUE?     │               │
│     └────┬────┘                  └─────────────────┘               │
│          │                                                         │
│          ▼                                                         │
│     ┌─────────┐     ┌─────────┐     ┌─────────┐                   │
│     │ EXECUTE │────▶│  REVIEW │────▶│  SAVE   │                   │
│     └─────────┘     └─────────┘     └────┬────┘                   │
│                                          │                         │
│                                          │                         │
│          ┌───────────────────────────────┘                         │
│          │                                                         │
│          ▼                                                         │
│     ┌─────────┐     ┌─────────┐     ┌─────────┐                   │
│     │ PAUSED  │     │ STOPPING│     │  DONE   │                   │
│     └─────────┘     └─────────┘     └─────────┘                   │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### 循环伪代码/Loop Pseudocode

```python
class AutonomousLoop:
    def __init__(self, goal: str):
        self.goal = goal
        self.state = "INITIAL"
        self.context = load_context()  # 跨会话加载
        self.budget = load_budget()
        self.decisions = []
        self.hard_timeout = time.monotonic() + self.budget.time_limit  # Hard timeout guard
        
    def run(self):
        """主循环/Main loop"""
        while True:
            # Hard timeout guard: force exit if budget exceeded
            if time.monotonic() >= self.hard_timeout:
                self.state = "STOPPING"
                self.save_and_exit()
                break
            # Budget check: stop if tokens or time exhausted
            if not self.budget.has_remaining():
                self.state = "STOPPING"
                self.save_and_exit()
                break
            
            # 1. 检查状态
            if self.state == "PAUSED":
                wait_for_resume()
                continue
            if self.state == "STOPPING":
                self.save_and_exit()
                break
            if self.state == "DONE":
                self.report_and_exit()
                break
            
            # 2. 感知当前状态
            perception = self.perceive()
            
            # 3. 决策下一步
            decision = self.decide(perception)
            
            # 4. 检查预算
            if not self.check_budget(decision):
                self.state = "STOPPING"
                continue
            
            # 5. 执行决策
            result = self.execute(decision)
            
            # 6. 审查结果
            review = self.review(result)
            
            # 7. 保存状态
            self.save_state(perception, decision, result, review)
            
            # 8. 决定是否继续
            if not self.should_continue(review):
                self.state = "DONE"
```

## 跨会话记忆/Cross-Session Memory

### 上下文存储/Context Storage

```json
{
  "session_id": "auto_001",
  "goal": "改进所有技能的神似程度",
  "started_at": "2024-01-01T00:00:00Z",
  "state": "RUNNING",
  "progress": {
    "completed_tasks": [
      {"id": 1, "task": "改进莎士比亚风格", "time": "45min"},
      {"id": 2, "task": "改进鲁迅风格", "time": "38min"}
    ],
    "current_task": {"id": 3, "task": "改进金庸风格", "progress": "60%"},
    "pending_tasks": [
      {"id": 4, "task": "改进古龙风格"},
      {"id": 5, "task": "改进卡尔维诺风格"}
    ]
  },
  "context": {
    "decisions": [
      {"id": 1, "choice": "深度重构", "rationale": "表面改进不够"},
      {"id": 2, "choice": "添加创作练习", "rationale": "提高实用性"}
    ],
    "assumptions": [
      {"id": 1, "content": "用户希望神似而非形似", "verified": true}
    ],
    "issues": [
      {"id": 1, "description": "部分规则文件过长", "status": "resolved"}
    ]
  },
  "budget": {
    "time_limit": "4h",
    "time_used": "1h 23min",
    "token_limit": 500000,
    "token_used": 185000
  },
  "snapshots": [
    {"id": 1, "time": "T+45min", "files_changed": 3},
    {"id": 2, "time": "T+1h23min", "files_changed": 5}
  ],
  "last_updated": "2024-01-01T01:23:00Z"
}
```

### 会话恢复/Session Recovery

```
新会话启动时/On New Session:
    ↓
检测活跃迭代/Detect active iteration
    ↓
┌─────────────────────────────────────┐
│ 发现未完成的迭代/Incomplete found    │
├─────────────────────────────────────┤
│ 目标/Goal: {goal}                   │
│ 进度/Progress: {completed}/{total}  │
│ 上次时间/Last: {timestamp}          │
│ 预算剩余/Budget: {remaining}        │
└─────────────────────────────────────┘
    ↓
请选择/Please Choose:
[A] 恢复迭代/Resume
[B] 查看日志/View Log
[C] 修改目标/Modify Goal
[D] 停止迭代/Stop
```

## 预算控制/Budget Control

### 预算分配/Budget Allocation

```
【时间预算/Time Budget】

tiny:      10 分钟   → 只做 P0 任务
small:     30 分钟   → P0 + 部分 P1
medium:    60 分钟   → P0 + P1 + 部分 P2
large:     120 分钟  → 完整迭代
xlarge:    240 分钟  → 多轮迭代
unlimited: 无限制    → 持续改进

【Token 预算/Token Budget】

每轮迭代估算:
- 感知/Perceive: ~2000 tokens
- 决策/Decide: ~3000 tokens
- 执行/Execute: ~10000 tokens (代码生成)
- 审查/Review: ~5000 tokens
- 保存/Save: ~1000 tokens

总计/Total: ~21000 tokens/iteration
```

### 预算检查/Budget Check

```python
def check_budget(self, decision: dict) -> bool:
    """检查预算是否允许执行决策"""
    
    estimated_tokens = estimate_tokens(decision)
    estimated_time = estimate_time(decision)
    
    # 时间检查
    time_remaining = self.budget.time_limit - self.budget.time_used
    if estimated_time > time_remaining * 0.9:  # 保留 10% 余量
        return False
    
    # Token 检查
    token_remaining = self.budget.token_limit - self.budget.token_used
    if estimated_tokens > token_remaining * 0.9:
        return False
    
    return True


def adjust_scope(self, budget_status: str):
    """根据预算状态调整任务范围"""
    
    if budget_status == "CRITICAL":  # <5% 剩余
        # 只做 P0 任务
        self.task_queue = [t for t in self.task_queue if t.priority == "P0"]
        
    elif budget_status == "LOW":  # <20% 剩余
        # 跳过 P2 任务
        self.task_queue = [t for t in self.task_queue if t.priority != "P2"]
        
    elif budget_status == "MEDIUM":  # <50% 剩余
        # 正常执行，但记录警告
        self.log_warning("Budget below 50%")
```

## 自我审查/Self-Review

### 审查维度/Review Dimensions

```markdown
## 自我审查表/Self-Review Checklist

### 代码质量/Code Quality
- [ ] 无语法错误/No syntax errors
- [ ] 命名清晰/Clear naming
- [ ] 函数简短/Short functions
- [ ] 无重复代码/No duplication

### 功能正确/Functionality
- [ ] 核心功能完整/Core complete
- [ ] 边界情况处理/Edge cases
- [ ] 错误处理完善/Error handling
- [ ] 测试覆盖/Test coverage

### 文档完整/Documentation
- [ ] README 更新/README updated
- [ ] 注释充分/Comments adequate
- [ ] 示例正确/Examples correct

### 安全审查/Security
- [ ] 无危险命令/No dangerous commands
- [ ] 无凭证泄露/No credential leak
- [ ] 无资源耗尽/No resource exhaustion
```

### 审查决策/Review Decision

```python
def review_result(self, result: dict) -> dict:
    """审查执行结果，决定下一步"""
    
    review = {
        "passed": True,
        "issues": [],
        "suggestions": [],
        "next_action": "continue"
    }
    
    # 检查代码质量
    if not check_code_quality(result["code"]):
        review["passed"] = False
        review["issues"].append("Code quality issues")
        review["next_action"] = "fix_quality"
    
    # 检查测试覆盖
    if get_test_coverage() < 70:
        review["suggestions"].append("Increase test coverage")
    
    # 检查预算
    if self.budget.remaining < 20%:
        review["next_action"] = "wrap_up"
    
    # 检查目标完成度
    if self.progress.completed >= 80%:
        review["next_action"] = "finalize"
    
    return review
```

## 安全机制/Safety Mechanisms

### 变更审查/Change Review

```python
def review_changes(self, changes: list) -> dict:
    """审查所有变更，确保安全"""
    
    review = {
        "approved": [],
        "rejected": [],
        "needs_confirm": []
    }
    
    for change in changes:
        risk = assess_risk(change)
        
        if risk.level == "CRITICAL":
            review["rejected"].append({
                "change": change,
                "reason": "Critical security risk"
            })
        elif risk.level == "HIGH":
            review["needs_confirm"].append({
                "change": change,
                "reason": "High risk, needs user confirm"
            })
        else:
            review["approved"].append(change)
    
    return review
```

### 回滚机制/Rollback

```python
def create_snapshot(self) -> str:
    """创建回滚快照"""
    
    snapshot_id = f"snapshot_{int(time.time())}"
    
    # 保存当前文件状态
    changed_files = get_changed_files()
    snapshot = {
        "id": snapshot_id,
        "timestamp": datetime.now().isoformat(),
        "files": {}
    }
    
    for file in changed_files:
        snapshot["files"][file] = {
            "content": read_file(file),
            "hash": hash_file(file)
        }
    
    # 保存快照
    save_snapshot(snapshot_id, snapshot)
    
    return snapshot_id


def rollback(self, snapshot_id: str) -> bool:
    """回滚到指定快照"""
    
    snapshot = load_snapshot(snapshot_id)
    if not snapshot:
        return False
    
    for file, data in snapshot["files"].items():
        write_file(file, data["content"])
    
    log_action("rollback", {"snapshot_id": snapshot_id})
    
    return True
```

## 使用示例/Examples

### 示例 1：改进所有技能

```
用户/User: /自控 改进所有技能的神似程度

→ 启动自主循环/Start autonomous loop
→ 分析所有技能/Analyze all skills
→ 制定改进计划/Create improvement plan
→ 执行改进/Execute improvements
→ 自我审查/Self-review
→ 保存状态/Save state
→ 跨会话继续/Cross-session continue
→ ...持续迭代/Continue iterating
→ 完成目标/Complete goal
→ 输出报告/Output report
```

### 示例 2：查看状态

```
用户/User: /自控 status

## 迭代状态/Iteration Status

**目标/Goal**: 改进所有技能的神似程度
**状态/State**: RUNNING
**进度/Progress**: 4/7 技能完成

**预算/Budget**:
- 时间/Time: 1h 23min / 4h (34%)
- Token: 185k / 500k (37%)

**当前任务/Current**:
- 改进金庸风格 (60%)

**待执行/Pending**:
- 改进古龙风格
- 改进卡尔维诺风格

**已创建快照/Snapshots**: 3
**可回滚/Rollback Available**: ✅
```

## Rules

- [rules/autonomous-loop.md](rules/autonomous-loop.md) - 自主循环/Autonomous Loop
- [rules/memory.md](rules/memory.md) - 跨会话记忆/Cross-Session Memory
- [rules/budget.md](rules/budget.md) - 预算控制/Budget Control
- [rules/safety.md](rules/safety.md) - 安全机制/Safety Mechanisms
- [rules/self-review.md](rules/self-review.md) - 自我审查/Self-Review

## 配置选项/Configuration

| 参数/Param | 默认值/Default | 说明/Description |
|-----------|---------------|-----------------|
| default_budget_time | 2h | 默认时间预算/Default time budget |
| default_budget_token | 200k | 默认 token 预算/Default token budget |
| auto_save_interval | 5min | 自动保存间隔/Auto-save interval |
| max_changes_per_loop | 10 | 每轮最大变更/Max changes per loop |
| require_confirm_risk | high | 需要确认的风险级别/Risk level for confirm |
| enable_rollback | true | 启用回滚/Enable rollback |
