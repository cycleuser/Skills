# 学术论文写作助手

## 状态：Beta

## 用途
面向顶级会议和期刊的学术论文写作助手，支持 AIGC 检测规避和出版级图表质量控制。提供从选题分析、文献检索、引用格式、论文结构、图表生成到审稿回复的全流程支持。

## 快速命令
| 命令 | 说明 |
|------|------|
| `/paper new <topic>` | 选题分析、缺口识别与贡献映射 |
| `/paper search <keywords>` | 文献检索与整理 |
| `/paper cite` | 格式化引用（IEEE/ACM/APA/GB-T7714） |
| `/paper structure` | 生成论文大纲 |
| `/paper review` | 论文审校、润色与降低 AIGC 标记 |
| `/paper detect <text>` | 分析文本中的 AIGC 特征 |
| `/paper zh <topic>` | 撰写中文期刊论文（CCF/知网格式） |
| `/paper figures` | 生成出版级 SVG/PDF 图表 |
| `/paper rebuttal` | 起草审稿回复信 |

## 适用场景
- 撰写顶级会议（AAAI/NeurIPS/CVPR）或期刊论文
- 文献检索与引用格式化
- 降 AIGC 检测率润色
- 中文 CCF 期刊/知网论文写作
- 出版级 SVG/PDF 图表生成
- 审稿意见回复

## 依赖
- 依赖 _shared/core/safety-rules.md

## 参见
- `/人话` from **humanizer** — 人性化学术文本
- `/agent-patterns` from **coding-agent-patterns** — 研究工作流自动化
- `/python-project` from **python-project-developer** — 实验代码脚手架
- `/patent` from **patent-writer** — 学术到专利的桥接

## 文件结构
```
skills/academic-writer/
├── README.md
├── SKILL.md
└── rules/
    ├── anti-ai-patterns.md
    ├── anti-aigc.md
    ├── writing-style.md
    ├── literature-search.md
    ├── citation-format.md
    ├── paper-structure.md
    ├── figure-quality.md
    ├── reviewer-response.md
    └── opencode-experience.md
```
