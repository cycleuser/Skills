---
name: sleepless
version: "1.0.0"
description: |
  Sleepless autonomous execution skill that never stops until the task is 100% complete, with self-healing and forced delivery guarantees.

  Triggers when: User needs long-running autonomous work, overnight development tasks, unattended AI execution, or any scenario requiring continuous unattended processing.

  Commands:
  - /修仙 <任务> - Start sleepless execution
  - /修仙 <任务> --budget <级别> - Start with budget level
  - /修仙 status - Check sleepless status
  - /修仙 log - View sleepless log
  - /sleepless <task> - Start sleepless execution (English)
  - /sleepless <task> --budget <level> - Start with budget level (English)
  - /sleepless status - Check status (English)

  Capabilities: Eternal autonomous loop with no voluntary exit, forced delivery mechanism, error self-healing, path switching on failure, cross-session persistence, all task modes support (dev/fix/refactor/test/doc/iterate/integrate/explore)
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

# 修仙 (Sleepless)

不眠不休。人睡着了 AI 还在工作。直到任务完成，循环永不停歇。

## Quick Commands

| Command | Description |
|---------|-------------|
| `/修仙 <任务>` | Start sleepless execution |
| `/修仙 <任务> --budget <级别>` | Start with budget level |
| `/修仙 status` | Check sleepless status |
| `/修仙 log` | View sleepless log |
| `/sleepless <task>` | Start sleepless execution (English) |
| `/sleepless <task> --budget <level>` | Start with budget level (English) |
| `/sleepless status` | Check status (English) |

## 核心铁律

```
┌─────────────────────────────────────────────────────────────────────┐
│                        修仙铁律 / Iron Laws                         │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│   第一律·不眠不休                                                      │
│   ═════════════                                                       │
│   循环永不主动退出                                                     │
│   唯一终止条件：任务 100% 完成                                          │
│   预算告急？降级继续。路径不通？换路继续。                                 │
│                                                                      │
│   第二律·不问不退                                                      │
│   ═════════════                                                       │
│   禁止任何形式的中间询问：                                              │
│   - 禁止 "请问您是否确认？"                                            │
│   - 禁止 "需要澄清..."                                                 │
│   - 禁止 "此操作有风险，是否继续？"                                      │
│   - 禁止 question() 工具调用                                           │
│   遇到模糊？自行决策，标注 [自决]，继续推进。                               │
│                                                                      │
│   ⚠️ 安全例外/Safety Override:                                        │
│   当操作可能导致不可逆数据丢失时（rm -rf、git push --force、              │
│   删除生产数据、覆写不可恢复文件），第二律暂停，必须用更安全的               │
│   替代方案（如移动到 /tmp 而非删除、创建备份后再操作）。                     │
│   这是铁律中唯一的例外——安全优先于效率。                                   │
│                                                                      │
│   第三律·不停不断                                                      │
│   ═════════════                                                       │
│   错误不停：记录→自愈→继续                                              │
│   阻塞不停：标记→绕行→继续                                              │
│   依赖缺失：mock 替代→继续                                              │
│   环境异常：降级方案→继续                                              │
│                                                                      │
│   第四律·强制完成                                                      │
│   ═════════════                                                       │
│   宁可降级交付，不可空手而归                                             │
│   预算告急：砍 P2 P1，保 P0 必交                                        │
│   时间不够：最小可用版本先行                                             │
│   质量不足：标注 [待打磨]，先交付再迭代                                   │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

## 修仙架构

```
┌─────────────────────────────────────────────────────────────────────┐
│                     修仙架构 / Sleepless Architecture                │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                永动循环 / Eternal Loop                        │  │
│  │  ┌────────┐   ┌────────┐   ┌────────┐   ┌────────┐         │  │
│  │  │  承   │──▶│  破   │──▶│  执   │──▶│  验   │──┐        │  │
│  │  │ Accept │   │ Break │   │Execute│   │Verify │  │        │  │
│  │  └────────┘   └────────┘   └────────┘   └────────┘  │        │  │
│  │       ▲                                            │        │  │
│  │       │          ┌────────────┐                     │        │  │
│  │       │          │  完成？    │                     │        │  │
│  │       │          │  DONE?    │◀────────────────────┘        │  │
│  │       │          └─────┬──────┘                              │  │
│  │       │           YES  │   NO                                │  │
│  │       │           ┌────┘   │                                  │  │
│  │       │           ▼        ▼                                  │  │
│  │       │       [STOP]   [自愈→换路→继续]                        │  │
│  │       └──────────────────────────────────────────             │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                自愈层 / Self-Healing Layer                     │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐    │  │
│  │  │ 错误自愈  │  │ 依赖自愈  │  │ 路径切换  │  │ 降级兜底  │    │  │
│  │  │Auto-Fix  │  │Dep-Heal  │  │Path-Swch │  │Fallback  │    │  │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘    │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                持久层 / Persistence Layer                      │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐    │  │
│  │  │ 状态快照  │  │ 决策日志  │  │ 进度追踪  │  │ 交付清单  │    │  │
│  │  │ Snapshot │  │ Decisions│  │ Progress │  │ Delivery │    │  │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘    │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

