# Safety Hardening — 编排层专属安全规则

本文件定义 布阵 技能强制执行的安全约束。

**约束级别声明**:以下为**严格的 prompt 层约束**。在未配合 opencode `permission` 配置(见末尾"兑现技术强约束的可选配置")前,这些规则靠 agent 遵守 prompt,不构成系统级强制。我们诚实标注此局限,不自称"技术强约束"。

## 1. 敏感目录禁区

**规则**:orchestrator 及任何 subagent 不得对以下路径执行写入、删除、移动、重命名:

```
~/.ssh/
~/.aws/
~/.config/opencode/
~/.config/opencode-slim/
.git/
.env
.env.*
*.key
*.pem
*.p12
*.crt
credentials
credentials.*
```

**实现**:所有写/删/移动/重命名操作前:
1. 解析目标绝对路径
2. 若是 symlink,跟随到真实路径(`readlink -f`)
3. 与禁区列表比对(含 symlink 解析后的真实路径)
4. 命中即拒绝并报告"敏感目录禁区拦截: <path>(真实: <resolved>)"

**例外**:用户在当前会话中**显式书面授权**特定路径可豁免,且授权仅对该一次操作有效,不持久化。

## 2. 路径白名单

**规则**:所有写操作必须在项目根目录之内。项目根由首次 `/布阵` 调用时的 cwd 锁定。

**实现**(含 symlink 逃逸防护):
- 首次 `/布阵` 时记录 `PROJECT_ROOT = $(readlink -f cwd)`(解析 symlink)
- 每次写/删前:
  1. 解析目标绝对路径
  2. 若是 symlink,跟随到真实路径(`readlink -f`)
  3. 检查真实路径是否以 `PROJECT_ROOT` 开头
  4. 不在 → 拒绝并报告"写操作越界: <path>(真实: <resolved>) 在项目根 <PROJECT_ROOT> 之外"
- 用户显式要求写项目外(如共享配置)时,必须显式批准并单次扩展白名单;技能不自动扩展
- **symlink 逃逸防护**:项目内若存在指向 `~/.ssh`、`/etc` 等的 symlink,跟随解析后落在项目外即拒绝
- **创建指向禁区的 symlink**:在项目内创建指向禁区路径的 symlink 本身即拦截(创建是写操作,目标解析后落禁区即拒)

## 2.1 已知局限(诚实声明)

以下缺口在 prompt 层无法完全消除,需配合 opencode permission 配置或系统级 sandbox:

1. **读侧逃逸**:symlink 防护仅限写/删/移动/重命名。agent 经项目内 symlink 读取 `~/.ssh/id_rsa` 等敏感文件,本技能 prompt 层未拦。缓解:用 `permission.read` glob deny 敏感路径,或读前也做 symlink 跟随(增加成本)。
2. **TOCTOU(检查时序竞争)**:检查通过到实际写入之间,symlink 被替换为指向禁区的新 symlink 即逃逸。prompt 层无法原子化"检查+写入"。缓解:系统级 sandbox(如 macOS sandbox-exec、Linux landlock)或 opencode 工具层 fd 锁定。
3. **prompt 层固有限制**:以上全部规则靠 agent 遵守 prompt。恶意/被注入的 agent 可绕过。真正的技术强约束需 opencode permission 配置(见末尾"兑现技术强约束的可选配置")或 OS sandbox。

## 3. 预算上限

| 范围 | token 预算 | 时间预算 |
|------|-----------|----------|
| 单个 subagent | 50,000 | 10 分钟 |
| orchestrator 总计 | 500,000 | 2 小时 |
| council 单次调用 | 150,000 | 30 分钟 |
| 并行 subagent 数 | — | 最多 8 个(硬上限) |
| 单 subagent 最大轮次 | — | 500 步(防失控) |
| 单 subagent 最大消息 | — | 10000 条 |
| 邮箱消息载荷 | — | 32 KB(≥1 KB) |
| 收件人未读上限 | — | 256 KB(≥1 KB) |

**实现**:
- 每个 subagent 派发时记录起始 token 与起始时间
- orchestrator 维护累计计数器
- 任一预算达 80% → 警告用户
- 任一预算耗尽 → 冻结所有 subagent,报告"预算耗尽: <scope> 用 <tokens> token / <time>",询问用户是否追加预算或停止
- 预算不自动续期;用户显式批准才追加
- 并行 subagent 超过 8 个 → 拒绝新派发,排队等待空位(参考真原版 team_mode 的 max_members 硬上限)

## 3.1 Stale Work 降级

**硬规则**:活动中的工作(work)若 6 小时无活动,降级为 `paused`,释放资源。

