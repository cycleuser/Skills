# Skills 技能仓库

专为 AI 编码代理设计的专业技能集合。提供结构化工作流、模板和开发指南。

## 特性

- **11 个生产级技能** - 覆盖架构设计、开发、测试、写作、专利、公文、文本人化和强力迭代
- **10 个中文命令** - 完整中文支持
- **OpenCode 原生支持** - 完全兼容 OpenCode 技能系统
- **自动发现** - 根据上下文自动加载相应技能
- **模块化设计** - 每个技能自包含规则和模板
- **跨平台** - 支持 macOS、Linux 和 Windows

## 技能概览

| 技能 | 描述 | 适用场景 |
|-----|------|---------|
| **skill-manager** | 技能注册和管理系统 | 自动加载 |
| **master-architect** | 顶级软件架构师代理 | 架构设计 |
| **python-project-developer** | Python CLI/GUI 开发规范 | Python 项目 |
| **software-planner** | 多接口软件规划 | 项目规划 |
| **coding-agent-patterns** | AI 编码代理模式 | 开发模式 |
| **iteration-manager** | 迭代测试和改进 | 质量保证 |
| **academic-writer** | 学术论文写作助手 | 研究写作 |
| **patent-writer** | 专利撰写助手 | 专利申请 |
| **official-document-writer** | 公文撰写助手（GB/T 9704-2012） | 公文撰写 |
| **humanizer** | AI文本人化处理 | 自然语言处理 |
| **power-iterate** | 强力迭代 - 自主持续工作 | 时间/token预算工作 |

## 安装

### 一键安装（推荐）

```bash
curl -sSL https://raw.githubusercontent.com/cycleuser/Skills/main/quick-install-opencode.sh | bash
```

### Python 安装器

```bash
# 从 GitHub 安装
curl -sSL https://raw.githubusercontent.com/cycleuser/Skills/main/install-opencode.py | python3 install

# 或克隆后本地安装
git clone https://github.com/cycleuser/Skills.git
cd Skills
python3 install-opencode.py install --source .
```

### 各平台安装命令

**macOS / Linux:**
```bash
curl -fsSL https://raw.githubusercontent.com/cycleuser/Skills/main/quick-install-opencode.sh | bash
```

**Windows (PowerShell):**
```powershell
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/cycleuser/Skills/main/install-opencode.py" -OutFile "install-opencode.py"
python install-opencode.py install
```

**Windows (WSL):**
```bash
curl -fsSL https://raw.githubusercontent.com/cycleuser/Skills/main/quick-install-opencode.sh | bash
```

## 验证安装

```bash
# 列出已安装技能
python3 install-opencode.py list

# 查看技能详情
python3 install-opencode.py info --skills master-architect

# 检查安装目录
ls ~/.config/opencode/skills/
```

## 快速命令

安装后，在 OpenCode 中使用以下命令：

### 命令列表

| 命令 | 说明 |
|-----|------|
| `/架构 <任务>` | 系统架构设计 |
| `/开发 <任务>` | Python 项目开发 |
| `/规划 <任务>` | 软件规划 |
| `/迭代 <任务>` | 迭代测试改进 |
| `/强力迭代 <任务> [预算]` | 自主迭代直到预算耗尽 |
| `/论文 <任务>` | 学术论文写作 |
| `/专利 <任务>` | 专利撰写 |
| `/公文 <任务>` | 公文撰写 |
| `/人话 <文本>` | AI文本人化处理 |
| `/技能` | 列出所有技能 |

### 命令示例

```bash
/架构 构建一个文本挖掘系统
/开发 创建一个 CSV 分析工具
/规划 设计一个多平台应用
/迭代 提高测试覆盖率到 90%
/强力迭代 构建完整REST API --time 60 --tokens 100000
/论文 撰写一篇关于深度学习的论文
/专利 撰写一种图像识别方法的专利交底书
/公文 撰写一份关于加强安全生产工作的通知
/技能  # 列出所有技能
```

**注：** 英文命令请参阅 [README.md](README.md) 英文文档。

## 使用示例

### 示例 1：架构设计

在 OpenCode 中描述你的项目：

```
我需要设计一个文本挖掘系统，支持 CLI 和 GUI 界面，
能够处理大规模文本数据并生成可视化报告。
请帮我规划完整的架构。
```

OpenCode 会自动加载 `master-architect` 技能并提供：
- 需求分析
- 架构设计
- 模块分解
- 迭代开发计划

### 示例 2：Python 项目开发

```
创建一个 Python 命令行工具，用于分析 CSV 文件并生成统计报告。
需要支持 JSON 输出和详细日志模式。
```

技能将提供：
- 项目结构模板
- CLI 标准化参数
- ToolResult API 模式
- 测试用例模板

### 示例 3：迭代改进

```
运行测试套件，分析覆盖率，并提出改进建议。
目标是达到 90% 以上的代码覆盖率。
```

### 示例 4：学术写作

