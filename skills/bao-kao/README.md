# 报考 (Bao-Kao)

## 状态：Beta

## 用途
类似资深报考顾问风格的高考和考研报考指导技能，从官方教育网站搜索公开数据并进行交叉对比分析，给出直接、有观点、有数据的实用建议。内置31省10年分数线数据和吉林省高校/专业就业数据。

## 快速命令
| 命令 | 说明 |
|------|------|
| `/报考 <查询内容>` | 搜索分析报考数据 |
| `/专业 <专业名>` | 分析专业就业前景 |
| `/学校 <学校名>` | 分析学校录取数据 |
| `/一分一段 <省份年份>` | 查询分数排名表 |
| `/分数线 <学校专业>` | 查询录取分数线 |
| `/enroll <query>` | Search enrollment data (English) |
| `/major <name>` | Analyze major prospects (English) |
| `/school <name>` | Analyze school data (English) |

## 适用场景
- 高考志愿填报分析与建议
- 考研院校专业选择指导
- 专业就业前景评估
- 历年分数线趋势分析
- 分数排名定位与院校匹配

## 依赖
- 依赖 _shared/core/safety-rules.md

## 参见
- [humanizer](../humanizer/README.md) — 人化报考咨询回复

## 文件结构
```
skills/bao-kao/
├── README.md
├── SKILL.md
└── rules/
    ├── analysis-methods.md
    ├── anti-aigc.md
    ├── consultant-style.md
    ├── data-sources.md
    ├── search-methods.md
    └── taboo-list.md
```
