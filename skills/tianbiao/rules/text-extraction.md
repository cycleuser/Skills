# 文本提取与纠正 / Text Extraction & Correction

从非结构化参考资料（PDF/图片/扫描件/混合文件包）提取文本，经 OCR 和错行纠正后，作为填表的内容来源。

适用场景：用户给一堆参考资料文件（可能是 PDF、扫描件截图、拍照的 Word、混合格式），需要从中提炼出可用于填表的干净文本。

## 1. 文件类型识别与路由

先按扩展名和 MIME 类型路由到合适的提取器：

```python
import os

def route_extractor(filepath):
    ext = os.path.splitext(filepath)[1].lower()
    mime = guess_mime(filepath)

    # 文本类 PDF（有文字层）
    if ext == '.pdf':
        if has_text_layer(filepath):
            return 'pdf_text'          # pdfplumber / pymupdf
        else:
            return 'pdf_ocr'           # 转图片后 OCR

    # 图片
    if ext in ('.png', '.jpg', '.jpeg', '.tif', '.tiff', '.bmp', '.webp'):
        return 'image_ocr'

    # Office 文档
    if ext in ('.docx', '.xlsx', '.pptx'):
        return 'office_native'         # python-docx / openpyxl / python-pptx
    if ext in ('.doc', '.xls', '.ppt'):
        return 'office_legacy'        # LibreOffice 先转 .docx/.xlsx

    # 纯文本
    if ext in ('.txt', '.md', '.csv', '.json', '.xml', '.html', '.htm'):
        return 'text_native'

    # 其他
    return 'unknown'
```

## 2. 提取器实现

### 2.1 PDF 文本层提取（首选）

```python
import pdfplumber

def extract_pdf_text(filepath):
    """从有文字层的 PDF 提取文本，保留表格结构"""
    pages = []
    with pdfplumber.open(filepath) as pdf:
        for page in pdf.pages:
            # 优先提取表格（保留行列结构）
            tables = page.extract_tables()
            if tables:
                for table in tables:
                    pages.append(table_to_text(table))
            # 提取纯文本（含位置信息，用于错行检测）
            text = page.extract_text(x_tolerance=2, y_tolerance=3)
            pages.append(text or '')
    return '\n\n'.join(pages)
```

`pymupdf`（fitz）速度更快，适合大文件：
```python
import fitz
def extract_pdf_text_fast(filepath):
    doc = fitz.open(filepath)
    return '\n\n'.join(page.get_text(sort=True) for page in doc)
```

### 2.2 PDF/图片 OCR（无文字层时）

```python
# 先把 PDF 每页转成图片
import fitz
def pdf_to_images(filepath, dpi=300):
    doc = fitz.open(filepath)
    images = []
    for page in doc:
        pix = page.get_pixmap(dpi=dpi)
        img_path = f'/tmp/page_{page.number}.png'
        pix.save(img_path)
        images.append(img_path)
    return images

# OCR 识别
import pytesseract
from PIL import Image

def ocr_image(img_path, lang='chi_sim+eng'):
    """用 Tesseract OCR 识别图片中的中英文"""
    return pytesseract.image_to_string(Image.open(img_path), lang=lang)

# 更高精度：用 PaddleOCR（对中文排版更准）
# from paddleocr import PaddleOCR
# ocr = PaddleOCR(use_angle_cls=True, lang='ch')
# result = ocr.ocr(img_path, cls=True)
# text = '\n'.join(line[1][0] for block in result for line in block)
```

OCR 引擎选择优先级：
| 引擎 | 中文精度 | 速度 | 安装难度 | 适用 |
|------|---------|------|---------|------|
| PaddleOCR | 高 | 中 | 中 | 中文扫描件首选 |
| Tesseract | 中 | 快 | 低 | 英文或混合 |
| 云服务（阿里/腾讯OCR） | 最高 | 快 | 需密钥 | 高精度需求 |

