---
name: gong-zhong-hao
version: "1.0.0"
description: |
  WeChat Official Account (公众号) full-archive scraper. Given a 公众号 name or
  biz-id, drive a real browser (Selenium) through 搜一搜 / 文章搜索 to enumerate
  the account's historical articles, then fetch each article URL, convert the
  rich HTML to clean Markdown (front-matter + readable body + image references),
  and save locally with dedup, resumable progress, and polite rate-limiting.

  Triggers when: User wants to download/archive all articles of a 公众号 by name
  or ID, convert 公众号 articles to Markdown, batch-save a 公众号's history, or
  back up a 公众号 locally.

  Commands:
  - /公众号 <名称或biz> - 抓取指定公众号全部文章为 Markdown
  - /公众号 resume <名称或biz> - 从上次断点继续
  - /公众号 refresh <名称或biz> - 只抓取新增文章（增量更新）
  - /公众号 search <关键词> - 在已存档中全文检索
  - /公众号 list - 列出已存档的公众号
  - /公众号 check - 检查依赖与浏览器环境
  - /gongzhonghao <name-or-biz> - English command
  - /gongzhonghao resume <name-or-biz> - Resume interrupted archive
  - /gongzhonghao refresh <name-or-biz> - Incremental update
  - /gongzhonghao search <keyword> - Full-text search across archives

  Capabilities: Browser-driven article enumeration via 搜一搜/文章搜索, biz-id
  extraction from article URLs, per-article HTML→Markdown conversion preserving
  headings/code/images/quotes, image download with local referencing, SHA-256
  dedup, resumable progress JSON, incremental update by crawl date, polite
  delay with jitter, user-data-dir cookie persistence for login state.

author: cycleuser
license: MIT
status: Beta
---

## Safety Rules

参见 [_shared/core/safety-rules.md](../_shared/core/safety-rules.md) — 所有安全规则从共享层加载。

关键补充：
- **尊重版权与平台规则**：仅用于个人学习存档，不重新分发、不商用；遵守微信 robots 与频率限制
- **浏览器自动化可见**：默认非 headless，让用户可见可控；遇到登录验证码由用户手动完成
- **不破解、不绕过**：遇到风控/限流/验证码即停止并报告，不尝试反制
- **写入走回收站**：批量覆盖前用 `/回收 overwrite`（见 hui-shou 技能），避免误删已有存档
- **频率克制**：默认每篇间隔 3-7 秒随机抖动，并发=1；不并发轰炸

# 公众号 (GongZhongHao / WeChat Official Account Archiver)

公众号文章存档技能。核心原则：**浏览器驱动枚举，逐篇抓取转 Markdown，断点续抓、增量更新**。

The one rule that matters: **drive a real browser to enumerate the account's
article list, fetch each article, convert to clean Markdown, save locally with
dedup and resumable progress.**

## Quick Commands

| Command | 说明 / Description |
|---------|-------------|
| `/公众号 <名称或biz>` | 抓取全部文章为 Markdown / Full archive to Markdown |
| `/公众号 resume <名称或biz>` | 从断点继续 / Resume interrupted archive |
| `/公众号 refresh <名称或biz>` | 只抓新增文章 / Incremental update |
| `/公众号 search <关键词>` | 已存档全文检索 / Full-text search in archives |
| `/公众号 list` | 列出已存档公众号 / List archived accounts |
| `/公众号 check` | 检查依赖与浏览器环境 / Check deps & browser |
| `/gongzhonghao <name-or-biz>` | English: full archive |
| `/gongzhonghao resume <name-or-biz>` | English: resume |
| `/gongzhonghao refresh <name-or-biz>` | English: incremental update |
| `/gongzhonghao search <keyword>` | English: full-text search |

## 核心理念 / Core Philosophy

公众号文章散落在微信生态里，没有官方"导出全部"功能；链接易失效、账号可能被封、历史文章难回溯。本技能用**真实浏览器**逐篇访问，把内容固化为本地 Markdown：

1. **滚雪球枚举**。微信文章页底部有"上一篇/下一篇"导航，其目标 URL 以 JS 变量形式含完整 `__biz/mid/idx/sn`。从一篇文章出发，BFS 递归遍历 prev/next 链即可发现同公众号的全部文章。这是发现全部文章的核心策略。
2. **合辑 API 补充**。文章页 JS 含 `album_id`，用 `appmsgalbum?action=getalbum&f=json` 拿合辑内全部文章列表（无需登录态）。
3. **逐篇转 Markdown**。每篇文章的富 HTML（标题、正文、代码块、引用、图片）转为干净 Markdown；图片下载到本地 `images/` 并改写链接为相对路径，保证离线可读。
4. **单遍抓取**。枚举与抓取合并——访问每篇文章一次，同时提取内容+邻接 URL，避免重复访问触发风控。
5. **断点续抓、增量更新**。进度存 `progress.json`（已抓 URL 集 + SHA-256 去重），中断后 `resume` 跳过已抓；`refresh` 只抓 `last_crawl` 之后的新文章。

