# 迭代管理器

## 状态：Beta

## 用途
自动化测试、验证和代码质量改进的迭代监督工具。在测试-分析-建议-应用-验证的循环中持续追踪质量指标，自动检测收敛趋势并生成详细迭代报告。

## 快速命令
| 命令 | 说明 |
|------|------|
| `/iterate <n>` | 运行 n 轮测试-改进迭代循环 |
| `/iterate stop` | 停止当前迭代循环 |
| `/iterate resume` | 恢复当前迭代循环 |
| `/iterate status` | 显示当前迭代状态 |
| `/iterate report` | 生成迭代报告 |

## 适用场景
- 需要自动化测试与反馈循环的代码质量保证
- 多轮迭代的回归测试与覆盖率提升
- 检测代码改进的收敛性和效果
- 生成结构化的迭代报告追踪历史

## 依赖
- 依赖 _shared/core/safety-rules.md

## 参见
- `/python-project test` from **python-project-developer** — 生成测试套件
- `/architect phase` from **master-architect** — 分阶段开发质量门
- `/把关 check` from **ba-guan** — 发布前质量验证

## 文件结构
```
skills/iteration-manager/
├── README.md
├── SKILL.md
└── rules/
    ├── testing-protocol.md
    ├── quality-metrics.md
    ├── iteration-workflow.md
    └── anti-aigc.md
```
