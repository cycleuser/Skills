# handwriting-ocr

把纸本/平板的手写笔记，经过「PaddleOCR → LLM 润色 → Markdown 索引」三步，转成可全文检索的 Markdown 笔记库。

- 输入：手机/扫描仪导出的手写扫描图（PNG/JPG）、iPad/平板导出的手写 PDF
- 输出：带「摘要 + 关键词索引 + 正文」的可检索 `.md`，以及 `INDEX.md` 目录索引

## 功能特性

- **批量 OCR**：支持图片与 PDF（自动拆页），PaddleOCR 本地推理，不依赖外部 API
- **GPU 加速**：有 NVIDIA 显卡时约 200 倍提速（`--device auto` 自动检测）
- **LLM 润色纠错**：合并断行、修正 OCR 错字（同音/形近字）、补全标点、按语义分段
- **自动摘要与关键词**：每份笔记生成摘要和关键词索引，便于全文检索与快速筛选
- **质量评估**：配合人工标注对照集，计算 CER/WER/关键词召回

## 安装

### CPU 版

```bash
pip install -r requirements.txt
```

### GPU 版（推荐，有 NVIDIA 显卡时）

```bash
pip uninstall paddlepaddle -y
pip install paddlepaddle-gpu==3.2.2 -i https://www.paddlepaddle.org.cn/packages/stable/cu126/
```

> `cu126` 对应 CUDA 12.6 驱动（`nvidia-smi` 右上角查看）；其他驱动版本替换为 `cu118` / `cu123`。

## 使用

```bash
# 完整流水线：批量 OCR → 产出 raw_ocr.json
python scripts/batch_ocr.py <笔记目录> --output raw_ocr.json --lang ch --device auto

# 按源文件拆分 raw OCR 文本
python scripts/dump_raw.py raw_ocr.json --out-dir . --format txt,md

# 评估打分（需人工标注对照集）
python scripts/evaluate.py <测试集目录> --report score_report.md --json metrics.json
```

完整工作流（含 LLM 润色协议、输出文件清单、常见坑）见 [SKILL.md](SKILL.md)。

## 目录结构

```
.
├── SKILL.md            # skill 定义与完整工作流说明
├── requirements.txt    # Python 依赖
├── scripts/
│   ├── batch_ocr.py    # 批量 OCR（PNG/JPG/PDF → raw_ocr.json）
│   ├── dump_raw.py     # raw_ocr.json 按源文件拆成 .raw.txt/.raw.md
│   └── evaluate.py     # 与人工标注对照集打分（CER/WER/关键词召回）
└── .gitignore
```

## License

MIT
