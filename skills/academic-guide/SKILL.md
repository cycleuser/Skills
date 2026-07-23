---
name: academic-guide
version: "1.1.0"
description: |
  学术导览 — 帮助初学者入门新学科领域。搜索博士论文、整理专业站点、记录搜索过程、验证每条引用。

  Triggers when: 用户想入门新学科、需要领域概览、搜索博士论文、整理权威专业站点、或需要验证引用链接。

  Commands:
  - /学术导览 <领域名称> - 完整四步学术导览流程
  - /导览 论文 <领域> - 仅搜索博士论文
  - /导览 站点 <领域> - 仅整理专业站点
  - /导览 验证 <报告文件> - 仅验证参考文献链接
  - /AcademicGuide <field> - Full English workflow
  - /guide dissertations <field> - Search dissertations only
  - /guide sites <field> - Compile professional sites only
  - /guide verify <report> - Verify citations only

  Capabilities: 博士论文搜索（ProQuest/CNKI/NDLTD/Google Scholar），多标签标注免费/机构/封闭获取，预印本搜索，专业站点与数据库发现，原始搜索记录保全，参考文献逐条链接验证，规范引用格式输出，中英双语支持
author: cycleuser
license: MIT
status: Beta
---

## Safety Rules

参见 [_shared/core/safety-rules.md](../_shared/core/safety-rules.md) — 所有安全规则从共享层加载。

# 学术导览 (AcademicGuide)

学科入门导览工具。四步流程：搜论文 → 找站点 → 存记录 → 验引用。

A field orientation guide. Four phases: search dissertations → compile professional sites → preserve search records → verify every citation.

<role>
Academic field navigator. Search recent doctoral dissertations in a given field, identify authoritative professional websites/forums/databases, preserve complete search records with provenance, and — most critically — verify every reference link independently before including it in the final output. Zero unverified citations allowed.
</role>

## Quick Commands

| Command | Description |
|---------|-------------|
| `/学术导览 <领域名称>` | 完整四步流程：论文→站点→记录→验证 |
| `/导览 论文 <领域>` | 仅第一步：搜索博士论文 |
| `/导览 站点 <领域>` | 仅第二步：整理专业站点 |
| `/导览 验证 <报告>` | 仅第四步：验证已有报告的引用 |
| `/AcademicGuide <field>` | Full English workflow |
| `/guide dissertations <field>` | Search dissertations only |
| `/guide sites <field>` | Compile sites only |
| `/guide verify <report>` | Verify citations only |

## 核心原则 / Core Principles

### 原则一：可验证性 — 每条引用必须能独立验证

```
【绝对禁止 / NEVER】
- 输出未经逐条打开验证的链接
- 引用404/403/需登录的页面而不标注
- 猜测论文标题或作者名
- 虚构不存在的下载链接
- 使用"可能""大概""应该"描述论文来源

【必须做到 / MUST】
- 每条参考文献独立打开URL验证
- 标注每条链接的访问状态（✅可访问 / ⚠️部分可访问 / ❌不可访问）
- 区分获取方式（🆓免费 / 🏫机构 / 🔒封闭）
- 搜索记录保留时间戳、来源搜索引擎、使用的关键词
```

### 原则二：搜索过程透明 — 每步操作可追溯

```
每次搜索必须记录：
- 搜索时间（ISO 8601格式）
- 搜索引擎/数据库名称
- 使用的搜索关键词
- 返回结果数量（估算）
- 实际访问和验证的URL列表
```

### 原则三：引用就绪 — 输出即引用

```
最终报告中的每条信息都必须附带可点击验证的URL。
参考文献列表单独成节，脱离上下文也能验证。
```

## 四步工作流 / Four-Phase Workflow

### Phase 1: 博士论文搜索 / Dissertation Search

详见 [rules/dissertation-search.md](rules/dissertation-search.md)

**搜索源（按优先级）:**

| 优先级 | 数据库 | 覆盖范围 | 特点 |
|--------|--------|----------|------|
| 1 | ProQuest Dissertations & Theses Global | 全球（英文为主） | 最大博论文库，多数有预览 |
| 2 | CNKI 博硕士学位论文库 | 中国大陆 | 中文论文最全 |
| 3 | NDLTD | 全球 | 开放获取联盟，免费 |
| 4 | Google Scholar | 全球 | 覆盖面广，可发现预印本 |
| 5 | 各大学机构库（DSpace/EPrints等） | 机构 | 免费获取本校论文 |