三条铁律：

1. **不破解不绕过**。遇到登录墙、验证码、风控限流立即停止并报告，由用户手动处理后再继续。不尝试破解、不伪装、不并发轰炸。
2. **存档只用于个人学习**。不重新分发、不商用、不冒充原创；图片与正文保留原作者署名与来源链接。
3. **写入前先回收**。覆盖已有存档目录前走 `/回收 overwrite`（hui-shou 技能），避免误删历史成果。

## 输出目录结构 / Output Layout

```
~/WeChatArchives/<公众号名-or-biz>/
├── articles/
│   ├── YYYYMMDD-<slug>.md      # 每篇文章一个 Markdown
│   └── ...
├── images/                      # 文章内图片本地副本
│   └── <sha1>.<ext>
├── progress.json                # 断点续抓状态（已抓 URL 集 + last_crawl）
├── manifest.jsonl               # append-only 文章元数据日志
└── index.md                     # 全部文章索引（标题/日期/链接）

~/WeChatArchives/
└── accounts.json                # 已存档公众号清单
```

- `articles/` 文件名：`YYYYMMDD-<短slug>.md`，日期取自动发布时间，slug 为标题前 30 字符 slugify
- `images/` 用内容 SHA-1 命名去重，Markdown 内引用 `../images/<sha1>.<ext>`
- `progress.json`：`{biz, account_name, crawled_urls: [...], last_crawl: ISO, last_url: "..."}`
- `manifest.jsonl`：append-only，每行一篇文章元数据（标题/URL/发布时间/本地路径/抓取时间/SHA-256）

## 五步工作流 / Five-Step Workflow

```
Step 0  环境检查 Check
  /公众号 check
  → 检查 selenium / webdriver-manager / readability / markdownify
  → 检查 Chrome 是否可用
  → 检查 user-data-dir 登录态（首次需手动扫码登录微信网页版/搜一搜）

Step 1  枚举 Enumerate
  输入：公众号名称 或 biz-id
  方式 A（推荐）：biz-id 已知
    直接构造历史消息页 URL，浏览器翻页枚举文章链接
  方式 B：仅名称
    浏览器打开搜一搜 https://weixin.sogou.com/weixin?type=1&query=<名称>
    定位公众号 → 取 biz → 进入历史文章列表 → 翻页枚举
  产出：article_urls 去重列表（保存到 progress.json 的 crawled_urls 对照）

Step 2  抓取 Fetch（逐篇）
  for url in article_urls:
    if url in progress.crawled_urls: skip        # 断点续抓
    driver.get(url)
    等待 #js_content 加载
    提取：标题(#activity-name) / 作者 / 发布时间(#publish_time) / 正文(#js_content)
    下载正文图片到 images/<sha1>.<ext>，改写 <img src> 为相对路径
    转 Markdown（markdownify + readability 清洗）
    写 articles/YYYYMMDD-<slug>.md
    manifest.jsonl append 一条
    progress.crawled_urls.add(url); progress.last_url = url
    随机延迟 3-7s（jitter）
    遇验证码/风控 → 暂停，报告，等用户处理后 resume

Step 3  转换 Convert（HTML→Markdown）
  清洗：去广告/推荐阅读/关注引导/二维码卡片
  保留：标题层级、代码块、引用、列表、图片、链接
  front-matter：
    ---
    title: ...
    author: ...
    account: <公众号名>
    publish_time: YYYY-MM-DD HH:MM
    source_url: <原链接>
    crawled_at: <抓取时间>
    sha256: <正文哈希>
    ---

Step 4  存档 Persist
  写 articles/、images/、append manifest.jsonl、更新 progress.json
  覆盖前若目录已存在：走 /回收 overwrite（hui-shou）保护旧存档
  生成 index.md（按日期倒序列出标题+本地链接+原链接）

Step 5  检索/更新 Search/Refresh
  /公众号 search <词>  → rg 全文检索 articles/，输出命中文件:行
  /公众号 refresh     → 读 progress.last_crawl，只抓其后新文章
  /公众号 resume      → 读 progress.crawled_urls，跳过已抓继续
```

## 关键实现要点 / Key Implementation Notes

