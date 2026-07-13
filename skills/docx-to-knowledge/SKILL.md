---
name: docx-to-knowledge
version: "1.0.0"
description: |
  Converts .docx documents (manuals, textbooks, reference books) into self-contained, searchable, mobile-friendly HTML knowledge bases with embedded images, chapter navigation, and full-text search.

  Triggers when: User provides a .docx file and requests a knowledge base, searchable HTML, mobile-friendly reader, or GangDan-compatible JSON.

  Commands:
  - /知识库 <docx路径> [输出目录] - Full pipeline: extract → clean → generate HTML + JSON + images
  - /知识库 extract <docx路径> - Extract text + images from docx, save to structured JSON
  - /知识库 clean <json路径> - Clean and polish the extracted JSON (spacing, headers, captions)
  - /知识库 generate <json路径> - Generate standalone HTML with search + nav + embedded images
  - /知识库 verify <html路径> - Run automated quality checks (images, spacing, search function)

  Capabilities: docx text+image+table extraction, CJK spacing normalization, stray header removal, image caption grouping, English diagram label separation, data-URI embedding for single-file output, full-text search with result excerpts, mobile-responsive layout, dark mode support
author: cycleuser
license: MIT
status: stable
---

## Safety Rules

参见 [_shared/core/safety-rules.md](../../_shared/core/safety-rules.md) — 所有安全规则从共享层加载。

# docx-to-knowledge 技能

## 核心定位

将 .docx 格式的各类文档（手册、教材、参考书）转换为**自包含、可搜索、移动端友好的 HTML 知识库**。同时生成 GangDan 兼容的 JSON 知识库文件。

## Quick Commands

| Command | Description |
|---------|-------------|
| `/知识库 <docx> [out]` | 完整流程：提取→清洗→生成 HTML+JSON+图片 |
| `/知识库 extract <docx>` | 仅提取文本+图片+表格到 JSON |
| `/知识库 clean <json>` | 清洗 JSON（空格、标题、标注） |
| `/知识库 generate <json>` | 从 JSON 生成独立 HTML |
| `/知识库 verify <html>` | 自动化质量检测 |

---

## 完整工作流程

### Step 1: Extract（提取）

从 docx 提取全部内容：
- 所有段落文本（保持顺序）
- 所有图片（导出为原始文件 + 记录位置）
- 所有表格（转换为 HTML 表格）

**关键注意事项**：
1. 图片必须记录在正确位置 — 图片出现在哪个段落之间，就放在哪个段落之间
2. 表格必须完整导出，保留所有行列
3. 章节检测用 `第\s*\d+\s*章` 正则，但需去重（docx 分页导致重复）
4. 用章节后的第一个 `X.X` 格式小节标题区分「目录条目」和「正文起始」

输出：`knowledge/<name>_full.json` + `images/` 目录

### Step 2: Clean（清洗）

对 JSON 进行多层清洗：

**第一层 — 空格修复**：
```python
# CJK 间多余空格
h = re.sub(r'([\u4e00-\u9fff]) ([ \u4e00-\u9fff])', r'\1\2', h)
# 中文标点前空格
h = re.sub(r'([\u4e00-\u9fff])\s+([，。；：！？、）】」])', r'\1\2', h)
# 全文双空格压缩
h = re.sub(r' {2,}', ' ', h)
```

**第二层 — 标题清理**：
- 删除正文中的孤立章节标题行：`<p>第X章XXX</p>` — 它们来自 docx 页眉/分页
- 合并被章节标题打断的断裂段落（如 `重于</p><p>空气` → `重于空气`）

**第三层 — 图片标注**：
- 图片后紧跟的短文本（如 `图1.1 系统构成`）识别为 `<figcaption>`
- 图片后连续 3+ 个超短 `<p>` 标签（如 `T型` `H型` `常规型`）归并为 `.img-legend`
- 全英文段落（英文占比 > 60%）包裹为 `.diagram-labels`