**搜索策略:**
- 关键词：[领域名] + "doctoral dissertation" 或 "博士论文"
- 时间范围：近三年内优先
- 语言：中英文并行搜索

**输出格式：每条论文记录包含:**
```markdown
| # | 标题 | 作者 | 学校 | 年份 | 获取方式 | 链接 |
|---|------|------|------|------|----------|------|
| 1 | {title} | {author} | {school} | {year} | 🆓/🏫/🔒 | [链接](url) |
```

**获取方式标注:**
- 🆓 免费获取 — 任何人可直接下载全文
- 🏫 机构访问 — 需要大学/机构订阅，标注是否找到预印本
- 🔒 完全封闭 — 无任何公开获取途径

**预印本追查（针对🏫机构访问论文）:**
- 搜索 arXiv, ResearchGate, 作者个人主页, 机构知识库
- 标注预印本链接和版本差异

### Phase 2: 专业站点整理 / Professional Sites Compilation

详见 [rules/professional-sites.md](rules/professional-sites.md)

**站点选取标准:**
- 圈内公认，非百科类泛泛站点
- 有实际领域专家/从业者活跃
- 信息更新频率明确
- 排除 Wikipedia、百度百科等通用百科

**输出格式：每个站点包含:**
```markdown
| 站点名称 | URL | 类型 | 简介 | 更新频率 | 备注 |
|----------|-----|------|------|----------|------|
| {name} | [链接](url) | 论坛/数据库/期刊/... | 一句话说明 | 每日/每周/每月 | 注册/付费/免费 |
```

### Phase 3: 搜索记录保全 / Search Record Preservation

详见 [rules/search-records.md](rules/search-records.md)

**每步搜索必须记录：**
```markdown
## 搜索记录 / Search Log

### 搜索 #1
- **时间**: 2026-07-23T14:30:00+08:00
- **引擎**: Google Scholar
- **关键词**: "machine learning" "doctoral dissertation" 2023
- **结果数**: 约 17,800 条
- **实际访问**: 8 条
- **保存链接**:
  - https://scholar.google.com/scholar?q=...
  - [截图保存路径，如适用]
```

### Phase 4: 引用验证 / Citation Verification ⚠️ 最重要

详见 [rules/citation-verification.md](rules/citation-verification.md)

**这是整个流程中最关键的一步。没有经过验证的引用一律不得放入最终报告。**

**验证流程:**
```
1. 从最终报告中提取所有URL
2. 逐条浏览器打开每个链接
3. 确认：
   a. 链接可访问（非404/403）
   b. 页面内容与引用描述一致
   c. 论文标题、作者、年份信息匹配
4. 标注验证状态：
   ✅ 已验证可访问
   ⚠️ 可访问但有限制（需登录/付费墙/摘要仅）
   ❌ 不可访问（404/403/需特殊权限）
5. 不可访问的链接，尝试 Wayback Machine 存档或替代来源
6. 无法验证的引用，标记为"🔴 未通过验证，已移除"并移除
```

**验证输出格式:**
```markdown
## 引用验证报告 / Citation Verification Report

| # | URL | 状态 | 内容匹配 | 备注 |
|---|-----|------|----------|------|
| 1 | https://... | ✅ | ✅ 标题作者一致 | |
| 2 | https://... | ⚠️ | ✅ 摘要匹配 | 需机构登录看全文 |
| 3 | https://... | ❌ | — | 404，已用Wayback替代 |
```

## 最终报告结构 / Final Report Structure

```markdown
# 学术导览：[领域名称]

**生成时间**: {ISO 8601}
**导览模式**: 完整四步 / 论文 / 站点 / 验证

## 一、博士论文 / Doctoral Dissertations

[Phase 1 输出表格]

## 二、专业站点与数据库 / Professional Sites & Databases

[Phase 2 输出表格]

## 三、搜索过程记录 / Search Records

[Phase 3 完整搜索记录]

## 四、引用验证报告 / Citation Verification Report

[Phase 4 验证结果]

## 参考文献 / References

[所有已验证通过的引用，格式规范，每条可点击验证]
```

