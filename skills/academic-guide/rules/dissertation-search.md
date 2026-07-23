# 博士论文搜索细则 (Dissertation Search Rules)

## 搜索源优先级

每次搜索必须按以下优先级尝试多个数据库，至少覆盖前 3 个：

### Tier 1 — 必须搜索
| 数据库 | URL | 覆盖 | 访问方式 |
|--------|-----|------|----------|
| Google Scholar | https://scholar.google.com | 全球 | 免费搜索 |
| NDLTD | https://ndltd.org | 全球 | 免费获取 |
| OATD | https://oatd.org | 全球 | 免费获取 |

### Tier 2 — 按领域选择
| 数据库 | URL | 覆盖 | 访问方式 |
|--------|-----|------|----------|
| ProQuest Dissertations | https://www.proquest.com/dissertations | 全球，英文为主 | 机构 |
| CNKI 博硕士 | https://kns.cnki.net/kns8s?classid=CDMD | 中国大陆 | 机构 |
| DART-Europe | https://www.dart-europe.eu | 欧洲 | 免费 |
| EThOS | https://ethos.bl.uk | 英国 | 免费 |

### Tier 3 — 补充搜索
| 数据库 | URL | 覆盖 | 访问方式 |
|--------|-----|------|----------|
| PQDT Open | https://pqdtopen.proquest.com | 已授权的PQDT论文 | 免费 |
| arXiv | https://arxiv.org | STEM | 免费 |
| ResearchGate | https://www.researchgate.net | 全球 | 免费（需注册） |
| SSRN | https://ssrn.com | 社会科学 | 免费 |

## 搜索关键词模板

### 英文搜索
```
"领域名" "doctoral dissertation" 年份
"领域名" PhD thesis 年份
"领域名" "dissertation" PDF
```

### 中文搜索
```
"领域名" 博士论文 年份
"领域名" 博士学位论文 年份
"领域名" 博士 毕业论文
```

### 高级技巧
- 使用 `site:edu` 限制教育机构
- 使用 `filetype:pdf` 找可下载全文
- 用 OR 连接同义词：`("machine learning" OR "deep learning") dissertation`
- 排除无关词：`-"master" -"硕士"` 排除硕士论文

## 论文信息提取

每条论文必须提取以下字段：
```yaml
title: 完整标题
author: 作者全名
school: 授予学位的大学/机构全称
year: 发表年份
url: 论文在数据库中的页面链接
access: 🆓 / 🏫 / 🔒
preprint_url: 预印本链接（如存在）
preprint_source: 预印本来源（arXiv/ResearchGate/个人主页等）
notes: 补充说明（如"摘要仅"、"需要机构VPN"等）
```

## 获取方式判定标准

### 🆓 免费获取
- 点击链接后可直接下载PDF全文
- 或经过简单注册（如ResearchGate账号）后可下载
- 标注具体的获取路径

### 🏫 机构访问
- 需要大学/研究机构订阅
- 或需要校园网 IP
- 必须附带预印本追查结果

### 🔒 完全封闭
- 仅印刷版、无电子版
- 或学校明确禁止论文公开
- 或需作者本人授权才能查看

## 预印本追查流程

对于标记为🏫的论文，逐条执行：
1. 搜索 arXiv.org — 关键词：作者名 + 论文关键词
2. 搜索 ResearchGate — 关键词：论文标题
3. 搜索 Google Scholar — 查看 [PDF] 或 [HTML] 侧边链接
4. 搜索作者个人主页 — `"作者名" homepage OR CV OR publications`
5. 搜索机构知识库 — `site:学校域名 "论文标题"`
6. 搜索 Semantic Scholar — https://www.semanticscholar.org/

追查结果在论文记录中标注：
```markdown
| 🏫 | [arXiv预印本](link) | 内容与正式版有差异，缺少第4章实验部分 |
| 🏫 | 未找到预印本 | — |
```

## 论文筛选标准

- 近三年内优先（超过三年的仅在相关论文不足10篇时补入）
- 与领域直接相关，仅通过关键词匹配的可保留最多5篇弱相关论文
- 排除硕士学位论文和本科毕业论文
- 同一作者同一课题的多篇博士论文，仅保留最新一篇

## 输出表格模板

```markdown
## 博士论文 / Doctoral Dissertations

**搜索时间**: 2026-07-23T14:30:00+08:00
**搜索数据库**: Google Scholar, NDLTD, OATD, ProQuest, CNKI
**时间范围**: 2023-2026
**找到总数**: 47 篇（收录 20 篇）

### 🆓 免费获取 ({n}篇)

| # | 标题 | 作者 | 学校 | 年份 | 下载链接 |
|---|------|------|------|------|----------|
| 1 | {title} | {author} | {school} | {year} | [PDF](url) / [页面](url) |

### 🏫 机构访问 ({n}篇)

| # | 标题 | 作者 | 学校 | 年份 | 官方链接 | 预印本 |
|---|------|------|------|------|----------|--------|
| 1 | {title} | {author} | {school} | {year} | [ProQuest](url) | [arXiv](url) ✅ / 未找到 ❌ |

### 🔒 完全封闭 ({n}篇)

| # | 标题 | 作者 | 学校 | 年份 | 说明 |
|---|------|------|------|------|------|
| 1 | {title} | {author} | {school} | {year} | 仅印刷版，无电子版 |
```