**第四层 — 最终验证**：
```python
# 零容忍检查
assert not re.search(r'[\u4e00-\u9fff] [\u4e00-\u9fff]', html)  # CJK间无空格
assert not re.search(r'<p>\s*第\d+章', html)  # 无孤悬章节标题
assert html.count('<img') == expected_count  # 图片数正确
```

### Step 3: Generate（生成 HTML）

**核心原则**：单文件、自包含、无需服务器

1. **图片嵌入**：所有图片转为 `data:image/...;base64,...` 内嵌
2. **搜索**：每个 `.chapter` div 预计算 `data-search` 属性（纯文本，供搜索）
   - 为什么用 `data-search` 而不是 `textContent`：data URI 会导致浏览器 `textContent` 返回空串
3. **导航**：自动生成 `<a href="#...">` 锚点链接
4. **布局**：左侧固定目录 + 右侧阅读区，移动端自适应

**生成的 HTML 结构**：
```html
<div class="content">
  <div class="chapter" id="ch1" data-search="纯文本...">
    <h2>第1章 概述</h2>
    <h3 id="s1_0">1.1 无人机的定义</h3>
    <p>...</p>
    <img src="data:image/jpeg;base64,...">
    <div class="diagram-labels">...</div>
  </div>
</div>
```

**搜索 JS 核心逻辑**：
```javascript
srch.oninput = function() {
  var q = srch.value.trim().toLowerCase();
  if (!q) { /* 显示全部 */ return; }
  chapters.forEach(function(ch) {
    var txt = (ch.getAttribute('data-search')||'').toLowerCase();
    if (txt.indexOf(q) >= 0) {
      // 添加到结果列表，显示摘要
    }
  });
  // 隐藏正文，显示搜索结果
};
```

### Step 4: Verify（验证）

自动检测：
1. 搜索功能 — 用 Playwright 真实浏览器测试 10 次
2. 图片完整性 — `img` 标签数 = JSON 中 `images` 总和
3. CJK 空格 — 全文扫描零容忍
4. 孤悬标题 — 全文扫描零容忍
5. JS 语法 — Node `--check` 静态分析

---

## 关键踩坑与解决方案

### 坑 1: 浏览器 `textContent` 返回空串

**现象**：搜索时所有章节都被隐藏

**原因**：大量内嵌 data URI 图片导致浏览器延迟渲染，`element.textContent` 在 JS 执行时返回空字符串

**解决**：在 Python 生成阶段预计算 `data-search` 属性（HTML 标签外纯文本），搜索直接读属性值

### 坑 2: JS 正则转义在 Python 模板中丢失

**现象**：`var re = new RegExp('('+q.replace(/[.*+?^${}()|[\]\\]/g,'\\$&')+')','gi')` 报 `Invalid regular expression: missing /`

**原因**：Python f-string / `'''` 模板中的反斜杠被 Python 提前转义

**解决**：不用正则高亮，改用 `split(q).join('<em>'+q+'</em>')` 方案

### 坑 3: docx 分页导致每页重复章节标题

**现象**：同一章出现 20+ 个 "第2章系统组成及介绍" 标题

**原因**：Word 文档每页页眉包含章节名，导出为 docx 时作为独立段落

**解决**：检测章节时只看「后面紧跟着 X.X 小节号」的章节标题，其余的过滤

---

## 输出文件清单

| 文件 | 说明 |
|------|------|
| `<name>.html` | 单文件知识库（6-8MB，自包含） |
| `knowledge/<name>_full.json` | 结构化 JSON 知识库（GangDan 兼容） |
| `images/` | 原始图片（431 张） |
| `extract_*.py` | 提取脚本（可复现） |
| `gen_html_*.py` | HTML 生成脚本（可复现） |

---

## 脚本位置

所有提取/清洗/生成脚本位于技能目录的 `scripts/` 子目录下：

| 脚本 | 功能 |
|------|------|
| `scripts/extract_final.py` | 从 docx 提取章节 + 图片 + 表格 |
| `scripts/gen_html_v4.py` | 从 JSON 生成独立 HTML |
| `scripts/refine_captions.py` | 图文标注归并清洗 |
