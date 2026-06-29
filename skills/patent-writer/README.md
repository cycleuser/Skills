# 专利撰写助手

## 状态：Beta

## 用途
面向中国专利申请的撰写助手，覆盖专利检索、交底书撰写、专利三性分析、申请流程指导和策略建议。帮助发明人完成从技术交底到提交的全流程准备。

## 快速命令
| 命令 | 说明 |
|------|------|
| `/patent search <keywords>` | 专利检索与现有技术分析 |
| `/patent disclosure <invention>` | 撰写专利交底书 |
| `/patent report <invention>` | 生成自检索报告与授权风险评估 |
| `/patent workflow` | 显示专利申请流程与时间线 |
| `/patent strategy <invention>` | 提供申请策略建议 |
| `/patent check <document>` | 检查专利文档合规性 |
| `/patent examples` | 展示专利撰写范例与最佳实践 |

## 适用场景
- 专利申请前的现有技术检索
- 发明专利/实用新型交底书撰写
- 专利三性（新颖性、创造性、实用性）分析
- 申请策略与时间线规划
- 交底书合规审查

## 依赖
- 依赖 _shared/core/safety-rules.md

## 参见
- `/paper` from **academic-writer** — 文献检索辅助现有技术分析
- `/人话` from **humanizer** — 人化专利描述文本

## 文件结构
```
skills/patent-writer/
├── README.md
├── SKILL.md
└── rules/
    ├── patent-search.md
    ├── disclosure-document.md
    ├── patent-workflow.md
    ├── writing-tips.md
    └── anti-aigc.md
```