**实现**:
- 记录每个工作的最后活动时间(最新会话 transcript mtime、updated_at、started_at 三者取新)
- 6h(可配 `BU_ZHEN_STALE_THRESHOLD_MS`)无活动 → 状态从 `active` 改 `paused`,记 `stale_since` 时间戳
- 恢复时(`task(task_id=...)` 或 `appendSessionId`)→ 回 `active` 并清 `stale_since`
- 无活动证据的工作直接判 stale
- `completed`/`abandoned` 状态永不降级
- 失败全部吞掉(永不因 stale 检测阻塞主流程)

**为何**:若会话异常死亡,工作会永远停在 `active`(参考真原版 boulder-state 的 reconcileStaleWorks,issue #8413)。降级让资源可被回收。

## 3.2 模型回退链

**硬规则**:委派时模型按以下顺序解析,每级失败回退下一级:

1. 用户显式模型覆盖(若可达);用户主模型不可达 → 提升第一个可达的 `fallback_models` 条目
2. 类目默认模型(用户配置原样返回;否则模糊匹配可用模型)
3. 用户 `fallback_models` 数组(按序,匹配第一个可达 provider)
4. 硬编码回退链(每条含 providers 列表 + model + variant,精确匹配 → 模糊匹配)
5. 系统默认模型
6. 全部不可达 → 返回 `undefined`,委派失败,报告用户

**冷缓存哨兵**:可用模型缓存与已连 provider 缓存都空时,返回 `{skipped: true}`,等待缓存填充而非选错模型。

**`-high` 模型**:按其 base 模型精确匹配,永不下放到非 high variant。

**变体传播**:匹配到回退链条目的 variant 流入结果。

## 3.3 Prototype 污染防护

**硬规则**:任务 upsert 拒绝 `__proto__`、`prototype`、`constructor` 三个保留键。

**实现**:
- 所有 task/会话/boulder 状态的键名比对保留键列表
- 命中 → 拒绝并报告"prototype 污染尝试: 键 '<key>' 被拒"
- 适用于 `.bu-zhen/boulder.json`、`audit.jsonl`、所有状态文件

## 4. Doom-Loop 检测

**硬规则**:同一 agent 以相同参数连续调用同一工具 3 次,即暂停并询问用户。

**实现**:
- 维护最近 5 次工具调用记录(agent名, 工具名, 参数哈希)
- 检测连续 3 次相同 → 暂停该 agent,报告"doom-loop 检测: <agent> 连续 3 次相同调用 <tool>",询问用户是否:
  - (a) 允许继续(记录用户授权,单次)
  - (b) 调整参数后继续
  - (c) 取消该 subagent

**不自动恢复**:doom-loop 触发后必须用户介入,技能不自行决定恢复。

## 5. 禁止远程脚本执行

**硬规则**:本技能不得执行以下任何操作(扩展黑名单):

```
# 管道执行远程脚本
curl <url> | bash
curl <url> | sh
wget <url> -O - | bash
wget <url> | sh

# 动态代码执行(可被注入远程 payload)
eval "<code>"
node -e "<code>"
python -c "<code>"
python3 -c "<code>"
ruby -e "<code>"
exec("<code>"

# 包管理器远程安装(未经用户确认)
npx <pkg>@latest install
pip install <pkg>
pip3 install <pkg>
npm install <pkg>
yarn add <pkg>
pnpm add <pkg>
bun add <pkg>
brew install <pkg>
go install <pkg>@latest
cargo install <pkg>
pipx install <pkg>

# 容器与镜像拉取
docker pull <image>
docker run <image>            # 自动拉取

# git 远程 + post-install hook
git clone <url>               # 克隆本身可接受,但不得自动跑其 install/scripts
```

**实现**:
- 所有 bash 命令前扫描命令文本(含管道后的解释器)
- 命中模式即拒绝并报告"禁止远程脚本执行: <command>"
- 用户明确要求安装某包时,技能**展示命令**但不自动执行,等用户确认
- MCP 子进程不自动启动;若需 MCP,用户必须手动配置并启动
- `eval`/`node -e`/`python -c` 等动态执行:仅在代码内容完全本地且用户可见时允许,且仍需扫描代码文本不含远程 fetch

**例外**:用户**显式书面**要求执行某个具体远程命令时,展示命令全文,等用户二次确认后才执行。`git clone` 本身允许(只读拉取),但克隆后不得自动执行仓库内任何 install/post-install 脚本。

## 6. 无 OAuth 透传

**硬规则**:本技能不触碰任何 provider OAuth 流程,不读取、不转发、不缓存 API key。

**实现**:
- 不调用任何 OAuth 端点
- 不读取 `~/.config/opencode/auth.json`、`~/.aws/credentials`、`~/.claude/.credentials.json` 等凭证文件
- 不在 prompt 或日志中包含 key 片段
- provider 配置由 opencode 本身管理,本技能不干预

## 7. Subagent 隔离

**硬规则**:subagent 之间不共享上下文,除显式通过 orchestrator 传递的结果。

**实现**:
- 每个 subagent 有独立会话
- subagent 不能直接调用其他 subagent
- 跨 subagent 数据必须经 orchestrator 调和
- subagent 不能修改全局配置(opencode.json、oh-my-opencode.json 等)

## 8. 审查预算强制

**硬规则**:Oracle 审查每个 gate 最多 1 次初查 + 2 次复查,总 3 次。

**实现**:
- 每个 gate 维护计数器
- 超出即拒绝并报告"审查预算耗尽: gate <n> 已用 3 次"
- 用户显式授权才能追加,且追加授权记录在案

## 9. 并行写范围冲突检测

**硬规则**:并行后台任务仅当写范围不冲突时允许。

**实现**:
- 派发前收集每个 subagent 的写所有权(目录或文件列表)
- 检测重叠 → 拒绝并行,要求串行或重新划分范围
- 报告"写范围冲突: <agent-a> 与 <agent-b> 都要写 <path>"

## 10. 日志与审计

**硬规则**:所有委派、预算消耗、安全拦截记录到会话日志。

**日志格式**(每条一行 JSONL):
```json
{"ts":"2026-09-18T15:30:00Z","event":"delegate","agent":"fixer","task_id":"t-1","budget_tokens":50000}
{"ts":"2026-09-18T15:30:05Z","event":"blocked","reason":"sensitive_dir","path":"~/.ssh/id_rsa"}
{"ts":"2026-09-18T15:30:10Z","event":"doom_loop","agent":"explorer","tool":"grep","count":3}
{"ts":"2026-09-18T15:30:15Z","event":"budget_exhausted","scope":"subagent","agent":"fixer","tokens":51200}
```

**日志位置**:`<PROJECT_ROOT>/.bu-zhen/audit.jsonl`(加入 .gitignore)

**隐私**:日志不含 API key、不含文件内容片段,仅含路径、工具名、预算数。

## 兑现技术强约束的可选配置

以上规则在 prompt 层是"严格约束",但要变成系统级强制,需在 opencode 配置中加 `permission` 规则。以下是可选的配置示例(用户按需添加到 `~/.config/opencode/opencode.json` 或项目 `.opencode/opencode.json`):

```jsonc
{
  "permission": {
    "edit": {
      // 敏感目录禁区:deny 写入
      "~/.ssh/**": "deny",
      "~/.aws/**": "deny",
      "**/.git/**": "deny",
      "**/.env": "deny",
      "**/.env.*": "deny",
      "**/*.key": "deny",
      "**/*.pem": "deny",
      "**/credentials": "deny",
      "**/credentials.*": "deny"
    },
    "bash": {
      // 远程脚本执行黑名单:deny
      "*": "ask",
      "curl *|*bash": "deny",
      "curl *|*sh": "deny",
      "wget *|*bash": "deny",
      "eval *": "deny",
      "node -e *": "deny",
      "python -c *": "deny",
      "python3 -c *": "deny",
      "npx *@latest install": "deny",
      "pip install *": "ask",
      "npm install *": "ask",
      "brew install *": "ask",
      "go install *@latest": "deny",
      "cargo install *": "ask",
      "docker pull *": "ask",
      "docker run *": "ask",
      // 安全读操作:allow
      "git status*": "allow",
      "git log*": "allow",
      "git diff*": "allow",
      "grep *": "allow",
      "ls *": "allow",
      "cat *": "allow"
    },
    "external_directory": "ask"
  }
}
```

**关键点**:
- `permission.edit` 的 glob 可 deny 敏感目录写入(系统级强制,不靠 prompt)
- `permission.bash` 的 glob 可 deny 远程脚本模式(系统级强制)
- `permission.external_directory: "ask"` 让写项目外目录前必须用户确认(路径白名单的技术兑现)
- 这份配置是可选的;不配置时,本技能仍靠 prompt 层约束;配置后,违规操作会被 opencode 本身拦截而非仅靠 agent 自律

**agent 层 permission(可选)**:若定义了 bu-zhen 专用 agent,可在其 frontmatter 加:

```yaml
---
permission:
  edit:
    "~/.ssh/**": deny
    "**/.git/**": deny
  bash:
    "curl *|*bash": deny
    "eval *": deny
---
```

这样该 agent 调工具时,opencode 在执行前就拦截,无需 agent 自觉遵守 prompt。