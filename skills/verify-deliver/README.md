# 先验证后交付 (Verify Before Deliver)

## 状态：Beta

## 用途

一切任务交付前的强制验证协议。把用户最高频的期望——"先自己完整测试验证，解决所有问题再汇报；要真实执行，不要只描述"——固化成五步交付协议：真实执行 → 校验清单 → 修复循环 → 无损确认 → 先结论后证据汇报。

## 快速命令

| 命令 | 说明 |
|------|------|
| `/先验证` | 进入交付前验证模式：列出产物、跑校验、修复、汇报 |
| `/先验证 check <产物>` | 对指定产物运行校验清单 |
| `/先验证 报告` | 输出验证结果与修复记录 |
| `/verify <artifact>` | English alias |

## 适用场景

- 任何交付前的自查（写代码/改文档/生成表图/填表/批量处理/论文排版）
- 需要"只有我改的那一处变了，其余未动"的审计场景
- 批量处理防文件丢失、数字多源一致性、格式保真

## 依赖

- 校验脚本 `scripts/verify.py`：docx/xlsx/pdf/图片可打开性、文本导出、类别计数、命名规范、图片方向（OCR）
- Python 依赖：`python-docx`、`openpyxl`、`pymupdf`、`PIL`、`rapidocr-onnxruntime`

## 参见

- [iteration-manager](../iteration-manager) — 代码迭代测试改进（本技能覆盖一切产物的交付前验证，侧重文档/表格/文件类）
- [tianbiao](../tianbiao) — 模板填表的格式保真校验
- [docx-editor](../docx-editor) — 改 docx 后校验"只有目标部件变了"

## 文件结构

```
skills/verify-deliver/
├── README.md
├── SKILL.md
├── rules/
│   ├── checklists.md    # 各产物类型校验清单
│   ├── fix-loop.md      # 修复-重验循环协议
│   └── reporting.md     # 汇报顺序与话术
└── scripts/
    └── verify.py        # 通用校验工具
```