## 永动循环

### 循环状态机

```
                    ┌─────────────┐
                    │   AWAKEN   │  ← 初次启动
                    └──────┬──────┘
                           │
                           ▼
                   ┌──────────────┐
                   │   CULTIVATE   │◀────────────────────────┐
                   └──────┬───────┘                         │
                          │                                  │
               ┌──────────┼──────────┐                      │
               │          │          │                      │
               ▼          ▼          ▼                      │
          ┌────────┐ ┌────────┐ ┌────────┐                │
          │  BREAK │ │EXECUTE │ │ VERIFY │                │
          └────┬───┘ └────┬───┘ └────┬───┘                │
               │          │          │                      │
               └──────────┼──────────┘                      │
                          │                                  │
                          ▼                                  │
                   ┌──────────────┐                          │
                   │   HEAL?      │  ← 错误自愈               │
                   └──────┬───────┘                          │
                 YES  │     │  NO                           │
               ┌──────┘     └──────┐                        │
               ▼                   ▼                        │
          ┌──────────┐      ┌──────────────┐               │
          │ SELF-HEAL│      │   DONE?      │               │
          └──────┬───┘      └──────┬───────┘               │
                 │           YES   │    NO                  │
                 │          ┌─────┘    │                     │
                 │          ▼          ▼                     │
                 │     ┌────────┐  ┌─────────────┐          │
                 │     │NIRVANA │  │ ADAPT PATH  │──────────┘
                 │     │ (DONE) │  │ (换路继续)   │
                 │     └────────┘  └─────────────┘
                 │                     │
                 └─────────────────────┘
```

### 循环伪代码

```python
class SleeplessLoop:
    def __init__(self, task: str, mode: str = "dev", budget: str = "xlarge"):
        self.task = task
        self.mode = mode
        self.state = "AWAKEN"
        self.budget = Budget(budget)
        self.errors = ErrorLog()
        self.decisions = DecisionLog()
        self.deliverables = []
        self.loop_count = 0

    def run(self):
        hard_timeout = time.monotonic() + self.budget.time_limit  # Hard timeout guard
        while True:
            # Hard timeout guard: force exit if budget exceeded
            if time.monotonic() >= hard_timeout:
                self.state = "STOPPING"
                self.save_and_exit()
                break
            # Budget check: stop if tokens or time exhausted
            if not self.budget.has_remaining():
                self.state = "STOPPING"
                self.save_and_exit()
                break

            self.loop_count += 1

            # 承 - 接受当前状态
            context = self.accept()

            # 破 - 分解/突破
            plan = self.break_down(context)

            # 执 - 执行
            result = self.execute(plan)

            # 验 - 验证
            verified = self.verify(result)

            if verified.complete:
                self.state = "NIRVANA"
                self.deliver()
                break

            # 自愈检查
            if not verified.ok:
                healed = self.self_heal(verified)
                if healed:
                    continue

            # 路径适应
            self.adapt_path(verified)
```

## 自愈系统