- **滚雪球（核心）**：微信文章页底部 `album_read_nav_prev/next` 的目标 URL 在 JS 变量里，含完整 `__biz/mid/idx/sn`（`\x26amp;` 转义）。正则提取后 BFS 递归遍历全部文章。单遍模式：访问一篇文章同时提取内容+邻接，不重复访问。
- **合辑 API**：`appmsgalbum?action=getalbum&album_id=<id>&f=json` 返回合辑内全部文章（无需登录态）。从文章页 JS 提取 `album_id`。
- **浏览器驱动**：Selenium + Chrome，持久化 `--user-data-dir` 保留登录态；非 headless，让用户可见可控。反检测最小化（只隐藏 `navigator.webdriver`）。
- **登录态**：首次运行需用户手动在弹出的浏览器里扫码登录；user-data-dir 持久化后后续免登录。登录态失效时报告，提示重新扫码。
- **图片处理**：`<img data-src>` 懒加载需先滚动触发；下载存 `images/<sha1>.<ext>` 去重；Markdown 改相对路径。微信图床有防盗链，下载时带 `Referer: https://mp.weixin.qq.com`。
- **HTML→Markdown**：用 `markdownify` + 预清洗（去广告/推荐卡片/二维码）。
- **去重**：URL 去重（progress.crawled_urls）+ 正文 SHA-256 去重（manifest 查重）。
- **频率**：每篇 `random.uniform(5, 10)` 秒，并发=1；遇 429/风控立即停止报告。
- **历史消息页已弃用**：`profile_ext?action=home` 常被微信 `Verify` 拦截，浏览器不可行。

详见 [scripts/gzh_archive.py](scripts/gzh_archive.py) —— 可复用的抓取/转换/存档工具。

## Rules

- [rules/workflow.md](rules/workflow.md) - 完整五步工作流与命令行操作
- [rules/enumeration.md](rules/enumeration.md) - 公众号文章枚举策略（搜一搜/biz/翻页）
- [rules/html-to-markdown.md](rules/html-to-markdown.md) - HTML 清洗与 Markdown 转换规则
- [rules/resume-dedup.md](rules/resume-dedup.md) - 断点续抓、增量更新、去重策略
- [rules/anti-aigc.md](rules/anti-aigc.md) - 存档报告与索引的反AIGC规则

## 使用示例 / Examples

### 示例 1：抓取一个公众号全部文章

```
用户/User: /公众号 某科技评论

→ Step 0: 检查环境（selenium/chrome 已就绪）
→ Step 1: 浏览器打开搜一搜搜"某科技评论"，定位 biz=MTIzNDU...
→ Step 2: 进入历史文章页，翻页枚举得 128 篇文章 URL
→ Step 3: 逐篇抓取，HTML→Markdown，图片下载到 images/
→ Step 4: 存档到 ~/WeChatArchives/某科技评论/
→ 输出：128 篇 .md + index.md，进度存 progress.json
→ 报告：抓取 128 篇，跳过 0 篇，失败 0 篇，耗时 14 分钟
```

### 示例 2：中断后续抓

```
用户/User: /公众号 resume 某科技评论

→ 读 progress.json：已抓 87 篇，last_url=...
→ 从第 88 篇继续，跳过已抓 URL
→ 输出：新增 41 篇，存档完成
```

### 示例 3：增量更新

```
用户/User: /公众号 refresh 某科技评论

→ 读 progress.last_crawl=2026-07-01
→ 重新枚举，只抓 2026-07-01 之后发布的新文章
→ 输出：新增 3 篇，存档更新
```

### 示例 4：全文检索

```
用户/User: /公众号 search 大模型

→ rg "大模型" ~/WeChatArchives/某科技评论/articles/
→ 输出：命中 12 篇，每篇文件路径 + 命中行
  articles/20260615-谈谈大模型的上下文.md:42: ...
  articles/20260720-大模型推理优化.md:15: ...
```

## 边界情况 / Edge Cases

- **登录态失效**：报告"需重新扫码"，保留已抓进度，重新登录后 `resume` 继续
- **验证码/风控**：立即停止，报告当前 URL 与进度，等用户手动处理后 `resume`；不反制不重试轰炸
- **文章被删/403**：记录到 manifest 的 `status=deleted`，跳过，继续下一篇
- **图片防盗链失败**：保留原远程 URL 在 Markdown（标注 `<!-- remote: URL -->`），不阻塞转换
- **超长文章**：分段转 Markdown，保留层级；单文件可能较大但不拆分（保持完整可读）
- **视频/音频卡片**：转成 `[视频卡片](原链接)` 占位，不下载媒体本体
- **付费/会员文章**：只能抓免费可见部分，付费墙后内容标注 `<!-- 付费内容，未抓取 -->`
- **同名公众号多个**：搜一搜列出候选，由用户选择具体一个（报 biz 与简介）
- **biz 失效**：公众号迁移/改名后 biz 可能变；`refresh` 时重新搜名称取新 biz
- **文章 URL 临时链接**：微信文章链接含 `chksm` 等时效参数，长期可能失效；存档时同时存原 URL 与正文 SHA-256，URL 失效后仍可按正文检索

