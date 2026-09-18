---
name: handwriting-ocr
version: "0.1.0"
description: |
  手写笔记 OCR 流水线：将纸本扫描图与平板 PDF 导出的手写笔记转成可检索的 Markdown。

  触发条件：用户提供一批图片（PNG/JPG）或 PDF，需要 OCR 转文字、做润色/纠错、加摘要索引；
  或者需要评估这个流水线本身在人工标注对照集上的 CER/WER/检索召回打分。

  命令：
  - /ocr-notes <目录> - 批量 OCR + LLM 润色 + 生成 MD
  - /ocr-notes refine <raw_ocr.json> - 仅做润色（OCR 已跑过）
  - /ocr-notes eval <测试集目录> - 评估打分（需人工标注对照集）
  - /ocr-notes install - 安装/检查 Python 依赖
  - /手写笔记 <目录> - 中文命令入口，等价于 /ocr-notes

  能力：PaddleOCR 本地推理（不依赖外部 API）、PDF 自动拆页、LLM 纠错与理顺、
  自动生成摘要与关键词索引、CER/WER/关键词召回打分、Markdown 可检索产物。
author: opencode
license: MIT
status: beta
---

# handwriting-ocr 技能

把纸本/平板的手写笔记，经过「PaddleOCR → LLM 润色 → Markdown 索引」三步，
变成可在文件系统中 `grep` 或在任何 Markdown 阅读器里全文检索的笔记库。

## Quick Commands

| 命令 | 作用 |
|------|------|
| `/ocr-notes install` | 检查并安装 Python 依赖（首次运行必跑） |
| `/ocr-notes <目录>` | 完整流水线：批量 OCR → 润色 → 生成 MD |
| `/ocr-notes refine <raw_ocr.json>` | 只做润色（OCR 已经跑过） |
| `/ocr-notes eval <测试集目录>` | 在人工标注对照集上打分 |
| `/手写笔记 <目录>` | 中文命令，等价于 `/ocr-notes` |

## 适用场景

- 笔记本扫描件（手机/扫描仪导出的 PNG/JPG）
- iPad/安卓平板导出手写笔记 PDF
- 历史手稿扫描归档
- 需要在电脑上全文检索 / 摘要整理

不适用：印刷体书籍（请直接用 `pdftotext` / 文档类技能）、
纯图示/公式笔记（需要专用 OCR 模型）。

---

## 依赖与首次安装

仅依赖本地 Python 包，不依赖外部 API：

```
paddlepaddle
paddleocr
pymupdf
jieba（可选，改善 WER 精度）
```

在终端里：

```bash
pip install -r ~/.config/opencode/skills/handwriting-ocr/requirements.txt
```

> **Python 3.13 注意**：请固定 `paddlepaddle==3.2.2`（3.3.x 在 Windows 有 oneDNN 转换 bug）。
> **GPU 加速（推荐，约 200 倍提速）**：有 NVIDIA 显卡时改用 GPU 版 paddle：
>
> ```bash
> pip uninstall paddlepaddle -y
> pip install paddlepaddle-gpu==3.2.2 -i https://www.paddlepaddle.org.cn/packages/stable/cu126/
> ```
>
> `cu126` 对应 CUDA 12.6 驱动（可用 `nvidia-smi` 查看右上角 CUDA Version）；
> 其他驱动版本替换为 `cu118` / `cu123` 等。装好后 `batch_ocr.py` 默认 `--device auto`
> 会自动使用 GPU，也可显式 `--device gpu` / `--device cpu`。
>
> 首次跑 PaddleOCR 会自动下载检测/识别模型（约 100MB），保持网络畅通。

技能自带 `/ocr-notes install` 命令帮用户跑安装并验证。

---

## 完整工作流

### Step 0 — 准备目录

让用户准备好一个目录，例如 `~/notes/2025-q1/`，
里面放 PNG/JPG/PDF：

```
~/notes/2025-q1/
├── 01.png
├── 02.jpg
├── meeting-0312.pdf      # 多页
└── ...
```

### Step 1 — 跑 PaddleOCR（脚本）

调用：

```bash
python ~/.config/opencode/skills/handwriting-ocr/scripts/batch_ocr.py \
    ~/notes/2025-q1/ \
    --output ~/notes/2025-q1/raw_ocr.json \
    --lang ch
```

产出 `raw_ocr.json`，结构：