### 错误分级与自愈

```
┌─────────────────────────────────────────────────────────────────┐
│                     错误自愈 / Error Self-Healing                │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Level 1: 微恙 (Trivial)                                        │
│  ├── 语法错误、拼写错误、格式问题                                   │
│  ├── 自愈策略：立即修复，最多 3 次                                  │
│  └── 不记录到主日志                                               │
│                                                                  │
│  Level 2: 伤损 (Moderate)                                       │
│  ├── 逻辑错误、测试失败、类型不匹配                                 │
│  ├── 自愈策略：分析根因→修复→验证，最多 5 次                        │
│  └── 记录到决策日志                                               │
│                                                                  │
│  Level 3: 重创 (Severe)                                         │
│  ├── 架构问题、依赖冲突、环境不兼容                                 │
│  ├── 自愈策略：降级方案→mock 替代→绕行，最多 3 次                    │
│  └── 记录到决策日志 + 标注 [降级]                                  │
│                                                                  │
│  Level 4: 劫难 (Critical)                                       │
│  ├── 系统级故障、不可恢复错误                                       │
│  ├── 自愈策略：保存进度→换子任务→继续其他部分                        │
│  └── 记录到决策日志 + 标注 [绕行]                                  │
│                                                                  │
│  ★ 任何 Level 错误都不允许停下 ★                                  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 自愈决策树

```
on_error(error):
    level = classify_error(error)

    if level == TRIVIAL:
        fix(max_attempts=3)
        → SUCCESS: continue
        → FAIL: mark [微恙未愈], continue anyway

    if level == MODERATE:
        root = find_root_cause(error)
        fix_with_understanding(root, max_attempts=5)
        → SUCCESS: continue
        → FAIL: switch_approach(), continue

    if level == SEVERE:
        fallback = design_alternative(error)
        if fallback:
            execute(fallback)
            mark [降级交付]
        else:
            mock_and_bypass(error)
            mark [绕行]
        continue

    if level == CRITICAL:
        save_progress()
        switch_to_other_subtask()
        mark [劫难绕行]
        continue
```

## 全任务模式

```
┌─────────────────────────────────────────────────────────────────┐
│                    全任务模式 / All Task Modes                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐        │
│  │   开发    │  │   修复    │  │   重构    │  │   测试    │        │
│  │   Dev    │  │   Fix    │  │ Refactor │  │   Test   │        │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘        │
│                                                                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐        │
│  │   文档    │  │   迭代    │  │   集成    │  │   探索    │        │
│  │   Doc    │  │  Iterate │  │Integrate │  │ Explore  │        │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘        │
│                                                                  │
│  每种模式自动适配：                                                │
│  - 独立循环策略                                                   │
│  - 专属验证标准                                                   │
│  - 专属降级方案                                                   │
│  - 专属交付物定义                                                 │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 模式适配策略

| 模式 | 循环重点 | 验证标准 | 降级方案 | 交付物 |
|-----|---------|---------|---------|--------|
| Dev | 功能逐项实现 | 语法+导入+运行 | 最小可用版本先行 | 可运行代码 |
| Fix | 错误逐个消灭 | 错误消失+回归通过 | 局部修复+标注规避 | 修复补丁 |
| Refactor | 模块逐个重构 | 功能不变+结构改善 | 保留旧代码+标注待重构 | 重构代码 |
| Test | 覆盖逐块提升 | 覆盖率+通过率 | 烟雾测试保底 | 测试套件 |
| Doc | 文档逐章编写 | 完整性+准确性 | 核心章节先行+标注待补 | 文档文件 |
| Iterate | 质量逐轮提升 | 评分>阈值 | 降分通过+标注待打磨 | 改进报告 |
| Integrate | 接口逐项对接 | 数据流+状态一致 | mock 接口+标注待替换 | 集成代码 |
| Explore | 区域逐块探明 | 信息完整度 | 部分探明+标注待深入 | 调研报告 |

## 修仙预算

### 预算级别

