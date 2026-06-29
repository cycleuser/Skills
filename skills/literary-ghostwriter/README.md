# 文豪代笔 (Literary Ghostwriter)

## 状态：Beta

## 用途
模仿七位文学大师风格的创作技能，涵盖莎士比亚、茨维格、卡尔维诺三位西方作家和鲁迅、老舍、金庸、古龙四位中国作家。以"神似而非形似"为核心原则，深入把握作家的精神内核和创作机制进行创作。

## 快速命令
| 命令 | 说明 |
|------|------|
| `/文豪 <作家> <选题>` | 以指定作家风格进行中文创作 |
| `/literary <author> <topic>` | 以指定作家风格进行英文创作 |

## 适用场景
- 创意写作（小说、剧本、散文）
- 特定作家风格模仿练习
- 文学风格研究与分析
- 跨语言文学创作
- 多角色多风格对话场景

## 依赖
- 依赖 _shared/core/safety-rules.md

## 参见
- [brief-write](../brief-write/README.md) — 简洁写作风格
- [humanizer](../humanizer/README.md) — 检测文学模仿中的AI痕迹

## 文件结构
```
skills/literary-ghostwriter/
├── README.md
├── SKILL.md
└── rules/
    ├── anti-aigc.md
    ├── calvino-style.md
    ├── gulong-style.md
    ├── jinyong-style.md
    ├── laoshe-style.md
    ├── luxun-style.md
    ├── shakespeare-style.md
    ├── vocabulary.md
    └── zweig-style.md
```
