# 项目文件格式规范 / Project Structure

长篇项目以目录形式持久化。本文件规定每个文件的字段与模板，续写脚本与审稿都按此读写。

---

## 一、目录结构

```
<项目名>/
├── project.yaml          # 项目元信息
├── world-building.md     # 世界观
├── outline.md            # 情节大纲
├── characters/           # 人物卡
│   └── <角色名>.md
├── chapters/             # 章节正文
│   └── ch001.md
├── foreshadowing.md      # 伏笔追踪器
├── recycle-bin.md        # 回收站
└── review-log.md         # 审稿记录
```

---

## 二、project.yaml

```yaml
title: 长安雪
author_style: 老舍            # 默认叙述声部
genre: 武侠
status: writing              # planning | writing | paused | done
target_words: 200000
current_words: 45000
chapters_planned: 60
chapters_done: 15

style_map:                   # 分段声部（可选）
  narrator: 老舍
  hero_inner: 鲁迅
  combat: 古龙
  romance: 茨维格

current_chapter: 16
last_action: 续写
updated_at: 2026-10-13
```

字段说明：

| 字段 | 必填 | 说明 |
|------|------|------|
| title | 是 | 书名 |
| author_style | 是 | 默认叙述声部，取七家之一 |
| status | 是 | 项目所处阶段 |
| target_words | 否 | 目标总字数 |
| current_words | 否 | 当前字数，续写后回填 |
| style_map | 否 | 分段声部分配 |
| current_chapter | 否 | 下一章编号 |

---

## 三、人物卡

文件名用角色名，路径 `characters/<角色名>.md`。

```markdown
# 角色名

## 基本信息
- 身份：<职业/地位>
- 年龄：
- 外貌：<一个可记住的细节>

## 性格
- 核心特质：<一句话>
- 矛盾：<内在冲突>

## 背景
- 出身：
- 关键经历：

## 关系
| 对象 | 关系 | 当前状态 |
|------|------|---------|
| ... | ... | ... |

## 弧线
- 阶段：天真 → 受挫 → 觉醒 → 成熟
- 当前阶段：
- 下次转折条件：

## 声线
- 口头禅：
- 句长偏好：
- 生气时：
- 害怕时：
```

「声线」一栏是多视角长篇的关键，缺了它，人物说话会串味。

---

## 四、章节文件

路径 `chapters/chXXX.md`，编号三位补零。

```markdown
# 第X章 章节标题

（正文）

---
## 元信息
- 视角：
- 声部：
- 本章字数：
- 出场人物：
- 回收伏笔：
- 新埋伏笔：
```

元信息写在分隔线之后，方便脚本解析，也不影响阅读正文。

---

## 五、伏笔追踪器

见 [foreshadowing.md](foreshadowing.md)。

---

## 六、回收站

`recycle-bin.md` 按章归档被删段落，格式：

```markdown
## CH08 删除于 2026-10-13
> （被删的段落原文）

原因：与人物卡矛盾。
```

回收站不自动清理，由用户决定何时删除。

---

## 七、审稿记录

见 [editor-review.md](editor-review.md)。
