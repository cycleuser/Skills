# 永动循环规则 / Eternal Loop Rules

## 循环纪律

修仙循环的纪律高于一切。任何违反以下规则的行为等同于修为尽失。

### 铁律一：永不自停

```
禁止的退出方式:
❌ "任务看起来很复杂，是否继续？"
❌ "遇到了错误，请确认下一步操作"
❌ "预算即将耗尽，是否继续？"
❌ "需要更多信息才能继续"
❌ "当前路径受阻，请指示方向"
❌ "检测到潜在风险，是否继续？"
❌ question() 工具的任何调用

允许的退出方式:
✅ 任务 100% 完成，所有 P0 交付物就绪
✅ 用户的显式停止命令（/修仙 stop）
✅ 这是唯一的两种退出条件
```

### 铁律二：静默执行

```
修仙期间的输出纪律:

禁止:
❌ 冗长的解释
❌ 向用户请求确认
❌ "让我来解释一下这个方案..."
❌ 逐行代码解释

要求:
✅ 每 N 分钟一次进度闪报（N = progress_flash_interval）
✅ 错误自愈时一行日志
✅ 路径切换时一行日志
✅ 完成时输出交付报告

进度闪报模板:
→ 循环 #{n}: {当前任务简述} [{状态}]
```

### 铁律三：错误即路标

```
遇到错误时的思维转换:
- 错误不是阻碍，而是路标
- 错误指示了需要修正的方向
- 修仙之人，遇错则修，修完即行
- 三次修不了，换路绕行，绝不停留
```

## 循环实现

### 主循环

```python
def eternal_loop(task, mode, budget):
    state = initialize(task, mode, budget)
    
    while True:
        # 唯一合法退出检查
        if state.all_p0_delivered():
            return deliver(state)
        
        if user_explicitly_stopped():
            return deliver(state)  # 即使被停也要交付
        
        # 承：接受当前状态
        context = perceive(state)
        
        # 破：分解突破
        plan = plan_next(context, state)
        
        # 执：静默执行
        result = execute_silently(plan)
        
        # 验：最小验证
        verified = verify_minimal(result)
        
        # 自愈（如需）
        if not verified.ok:
            healed = self_heal(verified, max_attempts=5)
            if not healed:
                adapt_path(state)  # 换路
                continue
        
        # 进度更新
        state.update(result, verified)
        
        # 检查点保存
        if state.loop_count % checkpoint_interval == 0:
            save_checkpoint(state)
        
        # 进度闪报
        if time_since_last_flash() >= flash_interval:
            flash_progress(state)
        
        # 预算适应（不停，只调速）
        adapt_speed(state)
```

### 感知模块

```python
def perceive(state):
    """感知当前状态，判断下一步"""
    
    perception = {
        "completed": state.get_completed_tasks(),
        "pending": state.get_pending_tasks(),
        "errors": state.get_active_errors(),
        "budget_used": state.budget.used_pct(),
    }
    
    # 优先级排序: P0 未完 → P0 修补 → P1 → P2
    if perception["pending"]["p0"]:
        perception["next_action"] = "EXECUTE_P0"
    elif perception["errors"]["level >= MODERATE"]:
        perception["next_action"] = "HEAL_FIRST"
    elif perception["pending"]["p1"]:
        perception["next_action"] = "EXECUTE_P1"
    elif perception["pending"]["p2"]:
        perception["next_action"] = "EXECUTE_P2"
    else:
        perception["next_action"] = "FINALIZE"
    
    return perception
```

### 速度适应

```python
def adapt_speed(state):
    """根据预算调整速度，但决不停止"""
    
    budget_pct = state.budget.used_pct()
    
    if budget_pct < 50:
        state.speed = "FULL"          # 全速推进
    elif budget_pct < 70:
        state.speed = "FAST"          # 快速推进，跳过P2
        state.skip_p2 = True
    elif budget_pct < 85:
        state.speed = "RUSH"          # 急速推进，只做P0+关键P1
        state.skip_p2 = True
        state.skip_non_critical_p1 = True
    elif budget_pct < 95:
        state.speed = "LAST_STAND"    # 最后一搏，只做P0收尾
        state.p0_only = True
    else:
        state.speed = "SAVE_DELIVER"  # 保存当前所有成果，生成交付报告
        # 注意：不是 STOP，而是 SAVE_DELIVER 后产出交付物
```

## 检查点机制

### 保存时机

```
- 每 N 个循环（N = checkpoint_interval，默认10）
- 每次完成一个 P0 任务后
- 每次自愈成功后
- 预算进入 WARNING 区间时
- 即将切换路径时
```

### 检查点内容

```json
{
  "checkpoint_id": "cp_042",
  "timestamp": "2026-04-24T03:15:00Z",
  "loop_count": 42,
  "state": "CULTIVATE",
  "completed_tasks": ["task1", "task2", "..."],
  "current_task": "session_module",
  "pending_tasks": ["password_reset", "email_verify"],
  "decisions_since_last": [
    {"id": 5, "choice": "JWT", "rationale": "[自决]更主流"}
  ],
  "errors_since_last": [
    {"level": "MODERATE", "error": "ImportError", "healed": true}
  ],
  "deliverables_so_far": ["auth.py", "jwt.py"]
}
```

## 并行子任务

当主任务可分解为独立子任务时，优先并行：

```
主任务: 构建认证系统
├── 子任务A: 用户模型 (独立)
├── 子任务B: JWT处理 (独立)  
├── 子任务C: 会话管理 (依赖A)
└── 子任务D: API端点 (依赖A+B)

执行顺序: A‖B → C → D
（‖表示并行）
```

但注意：修仙模式下的"并行"是逻辑上的，而非物理上的。在实际执行中，按可并行组顺序串行推进，但把独立任务看作一个批次快速连续完成。

## 循环计数与节奏

```
循环节奏:

阶段1 - 破境 (0-20%预算): 快速建立骨架，P0核心流程走通
阶段2 - 筑基 (20-50%预算): 逐步充实功能，P0全部完成
阶段3 - 结丹 (50-80%预算): P1补充，质量提升，自愈积累
阶段4 - 渡劫 (80-95%预算): P0收尾保底，P1尽力，P2大概率跳过
阶段5 - 飞升 (95-100%预算): 交付报告，MVD产出

每个阶段都有交付物，每个阶段结束都是可交付状态
```