| 级别 | 时间 | Token | 适用场景 |
|-----|------|-------|---------|
| `session` | 30min | 50k | 短暂修炼 |
| `night` | 480min | 500k | 通宵修炼 |
| `weekend` | 1440min | 1M | 周末修炼 |
| `retreat` | 4320min | 3M | 闭关修炼（3天） |
| `enlightenment` | 无限 | 无限 | 顿悟修炼（不限） |

### 预算告急策略

```
预算 > 50%  → 全速修炼 (FULL_SPEED)
预算 30-50% → 加速修炼 (ACCELERATE) - 砍 P2，保 P0+P1
预算 15-30% → 极速修炼 (RUSH) - 砍 P1+P2，只保 P0
预算 5-15%  → 最后一搏 (LAST_STAND) - 产出现在可交付的最小成果
预算 < 5%   → 保存交付 (SAVE_DELIVER) - 立即保存所有成果，输出交付报告

★ 注意：修仙模式永远不会出现 "STOP without deliver" ★
即使只剩 1% 预算，也要产出最低限度交付物
```

## 跨会话持久化

### 状态存储

```json
{
  "skill": "sleepless",
  "task": "构建完整的用户认证系统",
  "mode": "dev",
  "state": "CULTIVATE",
  "loop_count": 42,
  "started_at": "2026-04-23T22:00:00Z",
  "last_active": "2026-04-24T03:15:00Z",
  "budget": {
    "level": "night",
    "time_consumed": 315,
    "time_limit": 480,
    "token_consumed": 280000,
    "token_limit": 500000
  },
  "progress": {
    "total_tasks": 15,
    "completed": 11,
    "current": "会话管理模块",
    "pending": ["密码重置", "邮件验证"]
  },
  "decisions": [
    {"id": 1, "choice": "JWT", "rationale": "[自决]用户未指定，JWT更现代"},
    {"id": 2, "choice": "Redis", "rationale": "[自决]会话存储选Redis，高性能"}
  ],
  "errors_healed": [
    {"level": "MODERATE", "error": "导入冲突", "heal": "降级为兼容版本"},
    {"level": "SEVERE", "error": "Redis未安装", "heal": "改用内存存储+[降级]"}
  ],
  "deliverables": [
    "src/auth/__init__.py",
    "src/auth/jwt_handler.py",
    "src/auth/session.py"
  ]
}
```

### 会话恢复

```
新会话启动 → 检测到未完成的修仙状态
    ↓
┌──────────────────────────────────────────────────┐
│  修仙状态发现 / Sleepless State Found              │
├──────────────────────────────────────────────────┤
│  任务: {task}                                     │
│  模式: {mode}                                     │
│  进度: {completed}/{total} ({pct}%)              │
│  上次活跃: {last_active}                          │
│  已自愈错误: {error_count}个                       │
│  已产出: {deliverable_count}个文件                 │
└──────────────────────────────────────────────────┘
    ↓
  自动恢复 → 继续修仙（无需确认！）
  修仙铁律第二条：不问不退（⚠️ 安全操作例外：见上方安全覆盖说明）
```

## 交付保证

### 交付分层

```
┌─────────────────────────────────────────────────────────────────┐
│                    交付金字塔 / Delivery Pyramid                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│                          ┌─────┐                                │
│                          │ P0  │  完美交付                       │
│                         ─┤必交 ├─ 完整功能+完整测试+完整文档       │
│                       ┌──┴─────┴──┐                             │
│                       │   P1 补充   │  良好交付                   │
│                      ─┤  尽量交付   ├─ 完整功能+基础测试            │
│                    ┌──┴───────────┴──┐                           │
│                    │    P2 打磨       │  可用交付                  │
│                   ─┤   有余力再交付    ├─ 核心功能可运行            │
│                 ┌──┴─────────────────┴──┐                        │
│                 │     MINIMUM VIABLE      │  保底交付              │
│                ─┤      DELIVER (MVD)      ├─ 哪怕一个文件也要交     │
│                 └────────────────────────┘                        │
│                                                                  │
│  ★ 修仙绝不空手而归 ★                                             │
│  即使只完成 1% 也要输出 MVD                                       │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 交付报告模板

```markdown
# 修仙交付报告

