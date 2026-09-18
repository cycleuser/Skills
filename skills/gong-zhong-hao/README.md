# 公众号 (GongZhongHao)

## 状态：Beta

## 用途

公众号文章存档技能。给定公众号名称或 biz-id，用真实浏览器（Selenium）枚举其全部历史文章，逐篇抓取 HTML 转为干净 Markdown（含 front-matter + 本地图片），保存到本地，支持断点续抓、增量更新、全文检索。

核心一句话：浏览器驱动枚举，逐篇抓取转 Markdown，断点续抓、增量更新。

## 快速命令

| 命令 | 说明 |
|------|------|
| `/公众号 <名称或biz>` | 抓取全部文章为 Markdown |
| `/公众号 resume <名称或biz>` | 从断点继续 |
| `/公众号 refresh <名称或biz>` | 只抓新增文章（增量更新） |
| `/公众号 search <关键词>` | 已存档全文检索 |
| `/公众号 list` | 列出已存档公众号 |
| `/公众号 check` | 检查依赖与浏览器环境 |
| `/gongzhonghao <name-or-biz>` | English: full archive |
| `/gongzhonghao resume <name-or-biz>` | English: resume |
| `/gongzhonghao refresh <name-or-biz>` | English: incremental update |

## 适用场景

- 备份喜欢的公众号全部文章到本地，防链接失效/账号被封
- 把公众号内容转为 Markdown 离线阅读
- 跨公众号全文检索历史文章
- 定期增量更新已存档公众号

## 为什么需要它

微信无官方"导出全部文章"功能，文章散落在生态里易失效；本技能用真实浏览器逐篇访问，固化为本地 Markdown，图片下载本地化保证离线可读，断点续抓保证大账号可分次抓完。

## 五步工作流

1. **检查** Check：检查 selenium/chrome/依赖，首次需手动扫码登录
2. **枚举** Enumerate：浏览器打开历史消息页，滚动加载 ajax 解析文章列表
3. **抓取** Fetch：逐篇访问，提取标题/作者/时间/正文，图片下载本地化
4. **转换** Convert：HTML 清洗去广告，markdownify 转 Markdown 加 front-matter
5. **存档** Persist：写 articles/、images/、append manifest.jsonl、更新 progress.json、生成 index.md

## 输出目录

```
~/WeChatArchives/<公众号名-or-biz>/
├── articles/YYYYMMDD-<slug>.md   # 每篇 Markdown
├── images/<sha1>.<ext>            # 图片本地副本
├── progress.json                 # 断点续抓状态
├── manifest.jsonl                # append-only 元数据日志
└── index.md                       # 全部文章索引
```

## 依赖

| 工具 | 用途 | 安装 |
|------|------|------|
| selenium | 浏览器自动化 | pip install selenium |
| webdriver-manager | chromedriver 管理 | pip install webdriver-manager |
| markdownify | HTML→Markdown | pip install markdownify |
| readability-lxml | 正文提取 | pip install readability-lxml |
| requests | 图片下载 | pip install requests |
| beautifulsoup4 | HTML 解析 | pip install beautifulsoup4 |
| pyyaml | front-matter | pip install pyyaml |
| ripgrep (rg) | 全文检索 | brew install ripgrep |

- 依赖 `_shared/core/safety-rules.md`

## 安全与合规原则

- **仅用于个人学习存档**，不重新分发、不商用
- **浏览器自动化可见**（非 headless），登录验证码由用户手动完成
- **不破解不绕过**：遇风控/限流/验证码即停止报告，不反制不轰炸
- **频率克制**：每篇 3-7 秒随机抖动，并发=1
- **写入走回收站**：覆盖前用 `/回收 overwrite`（hui-shou 技能）保护旧存档
- 保留原作者署名与来源链接

## 文件结构

```
skills/gong-zhong-hao/
├── README.md
├── SKILL.md
├── rules/
│   ├── workflow.md           # 五步工作流与命令行操作
│   ├── enumeration.md        # 文章枚举策略（搜一搜/biz/翻页）
│   ├── html-to-markdown.md   # HTML 清洗与 Markdown 转换
│   ├── resume-dedup.md       # 断点续抓、增量更新、去重
│   └── anti-aigc.md          # 存档报告反AIGC规则
└── scripts/
    └── gzh_archive.py        # 抓取/转换/存档/检索工具
```

## 参见

- `/回收` from **hui-shou** — 覆盖存档前先入回收站，保护旧成果
- `/安检` from **an-jian** — 审查本技能无危险命令
- `/视频萃取` from **video-extract** — 公众号文章内的视频可转交此技能萃取