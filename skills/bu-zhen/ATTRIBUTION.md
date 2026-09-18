# Attribution

## 原创性声明

本技能(布阵 / bu-zhen)的所有 prompt 文本、安全规则、工作流协议、预算机制均为**完全重写的原创实现**。没有任何文本直接复制自任何上游仓库。

## 灵感来源

本技能的架构思路(一个 orchestrator + 多个专家 subagent + 委派契约)受以下两个开源项目启发:

### 1. code-yeongyu/oh-my-openagent(真正的原版)

- 仓库: https://github.com/code-yeongyu/oh-my-openagent
- npm 包名: `oh-my-opencode`(双名发布过渡期)
- 许可证: **Sustainable Use License v1.0**
- 仓库结构: 大型 monorepo(`packages/` 含 45+ 子包),核心在 `packages/prompts-core/`、`packages/boulder-state/`、`packages/delegate-core/`、`packages/team-core/`、`packages/omo-opencode/`
- 借鉴的架构思路:
  - Atlas orchestrator prompt(反重复规则、六段委派结构、自动继续策略、默认并行、task_id 失败重试、notepad 系统、boulder 完成响应)
  - Boulder-state(工作追踪状态机、stale work 降级、prototype 污染防护)
  - Delegate-core(模型回退链、9 种委派错误检测、重试指引)
  - Team-core(并行成员硬上限 max_members、max_wall_clock_minutes、mailbox 载荷上限、成员资格 eligible/conditional/hard-reject)
  - Ultrawork prompt(100% 确定性才实现、无借口交付、plan agent 强制)
- **重要**:由于 SUL 限制商用再分发且要求修改声明负担,本技能**未复制**该项目的任何 prompt 文本或代码。仅借鉴通用架构思路(不受版权保护),并用中文完全重写。

### 2. alvinunreal/oh-my-opencode-slim

- 仓库: https://github.com/alvinunreal/oh-my-opencode-slim
- 许可证: **MIT** (Copyright (c) 2025)
- 借鉴的架构思路:
  - 七 agent 架构(Orchestrator、Explorer、Oracle、Council、Librarian、Designer、Fixer、Observer)
  - 委派契约(路由阈值、派发效率、会话复用)
  - **per-agent 模型编排 preset**(参考其 `opencode-zen-free` preset:每个 agent 配独立 model/variant/temperature/skills/mcps;我们用 opencode 原生 agent frontmatter 实现,并提供 opencode-free/deepseek/mixed 三套)
  - deepwork 多阶段工作流
  - codemap 仓库地图生成
  - verification-planning 证据路径
  - reflect 会话反思

## 关于 opensoft/oh-my-opencode

**注意**:之前一度克隆的 `opensoft/oh-my-opencode` 经核实**不是原版**,是真原版 README 中警告的冒充/钓鱼生态的一部分。已弃用该参考,所有归因指向 `code-yeongyu/oh-my-openagent`。

## 本技能的许可证

MIT (见主仓库 LICENSE)

## 与上游的关键差异(本技能的安全硬化)

本技能在借鉴架构思路之上,加入了上游缺失或仅靠 prompt 自律的技术强约束:

1. **敏感目录禁区** — `~/.ssh`、`~/.aws`、`.git/`、`.env*`、`*.key` 等硬拒绝
2. **路径白名单** — 项目根锁定,写操作不得越界
3. **预算上限** — subagent 50k token / 10min,orchestrator 500k / 2h,并行成员 ≤8,耗尽冻结
4. **Doom-loop 检测** — 3 次相同调用暂停,必须用户介入
5. **禁止远程脚本执行** — 不 `curl|bash`、不自动 `npx install`、不自动启动 MCP 拉远程包
6. **无 OAuth 透传** — 不触碰 provider OAuth,不读凭证文件
7. **Stale work 降级** — 6h 无活动降为 paused(参考真原版 boulder-state #8413)
8. **Prototype 污染防护** — `__proto__`/`prototype`/`constructor` 键拒绝
9. **模型回退链** — 6 级回退,冷缓存哨兵(参考真原版 delegate-core)

详见 [rules/safety-hardening.md](rules/safety-hardening.md)。

## 上游安全风险记录(本技能已规避)

- 真原版 `code-yeongyu/oh-my-openagent` 的 README 明确:"Anthropic blocked OpenCode because of us" —— 该项目被 Anthropic 点名,有插件伪造 Claude Code OAuth 签名。本技能不触碰 OAuth。
- 两个上游推荐 `curl|bash` 或 `npx install` 远程安装模式;真原版警告了冒充钓鱼站点。本技能禁止远程脚本执行。
- 真原版的"never stop"模式(ultrawork、boulder、goal)虽有 max_wall_clock_minutes 等上限,但仍是软约束。本技能有硬预算冻结 + doom-loop 强制用户介入。
- 上游的写权限下放靠 prompt 自律,无路径白名单技术约束。本技能有 PROJECT_ROOT 锁定。