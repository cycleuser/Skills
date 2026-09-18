# Reflect Workflow

回顾近期工作,发现重复工作流模式,建议可复用的 skill、agent、命令、配置改动或 playbook。用户要求从过往会话学习、改进重复工作流、或识别应转为可复用 agent 指令的内容时使用。

## 核心契约

Reflect 必须保守且基于证据。

必需行为:
- 提议前检视现有资产
- 优先近期、重复、用户可见的摩擦,而非孤立事件
- 推荐最小有用形态
- 证据弱时把"什么都不建"视为成功结果
- 改 prompt、skill、命令、agent、MCP 访问或配置前先问
- 避免重复现有资产
- 解释 opencode 配置/prompt/agent/skill/MCP/插件改动的重启要求

## 何时使用

用户要求:
- `/布阵 reflect` 或 `/布阵 reflect <focus>`
- `/布阵 reflect --sessions` 做会话考古
- 从近期会话或重复工作流学习
- 找一直手动做的事
- 基于实际使用改进 布阵 设置
- 审查重复流程是否应成可复用 playbook
- 把重复工作流摩擦转为更安全的未来默认

**不用于**普通实现工作、一次性调试、广泛架构审查、无工作流证据的投机 agent 创建。

## 会话模式

用户含 `--sessions` 时,转向会话考古:分析跨所有 repo 的历史 opencode 会话找重复模式、摩擦与改进机会。

### 会话发现

1. **加载近期会话** —— 直接查 SQLite 数据库:

```bash
python3 -c "import sqlite3, json; db = sqlite3.connect('$HOME/.local/share/opencode/opencode.db'); print(json.dumps(db.execute('SELECT id, directory, title, agent, model, time_created, cost, tokens_input, tokens_output FROM session ORDER BY time_created DESC LIMIT 50').fetchall(), default=str))"
```

按需调整 `LIMIT 50` 为 `--last N`。

**会话表列**: `id, directory, title, agent, model, time_created, cost, tokens_input, tokens_output`

2. **加载会话消息** —— 每会话 ID 查消息表:

```bash
python3 -c "import sqlite3, json; db = sqlite3.connect('$HOME/.local/share/opencode/opencode.db'); print(json.dumps(db.execute('SELECT data FROM message WHERE session_id = ?', ('<session_id>',)).fetchall(), default=str))"
```

**消息表列**: `id, session_id, time_created, time_updated, data`(data 为 JSON 含 role、agent、model、summary 等)

### 每会话分析

每会话分析与结构化摘要:

```json
{
  "session": "ses_14de9c68effegtZtlATm42wnz7",
  "project": "/home/user/Projects/bu-zhen",
  "timestamp": "2026-06-10T15:08:45.427Z",
  "goal": "修 CI 失败",
  "success": true,
  "frictions": [
    "反复 grep 找测试文件",
    "三次失败测试后才通过"
  ],
  "recommendations": [
    "创建 /test-ci 命令"
  ],
  "duration_minutes": 18,
  "models_used": ["opencode/mimo-v2.5-free"],
  "agents_used": ["orchestrator", "fixer", "explorer"],
  "tools_used": ["Read", "Edit", "Bash"],
  "confidence": 0.85
}
```

**置信度评分**:
- 0.9-1.0: 清晰成功/失败,明显模式
- 0.7-0.9: 可能结果,从工具使用推断模式
- 0.5-0.7: 不确定结果,证据有限
- <0.5: 跳过或标"需更多证据"

### 存储与缓存

会话摘要存 `~/.config/opencode/bu-zhen/reflections/sessions/`。

**缓存逻辑**:
1. 查 reflections 目录是否有 `<session-id>.json`
2. 有 → 加载(省 token)
3. 无 → 分析会话并存摘要
4. 跨所有摘要聚合最终报告

### 聚合

全部分析后聚合发现:
1. **按主题分组** —— 类似摩擦的会话聚类
2. **计频率** —— "42/50 会话编辑前反复 grep"
3. **按影响力排序** —— 优先最常出现的推荐
4. **过滤噪音** —— 跳过一次性问题,聚焦重复模式
5. **交叉引用** —— 看模式是否与特定 model、agent 或 repo 相关

**范围分类**:
- **全局** —— 适用于所有 repo(模式见 >50% repo)
- **跨 repo** —— 适用于模式出现的特定 repo
- **项目专属** —— 仅相关于一个 repo

### 输出格式

返回紧凑报告:

```
会话反思报告
分析跨 8 repo 的 50 个最近会话。

分析 repo:
- <repo> (<N> 会话)
- ... (M more)

发现
- <模式>: N/50 会话跨 M repo。
  - 范围: 全局 | 跨 repo (<repos>) | 项目专属 (<repo>)
  - 置信度: 0.95
  - 影响力: 高 | 中 | 低

推荐改动
- <资产>: <目的>
  - 范围: ...
  - 置信度: 0.97
  - 预计省时: 高 | 中 | 低

跳过
- <候选>: 为何现在不值得打包。
  - 范围: <原因>
  - 置信度: <分>

需更多证据
- <候选>: 什么会让它可行动。
  - 当前范围: <所见>
  - 所需范围: <什么能确认>
```

