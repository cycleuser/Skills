# 技能管理器

## 状态：Beta

## 用途
技能注册中心与管理中枢，在会话启动时自动加载，负责发现、列出、激活和重载工作区内的所有技能。

## 快速命令
| 命令 | 说明 |
|------|------|
| `/skills` | 列出所有可用技能及描述 |
| `/skill <name>` | 加载并激活指定技能 |
| `/skill help <name>` | 查看技能详细帮助 |
| `/skill reload` | 刷新技能注册表 |

## 适用场景
- 发现和浏览工作区中所有可用技能
- 动态加载某个技能到当前会话
- 添加/修改技能后刷新注册表
- 查看技能的版本、触发条件和命令列表

## 依赖
- 依赖 _shared/core/safety-rules.md

## 参见
- skill-refiner — 优化打磨注册表中的技能
- coding-agent-patterns — 技能内存系统与加载模式

## 文件结构
```
skills/skill-manager/
├── README.md
├── SKILL.md
└── rules/
    └── registry.md
```
