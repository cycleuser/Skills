# 输出格式与引用格式规范 (Output & Citation Format Rules)

## 最终报告结构

```markdown
# 学术导览：[领域名称]

**生成时间**: 2026-07-23T15:30:00+08:00
**导览范围**: {领域英文名 / 中文名}
**导览模式**: 完整四步 / 仅论文 / 仅站点 / 仅验证
**执行时间**: Phase 1: 15min, Phase 2: 10min, Phase 3: — , Phase 4: 20min
**联系方式**: [留空，用户可自行填写]

---

## 快速导读 / Quick Guide

{3-5句话概述该领域当前的研究格局：主要方向、活跃的研究群体、核心基础设施（数据库/工具链）、入门建议。每条信息在后文中必须有来源支撑。}

---

## 一、博士论文 / Doctoral Dissertations

{详见 dissertation-search.md 输出格式}

---

## 二、专业站点与数据库 / Professional Sites & Databases

{详见 professional-sites.md 输出格式}

---

## 三、搜索过程记录 / Search Records

{详见 search-records.md 输出格式}

---

## 四、引用验证报告 / Citation Verification Report

{详见 citation-verification.md 输出格式}

---

## 参考文献 / References

{所有已验证引用，格式见下方}

---

## 入门建议 / Getting Started

{基于上述收集的信息，给出3-5条具体的入门建议。每条建议必须引用上文的搜索结果。
例如："建议从 arXiv 上的综述论文 [1] 开始了解全貌，然后选择 GitHub 上的 {项目名} [4] 作为代码参考。"}

---

> **关于本报告**: 所有引用链接生成于 {日期}，已通过逐条验证。如果链接失效，请尝试 Wayback Machine 或联系报告生成者获取更新。
```

## 引用格式规范

### 论文引用 — APA 7th 格式

**英文论文:**
```
Author, A. A., & Author, B. B. (Year). Title of dissertation: Subtitle if any (Publication No. xxxxxx) [Doctoral dissertation, University Name]. Database Name. https://doi.org/xxxxx
```

简化版（用于此导览报告）:
```
Author, A. (Year). Title of Dissertation. PhD thesis, University Name. URL [✅/⚠️/🏫 验证状态]
```

**中文论文 (GB/T 7714):**
```
作者. 论文标题[D]. 学校所在地: 学校名称, 年份. URL [验证状态]
```

### 网站引用
```
Site Name. (Year). Description of the site. URL [验证状态]
```

### 预印本引用
```
Author, A. (Year). Title. arXiv preprint arXiv:xxxx.xxxxx. https://arxiv.org/abs/xxxx.xxxxx [验证状态]
```

### 期刊论文引用
```
Author, A. (Year). Title. Journal Name, Volume(Issue), Pages. https://doi.org/xxxxx [验证状态]
```

## 参考文献编号与排序

- 使用方括号编号 [1], [2], [3] ...
- 按出现顺序排列（正文中先引用的排前面）
- 同一处引用多个文献：`[1-3]` 或 `[1,3,5]`

## 中英双语规范

- 领域名、论文标题、作者名：保留原始语言
- 分析说明：用户使用什么语言发问就用什么语言输出
- 中文命令（`/学术导览`）→ 中文报告
- 英文命令（`/AcademicGuide`）→ 英文报告
- 表格标题、章节标题双语

## 文件命名

```
final-report.md          # 最终报告（唯一交付物）
final-report-en.md       # 英文版（如需要）
```

临时工作文件保存在 `/tmp/academic-guide/{YYYYMMDD-HHmmss}/`，不交付给用户。

## Markdown 规范

- 标题层级：`#` → `##` → `###` → `####`，最多四级
- 表格必须对齐，不得使用不完整的表格
- 链接格式：`[显示文本](URL)`，不裸露 URL
- 代码/命令：反引号包裹
- 文件名/路径：反引号包裹
- 强调：用 `**粗体**`，不用 `__下划线__`
- 图片：用 `![描述](URL)` 并附带 alt text

## 输出检查清单

最终报告输出前：
- [ ] 章节结构完整，无缺节
- [ ] 所有链接已验证且标注状态
- [ ] 参考文献格式规范，可独立验证
- [ ] 表格对齐无错乱
- [ ] 无空表格或无内容章节
- [ ] 快速导读涵盖后文关键发现
- [ ] 入门建议有具体文献引用 [1][2]...
- [ ] 最终报告保存路径已告知用户