### 2.3 Office 文档提取

```python
import docx
def extract_docx_text(filepath):
    """提取 docx 全文（含表格）"""
    d = docx.Document(filepath)
    parts = []
    for para in d.paragraphs:
        if para.text.strip():
            parts.append(para.text)
    for table in d.tables:
        for row in table.rows:
            cells = [cell.text.strip() for cell in row.cells]
            parts.append('\t'.join(cells))
    return '\n'.join(parts)

import openpyxl
def extract_xlsx_text(filepath):
    """提取 xlsx 所有工作表"""
    wb = openpyxl.load_workbook(filepath, data_only=True)
    parts = []
    for ws in wb.worksheets:
        for row in ws.iter_rows(values_only=True):
            if any(c is not None for c in row):
                parts.append('\t'.join(str(c) if c is not None else '' for c in row))
    return '\n'.join(parts)
```

## 3. 错行检测与纠正

PDF 提取最常见的问题：**多栏排版被读成一行交错的文本**。检测和修复方法：

### 3.1 检测错行

```python
def detect_misaligned_lines(text):
    """检测可能的错行：行内突然出现不相关片段"""
    lines = text.split('\n')
    suspicious = []
    for i, line in enumerate(lines):
        # 信号1：一行内同时出现中英文且无明显分隔（多栏交错）
        cn_segments = re.findall(r'[\u4e00-\u9fff]{5,}', line)
        en_segments = re.findall(r'[A-Za-z]{10,}', line)
        if len(cn_segments) >= 2 and len(en_segments) >= 2:
            suspicious.append((i, 'multi_column_interleave'))
        # 信号2：行内出现"……。…，…"（逗号后紧跟句号，句子被打断）
        if re.search(r'。.{0,3}[，、]', line) or re.search(r'[，、].{0,3}。', line):
            suspicious.append((i, 'broken_sentence'))
    return suspicious
```

### 3.2 用坐标信息重排行

`pdfplumber` 提供 `x0, y0, x1, y1` 坐标，可按 Y 坐标分行、X 坐标分栏：

```python
def extract_pdf_by_layout(filepath):
    """按物理布局提取，避免错行"""
    pages_text = []
    with pdfplumber.open(filepath) as pdf:
        for page in pdf.pages:
            words = page.extract_words(x_tolerance=2, y_tolerance=3,
                                       keep_blank_chars=False,
                                       use_text_flow=False)
            # 按 Y 坐标分组（同一行的词 y 坐标接近）
            lines = group_words_by_y(words, tolerance=3)
            # 每行内按 X 排序
            for line in lines:
                line.sort(key=lambda w: w['x0'])
            pages_text.append('\n'.join(' '.join(w['text'] for w in line) for line in lines))
    return '\n\n'.join(pages_text)
```

### 3.3 OCR 结果的纠错

OCR 常见错误模式：

| 错误模式 | 例子 | 纠正方法 |
|---------|------|---------|
| 形近字 | 已→己，未→末 | 上下文规则 + 字典校验 |
| 数字混淆 | 0→O，1→l，5→S | 该字段应全是数字则强制转数字 |
| 标点丢失 | 句末无句号 | 段落结尾补标点 |
| 换行错位 | 一句话被拆成两行 | 合并以句号/问号结尾的行 |
| 乱码字符 | ï»¿（BOM） | strip BOM 和控制字符 |

```python
def clean_ocr_text(text):
    """OCR 结果常规清洗"""
    # 去 BOM 和控制字符
    text = text.replace('\ufeff', '').replace('\x00', '')
    # 合并被错误拆分的行（不以标点结尾的行与下一行合并）
    lines = text.split('\n')
    merged = []
    for line in lines:
        if merged and not re.search(r'[。！？.!?；;]$', merged[-1].strip()):
            merged[-1] += line.strip()
        else:
            merged.append(line.strip())
    # 常见形近字纠正（需根据具体文档调整）
    fixes = {'己经': '已经', '末来': '未来', '按耐': '按捺'}
    for wrong, right in fixes.items():
        text = text.replace(wrong, right)
    return '\n'.join(merged)
```