## 常见问题排查 / Troubleshooting

- **搜一搜搜不到公众号** → 名称有特殊字符/英文，试精确匹配；或直接提供 biz-id
- **浏览器一闪就关** → 用了 headless 且登录态失效；去掉 `--headless`，手动扫码登录
- **翻页只抓到 10 篇就停** → 历史消息页是 ajax 滚动加载，需 `scroll_to_bottom` 循环；检查 [rules/enumeration.md](rules/enumeration.md)
- **图片下载 403** → 缺 `Referer: https://mp.weixin.qq.com`；脚本已带，检查是否被中间页跳转
- **Markdown 里有乱码** → 正文用了 `data-src` 懒加载，需先滚动触发；或微信用了变体字体，需 `readability` 清洗
- **抓取中途断网** → 进度已存 `progress.json`，`/公众号 resume` 继续
- **重复抓到同一篇** → URL 去重集生效；若微信同篇多 URL（参数不同），按正文 SHA-256 二次去重
- **selenium 找不到元素** → 微信页面结构变更，更新 [rules/enumeration.md](rules/enumeration.md) 的选择器

## 配置选项 / Configuration

| 参数/Param | 默认值/Default | 说明/Description |
|-----------|---------------|-----------------|
| archives_root | `~/WeChatArchives` | 存档根目录 / Archives root |
| user_data_dir | `~/.opencode-gzh-profile` | 浏览器登录态持久化 / Cookie persistence |
| headless | false | 无头模式（不推荐，登录态难维护） |
| min_delay | 3 | 每篇最小延迟秒 / Min delay per article |
| max_delay | 7 | 每篇最大延迟秒 / Max delay per article |
| max_concurrency | 1 | 并发数（始终 1，不并发） / Concurrency (always 1) |
| download_images | true | 下载图片到本地 / Download images locally |
| retry_on_block | 3 | 风控重试次数，超过即停 / Block retry count |
| backoff_base | 60 | 风控退避基础秒 / Backoff base seconds |

## 集成 / Integration

### 与回收技能集成 / Integration with hui-shou

```
覆盖已有存档目录前 / Before overwriting existing archive:
    ↓
/回收 overwrite <存档目录>   # hui-shou 技能
    ↓
旧存档入回收站（可回滚）
    ↓
写入新存档
```

### 与其他技能集成 / Skill Integration

```
/安检 an-jian 审查本技能
    ↓
确认无危险命令（curl|bash/rm -rf）
    ↓
建议启用 /回收 guard on 守护覆盖操作
    ↓
/公众号 抓取 → /回收 保护旧存档
```

## Anti-Patterns

| 违规 / Violation | 严重度 / Severity | 后果 / Consequence |
|------|--------|------|
| 并发抓取 / Concurrent scraping | 高/High | 触发风控、IP 封禁 / Trigger rate-limit, IP ban |
| 破解验证码 / Bypass captcha | 严重/Critical | 违反平台规则 / Violates platform ToS |
| 去掉延迟全速抓 / Remove delay | 高/High | 风控限流 / Rate-limited |
| 不保留原作者署名 / Drop attribution | 高/High | 侵权 / Copyright infringement |
| 覆盖存档不走回收站 / Overwrite without trash | 中/Medium | 旧存档丢失 / Old archive lost |
| headless 跑导致登录失败不报 / Silent login fail in headless | 中/Medium | 抓到空内容 / Empty content scraped |

## AIGC检测意识 / AIGC-Aware Output

存档报告与索引必须给出具体数字与路径，不写"已成功抓取"这类空话。参见 [rules/anti-aigc.md](rules/anti-aigc.md)。

核心要求：
- 不写"已抓取公众号文章"，写"抓取 128 篇，跳过 0 篇，失败 0 篇，存档于 ~/WeChatArchives/某科技评论/，耗时 14 分钟"
- index.md 列出每篇标题+日期+本地路径，不写"全部文章已保存"

## 版本历史 / Version History

| 版本 | 日期 | 变更 |
|------|------|------|
| 1.0.0 | 2026-07-29 | 初始版本：浏览器枚举、逐篇抓取转 Markdown、图片本地化、断点续抓、增量更新、全文检索 |

## See Also / 相关技能

- `/回收` from **hui-shou** — 覆盖存档前先入回收站，保护旧成果
- `/安检` from **an-jian** — 审查本技能无危险命令
- `/视频萃取` from **video-extract** — 公众号文章内的视频可转交此技能萃取