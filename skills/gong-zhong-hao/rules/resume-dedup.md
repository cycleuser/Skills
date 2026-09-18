# 断点续抓、增量更新、去重 / Resume, Incremental, Dedup

保证抓取可中断、可恢复、不重复。核心：**进度持久化，URL+内容双去重**。

## progress.json 结构 / Progress Schema

```json
{
  "biz": "YOUR_BIZ_ID",
  "account_name": "某科技评论",
  "crawled_urls": ["https://mp.weixin.qq.com/s?...", "..."],
  "crawled_hashes": ["a1b2c3d4...", "..."],
  "pending_urls": ["...", "..."],
  "last_url": "https://mp.weixin.qq.com/s?...",
  "last_crawl": "2026-07-29T15:00:00+08:00",
  "last_article_date": "2026-07-28",
  "stats": {
    "total": 128,
    "success": 125,
    "failed": 2,
    "deleted": 1
  },
  "failed_urls": [{"url": "...", "reason": "403", "time": "..."}]
}
```

每次抓取一篇后立即原子写入（写临时文件 + rename），防中断丢失。

## manifest.jsonl / Append-only Log

每行一篇文章元数据：

```json
{"url":"...","title":"...","publish_time":"2026-07-28 14:30","local_path":"articles/20260728-xxx.md","sha256":"a1b2...","crawled_at":"2026-07-29T15:00:00+08:00","status":"ok"}
```

append-only，永不改写历史行；`status` 字段：`ok`/`deleted`/`convert_error`/`paywalled`。

## 三种去重 / Three Dedup Layers

### 1. URL 去重（断点续抓）

```python
def normalize_url(url):
    # 去时效参数，规范化
    from urllib.parse import urlparse, parse_qsl, urlencode
    p = urlparse(url)
    q = dict(parse_qsl(p.query))
    # 保留 __biz, mid, idx, sn；去 chksm, sessionid, scene 等时效参数
    keep = {k: v for k, v in q.items() if k in ("__biz", "mid", "idx", "sn")}
    return f"{p.scheme}://{p.netloc}{p.path}?{urlencode(keep)}"

crawled = {normalize_url(u) for u in progress["crawled_urls"]}
if normalize_url(url) in crawled:
    skip
```

### 2. 正文 SHA-256 去重（跨 URL 同文）

同篇文章可能通过不同参数 URL 访问，按正文哈希二次判定：

```python
sha = hashlib.sha256(body_text.encode()).hexdigest()
if sha in progress["crawled_hashes"]:
    # 同文不同 URL，跳过但记 manifest 的 duplicate
    manifest_append({"url": url, "sha256": sha, "status": "duplicate_of", "dup_of": existing_url})
    skip
progress["crawled_hashes"].add(sha)
```

### 3. 文件名去重（同名文章）

```python
def unique_path(dir, base):
    p = dir / f"{base}.md"
    if not p.exists():
        return p
    i = 2
    while (dir / f"{base}-v{i}.md").exists():
        i += 1
    return dir / f"{base}-v{i}.md"
```

## 断点续抓 / Resume

```bash
python3 scripts/gzh_archive.py fetch "<biz>" --resume
```

流程：
1. 读 `progress.json`，加载 `crawled_urls` + `crawled_hashes`
2. 从 `pending_urls` 取未抓的（或重新枚举后与 `crawled` 取差集）
3. 跳过已抓，从 `last_url` 之后继续
4. 每篇抓完立即写回 `progress.json`（原子写）

```python
def atomic_save(path, data):
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2))
    tmp.rename(path)  # 原子
```

## 增量更新 / Refresh

```bash
python3 scripts/gzh_archive.py refresh "<biz>"
```

流程：
1. 读 `progress.last_crawl`（或 `last_article_date`）
2. 重新枚举全部文章 URL
3. 过滤出 `publish_time > last_crawl` 的新文章
4. 只抓新文章，旧的不动
5. 更新 `last_crawl`、`crawled_urls`、stats

```python
def refresh(biz):
    progress = load_progress(biz)
    last = progress["last_crawl"]
    all_urls = enumerate_articles(biz)
    new_urls = [u for u in all_urls if u["publish_time"] > last]
    for url in new_urls:
        fetch_one(url)
    progress["last_crawl"] = iso_now()
    save_progress(progress)
```

## 失败处理 / Failure Handling

| 失败类型 | 动作 |
|---------|------|
| 网络断 | 进度已存，`resume` 继续；不重试当前篇 |
| 403/已删 | manifest 记 `status=deleted`，跳过 |
| 验证码/风控 | 立即停止，报告进度，等用户处理 |
| 转换异常 | 存原始 HTML 到 `articles/<id>.html`，记 `status=convert_error`，继续 |
| 登录失效 | 停止，提示重新扫码，保留进度 |

失败 URL 记 `progress.failed_urls`，`resume` 时可选重试（`--retry-failed`）。

## 原子性 / Atomicity

- `progress.json`：临时文件 + rename，防写一半中断
- `manifest.jsonl`：append-only + flock，见 hui-shou 技能的 manifest 模式
- 文章 `.md`：先写 `.tmp` 再 rename，防半写文件

## 并发安全 / Concurrency

- 并发=1，不并发（防风控）
- 单进程，无多线程
- `progress.json` 由单进程独占，无需锁