## 4. 提取结果的结构化

从一堆参考资料提取出干净文本后，需要**结构化**才能填表：

```python
def structure_extracted_text(raw_text, target_fields):
    """
    将提取的文本结构化为字段-值映射，供填表使用。

    target_fields: 模板需要的字段列表，如 ['课程名称', '授课教师', '平均分', '及格率']
    """
    structured = {}
    for field in target_fields:
        # 用正则或上下文匹配在原文中定位该字段的值
        pattern = rf'{field}[:：\s]*([^\n，。]+)'
        match = re.search(pattern, raw_text)
        if match:
            structured[field] = match.group(1).strip()
        else:
            structured[field] = None  # 未找到，留待人工补
    return structured
```

对复杂资料（如需要从分析报告提炼"改进措施"这类长文本字段），用 LLM 辅助：把提取的原文 + 模板字段喂给模型，让它从资料中提炼出对应内容。但 LLM 输出必须与原文交叉校验，不能凭空编造。

## 5. 提取质量校验

提取完成后必须校验，不能直接用：

```python
def verify_extraction(extracted, source_file):
    """校验提取结果与源文件是否一致"""
    issues = []
    # 1. 关键数字回查：提取的分数/人数等数字，OCR 回原文位置核对
    for field, value in extracted.items():
        if isinstance(value, (int, float)):
            # 在原 PDF/图片对应位置回查该数字
            if not confirm_number_in_source(value, source_file):
                issues.append(f'{field}={value} 在源文件中未找到对应位置，可能 OCR 有误')
    # 2. 完整性：模板需要的字段是否都提取到了
    missing = [k for k, v in extracted.items() if v is None]
    if missing:
        issues.append(f'以下字段未从资料中提取到：{missing}，需人工补')
    # 3. 合理性：数字范围是否合理（分数 0-100、人数 > 0、比例 0-100%）
    if '平均分' in extracted and not (0 <= extracted['平均分'] <= 100):
        issues.append(f'平均分 {extracted["平均分"]} 超出合理范围')
    return issues
```

## 6. 工具安装

```bash
# PDF 提取
pip install pdfplumber pymupdf

# OCR
pip install pytesseract pillow
# macOS: brew install tesseract tesseract-lang
# 中文语言包：brew install tesseract-lang  (包含 chi_sim)

# PaddleOCR（中文高精度，可选但推荐）
pip install paddlepaddle paddleocr

# Office 文档
pip install python-docx openpyxl python-pptx
```

LibreOffice（用于 .doc/.xls 转 .docx/.xlsx）：
```bash
# macOS
brew install --cask libreoffice
# Ubuntu
sudo apt install libreoffice
```

## 7. 与填表工作流的衔接

提取并纠正后的文本，按以下方式进入填表流程：

1. **结构化字段**（课程名、教师、分数、人数）→ 直接进入 `data-integrity.md` 的数据准备阶段
2. **长文本字段**（分析、原因、改进措施）→ 进入 `writing-analysis.md` 的文字撰写阶段
3. **无法自动提取的字段** → 列入"需人工补"清单，在交付说明中标注

提取阶段产出的中间产物保存到 `/tmp/tianbiao-extract-{timestamp}/`，包含：
- `raw_text.txt`：原始提取文本（含错行）
- `cleaned_text.txt`：纠正后文本
- `structured.json`：结构化字段-值映射
- `extraction_report.md`：提取报告（来源文件、提取方法、可疑项、未提取字段）

## See Also

- [workflow.md](workflow.md) — 填表五步工作流（提取作为新的 Step 2.5）
- [data-integrity.md](data-integrity.md) — 结构化数据的校验
- [writing-analysis.md](writing-analysis.md) — 从提取文本生成分析类文字