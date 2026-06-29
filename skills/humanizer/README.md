# 人话 (Humanizer)

## 状态：Stable

## 用途
AI文本人化处理技能，基于AIGC检测原理将AI生成文本转化为自然人类语言。通过困惑度、突发性、词汇分布等多维度检测，以六种反检测策略进行多轮迭代优化，支持中英双语、口语和书面两种风格。

## 快速命令
| 命令 | 说明 |
|------|------|
| `/人话 <文本>` | 人化处理文本 |
| `/人话 --style formal <文本>` | 书面风格人化 |
| `/人话 --style casual <文本>` | 口语风格人化 |
| `/humanize <text>` | Humanize AI-generated text (English) |
| `/detect <文本>` | 检测AIGC特征 |
| `/demo` | 生成示例并演示处理 |

## 适用场景
- 降低AI生成文本的AIGC检测率
- 将AI写作优化为自然人类语言
- 学术论文去AI化（配合academic-writer）
- 公文人化处理（配合official-document-writer）
- 专利文本人化（配合patent-writer）
- 博客文章自然化（配合brief-write）

## 依赖
- 依赖 _shared/core/safety-rules.md

## 参见
- [brief-write](../brief-write/README.md) — 博客风格写作
- [academic-writer](../../.opencode/skills/academic-writer/SKILL.md) — 学术写作
- [official-document-writer](../../.opencode/skills/official-document-writer/SKILL.md) — 公文写作
- [patent-writer](../../.opencode/skills/patent-writer/SKILL.md) — 专利写作

## 文件结构
```
skills/humanizer/
├── README.md
├── SKILL.md
└── rules/
    ├── ai-features.md
    ├── anti-aigc.md
    ├── detection-methods.md
    ├── examples.md
    ├── formal-humanization.md
    ├── humanization.md
    └── iteration.md
```
