# 审视 (GitHub Triage)

## 状态：Beta

## 用途
只读 GitHub 审查技能。分析仓库的开放 Issues 和 PRs，进行分类、优先级评估、代码定位，生成有 GitHub permalink 证据支持的审查报告。

## 快速命令
| 命令 | 说明 |
|------|------|
| `/审视 <仓库>` | 分析仓库所有开放 Issue 和 PR |
| `/审视 issues <仓库>` | 只分析 Issues |
| `/审视 prs <仓库>` | 只分析 PRs |
| `/审视 <URL>` | 分析特定 Issue 或 PR |
| `/analyze <repo>` | 英文版仓库分析 |

## 适用场景
- 分析 GitHub 仓库的开放 Issues 和 PRs
- 问题分类与优先级评估（P0/P1/P2）
- 生成有代码级证据的审查报告
- 并行后台处理大量 Issue/PR

## 依赖
- 依赖 `_shared/core/safety-rules.md` 共享安全规则

## 参见
- [ba-guan](../ba-guan) — 基于证据模式的发布前审查
- [an-jian](../an-jian) — Issues 的安全分类审查

## 文件结构
```
skills/shen-shi/
├── README.md
├── SKILL.md
└── rules/
    ├── evidence.md
    ├── classification.md
    ├── report-format.md
    └── anti-aigc.md
```