### 错误处理

**日志文件问题**:
- 日志不存在 → "在 <path> 未找到 opencode 日志。先在至少一个 repo 跑 opencode。"
- 日志空 → "opencode 日志为空。无会话可分析。"

**会话加载问题**:
- 会话 ID 不可加载 → 跳过并警告:"会话 <id> 无法加载,跳过。"
- 会话无消息 → 跳过:"会话 <id> 无消息。"

**恢复模式**:
- 记录失败
- 用剩余会话继续
- 末尾报告失败:"3 会话因加载错误跳过"

## 证据来源

按此顺序用可用证据:

1. 当前对话与显式用户指令
2. 项目本地指引与记忆,如 `AGENTS.md`、`.opencode/`、`.bu-zhen/`、笔记、检查点、任务进度文件、codemap
3. 现有 skill、命令、agent、prompt 覆盖、MCP 权限、布阵 配置
4. 近期 opencode 日志或会话产物(可用且安全检视时)
5. 仅当提议工作流依赖第三方工具或库、需确认其行为时用外部文档

尊重隐私与安全边界。**不**检视无关个人文件、凭证、私讯或外部账户,除非用户明确要求且工作流需要。

## 工作流

可直接触发:

```
/布阵 reflect
/布阵 reflect 发布工作流与检查
/布阵 reflect --sessions
/布阵 reflect --sessions --last 100
```

无参数 → 广泛回顾近期工作。有参数 → 聚焦该工作流区域,同时仍查现有资产是否已覆盖。

### 1. 盘点现有资产

提议前,识别已存在的:
- 内置与用户安装的 skill
- 自定义 agent 及其 orchestrator prompt 指引
- 自定义命令
- prompt 覆盖与追加文件
- 活跃 布阵 预设、model 路由、skill、MCP 权限
- 项目 playbook、文档、codemap、本地工作流笔记

现有资产已覆盖候选时,推荐扩展或使用该资产,而非创建近似重复。

### 2. 找重复工作流模式

找重复信号:
- 同命令序列跨会话出现
- 用户反复要求相同审查、设置、发布、调试流程
- 相同手动研究或上下文收集步骤反复
- 相同专家路由决策反复需要
- 相同项目专属规则反复重述
- agent 因缺稳定指令、工具或权限边界而反复失败

强候选通常至少出现两次、有稳定输入、清晰输出、清晰停止条件。

### 3. 评分候选

每候选判断:
- **频率**: 多常发生?
- **成本**: 浪费有意义时间、上下文、钱、注意力?
- **风险**: 不一致执行致 bug、回归、坏决策、不安全改动?
- **稳定性**: 输入与期望输出可预测?
- **覆盖**: 已有资产处理好?

仅在置信度高时推荐创建或改资产。

### 4. 选最小有用形态

选解决问题最弱形态:
- **Prompt/配置规则**: 现有 agent 的小行为改动
- **Skill**: 任务形状的可复用工作流指引
- **命令**: 稳定输入的可重复手动触发
- **自定义 agent**: 有清晰委派规则的独特专家 lane
- **MCP/工具权限改动**: 现有 agent 的安全访问调整
- **项目 playbook/文档**: 自动化太重时的可读流程指引
- **跳过**: 弱、一次性、模糊、敏感或已覆盖的工作

skill 够时避免创建自定义 agent。短 playbook 够时避免创建 skill。收益不清时避免配置改动。

### 5. 改前提议

除非用户明确要求特定编辑,写文件或改配置前呈现简明提议:

```
发现 2 个强重复工作流与 1 个弱候选。

推荐:
- 为 <工作流> 加一小 orchestrator prompt 规则,因为 <证据>。
- 扩展现有 <skill> 而非新建,因为 <重叠>。

跳过:
- <候选> 因仅出现一次。

执行提议的编辑吗?
```

应用改动时,保留现有用户设置,优先窄、仅追加的编辑。

## 护栏

- 不为证明工作流合理而制造资产
- 不创建重叠 skill 或 agent
- 不静默改全局配置、prompt 或权限
- 不加让 agent 更激进、更贵、更侵入的宽泛指令,无清晰收益时
- 不对单会话过拟合,除非用户明确要求该可复用工作流
- 不用私人或敏感材料作为生成资产的示例
- 配置/prompt/agent/skill/MCP/插件文件改动时告知用户:"这应在下次 opencode 运行时生效;需立即生效请重启 opencode。"

## 安全叠加

- 会话数据库查询用只读连接
- 反射产物不写入会话数据库,仅读
- 反射摘要不含 API key、不含文件内容片段,仅含路径、工具名、频率
- 反射目录 `~/.config/opencode/bu-zhen/reflections/` 不在敏感目录禁区,但仍受路径白名单保护(仅该子目录可写)