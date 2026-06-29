# 公文写作助手

## 状态：Beta

## 用途
基于 GB/T 9704-2012 国家标准的党政机关公文写作助手。支持 15 种法定公文类型的撰写、格式规范检查和排版要求，确保公文符合国家标准。

## 快速命令
| 命令 | 说明 |
|------|------|
| `/gongwen notice <topic>` | 撰写通知 |
| `/gongwen report <topic>` | 撰写报告 |
| `/gongwen request <topic>` | 撰写请示 |
| `/gongwen reply <topic>` | 撰写批复 |
| `/gongwen letter <topic>` | 撰写函 |
| `/gongwen minutes <topic>` | 撰写纪要 |
| `/gongwen check <document>` | 检查公文合规性 |
| `/gongwen format` | 显示 GB/T 9704-2012 格式规范 |

## 适用场景
- 撰写党政机关通知、报告、请示等公文
- 检查公文格式是否符合 GB/T 9704-2012 标准
- 学习层次序号、字体字号、页面设置等排版规范
- 公文合规性审查

## 依赖
- 依赖 _shared/core/safety-rules.md

## 参见
- `/人话` from **humanizer** — 在适当场景下将公文语言人化处理

## 文件结构
```
skills/official-document-writer/
├── README.md
├── SKILL.md
└── rules/
    ├── document-types.md
    ├── formatting-rules.md
    ├── writing-guidelines.md
    ├── templates.md
    └── anti-aigc.md
```