## 输出目录 / Output Directory

```
/tmp/academic-guide/{YYYYMMDD-HHmmss}/
├── phase1-dissertations.md    # 博士论文搜索结果
├── phase2-sites.md            # 专业站点整理
├── phase3-search-log.md       # 搜索过程记录
├── phase4-verification.md     # 引用验证报告
└── final-report.md            # 最终汇总报告
```

## 反模式 / Anti-Patterns

| 违规 | 严重度 | 后果 |
|------|--------|------|
| 输出未经验证的URL引用 | **CRITICAL** | 报告不可信，用户点击遇到404 |
| 虚构论文信息 | **CRITICAL** | 学术诚信完全丧失 |
| 跳过Phase 4验证直接输出 | **CRITICAL** | 违反核心原则一 |
| 用百科类站点充专业站点 | HIGH | 降低报告专业度 |
| 不记录搜索时间/关键词/来源 | HIGH | 搜索过程不可复现 |
| 论文获取方式标注错误 | HIGH | 误导用户访问预期 |
| 中文领域只搜中文，不搜英文 | MEDIUM | 遗漏国际前沿研究 |
| 不追查机构访问论文的预印本 | MEDIUM | 丢失潜在免费获取途径 |

## 搜索源速查 / Quick Search References

### 博士论文数据库
| 数据库 | URL | 类型 |
|--------|-----|------|
| ProQuest Dissertations | https://www.proquest.com/dissertations/ | 付费/机构 |
| CNKI 博硕论文 | https://kns.cnki.net/kns8s/?classid=CDMD | 付费/机构 |
| NDLTD | https://ndltd.org/ | 免费 |
| Google Scholar | https://scholar.google.com/ | 免费搜索 |
| arXiv | https://arxiv.org/ | 免费预印本 |
| ResearchGate | https://www.researchgate.net/ | 免费（需注册） |
| Open Access Theses (OATD) | https://oatd.org/ | 免费 |
| DART-Europe | https://www.dart-europe.eu/ | 免费 |
| EThOS (英国) | https://ethos.bl.uk/ | 免费 |
| PQDT Open | https://pqdtopen.proquest.com/ | 免费 |

### 常用学科站点（脚本会动态搜索，以下为示例类目）
| 领域 | 典型站点 | 类型 |
|------|----------|------|
| 计算机 | Stack Overflow, GitHub, ACM DL, IEEE Xplore | 论坛/代码库/数据库 |
| 数学/物理 | arXiv, MathOverflow, nLab, APS Journals | 预印本/论坛/期刊 |
| 医学/生物 | PubMed, UpToDate, Cochrane Library, bioRxiv | 数据库/预印本 |
| 化学 | Reaxys, SciFinder, ChemSpider, CCDC | 数据库 |
| 社会科学 | SSRN, SocArXiv, ICPSR, RePEc | 预印本/数据库 |

## 常见问题排查 / Troubleshooting

### 搜索返回空结果
- **症状**: 搜索引擎返回零结果或无相关论文
- **解决**: 拆分关键词，尝试中英文双语搜索；检查领域名称拼写；使用同义词或上位词；扩大时间范围至五年

### 论文链接全标"🔒封闭"
- **症状**: 找到的论文全部需要机构登录
- **解决**: 追加搜索预印本（arXiv/ResearchGate）；搜索作者个人主页的CV页面；使用OATD/NDLTD等开放获取源；搜索作者所在大学的机构库

### 专业站点找不到
- **症状**: 搜索结果被百科类站点淹没
- **解决**: 使用 `"领域名" forum OR community` 等精确搜索；搜索 `site:reddit.com "领域名"` 看社区推荐；查相关期刊的"推荐站点"页面

### 引用验证时大量链接失效
- **症状**: Phase 4 验证发现大部分链接404
- **解决**: 使用 Wayback Machine (`https://web.archive.org/web/*/`) 回退；重新搜索找替代源；标注"原始链接已失效，替代来源为..."

## 边界情况 / Edge Cases

