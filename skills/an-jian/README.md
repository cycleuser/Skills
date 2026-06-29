# 安检 (Security Review)

## 状态：Beta

## 用途
技能安装前的安全审查工具。通过静态代码分析检测危险模式（命令注入、凭证泄露、资源耗尽等），评估风险等级并提供自动修复方案，确保技能安装安全可靠。

## 快速命令
| 命令 | 说明 |
|------|------|
| `/安检 <技能路径>` | 审查指定技能安全 |
| `/安检 scan <路径>` | 深度扫描 |
| `/安检 list` | 列出已安装技能风险 |
| `/安检 fix <技能>` | 自动修复安全问题 |
| `/security <path>` | 英文版安全审查 |

## 适用场景
- 安装新技能前的安全审查
- 定期扫描已安装技能的安全风险
- 检测并修复技能中的危险命令和凭证泄露
- 评估外部依赖的供应链安全

## 依赖
- 依赖 `_shared/core/safety-rules.md` 共享安全规则

## 参见
- [ba-guan](../ba-guan) — 发布前审查中的安全审计层
- [shen-shi](../shen-shi) — 只读仓库审计模式
- [skill-refiner](../skill-refiner) — 修炼过程中修复安全缺陷

## 文件结构
```
skills/an-jian/
├── README.md
├── SKILL.md
└── rules/
    ├── dangerous-patterns.md
    ├── risk-assessment.md
    ├── fix-strategies.md
    ├── audit-format.md
    └── anti-aigc.md
```
