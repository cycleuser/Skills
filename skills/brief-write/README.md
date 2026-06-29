# 简写 (Brief-Write)

## 状态：Beta

## 用途
模仿用户博客风格的写作技能，以简洁直接、口语化、真诚坦率的语言表达，避免"一眼AI"的写作模式。涵盖技术教程、技术解释、个人故事、观点讨论四类文体，以坦诚度、口语化、细节密度、简洁性、共情度五个维度评判写作质量。

## 快速命令
| 命令 | 说明 |
|------|------|
| `/简写 <主题或文本>` | 以用户风格写作或改写 |
| `/风格检查 <文本>` | 检查写作风格合规性 |
| `/write <topic/text>` | Write in user's style (English) |
| `/style-check <text>` | Check writing style compliance (English) |

## 适用场景
- 技术博客文章写作
- 技术教程与文档编写
- 个人故事和观点文章
- AI文本转为自然博客风格
- 风格一致性检查

## 依赖
- 依赖 _shared/core/safety-rules.md

## 参见
- [humanizer](../humanizer/README.md) — 互补的AIGC检测规避策略
- [literary-ghostwriter](../literary-ghostwriter/README.md) — 文学风格参考

## 文件结构
```
skills/brief-write/
├── README.md
├── SKILL.md
└── rules/
    ├── ai-patterns-avoid.md
    ├── anti-aigc.md
    └── user-style.md
```
