# 公众号存档工作流 / Archive Workflow

完整五步操作流程。核心：**浏览器驱动枚举，逐篇抓取转 Markdown，断点续抓**。

## Step 0 — 环境检查 Check

```bash
python3 scripts/gzh_archive.py check
```

检查项：
- `selenium`、`webdriver-manager`、`markdownify`、`readability-lxml` 是否安装
- Chrome 浏览器是否可用
- `user-data-dir`（默认 `~/.opencode-gzh-profile`）是否存在（首次需手动登录）

首次运行：浏览器会弹出，需用户手动在微信网页版/搜一搜扫码登录；登录态持久化后后续免登录。

## Step 1 — 枚举 Enumerate

```bash
python3 scripts/gzh_archive.py enumerate "<公众号名或biz>"
```

### 方式 A：biz-id 已知（推荐）

公众号 biz 在文章 URL 的 `__biz=` 参数里，形如 `MzIwNDM5...`。直接构造历史消息页：

```
https://mp.weixin.qq.com/mp/profile_ext?action=home&__biz=<biz>&scene=124#wechat_redirect
```

浏览器打开后滚动加载，解析 ajax 返回的 `general_msg_list` JSON，提取每篇文章的 `url`、`title`、`publish_time`。

### 方式 B：仅名称（走搜一搜）

```bash
# 浏览器打开搜一搜
https://weixin.sogou.com/weixin?type=1&query=<URL编码的名称>
```

定位公众号认证账号 → 取 biz → 进入历史文章列表 → 翻页枚举。

> 搜狗微信搜索有反爬，优先用方式 A。名称搜索用于未知 biz 时定位。

### 方式 C：登录公众号后台（最可靠，管理员可扫码）【首选】

**这是抓取全部文章（含独立推送，不受合辑限制）的唯一可靠路径。** 公众号后台的 `list_ex` API 返回全部已发布图文消息。

1. **复用登录态**：从用户浏览器复制含微信 cookies 的 profile，Selenium 启动即登录。Firefox 在 `~/Library/Application Support/Firefox/Profiles/*.default-release/`，复制 `cookies.sqlite` 等文件到临时 profile 目录。

```python
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
options = Options()
options.add_argument("-profile")
options.add_argument("/tmp/opencode/gzh-firefox-profile")  # 复制的登录态 profile
options.binary_location = "/Applications/Firefox.app/Contents/MacOS/firefox"
driver = webdriver.Firefox(options=options, service=Service("/opt/homebrew/bin/geckodriver"))
driver.get("https://mp.weixin.qq.com/")
token = re.search(r'token=(\d+)', driver.current_url).group(1)
cookies = driver.get_cookies()  # 拿 cookies 供 requests 用
```

2. **调用后台 API**（带登录 cookies + token）：

```python
import requests
session = requests.Session()
for c in cookies: session.cookies.set(c['name'], c['value'])
url = f"https://mp.weixin.qq.com/cgi-bin/appmsg?action=list_ex&begin={begin}&count=20&type=9&token={token}&lang=zh_CN"
data = session.get(url).json()
# app_msg_cnt = 总数, app_msg_list = 本页文章
```

3. **`type` 参数**：`type=9`（图文消息，含 URL，推荐），`type=10`（素材/历史素材）。`app_msg_cnt` 是总数。

4. **翻页**：`begin` 每页 +20，直到 `begin >= app_msg_cnt`。

5. **文章 URL** 在 `app_msg_list[].appmsg_list[].link`（可能嵌套多图文），`&amp;` 需转 `&`。

6. **逐个抓取**：登录态下 `session.get(article_url)` 即可拿正文 HTML（无需 Selenium 逐篇，速度快、稳定、不吃风控）。

### 翻页加载（方式 B：仅名称走搜一搜）

```python
last_height = 0
while True:
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
    time.sleep(2)
    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        break  # 到底
    last_height = new_height
    # 解析新加载的 general_msg_list
```

产出：`article_urls` 去重列表，写入 `progress.json` 的 `pending_urls`。

## Step 2 — 抓取 Fetch（逐篇）

```bash
python3 scripts/gzh_archive.py fetch "<biz>" --resume
```

逐篇流程：

