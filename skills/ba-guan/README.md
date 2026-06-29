# 把关 (Pre-Publish Review)

## 状态：Beta

## 用途
发布前的多层深度审查技能。通过逐变更分析、多角色并行审查（架构师/开发者/测试员/安全专家/文档）和综合评估，确保发布代码的质量与安全。

## 快速命令
| 命令 | 说明 |
|------|------|
| `/把关` | 启动完整发布前审查 |
| `/把关 check` | 检查未发布变更 |
| `/把关 version` | 建议版本号升级 |
| `/把关 report` | 生成审查报告 |
| `/review <task>` | 英文版发布前审查 |

## 适用场景
- npm 包发布前的质量审查
- 代码变更的深度分析与风险评估
- 版本升级建议（major/minor/patch）
- 多角色并行审查与综合报告生成

## 依赖
- 依赖 `_shared/core/safety-rules.md` 共享安全规则

## 参见
- [an-jian](../an-jian) — 发布审查中的安全审计层
- [master-architect](../master-architect) — 架构审查层
- [he-bing](../he-bing) — 审查通过后的 PR 工作流

## 文件结构
```
skills/ba-guan/
├── README.md
├── SKILL.md
└── rules/
    ├── change-detection.md
    ├── review-roles.md
    ├── version-bump.md
    └── anti-aigc.md
```
