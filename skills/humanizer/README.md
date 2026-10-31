# 人话 (Humanizer)

## 状态：Stable（2.0）

## 用途

把 AI 生成的文字改得像人写的。中英双语，两套特征库，量化阈值，可执行体检脚本。

和常见"去 AI 味"方案的区别：

- **先量再改**：`humanize_lint.py` 给出分数和分项，改写前后可对比，不靠感觉。
- **误杀边界**：每条特征都写明什么时候不该改，避免把专业文本改坏。
- **不编细节**：没有真实数据就标注待补，不许虚构案例。
- **承认局限**：目标是读起来像人，不是骗过检测器；检测器本身不可靠。

## 快速命令

| 命令 | 说明 |
|------|------|
| `/人话 <文本>` | 人化改写，自动判语言与文体 |
| `/人话 --style casual <文本>` | 口语体 |
| `/人话 --style formal <文本>` | 书面体 |
| `/人话 --mode light <文本>` | 只润色 |
| `/人话 --mode full <文本>` | 重写 |
| `/人话 check <文件\|文本>` | 只体检 |
| `/人话 diff <改写前> <改写后>` | 前后指标对比 |
| `/humanize <text>` | 英文命令 |
| `/detect <文本>` | 体检摘要 |
| `/demo` | 样例演示 |

## 直接用脚本

```bash
python3 scripts/humanize_lint.py check draft.md --lang zh --profile prose
python3 scripts/humanize_lint.py score draft.md
python3 scripts/humanize_lint.py check draft.md --json
cat draft.md | python3 scripts/humanize_lint.py score - --lang en
python3 scripts/humanize_lint.py rules
```

纯标准库，Python 3.9+，只读不改文件。退出码：分数超阈值返回 1。

自测：

```bash
python3 tests/test_lint.py    # 23 项
```

## 适用场景

- 博客 / 公众号 / 帖子去 AI 腔
- 学术论文、报告的表述润色（配合 academic-writer）
- 公文、总结材料（配合 official-document-writer）
- 专利说明书（配合 patent-writer）
- 英文写作（邮件、README、文章）
- 批量体检：对一整个目录跑分数，挑出最像 AI 的几篇先改

## 文件结构

```
skills/humanizer/
├── SKILL.md                        # 入口：命令、工作流、硬约束
├── README.md
├── rules/
│   ├── zh-patterns.md              # 中文 Z01–Z29
│   ├── en-patterns.md              # 英文 E01–E25
│   ├── metrics.md                  # 阈值与 profile
│   ├── rewrite-protocol.md         # 五遍法 + 自检 10 条
│   ├── ai-features.md              # 五维模型与评分
│   ├── humanization.md             # 口语化策略
│   ├── formal-humanization.md      # 书面化策略
│   ├── iteration.md                # 迭代流程
│   ├── examples.md                 # 前后对照
│   ├── detection-methods.md        # 检测器原理与局限
│   └── anti-aigc.md                # 薄索引
├── scripts/humanize_lint.py        # 双语体检器
├── tests/                          # 自测 + 中英对照样本
└── references/                     # 研究底稿（含出处与倍数）
```

## 依赖

- 依赖 `_shared/core/safety-rules.md`
- 脚本：Python 3.9+，仅标准库

## 参见

- [brief-write](../brief-write/README.md) — 用户博客口吻
- [academic-writer](../academic-writer/SKILL.md) — 学术写作
- [official-document-writer](../official-document-writer/SKILL.md) — 公文
- [patent-writer](../patent-writer/SKILL.md) — 专利
- [you-ju](../you-ju/SKILL.md) — 防幻觉审计（人化前先过一遍）