```python
for url in pending_urls:
    if url in progress["crawled_urls"]:
        continue  # 断点续抓
    driver.get(url)
    wait_for("#js_content")  # 等正文加载
    title = text("#activity-name")
    author = text("#js_name") or attr("#meta_content", "data-author")
    publish_time = text("#publish_time") or parse_from_url(url)
    html = html_of("#js_content")
    # 下载图片，改写链接
    html = download_and_rewrite_images(html, images_dir, referer=url)
    # 转 Markdown
    md = html_to_markdown(html, front_matter={...})
    write(f"articles/{publish_time:%Y%m%d}-{slug(title)}.md", md)
    # 记录
    manifest_append({...})
    progress["crawled_urls"].add(url)
    progress["last_url"] = url
    save(progress)
    time.sleep(random.uniform(MIN_DELAY, MAX_DELAY))  # 频率克制
```

### 风控处理

- 遇验证码/429/风控页 → 立即停止，报告当前 URL 与进度
- 不重试轰炸、不反制、不绕过
- 用户手动处理后 `/公众号 resume` 继续

### 失败记录

- 文章 403/已删 → manifest 记 `status=deleted`，跳过继续
- 网络断 → 进度已存，`resume` 继续
- 转换异常 → 记 `status=convert_error`，保留原始 HTML 到 `articles/<id>.html` 待人工处理

## Step 3 — 转换 Convert（HTML→Markdown）

详见 [rules/html-to-markdown.md](rules/html-to-markdown.md)。核心：

```python
def html_to_markdown(html, front_matter):
    # 1. 预清洗：去广告/推荐阅读/关注引导/二维码卡片
    clean = preprocess(html)
    # 2. readability 提取正文主体
    body = readability(clean)
    # 3. markdownify 转 Markdown
    md = markdownify(body, heading_style="ATX", strip=["script", "style"])
    # 4. 后处理：去多余空行、修图片路径
    md = postprocess(md)
    # 5. 加 front-matter
    return f"---\n{yaml(front_matter)}\n---\n\n{md}"
```

### front-matter 字段

```yaml
---
title: 文章标题
author: 作者
account: 公众号名
publish_time: 2026-07-29 14:30
source_url: https://mp.weixin.qq.com/s?__biz=...
crawled_at: 2026-07-29T15:00:00+08:00
sha256: 正文哈希
---
```

## Step 4 — 存档 Persist

```bash
python3 scripts/gzh_archive.py persist "<biz>"
```

- 写 `articles/YYYYMMDD-<slug>.md`
- 图片写 `images/<sha1>.<ext>`
- `manifest.jsonl` append 一条元数据
- 更新 `progress.json`（crawled_urls + last_crawl + last_url）
- 生成 `index.md`（按日期倒序列出标题 + 本地路径 + 原链接）

### 覆盖保护

若 `articles/` 已存在同名文件：
- 默认追加版本后缀（`-v2`）
- `--force` 覆盖前走 `/回收 overwrite`（hui-shou 技能）保护旧文件
- 不直接覆盖

## Step 5 — 检索/更新 Search/Refresh

### 全文检索

```bash
python3 scripts/gzh_archive.py search "大模型"
```

用 `rg` 全文检索 `archives_root/*/articles/`，输出命中文件:行:内容。

### 增量更新

```bash
python3 scripts/gzh_archive.py refresh "<biz>"
```

读 `progress.last_crawl`，重新枚举，只抓 `last_crawl` 之后发布的新文章。

### 断点续抓

```bash
python3 scripts/gzh_archive.py fetch "<biz>" --resume
```

读 `progress.crawled_urls`，跳过已抓，从 `last_url` 之后继续。

## 命令映射 / Command Mapping

| 命令 | 动作 |
|------|------|
| `/公众号 check` | Step 0 |
| `/公众号 <名称或biz>` | Step 1-4（完整流程） |
| `/公众号 resume <名称或biz>` | Step 2 续抓 |
| `/公众号 refresh <名称或biz>` | Step 1 重枚举 + Step 2 增量 |
| `/公众号 search <词>` | Step 5 检索 |
| `/公众号 list` | 列出 accounts.json |

英文命令 `/gongzhonghao [resume|refresh|search] ...` 行为一致。