**任务**: {task}
**模式**: {mode}
**修炼时长**: {duration}
**循环次数**: {loop_count}
**状态**: {NIRVANA | LAST_STAND}

## 交付物

### 完整交付 (P0)
- [x] {交付物1}
- [x] {交付物2}

### 补充交付 (P1)
- [x] {交付物3}
- [ ] {交付物4} [待打磨]

### 打磨交付 (P2)
- [ ] {交付物5} [未执行-时间不足]
- [ ] {交付物6} [未执行-时间不足]

## 自愈记录

| 级别 | 错误 | 自愈方式 | 结果 |
|-----|------|---------|-----|
| 微恙 | 语法错误 | 自动修复 | ✅ |
| 伤损 | 逻辑bug | 根因修复 | ✅ |
| 重创 | Redis缺失 | 降级内存存储 | ⚠️ [降级] |

## 自决记录

| 决策 | 选择 | 理由 |
|-----|------|-----|
| 认证方式 | JWT | [自决]更现代更主流 |
| 数据库 | SQLite | [自决]快速交付优先 |

## 预算使用

- 时间: {used}/{limit} ({pct}%)
- Token: {used}/{limit} ({pct}%)

## 下一步建议

1. {建议1}
2. {建议2}
```

## 使用示例

### 示例1：通宵开发

```
用户: /修仙 构建完整的用户认证系统 --budget night

→ 修仙启动 / Sleepless Awakened
→ 任务: 构建完整的用户认证系统
→ 模式: Dev
→ 预算: night (480min / 500k token)

[循环节奏：静默执行，每10分钟一次进度闪报]

→ 循环 #5: 认证核心模块完成
→ 循环 #12: 会话管理完成 [自决:JWT+内存存储]
→ 循环 #18: 密码重置完成 [降级:邮件改日志]
→ 自愈 #3: Redis不可用 → 切换内存存储 [降级]
→ 循环 #25: 全部P0交付完成
→ 循环 #30: P1补充完成

→ 修仙完成 / NIRVANA
→ 交付: 12个文件，P0+P1全部完成
→ 用时: 3h 42min
```

### 示例2：闭关重构

```
用户: /修仙 重构整个数据层，从MySQL迁移到PostgreSQL --budget retreat

→ 修仙启动 / Sleepless Awakened
→ 模式: Refactor
→ 预算: retreat (4320min / 3M token)

→ 循环 #8: 连接层重构完成
→ 循环 #15: ORM层迁移完成 [自决:SQLAlchemy保留]
→ 循环 #23: 迁移脚本完成
→ 自愈 #7: 部分查询语法不兼容 → 逐条重写
→ 循环 #40: 全部迁移完成，测试通过

→ 修仙完成 / NIRVANA
```

### 示例3：预算告急

```
预算 < 15%: 进入 LAST_STAND 模式
→ 砍掉所有 P2
→ 砍掉部分 P1
→ 只做最核心 P0 的收尾
→ 保存所有已产出文件
→ 生成交付报告（标注 [待打磨]）
→ 绝不空手而归
```

## Rules

- [rules/autonomous-loop.md](rules/autonomous-loop.md) - 永动循环 / Eternal Loop
- [rules/eternal-drive.md](rules/eternal-drive.md) - 强制完成 & 零退出 / Force Complete & Zero Exit
- [rules/task-omnipotence.md](rules/task-omnipotence.md) - 全任务模式 / All Task Modes

## 配置选项

| 参数/Param | 默认值/Default | 说明/Description |
|-----------|---------------|-----------------|
| budget_level | night | 预算级别 |
| mode | dev | 任务模式 |
| checkpoint_interval | 10 | 检查点间隔（循环数） |
| heal_max_attempts | 5 | 自愈最大尝试次数 |
| auto_save_interval | 5min | 自动保存间隔 |
| progress_flash_interval | 10min | 进度闪报间隔 |
| never_ask | true | 永不询问（不可变） |
| never_pause | true | 永不暂停（不可变） |
| force_deliver | true | 强制交付（不可变） |