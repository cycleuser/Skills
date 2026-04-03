# 自主循环/Autonomous Loop

## 循环实现/Loop Implementation

```python
class AutonomousIteration:
    """自主迭代核心类"""
    
    def __init__(self, goal: str, config: dict = None):
        self.goal = goal
        self.config = config or {}
        self.state = "INITIAL"
        self.context = self.load_or_init_context()
        self.budget = BudgetManager(self.config.get("budget", {}))
        self.loop_count = 0
        self.max_loops = self.config.get("max_loops", 100)
        
    def run(self):
        """主循环入口/Main loop entry"""
        
        # 1. 初始化/Initialize
        self.initialize()
        
        # 2. 主循环/Main loop
        while self.should_continue():
            try:
                self.loop_count += 1
                
                # 感知/Perceive
                perception = self.perceive()
                
                # 决策/Decide
                decision = self.decide(perception)
                
                # 预算检查/Budget check
                if not self.budget.check(decision):
                    self.log("Budget insufficient, stopping")
                    self.state = "STOPPING"
                    break
                
                # 执行/Execute
                result = self.execute(decision)
                
                # 审查/Review
                review = self.review(result)
                
                # 保存/Save
                self.save_state(perception, decision, result, review)
                
                # 决定是否继续/Decide whether to continue
                if not self.should_continue(review):
                    self.state = "DONE"
                    
            except Exception as e:
                self.handle_error(e)
                # 错误后继续/Error and continue
                if self.config.get("continue_on_error", True):
                    continue
                else:
                    self.state = "ERROR"
                    break
        
        # 3. 清理/Cleanup
        self.finalize()
```

## 感知模块/Perception Module

```python
def perceive(self) -> dict:
    """感知当前状态/Perceive current state"""
    
    perception = {
        "timestamp": datetime.now().isoformat(),
        "goal": self.goal,
        "progress": self.get_progress(),
        "environment": self.scan_environment(),
        "issues": self.detect_issues(),
        "opportunities": self.identify_opportunities()
    }
    
    # 扫描工作区/Scan workspace
    perception["workspace"] = {
        "files_changed": get_changed_files(),
        "tests_status": get_test_status(),
        "build_status": get_build_status()
    }
    
    # 检测问题/Detect issues
    perception["code_quality"] = analyze_code_quality()
    perception["test_coverage"] = get_coverage()
    perception["security_issues"] = scan_security()
    
    # 识别机会/Identify opportunities
    perception["improvements"] = suggest_improvements()
    perception["refactors"] = suggest_refactors()
    perception["optimizations"] = suggest_optimizations()
    
    return perception
```

## 决策模块/Decision Module

```python
def decide(self, perception: dict) -> dict:
    """基于感知做出决策/Make decision based on perception"""
    
    # 1. 分析感知/Analyze perception
    analysis = self.analyze_perception(perception)
    
    # 2. 生成候选行动/Generate candidate actions
    candidates = []
    
    # P0 任务：修复问题
    if analysis["critical_issues"]:
        for issue in analysis["critical_issues"]:
            candidates.append({
                "action": "fix",
                "priority": "P0",
                "issue": issue,
                "estimated_tokens": 5000,
                "estimated_time": 5
            })
    
    # P1 任务：改进建议
    if analysis["improvements"]:
        for improvement in analysis["improvements"]:
            candidates.append({
                "action": "improve",
                "priority": "P1",
                "improvement": improvement,
                "estimated_tokens": 8000,
                "estimated_time": 10
            })
    
    # P2 任务：优化
    if analysis["optimizations"]:
        for opt in analysis["optimizations"]:
            candidates.append({
                "action": "optimize",
                "priority": "P2",
                "optimization": opt,
                "estimated_tokens": 10000,
                "estimated_time": 15
            })
    
    # 3. 按优先级排序/Sort by priority
    candidates.sort(key=lambda x: (x["priority"], -x["estimated_time"]))
    
    # 4. 选择下一个行动/Select next action
    # 考虑预算/Consider budget
    selected = None
    for candidate in candidates:
        if self.budget.can_afford(candidate):
            selected = candidate
            break
    
    if not selected:
        selected = {
            "action": "wrap_up",
            "priority": "P0",
            "reason": "Budget insufficient for any task"
        }
    
    # 5. 记录决策/Record decision
    self.log_decision(selected, analysis)
    
    return selected
```

