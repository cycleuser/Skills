# 公众号文章枚举策略 / Article Enumeration

微信无公开"全部文章 API"，必须用浏览器翻页枚举。核心：**真实浏览器、滚动加载、ajax 解析**。

## 两种入口 / Two Entry Points

### 方式 A：给定一篇文章 URL（推荐，最可靠）

用户提供一篇公众号文章的完整 URL（含 `__biz/mid/idx/sn`，或短链 `/s/<id>`）。从该文章页提取 biz + album_id + prev/next 链接，然后用**滚雪球**递归遍历全部文章。

```
给定文章 URL
    ↓
访问文章页 → 提取 __biz, album_id, 上一篇/下一篇 URL
    ↓
滚雪球 BFS: 从起始文章出发，沿 prev/next 链递归访问
    ↓
每篇文章页再提取其 prev/next，加入队列
    ↓
直到链到头（无邻接或全部已访问）
    ↓
同时抓取合辑 API 补充（album_id → appmsgalbum）
```

### 方式 B：biz-id 已知

公众号 biz 在文章 URL 的 `__biz=` 参数里。需先有一篇该公众号的文章 URL 才能启动滚雪球（biz 本身不足以访问文章——缺 `sn`）。

### 方式 C：仅名称（搜一搜，兜底）

```
https://weixin.sogou.com/weixin?type=1&query=<URL编码的名称>
```

定位认证账号 → 取 biz → 走方式 A。

> 搜狗有反爬，优先用方式 A。名称搜索仅用于未知 biz 时定位。

## biz 获取 / Getting biz

### 从单篇文章 URL

```
https://mp.weixin.qq.com/s?__biz=YOUR_BIZ_ID&mid=...&idx=1&sn=...
                                    ^^^^^^^^^^^^^^^^^^^^^^^^
                                    这段就是 biz
```

### 从搜一搜结果页

搜一搜结果列表里每个公众号项的链接含 `__biz=` 参数。

### 从公众号名片页

公众号名片分享链接 `https://mp.weixin.qq.com/mp/profile_ext?action=home&__biz=<biz>` 直接含 biz。

## 翻页加载 / Pagination

历史消息页是 ajax 滚动加载，非传统分页：

```python
def enumerate_articles(driver, biz):
    url = f"https://mp.weixin.qq.com/mp/profile_ext?action=home&__biz={biz}&scene=124"
    driver.get(url)
    wait_for("#app", timeout=20)
    
    articles = []
    last_height = 0
    scroll_count = 0
    max_scrolls = 500  # 硬上限，防无限滚
    
    while scroll_count < max_scrolls:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(random.uniform(2, 4))  # 克制
        
        # 从 ajax 拦截 general_msg_list
        msgs = driver.execute_script("""
            if (window.__app_msg_list) return window.__app_msg_list;
            // 或从页面 DOM 提取
            var items = document.querySelectorAll('.weui_msg_card');
            return Array.from(items).map(function(it) {
                return {
                    title: it.querySelector('.weui_msg_card_title')?.textContent?.trim(),
                    url: it.querySelector('a')?.href,
                    datetime: it.querySelector('.weui_msg_card_extra')?.textContent?.trim()
                };
            });
        """)
        if msgs:
            articles.extend(msgs)
        
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break  # 到底
        last_height = new_height
        scroll_count += 1
    
    return dedup_by_url(articles)
```

### ajax 拦截（更可靠）

页面加载时注入脚本拦截 `profile_ext?action=getmsg` 的 ajax 响应：

```python
driver.execute_cdp_cmd("Network.enable", {})
# 通过 performance log 捕获 ajax
options.set_capability("goog:loggingPrefs", {"performance": "ALL"})

# 解析 performance log
for entry in driver.get_log("performance"):
    msg = json.loads(entry["message"])["message"]
    if msg["method"] == "Network.responseReceived":
        req_url = msg["params"]["response"]["url"]
        if "action=getmsg" in req_url:
            # 取响应体
            body = driver.execute_cdp_cmd("Network.getResponseBody", {
                "requestId": msg["params"]["requestId"]
            })["body"]
            data = json.loads(body)
            articles.extend(data["general_msg_list"])
```

## 文章 URL 解析 / URL Parsing

`general_msg_list` 每项含：

```json
{
  "comm_msg_info": {
    "id": 123456,
    "type": 49,
    "datetime": 1753789800
  },
  "app_msg_ext_info": {
    "title": "文章标题",
    "content_url": "s?__biz=...&mid=...&idx=1&sn=...",
    "author": "作者",
    "cover": "https://mmbiz.qpic.cn/..."
  }
}
```

提取：
- `url` = `https://mp.weixin.qq.com/` + `content_url`（注意 `&` 转义 `&amp;`）
- `title` = `app_msg_ext_info.title`
- `publish_time` = `datetime.fromtimestamp(comm_msg_info.datetime)`

## 滚雪球遍历 / Snowball Traversal（核心策略）

微信文章页底部有"上一篇/下一篇"导航（`album_read_nav_prev/next`），其目标 URL 以 JS 变量形式存在页面 HTML 里，含完整 `__biz/mid/idx/sn`：