```
帮我撰写一篇关于深度学习在自然语言处理中应用的论文，
目标会议是 AAAI 2024。
```

## 技能分类

### 核心技能（自动加载）

| 技能 | 用途 |
|-----|------|
| skill-manager | 技能注册、发现和调用 |

### 架构与规划

| 技能 | 用途 |
|-----|------|
| master-architect | 顶级架构设计和迭代开发 |
| software-planner | 多接口项目规划（CLI+GUI+Web） |

### 开发

| 技能 | 用途 |
|-----|------|
| python-project-developer | Python CLI/GUI 开发与 ToolResult 模式 |
| coding-agent-patterns | AI 代理模式（Claude Code、Codex 等） |
| iteration-manager | 迭代测试和质量改进 |

### 文档

| 技能 | 用途 |
|-----|------|
| academic-writer | 学术论文写作（AAAI/IJCAI/IEEE） |

## 命令行管理

```bash
# 列出所有已安装技能
python3 install-opencode.py list

# 查看技能信息
python3 install-opencode.py info --skills <技能名>

# 安装特定技能
python3 install-opencode.py install --skills master-architect python-project-developer

# 安装到项目目录（而非全局）
python3 install-opencode.py install --local

# 卸载技能
python3 install-opencode.py uninstall --skills <技能名>
```

## 技能结构

每个技能遵循标准结构：

```
skill-name/
├── SKILL.md              # 主技能定义（含 frontmatter）
└── rules/
    ├── rule1.md          # 详细规则和模式
    └── rule2.md
```

### SKILL.md 格式

```yaml
---
name: skill-name
description: 技能简短描述
license: MIT
compatibility: opencode
metadata:
  version: "1.0.0"
  author: cycleuser
---

# 技能标题

详细的技能说明和模板...
```

## 技能触发条件

| 技能 | 触发关键词 |
|-----|-----------|
| master-architect | 架构设计, 系统设计, 模块分解, 项目规划 |
| python-project-developer | Python 项目, CLI 工具, GUI 应用, PyPI 发布 |
| software-planner | 开发计划, 项目规划, 接口设计 |
| iteration-manager | 迭代测试, 质量改进, 覆盖率, 测试套件 |
| academic-writer | 论文, 学术, AAAI, IEEE, 文献 |

## 与 AGENTS.md 配合

在项目根目录创建 `AGENTS.md`：

```markdown
# 项目说明

本项目使用 cycleuser/Skills 规范进行开发。

## 开发规范
- 遵循 python-project-developer 的 CLI 参数标准
- 使用 ToolResult 模式作为 API 返回类型
- 测试覆盖率要求 80% 以上
```

## 创建自定义技能

```bash
# 创建技能目录
mkdir -p skills/my-skill/rules

# 创建 SKILL.md
cat > skills/my-skill/SKILL.md << 'EOF'
---
name: my-skill
description: 技能描述
license: MIT
compatibility: opencode
---

# 我的技能

详细的指令说明。
EOF

# 添加规则
echo "# 规则标题\n\n规则内容..." > skills/my-skill/rules/my-rule.md

# 安装技能
python3 install-opencode.py install --source .
```

## 输出规范

### master-architect 输出格式

```markdown
# 系统架构文档

## 1. 概述
[系统描述]

## 2. 高层设计
[架构图]

## 3. 模块分解
| 模块 | 职责 | 依赖 |
|-----|------|-----|

## 4. 接口契约
[API 定义]

## 5. 技术栈
| 层 | 技术 | 理由 |
|---|-----|-----|
```

### python-project-developer 输出格式

```python
# 项目结构
project/
├── package_name/
│   ├── __init__.py
│   ├── core.py
│   ├── cli.py
│   └── api.py
├── tests/
├── pyproject.toml
└── README.md

# API 模式
@dataclass
class ToolResult:
    success: bool
    data: Any = None
    error: Optional[str] = None
    metadata: dict = field(default_factory=dict)
```

## 故障排除

### 技能未加载

1. 确认安装目录：`~/.config/opencode/skills/`
2. 检查 SKILL.md 文件是否存在
3. 验证 frontmatter 格式正确

### 权限问题

```bash
chmod +x quick-install-opencode.sh
```

### 重新安装

```bash
python3 install-opencode.py uninstall --skills <技能名>
python3 install-opencode.py install
```

## 文档

- [OpenCode 使用指南](OPENCODE_USAGE.md) - 详细使用示例
- [技能规范](skills.json) - 技能注册表
- [OpenCode 文档](https://opencode.ai/docs/skills/) - 官方文档

## 贡献

欢迎贡献！请：

1. Fork 本仓库
2. 创建功能分支
3. 按标准结构添加技能
4. 提交 Pull Request

## 许可证

MIT License - 详见 [LICENSE](LICENSE)

## 链接

- **GitHub**: https://github.com/cycleuser/Skills
- **问题反馈**: https://github.com/cycleuser/Skills/issues
- **发布版本**: https://github.com/cycleuser/Skills/releases
- **OpenCode**: https://opencode.ai