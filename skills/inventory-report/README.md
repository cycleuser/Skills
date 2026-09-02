# 盘点归纳 (Inventory & Report)

## 状态：Beta

## 用途

从任意杂乱目录盘点某类素材（成果、文献、证书、内容库、名单），定义分类法 → 全目录检索 → 多源交叉核验 → 输出结构化汇总（xlsx 表格 + 一段话总结 + 可选 docx 报告）。泛化于一切"整理一堆东西并交叉核对后给出汇总"的任务。

## 快速命令

| 命令 | 说明 |
|------|------|
| `/盘点 <目录> [主题]` | 盘点并生成汇总表 + 一段话总结 |
| `/盘点 核对 <清单>` | 多源交叉核验，输出证据链 |
| `/盘点 报告` | 生成 docx 版盘点报告 |
| `/inventory <dir> [topic]` | English alias |

## 适用场景

- 年度/学年成果盘点（论文、软著、专利、项目、获奖、指导学生获奖）
- 文献库整理与覆盖率核对
- 内容收藏（音频/视频/文本）统计与去重
- 证书台账、学生获奖名单、资产盘点

## 依赖

- Python：`openpyxl`、`pymupdf`、`rapidocr-onnxruntime`、`python-docx`、`PIL`
- 脚本：
  - `scripts/robust_xlsx.py` — WPS/异常 xlsx → 文本行（zipfile+XML 兜底）
  - `scripts/gen_summary.py` — 生成 xlsx 分类汇总表 + 一段话总结

## 参见

- [verify-deliver](../verify-deliver) — 交付前校验协议（本技能产出的表/报告用它自检）
- [academic-guide](../academic-guide) — 文献检索与引用核验（文献类盘点的细分场景）

## 文件结构

```
skills/inventory-report/
├── README.md
├── SKILL.md
├── rules/
│   ├── taxonomy.md      # 分类法与关键词检索
│   ├── verification.md  # 多源交叉核验协议
│   └── output.md        # 输出规范与口径铁律
└── scripts/
    ├── robust_xlsx.py
    └── gen_summary.py
```
