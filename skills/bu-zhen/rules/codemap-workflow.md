# Codemap Workflow

为不熟悉的仓库生成层次化 codemap。昂贵操作 —— 仅当明确要求代码库文档或初始仓库映射时使用。

## 何时使用

- 用户要求理解/映射仓库
- 用户想要代码库文档
- 开始在不熟悉的代码库上工作

## 工作流

### 步骤 1:检查现有状态

先检查项目根 `.bu-zhen/codemap.json` 是否存在。

- 不存在 → 继续步骤 2(初始化)
- 存在 → 跳到步骤 3(检测变更)

### 步骤 2:初始化(仅无状态时)

1. **分析仓库结构** —— 列文件,理解目录
2. **仅对核心代码/配置文件推断包含模式**:
   - **包含**: `src/**/*.ts`、`package.json` 等
   - **强制排除**: 不含测试、文档、翻译
     - 测试: `**/*.test.ts`、`**/*.spec.ts`、`tests/**`、`__tests__/**`
     - 文档: `docs/**`、`*.md`(除根 `README.md` 若需要)、`LICENSE`
     - 构建/依赖: `node_modules/**`、`dist/**`、`build/**`、`*.min.js`
   - 自动尊重 `.gitignore`

3. **生成 codemap 状态文件** —— 记录文件与文件夹哈希用于变更检测

4. **委派 codemap 写作给 fixer agent** —— 每文件夹一个 fixer,读代码并创建或更新该文件夹的 `codemap.md`

**安全约束**:
- codemap 写作仅用只读工具(grep/glob/read)
- 不启动任何 MCP 子进程
- 不拉远程脚本

### 步骤 3:检测变更(状态已存在时)

1. 重算哈希对比,显示:新增、删除、修改文件,受影响文件夹
2. 仅更新受影响 codemap —— 每受影响文件夹一个 fixer 更新其 `codemap.md`
3. 更新状态文件

### 步骤 4:完成仓库图集(根 Codemap)

所有特定目录映射后,orchestrator 创建或更新根 `codemap.md`。此文件是任何进入仓库的 agent 或人的**主入口**。

1. **映射根资产**:记录根级文件(如 `package.json`、`index.ts`)与项目整体目的
2. **聚合子图**:创建"仓库目录图"段。每个有 `codemap.md` 的文件夹,提取其**职责**摘要,以表或列表纳入根图
3. **交叉引用**:根图含子图绝对/相对路径,agent 可直接跳到相关详情

### 步骤 5:在 AGENTS.md 注册 Codemap

opencode 自动加载 `AGENTS.md` 到每会话上下文。确保 agent 自动发现并使用 codemap:

1. `AGENTS.md` 已有 `## Repository Map` 段 → 跳过
2. 有 `AGENTS.md` 无此段 → 追加
3. 无 `AGENTS.md` → 创建含此段

```markdown
## Repository Map

完整 codemap 在项目根的 `codemap.md`。

开始任何任务前,读 `codemap.md` 理解:
- 项目架构与入口点
- 目录职责与设计模式
- 模块间数据流与集成点

深入某文件夹工作时,也读该文件夹的 `codemap.md`。
```

此操作幂等 —— 重复 codemap 运行会检测已有段并跳过,无重复。

## Codemap 内容

fixer 在此工作流中负责写 `codemap.md` 文件。用精确技术术语记录实现:

- **职责** —— 用标准软件工程术语定义该目录的具体角色(如"服务层"、"数据访问对象"、"中间件")
- **设计模式** —— 识别并命名使用的具体模式(如"观察者"、"单例"、"工厂"、"策略")。详述抽象与接口
- **数据与控制流** —— 显式追踪数据如何进出模块。提及具体函数调用序列与状态转换
- **集成点** —— 列依赖与消费者模块。用技术名指代 hook、事件、API 端点

### 示例 codemap

```markdown
# src/agents/

## 职责
定义 agent 人格并管理其配置生命周期。

## 设计
每个 agent = prompt + 权限集。配置系统:
- 默认 prompt(orchestrator.ts、explorer.ts 等)
- 来自 ~/.config/opencode/ 的用户覆盖
- skill/MCP 访问控制的权限通配符

## 流
1. 插件加载 → 调 getAgentConfigs()
2. 读用户配置预设
3. 合并默认与覆盖
4. 应用权限规则(通配符扩展)
5. 返回 agent 配置给 opencode

## 集成
- 被消费于:主插件(src/index.ts)
- 依赖:配置加载器、skills 注册表
```

### 示例根 Codemap(图集)

```markdown
# 仓库图集: 布阵

## 项目职责
为 opencode 提供多 agent 编排技能,聚焦专家 subagent 委派与安全硬化。

## 系统入口
- `SKILL.md`: 技能定义与 frontmatter
- `rules/`: 角色契约与安全规则
- `package.json`: 依赖清单与构建脚本

## 目录图(聚合)
| 目录 | 职责摘要 | 详细图 |
|------|---------|--------|
| `rules/` | 编排契约、专家 prompt、安全硬化、deepwork 协议 | [查看](rules/codemap.md) |
| `_shared/` | 跨技能共享安全规则与模板 | [查看](_shared/codemap.md) |
```

## 安全约束(本工作流专属)

- **只读优先**:codemap 生成仅用 grep/glob/read
- **无远程拉取**:不启动 MCP 子进程,不 `npx install`,不 `curl|bash`
- **路径白名单**:codemap 写入仅限 `.bu-zhen/codemap.json`、`codemap.md`、`AGENTS.md`;不碰敏感目录
- **预算**:整个 codemap 生成预算 100k token / 30 分钟;超出即暂停问用户
- **敏感文件不映射**:`.env*`、`*.key`、`*.pem`、`credentials` 不纳入 codemap,不读其内容