```json
{
  "source_dir": "...",
  "lang": "ch",
  "items": [
    {
      "id": "01",
      "source_file": "01.png",
      "page": 1,
      "image_path": "page_images/01.png",
      "raw_text": "原始 OCR 文本（按行用 \\n 拼接）",
      "raw_text_lines": ["第一行", "第二行", ...],
      "confidence": 0.876,
      "char_count": 234,
      "bbox_count": 18,
      "error": null
    },
    ...
  ]
}
```

同时把图片（含 PDF 拆出的页）复制/渲染到同目录的 `page_images/` 下，
方便后续校对。

如果脚本抛出「PaddleOCR 未安装」或「PyMuPDF 未安装」，立即转去 `/ocr-notes install`。

### Step 2 — 拆 raw_ocr.json 为按源文件的 `.raw.txt`（脚本）

```bash
cd ~/notes/2025-q1
python ~/.config/opencode/skills/handwriting-ocr/scripts/dump_raw.py \
    raw_ocr.json --out-dir . --format txt,md
```

产出：

- `<源文件名stem>.raw.txt` — 纯文本（多页用 `\n\n---\n\n` 分隔）
- `<源文件名stem>.raw.md` — Markdown 版（含分页标记与置信度）

`evaluate.py` 直接读 `.raw.txt`；LLM 润色时读 `.raw.md` 更直观。

### Step 3 — LLM 润色与理顺（本会话内完成，无外部 API）

**这一步骤由 opencode 当前会话的大模型直接执行**，不需要调用第三方 LLM。
请按下面的「润色协议」逐个处理 `<stem>.raw.md`。

#### 润色协议

对每个源文件（如 `01.png`、`meeting-0312.pdf`）：

1. 用 `read` 工具读取 `<stem>.raw.md` 与对应 `raw_ocr.json` 的条目
2. **纠错**：依据上下文修正 OCR 错字（如同音字、形近字、断行错误）
3. **理顺**：合并断行、补全标点、按语义分段，必要时加标题/列表/代码块
4. **保真**：只修可由上下文推出的内容，不要凭空补写；不确定处用 `[?]` 标记
5. **生成产物**：
   - `<stem>.refined.txt` — 仅正文纯文本（用于 evaluate.py 二次打分）
   - `<stem>.md` — 完整 Markdown，结构如下：

```markdown
# <自动推断的标题或用源文件名>

> **来源**: `01.png`
> **OCR 引擎**: PaddleOCR（lang=ch, use_angle_cls=True）
> **OCR 平均置信度**: 0.876
> **生成时间**: 2026-08-17

## 摘要

<3-5 句话概括本页/本份笔记的核心内容，便于检索时一眼判断是否相关>

## 关键词索引

- 关键词1
- 关键词2
- ...

## 正文

<润色后的正文，按页面用 `### 第 N 页` 分隔>

<!--
以下为原始 OCR 文本，供校对（不计入检索）：
<details><summary>查看原始 OCR</summary>

\`\`\`
<原 raw_text>
\`\`\`

</details>
-->
```

#### 分块策略

如果某个源文件页数很多（如 30+ 页的 PDF），单次会话上下文可能装不下：

- **按页分块**：每次只读 1 个 `raw_text_lines`，润色并追加到当前 `*.md`
- 用 `bash` + 工具保持写入原子：先写 `<stem>.md.tmp`，最后 `mv` 覆盖
- 在每次 refine 之后输出当前进度，避免用户长时间等待无反馈

#### 关键约束（refine 时必须遵守）

| 不要做 | 要做 |
|--------|------|
| 凭想象补写原文不存在的内容 | 用 `[?]` 标注不确定字符 |
| 删去 OCR 已经能看清的细节 | 保留可识别的数字、符号、列表结构 |
| 把所有笔记润成「标准书面语」 | 保留原文的语气、口语、笔记习惯用法 |
| 一次性把全部内容塞进 LLM 上下文 | 按源文件/按页分次润色 |

### Step 4 — 生成目录索引（可选）

跑完 Step 3 后，额外生成一个 `INDEX.md`：

```markdown
# 笔记索引 — <目录名>

| 文件 | 标题 | 摘要 | 关键词 |
|------|------|------|--------|
| [01.md](01.md) | ... | ... | ... |
| [meeting-0312.md](meeting-0312.md) | ... | ... | ... |
```

`grep` 或 IDE 全文搜索时，从 `INDEX.md` 入手。

---

## 评估打分（`/ocr-notes eval <测试集目录>`）

### 准备对照集

目录约定：

