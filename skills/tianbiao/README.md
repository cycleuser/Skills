# 填表 (TianBiao)

## 状态：Beta

## 用途

模板保真填表技能。面对固定格式的学校/机关表格（成绩单、试卷质量分析表、成绩分析表、过程性评价档案、考查课报告等），**复制原模板，把真实数据填进对应单元格，并严格保持原有字体、边框、合并单元格和版式**，绝不从零重排。

核心一句话：照着原表填，不重排。

## 快速命令

| 命令 | 说明 |
|------|------|
| `/填表 <模板> <数据>` | 按模板填充数据，保持格式 |
| `/填表 convert <文件>` | 将 .doc/.xls 模板转为可编辑的 .docx/.xlsx |
| `/填表 inspect <模板>` | 填写前摸清模板的表格/单元格/字体结构 |
| `/填表 check <文档>` | 校验填好文档的格式保真度与数据一致性 |
| `/tianbiao <template> <data>` | Fill template preserving format |
| `/tianbiao convert <file>` | Convert legacy template |
| `/tianbiao inspect <template>` | Map template structure |
| `/tianbiao check <doc>` | Verify fidelity & data |

## 适用场景

- 学校期末材料：试卷质量分析表、成绩分析表、过程性评价档案等按固定模板填写
- 任何"表头固定、需批量填人名/分数"的表格
- 老 `.doc`/`.xls` 模板转换后精确填充
- 需要输出与原模板**一模一样**格式的正式表格

## 为什么需要它

用 python-docx 从零画表，会让字体、字号、边框、行高、合并单元格全部走样；批量名单还容易松散跨页、翻页丢表头、行被拦腰截断。本技能的做法是：打开**原模板**只改单元格文字、继承原字体，明细表用"表头跨页重复 + 行不断裂 + 紧凑小字号"保持规整。

## 五步工作流

1. **转换** Convert：`.doc/.xls` → `.docx/.xlsx`（LibreOffice headless 保真）
2. **摸底** Inspect：读出模板表格结构、合并单元格、关键单元格字体
3. **备数据** Prepare：从源文件提取结构化数据，必要时反推计算公式并全样本验证
4. **填充** Fill：在原模板上按可见单元格定位填值；明细表用紧凑防散架表格
5. **校验** Verify：核对表结构/字体/数据一致性，无占位符残留、无模板示例残留

## 依赖

- Python 库：`python-docx`（Word）、`openpyxl`（Excel .xlsx）、`xlrd`（读 .xls）
- 转换引擎：LibreOffice（`soffice --headless`）；macOS 缺失时 `brew reinstall --cask libreoffice`
- 依赖 `_shared/core/safety-rules.md`

## 数据与合规原则

- **永不覆盖原模板**，输出为新文件（`<主体>-<文档名>`）
- 数据真实可追溯，缺失项留空并标注"需人工补"，不编造
- 分析文字客观中性：不贬损教师学识、不否定学生；实践类课程强调依学情动态调整、反对僵化固定课时；客观条件（设备/场地）优先归因

## 文件结构

```
skills/tianbiao/
├── README.md
├── SKILL.md
├── rules/
│   ├── workflow.md              # 五步工作流与命令行操作
│   ├── format-preservation.md   # 保格式的 OOXML 技术
│   ├── data-integrity.md        # 数据提取、公式反推与校验
│   ├── writing-analysis.md      # 分析类文字填写原则
│   └── anti-aigc.md             # 反AIGC与套话规避
└── scripts/
    └── fill_docx_template.py    # 可复用填表工具函数库
```

## 参见

- `/公文` from **official-document-writer** — 需要从零撰写公文正文时
- `/人话` from **humanizer** — 分析类文字需要更自然、去AI味时