```
__biz=YOUR_BIZ_ID\x26amp;mid=...\xx26amp;idx=1\x26amp;sn=...
```

正则提取（注意 `\x26amp;` 转义）：

```python
for m in re.finditer(r'__biz=([A-Za-z0-9+/=]+)\\x26amp;mid=(\d+)\\x26amp;idx=(\d+)\\x26amp;sn=([a-f0-9]+)', src):
    biz, mid, idx, sn = m.groups()
    url = f"https://mp.weixin.qq.com/s?__biz={biz}&mid={mid}&idx={idx}&sn={sn}&scene=124"
```

BFS 遍历：

```python
visited = set()
queue = [start_url]
while queue:
    url = queue.pop(0)
    if normalize_url(url) in visited: continue
    visited.add(normalize_url(url))
    driver.get(url)
    # 提取内容（抓取）
    md = extract_and_convert(driver)
    # 提取邻接
    for nu in extract_prev_next_urls(driver):
        if normalize_url(nu) not in visited:
            queue.append(nu)
```

**关键**：枚举与抓取合并为单遍——访问每篇文章一次，同时提取内容+邻接，避免重复访问触发风控。

## 合辑 API / Album API

文章页 JS 含 `album_id`（合辑 ID）。用 `appmsgalbum` JSON API 拿合辑内全部文章（无需登录态）：

```
https://mp.weixin.qq.com/mp/appmsgalbum?__biz=<biz>&action=getalbum&album_id=<id>&count=100&begin=0&f=json
```

返回 JSON：

```json
{"getalbum_resp":{"article_list":[{"url":"http://mp.weixin.qq.com/s?__biz=...&mid=...&sn=...","title":"..."}]}}
```

翻页：`begin` 参数以 100 递增，返回少于 100 即末页。

**一个公众号可有多个合辑**（如 #基础知识、#大语言模型、#二手架构师杂谈、#虚拟化操作系统小工具）。每个合辑上限 20 篇。单篇文章页的 `album_id` 只含它所属的 1-2 个合辑。

**发现全部合辑**：遍历已抓文章页，逐篇提取 `album_id`（JS 变量），聚合去重。采样不同时间段的文章可发现更多合辑。

跨合辑发现也靠滚雪球（不同合辑文章通过 prev/next 链相连）。

### 已知合辑上限与翻页技巧

微信合辑每册文章数不定（20-60 篇），但**未登录态的 API 只返回最新 20 篇**。关键技巧：

1. **`is_reverse=1` 拿更老文章**：合辑 HTML 页 `?is_reverse=1` 会渲染**最老的 20 篇**，与默认（`is_reverse=0`，最新 20 篇）互补，覆盖两端。
2. **`count=60` 扩渲染量**：HTML 页加 `&count=60` 可让初始 SSR 渲染 20 篇（默认 10），配合滚动懒加载能拿到更多。
3. **`f=json` API**：`begin/offset/from_msgid` 参数全部无效（未登录态），始终返回相同 20 篇。仅作最新文章入口。
4. **组合枚举**：对每个合辑用 `is_reverse=0/1` × `count=60` 各访问一次 + 滚动 + 滚雪球，覆盖最新/最老两端 + prev/next 链。
5. **去重**：同一文章会出现在多个合辑（跨合辑重叠），按 mid 去重。

```bash
# 获取合辑最新 20 篇
https://mp.weixin.qq.com/mp/appmsgalbum?__biz=<biz>&action=getalbum&album_id=<id>&count=60&is_reverse=0
# 获取合辑最老 20 篇
https://mp.weixin.qq.com/mp/appmsgalbum?__biz=<biz>&action=getalbum&album_id=<id>&count=60&is_reverse=1
```

## 历史消息页（已弃用）

`mp.weixin.qq.com/mp/profile_ext?action=home&__biz=<biz>` 常被微信 `Verify` 拦截（需微信客户端内打开），浏览器自动化不可行。**不再依赖此路径**。

## 去重 / Dedup

- URL 去重：`content_url` 去 `&chksm`/`&sessionid` 等时效参数，按 `__biz+mid+idx+sn` 规范化
- 正文 SHA-256 去重：同篇多 URL（参数不同）按正文哈希二次判定

## 边界 / Edge Cases

- **登录态失效**：历史消息页跳登录 → 报告，提示重新扫码
- **公众号设为不可见**：历史消息页空 → 报告"该公众号未开放历史"
- **仅近 10 篇可见**：部分公众号限制历史可见数量 → 抓到即止，报告"仅可见 N 篇"
- **滚动加载卡住**：网络慢/ajax 超时 → 设 `max_scrolls` 硬上限 + 超时退出
- **biz 失效**：公众号迁移/改名 → 重新搜名称取新 biz
- **搜一搜反爬**：验证码/限流 → 报告，不绕过；改用已知 biz 方式 A

## 合规 / Compliance

- 遵守 `robots.txt`：`mp.weixin.qq.com/robots.txt` 禁止的路径不抓
- 频率克制：滚动间隔 2-4s，文章间隔 3-7s，并发=1
- 不并发、不伪装指纹、不破解验证码
- 遇风控即停，不重试轰炸