```
test_set/
├── 01.png             # 原图
├── 01.gt.md           # 人工逐字转录（必填）
├── 01.gt.json         # 可选，结构化 GT
└── 01.raw.txt         # Step 2 产出
└── 01.refined.txt     # Step 3 产出
```

`01.gt.json` 示例（关键词评估需要它）：

```json
{
  "text": "原始笔记的人工转录文本",
  "keywords": ["检索关键词1", "检索关键词2"]
}
```

### 跑评估

```bash
python ~/.config/opencode/skills/handwriting-ocr/scripts/evaluate.py \
    test_set/ \
    --report score_report.md \
    --json metrics.json
```

产出：

- `score_report.md` — 0-100 综合分、CER/WER、关键词召回、逐条详情
- `metrics.json` — 详细数值，便于二次分析

### 综合分公式

```
score = 0.7 × (1 - CER) × 100 + 0.3 × 关键词召回 × 100
```

无关键词标注时退化为 `(1 - CER) × 100`。

| CER | 关键词召回 | 综合分 |
|-----|-----------|--------|
| 0.10 | 0.90 | **90** |
| 0.20 | 0.80 | **80** |
| 0.05 | 0.95 | **95** |

### 打分目标

| 场景 | 及格线 | 良好 | 优秀 |
|------|--------|------|------|
| 印刷体 | 85 | 92 | 96 |
| 工整手写 | 75 | 85 | 92 |
| 潦草手写 | 60 | 75 | 85 |

如果润色后分数低于原始 OCR 分数，说明润色反而引入了错误，
此时应在 refine 协议里加重「不要改写」约束。

---

## 输出文件清单

| 文件 | 说明 |
|------|------|
| `<dir>/raw_ocr.json` | OCR 原始输出（含置信度、行、坐标） |
| `<dir>/page_images/` | 单页图片（扫描原图 + PDF 拆页） |
| `<dir>/<stem>.raw.txt` | 按源文件聚合的纯文本 |
| `<dir>/<stem>.raw.md` | 按源文件聚合的 Markdown（带分页） |
| `<dir>/<stem>.refined.txt` | 润色后纯文本（evaluate 用） |
| `<dir>/<stem>.md` | 最终可检索 Markdown（含摘要 + 关键词 + 正文） |
| `<dir>/INDEX.md` | 全目录索引（可选） |
| `<test_dir>/score_report.md` | 评估报告 |
| `<test_dir>/metrics.json` | 评估明细 |

---

## 常见踩坑

### 坑 1: paddlepaddle 在 Windows 上 pip 装不上

**现象**：`pip install paddlepaddle` 报编码错误 / 找不到版本。

**解决**：

```bash
python -m pip install --upgrade pip setuptools wheel
pip install paddlepaddle -i https://pypi.tuna.tsinghua.edu.cn/simple
# 或 GPU 版：
# pip install paddlepaddle-gpu==2.6.1.post118 -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 坑 2: PDF 拆页失败

**现象**：`PyMuPDF not installed` 或 `cannot open PDF`。

**解决**：先 `pip install pymupdf`；若 PDF 加密，先用其他工具解密。

### 坑 3: PaddleOCR 首次运行太慢

**现象**：跑一张图要 5+ 分钟。

**原因**：首次下载检测/识别/方向分类三个模型。

**解决**：耐心等待；模型缓存到 `~/.paddleocr/` 后后续秒开。

### 坑 4: 中文 OCR 串行断行

**现象**：「今天开会 / 议讨论了 / 项目进度」其实应为「今天会议讨论了项目进度」。

**解决**：LLM 润色时按语义合并；不要在 OCR 阶段硬合并。

### 坑 5: 评估分数比润色前还低

**现象**：原始 CER=0.20，refined 后 CER=0.25。

**原因**：LLM 错误补写了原文不存在的内容，或过度「书面化」。

**解决**：调整润色 prompt，加重「保守/不补写」约束；考虑针对不同样本关闭润色。

### 坑 6: 上下文塞不下

**现象**：20 页 PDF 的 raw_text 超过会话上下文。

**解决**：按页分块；或先 refine 前 5 页 → 让用户确认效果 → 再批量续跑剩余页。

---

## 脚本位置

| 脚本 | 功能 |
|------|------|
| `scripts/batch_ocr.py` | 批量 OCR（PNG/JPG/PDF → raw_ocr.json） |
| `scripts/dump_raw.py` | 把 raw_ocr.json 按源文件拆成 `.raw.txt` / `.raw.md` |
| `scripts/evaluate.py` | 与人工标注对照集打分（CER/WER/关键词召回） |

依赖见同目录 `requirements.txt`。