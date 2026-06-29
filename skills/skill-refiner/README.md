# 修炼 (Skill Refiner)

## 状态：Beta

## 用途
技能打磨系统，对任意技能从完整性、可读性、实用性、一致性、可扩展性五个维度进行诊断，生成改进方案并迭代优化，直到技能达到最优状态。支持快速、标准、深度三种修炼策略。

## 快速命令
| 命令 | 说明 |
|------|------|
| `/修炼 <技能名>` | 打磨指定技能 |
| `/refine <skill>` | Refine a specific skill (English) |

## 适用场景
- 新技能编写后的质量检查与优化
- 已有技能的文档改进和规则完善
- 技能版本升级前的全面审查
- 多技能风格统一化和标准化
- 技能缺陷定位与修复

## 依赖
- 依赖 _shared/core/safety-rules.md

## 参见
- [skill-manager](../../.opencode/skills/skill-manager/SKILL.md) — 技能注册管理
- [an-jian](../../.opencode/skills/an-jian/SKILL.md) — 安全审计

## 文件结构
```
skills/skill-refiner/
├── README.md
├── SKILL.md
└── rules/
    ├── anti-aigc.md
    ├── diagnosis.md
    ├── improvement.md
    ├── templates.md
    └── validation.md
```
