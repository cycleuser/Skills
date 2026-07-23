# 专业站点整理细则 (Professional Sites Compilation Rules)

## 站点选取原则

### 准入标准（必须满足 ≥2 条）
1. 圈内公认 — 在领域的论文、课程、社区中反复被推荐
2. 有活跃用户/维护者 — 非僵尸站点
3. 信息有明确更新时间 — 站内内容或数据库有明确的更新日期
4. 内容专业深度 — 不是百科级别的浅层介绍

### 排除列表
- Wikipedia、百度百科、知乎百科等通用百科
- SEO 垃圾站、采集站
- 超过 2 年未更新的死站（除非是归档性数据库）
- 纯商业推广站（如培训班官网、加盟介绍页）

## 站点分类体系

### 预印本/论文库 (Preprint/Repository)
- 研究者直接上传论文的开放获取平台
- 示例：arXiv, bioRxiv, SSRN, RePEc

### 文献数据库 (Literature Database)
- 收录已发表论文的索引/摘要库
- 示例：PubMed, IEEE Xplore, ACM Digital Library, Scopus

### 专业论坛/社区 (Forum/Community)
- 领域从业者交流讨论的平台
- 示例：Stack Overflow (CS), MathOverflow (Math), ResearchGate Q&A

### 代码/数据平台 (Code/Data Platform)
- 领域内共享代码、数据集、模型的平台
- 示例：GitHub, Hugging Face, Kaggle, Zenodo

### 专业学会/组织 (Society/Organisation)
- 领域内的专业学会、协会网站
- 示例：ACL, ACM, APS, ACS

### 工具/资源目录 (Tool/Resource Directory)
- 汇总领域内工具、资源、教程的站点
- 示例：Papers With Code, NLP-progress

### 期刊/会议主页 (Journal/Conference)
- 领域内顶级期刊和会议的官方网站
- 示例：nature.com (Nature), cv-foundation.org (CVPR/ICCV)

## 站点信息收集模板

每条站点记录：
```yaml
name: 站点名称
url: 完整URL
type: 类型（预印本库/数据库/论坛/代码平台/学会/工具目录/期刊/会议）
language: 主要语言
description: 一句话简介（50字内）
update_frequency: 每日/每周/每月/实时发布/不定期
access: 免费/部分免费/付费墙/需注册
notes: 补充信息（如"中文仅有摘要"、"API免费但限频"等）
```

## 搜索方法

### 方法一：搜索引擎
```
"领域名" forum OR community OR "online community"
"领域名" database OR repository
"领域名" "recommended websites" OR "top resources"
"学习领域名" "推荐网站" OR "资源汇总"
site:reddit.com "领域名" "where to start" OR "resources"
```

### 方法二：论文反向发现
- 查该领域的综述论文（review/survey），看 Reference 或 Resources 章节
- 查该领域教材/书籍的附录"推荐资源"
- 查该领域的 GitHub awesome list：`awesome 领域名 site:github.com`

### 方法三：学术社区探索
- 查领域顶会的 Sponsor/Exhibitor 页面
- 查领域学会的 "Resources" 或 "Links" 页面
- 查领域内著名教授的个人主页上的 "Links" 页面

## 输出表格模板

```markdown
## 专业站点与数据库 / Professional Sites & Databases

**搜索时间**: 2026-07-23T14:45:00+08:00
**选取标准**: 圈内公认站点，排除通用百科。选取满足 ≥2 条准入标准。

### 预印本/论文库
| 站点 | URL | 简介 | 更新频率 | 访问 |
|------|-----|------|----------|------|
| arXiv | [链接](url) | 物理学、数学、CS预印本 | 每日 | 🆓 |

### 文献数据库
| 站点 | URL | 简介 | 更新频率 | 访问 |
|------|-----|------|----------|------|
| {name} | [链接](url) | {描述} | {频率} | 🆓/🏫 |

### 专业论坛/社区
| 站点 | URL | 简介 | 更新频率 | 访问 |
|------|-----|------|----------|------|
| {name} | [链接](url) | {描述} | {频率} | 🆓/需注册 |

### 代码/数据平台
| 站点 | URL | 简介 | 更新频率 | 访问 |
|------|-----|------|----------|------|
| {name} | [链接](url) | {描述} | {频率} | 🆓 |

### 专业学会/组织
| 站点 | URL | 简介 | 更新频率 | 访问 |
|------|-----|------|----------|------|
| {name} | [链接](url) | {描述} | {频率} | 🆓/会员制 |

### 期刊/会议
| 站点 | URL | 简介 | 更新频率 | 访问 |
|------|-----|------|----------|------|
| {name} | [链接](url) | {描述} | {频率} | 🆓/🏫 |
```

## 特殊说明模板（按领域）

```markdown
### 领域说明

**{领域名}** 的主要学术交流渠道为：
- 预印本：{平台名}，该领域学者高度依赖预印本交流
- 会议：{会议缩写}（CCF-A / CORE A*），年收稿 {n} 篇
- 期刊：{期刊名}（IF: {n}），该领域顶级期刊
- 社区：{论坛名}（月活 {n} 万），日常讨论集中于此

> ⚠️ 以上频度数据基于搜索当日可获取的公开信息估算，具体数字可能变化。
```
