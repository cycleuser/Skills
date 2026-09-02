# 申报材料包 (Application Bundle)

## 状态：Beta

## 用途

把"申报/上报需求"组装成套：填表格模板（合并单元格保格式）→ 生成正文（事迹/申报书/报告）→ 匹配并嵌入证据附件图 → 统一命名打包。泛化于评优推荐、职称申报、课题申报、验收材料、答辩材料等一切"表格+正文+证据"型材料。

## 快速命令

| 命令 | 说明 |
|------|------|
| `/材料包 <需求>` | 组装整套申报材料（表格+正文+证据+打包） |
| `/材料包 填表 <模板.docx> <数据>` | 填写表格模板（合并单元格保格式） |
| `/材料包 正文 <内容>` | 生成事迹/申报正文 docx |
| `/材料包 证据 <清单>` | 收集并嵌入证据图（PDF→PNG） |
| `/材料包 打包 <目录>` | 整理成材料包目录 |
| `/bundle <req>` | English alias |

## 适用场景

- 优秀个人/先进集体推荐表 + 事迹材料 + 证书证据
- 职称申报表 + 业绩佐证材料册
- 课题申报书 + 支撑材料
- 验收/答辩材料打包

## 依赖

- Python：`python-docx`、`openpyxl`、`pymupdf`、`PIL`
- 脚本：`scripts/fill_docx.py`（表格解析/填充）、`scripts/embed_evidence.py`（证据图收集）
- 校验：复用 verify-deliver

## 参见

- [tianbiao](../tianbiao) — 通用模板填表（本技能聚焦"申报材料成套组装"）
- [docx-editor](../docx-editor) — 无损改 docx（本技能生成新材料，它改已有文档）
- [official-document-writer](../official-document-writer) — 公文正文撰写

## 文件结构

```
skills/application-bundle/
├── README.md
├── SKILL.md
├── rules/
│   ├── table-filling.md  # 合并单元格填写与保格式
│   ├── evidence.md       # 证据图收集与嵌入
│   └── packing.md        # 材料包目录与命名
└── scripts/
    ├── fill_docx.py
    └── embed_evidence.py
```
