# HTML 清洗与 Markdown 转换 / HTML to Markdown

公众号文章富 HTML 转为干净可读 Markdown。核心：**清洗广告噪声，保留语义结构**。

## 转换流程 / Conversion Pipeline

```python
def html_to_markdown(html, front_matter):
    # 1. 预清洗：去广告/推荐/关注引导
    clean = preprocess(html)
    # 2. readability 提取正文主体
    body = readability_extract(clean)
    # 3. 图片：data-src 懒加载修正 + 下载本地化
    body = fix_images(body)
    # 4. markdownify 转 Markdown
    md = markdownify(body, heading_style="ATX", strip=["script","style","iframe"])
    # 5. 后处理：去多余空行、修路径、去残留标签
    md = postprocess(md)
    # 6. 加 front-matter
    return f"---\n{yaml_dumps(front_matter)}\n---\n\n{md}"
```

## 预清洗 / Preprocess

去除公众号文章常见的噪声区块：

| 选择器 / Selector | 内容 / Content | 动作 / Action |
|------------------|--------------|--------------|
| `.qr_code_pc` / `[data-src*="qrcode"]` | 二维码 | 删除 |
| `.weui-msg__tips` | "点击关注"引导 | 删除 |
| `.rich_media_tool` | 底部工具栏 | 删除 |
| `#js_pc_qr_code_img` | PC 二维码 | 删除 |
| `.reward_area` / `#js_reward_area` | 赞赏区 | 删除 |
| `.profile_container` | 作者名片卡 | 转为 `> 作者：...` 引用 |
| `.recommend_area` | 推荐阅读 | 删除 |
| `script` / `style` / `iframe` | 脚本样式 | 删除 |
| `.ct_ipdct_wrp` | 版权声明卡 | 保留为引用 |

用 BeautifulSoup：

```python
from bs4 import BeautifulSoup

NOISE_SELECTORS = [
    ".qr_code_pc", "[data-src*='qrcode']", ".weui-msg__tips",
    ".rich_media_tool", "#js_pc_qr_code_img", ".reward_area",
    ".recommend_area", "script", "style", "iframe",
]

def preprocess(html):
    soup = BeautifulSoup(html, "html.parser")
    for sel in NOISE_SELECTORS:
        for el in soup.select(sel):
            el.decompose()
    return str(soup)
```

## readability 提取 / Body Extraction

用 `readability-lxml` 提取正文主体，去除外围布局：

```python
from readability import Document
def readability_extract(html):
    doc = Document(html)
    return doc.summary(html_partial=True)  # 返回正文 HTML 片段
```

> 公众号文章主体在 `#js_content`，也可直接取该节点跳过 readability。readability 用于兜底（页面结构变更时）。

## 图片处理 / Images

公众号图片用 `data-src` 懒加载，`src` 可能是占位图：

```python
def fix_images(soup, images_dir, referer):
    for img in soup.find_all("img"):
        src = img.get("data-src") or img.get("src")
        if not src or src.startswith("data:"):
            continue
        # 下载到本地
        local = download_image(src, images_dir, referer)
        if local:
            img["src"] = f"../images/{local.name}"
        else:
            # 下载失败保留远程 URL，加注释
            img["src"] = src
            img.insert_after(soup.new_string(f"<!-- remote: {src} -->"))
        # 去 data-src 防重复
        if img.get("data-src"):
            del img["data-src"]
    return soup
```

### 图片下载

```python
import hashlib, requests
def download_image(url, images_dir, referer="https://mp.weixin.qq.com"):
    headers = {"Referer": referer, "User-Agent": "Mozilla/5.0 ..."}
    r = requests.get(url, headers=headers, timeout=15)
    if r.status_code != 200:
        return None
    ext = ".jpg"
    ct = r.headers.get("Content-Type", "")
    if "png" in ct: ext = ".png"
    elif "gif" in ct: ext = ".gif"
    elif "webp" in ct: ext = ".webp"
    h = hashlib.sha1(r.content).hexdigest()[:16]
    path = images_dir / f"{h}{ext}"
    if not path.exists():  # 去重
        path.write_bytes(r.content)
    return path
```

> 微信图床 `mmbiz.qpic.cn` 有防盗链，必须带 `Referer: https://mp.weixin.qq.com`。

## markdownify 转换 / To Markdown

```python
from markdownify import markdownify as md

def to_markdown(html):
    return md(html, heading_style="ATX", strip=["script","style","iframe"],
              bullets="-", code_language="text")
```

### 标签映射

| HTML | Markdown |
|------|----------|
| `<h1>`-`<h6>` | `#`-`######` |
| `<p>` | 段落（空行分隔） |
| `<strong>`/`<b>` | `**bold**` |
| `<em>`/`<i>` | `*italic*` |
| `<code>` | `` `code` `` |
| `<pre>` | ```` ```python ```` 代码块 |
| `<blockquote>` | `> quote` |
| `<ul>`/`<ol>` | `-` / `1.` |
| `<img>` | `![alt](path)` |
| `<a>` | `[text](url)` |
| `<table>` | Markdown 表格 |
| `<br>` | 行尾两空格 |

## 后处理 / Postprocess

```python
def postprocess(md):
    # 去连续空行（>2→2）
    md = re.sub(r"\n{3,}", "\n\n", md)
    # 去残留 HTML 标签
    md = re.sub(r"</?(?:div|span|section|article)[^>]*>", "", md)
    # 修图片 alt 为空
    md = re.sub(r"!\[\]\(", "![image](", md)
    # 去多余尾部空格
    md = "\n".join(line.rstrip() for line in md.splitlines())
    return md.strip() + "\n"
```

## front-matter / YAML Front Matter

```yaml
---
title: 文章标题
author: 作者名
account: 公众号名
publish_time: 2026-07-29 14:30
source_url: https://mp.weixin.qq.com/s?__biz=...
crawled_at: 2026-07-29T15:00:00+08:00
sha256: a1b2c3d4...
---
```

`sha256` 为正文（去 front-matter 后）的哈希，用于去重。

## 特殊内容 / Special Content

| 类型 / Type | 处理 / Handling |
|------------|----------------|
| 视频号卡片 | `[视频号内容](原链接)` 占位 |
| 音频卡片 | `[音频内容](原链接)` 占位 |
| 小程序卡片 | `[小程序：名称](原链接)` 占位 |
| 投票组件 | `[投票组件，原链接]` 占位 |
| 付费阅读墙 | `<!-- 付费内容，未抓取 -->` 标注 |
| 外链卡片 | 保留为 `[标题](url)` |
| 数学公式 | 尝试保留原 LaTeX（公众号公式多为图片，下载存 images/） |
| 表格 | markdownify 转 Markdown 表格；复杂表格保留 HTML 注释 |

## 文件命名 / File Naming

```
articles/YYYYMMDD-<slug>.md
```

- `YYYYMMDD`：发布日期
- `slug`：标题 slugify（中文保留，去标点，空格转 `-`，截前 30 字符）
- 重名：追加 `-v2`、`-v3`

示例：`20260729-谈谈大模型的上下文窗口.md`

## 质量校验 / Quality Check

转换后检查：
- [ ] front-matter 完整（title/author/publish_time/source_url/sha256）
- [ ] 无残留 `<div>`/`<span>` 等空标签
- [ ] 图片路径均为相对 `../images/`
- [ ] 无连续 3+ 空行
- [ ] 代码块语言标注（`text` 兜底）
- [ ] 正文非空（非 403/删除页）