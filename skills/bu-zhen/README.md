# 布阵 (bu-zhen)

多 agent 编排技能,为 opencode 提供 **8 个真实 agent**(1 编排者 + 7 专家)的协作框架。

## 特性

- **8 个真实 opencode agent**:`bz-orchestrator`(primary)+ `bz-explorer`/`bz-oracle`/`bz-council`/`bz-librarian`/`bz-designer`/`bz-fixer`/`bz-observer`(subagent),各有独立模型、温度、权限
- **3 套 preset**:`opencode-free`(零成本)/ `deepseek` / `mixed`,脚本一键切换
- **config 层安全强制**:agent frontmatter 的 `permission` 由 opencode 在执行前拦截(敏感目录 deny、远程脚本 deny),实测写 `.git/` 被 opencode 直接拒绝
- **prompt 层规则**:预算上限、doom-loop 检测、stale-work 降级、prototype 污染防护、6 级模型回退、9 种委派错误检测
- **编排契约**:反重复规则、六段委派 prompt、自动继续、默认并行、task_id 失败重试、notepad 系统、boulder 完成响应
- **工作流**:deepwork 多阶段 + oracle gate、codemap 生成、验证规划、会话反思

## 命令

| Command | Description |
|---------|-------------|
| `/布阵 <task>` | 启动编排多 agent 工作 |
| `/布阵 plan <task>` | 仅规划不执行 |
| `/布阵 status` | 显示活跃 subagent 与预算 |
| `/布阵 stop` | 取消所有 subagent |
| `/布阵 review` | 请求 oracle 审查 |
| `/布阵 council <question>` | 多模型共识 |
| `/布阵 codemap` | 生成仓库地图 |
| `/布阵 deepwork <task>` | 高风险多阶段工作流 |
| `/布阵 reflect` | 会话反思 |
| `/布阵 verify` | 证据路径规划 |
| `/布阵 install` | 安装 8 个 bz-* agent 到全局 |
| `/布阵 preset <name>` | 切换模型预设 |

## 安装

### 方式 1:仅 skill(描述性契约)

把 `bu-zhen/` 放进 opencode skills 目录:

```
~/.config/opencode/skills/bu-zhen/
```

opencode 自动发现,`/布阵` 命令可用。此时专家角色靠 prompt 描述,派发时映射到内置 `explore`/`general`。

### 方式 2:完整安装(真实 agent + preset)

```bash
cd ~/.config/opencode/skills/bu-zhen

# 查看预设
python3 scripts/apply_preset.py list

# 切换并安装(推荐 deepseek 或 mixed,opencode zen 在你环境有证书问题)
python3 scripts/apply_preset.py deepseek --install

# 查看当前分配
python3 scripts/apply_preset.py status
```

安装后 opencode 原生识别 8 个 agent,orchestrator 可用
`task(subagent_type="bz-oracle")` 真实调用,各 agent 跑各自配置的模型。

## 目录结构

```
bu-zhen/
├── SKILL.md              # 技能主文档
├── ATTRIBUTION.md        # 归因与许可证
├── README.md
├── agents/               # 8 个真实 opencode agent 定义
│   ├── bz-orchestrator.md
│   ├── bz-explorer.md
│   ├── bz-oracle.md
│   ├── bz-council.md
│   ├── bz-librarian.md
│   ├── bz-designer.md
│   ├── bz-fixer.md
│   └── bz-observer.md
├── presets/              # 模型预设
│   ├── opencode-free.jsonc
│   ├── deepseek.jsonc
│   └── mixed.jsonc
├── scripts/
│   └── apply_preset.py   # preset 切换 + agent 安装
└── rules/                # 契约与安全规则
    ├── orchestrator-contract.md
    ├── specialist-prompts.md
    ├── safety-hardening.md
    ├── deepwork-protocol.md
    ├── codemap-workflow.md
    ├── verification-planning.md
    ├── reflect-workflow.md
    ├── retry-patterns.md
    └── anti-aigc.md
```

## 灵感来源与许可证

见 [ATTRIBUTION.md](ATTRIBUTION.md)。架构思路受 code-yeongyu/oh-my-openagent(真原版,SUL)与 alvinunreal/oh-my-opencode-slim(MIT)启发,所有 prompt 与规则为原创中文重写,并加入了上游缺失的安全硬化。MIT 许可证。
