# 批量文件管道 (Batch File Pipeline)

## 状态：Beta

## 用途

对一批文件执行可复用的处理管道：方向检查与校正（OCR 检测旋转）、按命名规范统一重命名、格式转换、内容去重、完整性校验。泛化于一切"一批文件要统一处理整理"的任务。防丢失是硬约束：先验证新文件，再动旧文件。

## 快速命令

| 命令 | 说明 |
|------|------|
| `/批量文件 <目录> orient` | 检测图片旋转方向（OCR 盒坐标） |
| `/批量文件 <目录> rotate [角度]` | 批量旋转校正（默认自动检测） |
| `/批量文件 <目录> rename <映射.csv>` | 按映射批量重命名（先确认） |
| `/批量文件 <目录> dedupe` | SHA-256 去重（只报告疑似重复，不删） |
| `/批量文件 <目录> convert <目标格式>` | 批量格式转换 |
| `/批量文件 <目录> verify <正则>` | 校验命名规范 |
| `/batchfiles <dir> <action>` | English alias |

## 适用场景

- 扫描证书/照片批量旋转 + 按命名规范重命名
- 下载媒体（B站/音频/视频）统一命名整理
- PDF 批量重命名、批量格式转换（PDF↔图片、docx↔md）
- 文件去重、命名规范校验、批次清单生成

## 依赖

- Python：`PIL`、`rapidocr-onnxruntime`、`pymupdf`、`python-docx`
- 脚本：`scripts/batch_pipeline.py`

## 参见

- [verify-deliver](../verify-deliver) — 批处理后的防丢失校验
- [inventory-report](../inventory-report) — 批处理前的盘点与核验

## 文件结构

```
skills/batch-file-pipeline/
├── README.md
├── SKILL.md
├── rules/
│   ├── orientation.md   # OCR 旋转检测与校正
│   ├── naming.md        # 命名规范与重命名安全
│   └── safety.md        # 防丢失协议
└── scripts/
    └── batch_pipeline.py
```
