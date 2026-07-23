# 学术导览 (Academic Guide)

## 状态：Beta

## 用途
学科入门导览工具。四步流程帮助初学者快速掌握一个新学科领域的概况：搜索近三年博士论文、整理领域内公认的专业站点和数据库、全程保留搜索记录、逐条验证每条引用链接。

## 快速命令
| 命令 | 说明 |
|------|------|
| `/学术导览 <领域名称>` | 完整四步学术导览流程 |
| `/导览 论文 <领域>` | 仅搜索博士论文 |
| `/导览 站点 <领域>` | 仅整理专业站点 |
| `/导览 验证 <报告>` | 仅验证参考文献链接 |
| `/AcademicGuide <field>` | English full workflow |
| `/guide dissertations <field>` | Search dissertations only |
| `/guide sites <field>` | Compile sites only |
| `/guide verify <report>` | Verify citations only |

## 适用场景
- 研究生选定新课题方向前的快速摸底
- 跨学科研究者了解新领域的核心文献和资源
- 报考研/博前了解目标领域的学术活跃度
- 写综述论文前收集领域博士论文和核心站点
- 验证已有学术资源链接的有效性

## 核心原则
1. **可验证性** — 每条引用必须经过独立打开验证，标注✅/⚠️/❌状态
2. **搜索透明** — 每次搜索记录时间、关键词、来源、结果数
3. **引用就绪** — 输出即引用，参考文献列表脱离上下文也能验证

## 依赖
- 依赖 `_shared/core/safety-rules.md` 共享安全规则

## 参见
- [academic-writer](../academic-writer) — 学术论文写作及深度文献搜索
- [bao-kao](../bao-kao) — 多源搜索交叉验证模式
- [shen-shi](../shen-shi) — 基于证据的分析与引用方法论

## 文件结构
```
skills/academic-guide/
├── README.md
├── SKILL.md
└── rules/
    ├── dissertation-search.md
    ├── professional-sites.md
    ├── search-records.md
    ├── citation-verification.md
    ├── output-format.md
    └── anti-aigc.md
```