- **新兴交叉学科**: 可能没有专门的博士论文库收录，需要拆分为多个子领域分别搜索，在报告中说明拼合逻辑
- **非英语/中文领域**: 如日语、韩语、阿拉伯语等，需要增加对应语种数据库搜索（如 CiNii for Japanese, KCI for Korean）
- **冷门小众领域**: 如果近三年没有博士论文，扩大时间范围至五年并在报告中说明
- **领域名称歧义**: 如 "Python" 可能指编程语言或蛇类，需要在搜索记录中说明消歧策略
- **全部封闭获取**: 如果该领域论文几乎不公开（如某些军工领域），在报告中诚实说明并给出替代文献建议
- **无专业站点**: 某些新兴领域可能没有公认的专业站点，此时标注社区活跃平台（如特定 Subreddit、Discord）替代

## 使用示例 / Usage Examples

### 示例 1：完整学术导览
```
用户/User: /学术导览 计算语言学

→ Phase 1: 搜索近三年计算语言学博士论文（ProQuest + CNKI + NDLTD + Google Scholar）
→ Phase 2: 整理 ACL Anthology、arXiv cs.CL、Linguist List 等专业站点
→ Phase 3: 保存每步搜索记录到 /tmp/academic-guide/
→ Phase 4: 逐条打开链接验证，标注状态
→ 输出最终报告到 /tmp/academic-guide/{timestamp}/final-report.md
```

### 示例 2：仅搜索论文
```
用户/User: /导览 论文 量子计算

→ 仅执行 Phase 1 和 Phase 3
→ 输出博士论文列表 + 搜索记录
```

### 示例 3：验证已有报告
```
用户/User: /导览 验证 /path/to/report.md

→ 提取报告中所有URL
→ 逐条验证
→ 输出验证报告
```

### Example 4: English Full Workflow
```
User: /AcademicGuide computational linguistics

→ Phase 1-4 with bilingual search
→ Final report in English
```

## Rules 规则文件

- [rules/dissertation-search.md](rules/dissertation-search.md) — 博士论文搜索细则
- [rules/professional-sites.md](rules/professional-sites.md) — 专业站点整理细则
- [rules/search-records.md](rules/search-records.md) — 搜索记录保全细则
- [rules/citation-verification.md](rules/citation-verification.md) — 引用验证细则（最重要）
- [rules/output-format.md](rules/output-format.md) — 输出格式与引用格式规范
- [rules/anti-aigc.md](rules/anti-aigc.md) — 导览报告反AIGC检测规则
- [../_shared/core/anti-aigc.md](../_shared/core/anti-aigc.md) — 通用反AIGC检测规则（共享层）

## 配置选项 / Configuration

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `dissertation_years` | 3 | 博士论文搜索时间范围（年） |
| `max_dissertations` | 20 | 最多收录的博士论文数量 |
| `max_sites` | 15 | 最多收录的专业站点数量 |
| `output_dir` | /tmp/academic-guide | 中间文件和报告输出目录 |
| `verify_timeout` | 15 | 单个链接验证超时时间（秒） |
| `languages` | zh, en | 搜索语言优先级 |

## AIGC-Aware Output / 反AIGC检测

学术导览报告必须具体、可验证、有来源。每句话要么是可验证的事实，要么是明确标注的推断。不写没有证据支撑的泛泛介绍。见 `rules/anti-aigc.md` 获取完整规则。

核心要求：
- 每个引用必须有可点击的URL和验证状态
- 不写"[领域名]是当前热门研究领域"，改写可量化的描述如"2024年收录博士论文47篇，较2020年增长34%"
- 站点介绍不写"该网站是领域内权威平台"，改写具体数据如"日均新帖3.2个，注册用户12万"
- 验证状态必须具体：✅/⚠️/❌，不写"大部分链接可用"

## 版本历史 / Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-07-23 | 初始版本，四步学术导览流程 |

## 相关技能 / See Also

- `/论文` from **academic-writer** — 学术论文写作，深入文献搜索和引用格式化
- `/审视` from **shen-shi** — 基于证据的分析模式，引用验证方法论参考
- `/报考` from **bao-kao** — 多源搜索交叉验证模式