## 执行模块/Execution Module

```python
def execute(self, decision: dict) -> dict:
    """执行决策/Execute decision"""
    
    result = {
        "action": decision["action"],
        "started_at": datetime.now().isoformat(),
        "success": False,
        "changes": [],
        "errors": []
    }
    
    try:
        if decision["action"] == "fix":
            result["changes"] = self.fix_issue(decision["issue"])
            
        elif decision["action"] == "improve":
            result["changes"] = self.improve(decision["improvement"])
            
        elif decision["action"] == "optimize":
            result["changes"] = self.optimize(decision["optimization"])
            
        elif decision["action"] == "wrap_up":
            result["changes"] = self.wrap_up()
        
        # 验证变更/Validate changes
        if result["changes"]:
            validation = self.validate_changes(result["changes"])
            result["validation"] = validation
            result["success"] = validation["passed"]
            
    except Exception as e:
        result["errors"].append(str(e))
        result["success"] = False
        
        # 尝试回滚/Attempt rollback
        if self.config.get("auto_rollback", True):
            self.rollback()
    
    result["completed_at"] = datetime.now().isoformat()
    
    return result
```

## 审查模块/Review Module

```python
def review(self, result: dict) -> dict:
    """审查执行结果/Review execution result"""
    
    review = {
        "passed": result["success"],
        "quality_score": 0,
        "issues": [],
        "suggestions": [],
        "next_action": "continue"
    }
    
    if not result["success"]:
        review["issues"].append("Execution failed")
        review["next_action"] = "retry_or_skip"
        return review
    
    # 代码质量审查/Code quality review
    quality = assess_code_quality(result["changes"])
    review["quality_score"] = quality["score"]
    
    if quality["score"] < 80:
        review["issues"].append(f"Code quality low: {quality['score']}")
        review["suggestions"].append("Refactor low quality code")
    
    # 测试覆盖审查/Test coverage review
    coverage = get_test_coverage(result["changes"])
    if coverage < 70:
        review["suggestions"].append(f"Add tests, coverage: {coverage}%")
    
    # 安全审查/Security review
    security = scan_security(result["changes"])
    if security["issues"]:
        review["issues"].extend(security["issues"])
        review["next_action"] = "fix_security"
    
    # 预算审查/Budget review
    budget_status = self.budget.get_status()
    if budget_status == "CRITICAL":
        review["next_action"] = "stop_immediately"
    elif budget_status == "LOW":
        review["next_action"] = "wrap_up"
    elif budget_status == "MEDIUM":
        review["next_action"] = "prioritize_p0"
    
    # 目标完成度/Goal completion
    progress = self.get_progress()
    if progress["completed"] >= 90:
        review["next_action"] = "finalize"
    
    return review
```

## 状态管理/State Management

```python
def save_state(self, perception, decision, result, review):
    """保存完整状态/Save complete state"""
    
    state = {
        "loop_id": self.loop_count,
        "timestamp": datetime.now().isoformat(),
        "state": self.state,
        "perception": perception,
        "decision": decision,
        "result": result,
        "review": review,
        "budget": self.budget.get_state(),
        "progress": self.get_progress()
    }
    
    # 保存到文件/Save to file
    state_file = get_state_file()
    with open(state_file, "w") as f:
        json.dump(state, f, indent=2)
    
    # 创建快照/Create snapshot
    if self.loop_count % 5 == 0:  # 每 5 轮创建快照
        self.create_snapshot(f"loop_{self.loop_count}")
    
    # 更新进度文件/Update progress file
    self.update_progress_file()


def load_or_init_context(self) -> dict:
    """加载或初始化上下文/Load or initialize context"""
    
    state_file = get_state_file()
    
    if os.path.exists(state_file):
        # 加载已有状态/Load existing state
        with open(state_file) as f:
            state = json.load(f)
        
        self.state = state.get("state", "INITIAL")
        self.loop_count = state.get("loop_id", 0)
        self.budget.load_state(state.get("budget", {}))
        
        return state
    else:
        # 初始化新上下文/Initialize new context
        return {
            "goal": self.goal,
            "started_at": datetime.now().isoformat(),
            "loops": [],
            "decisions": [],
            "snapshots": []
        }
```