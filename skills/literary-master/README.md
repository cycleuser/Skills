# 文宗 Literary Master

## 状态：Beta

## 用途
基于 **559 部公有领域世界文学名著 + 292 部诺贝尔文学奖作品** 语料库深析建立的"作家级写作工艺系统"。
四层工艺（叙述声部 → 人物建构 → 故事工程 → 文体标记）× 四维索引（流派 / 时代 / 国别学派 / 作家签名）。

## 快速命令
| 命令 | 说明 |
|------|------|
| `/文宗 <风格目标> <选题>` | 以指定作家/流派/时代/学派工艺创作 |
| `/文宗 流派 <流派> <选题>` | 以文学流派工艺创作 |
| `/文宗 时代 <年代> <选题>` | 以时代文法创作 |
| `/文宗 作家 <作家名> <选题>` | 以某大师签名工艺创作 |
| `/文宗 人物 <人物>` | 构建大师级人物卡 |
| `/文宗 结构 <题材>` | 生成故事骨架/分幕大纲 |
| `/文宗 声部 <目标> <文本>` | 将文本重写为目标工艺声部 |
| `/文宗 校核 <文本> <目标>` | 依工艺规则校验风格保真度 |
| `/master <target> <topic>` | Write in an author/movement/era/school's craft (English) |

## 适用场景
- 以某位文学大师的真实工艺创作（40+ 作家签名）
- 以某一文学流派创作（20+ 流派：现实主义/魔幻现实主义/意识流/荒诞派…）
- 以某一时代文法创作（古典/中世纪/19世纪/20世纪…）
- 以某一国别学派创作（俄罗斯/法国/英国/美国/德国北欧/日本…）
- 大师级人物建构与故事工程
- 自由间接引语、声部控制、反 AI 文学写作

## 与文豪（literary-ghostwriter）的关系
- 文豪：7 位作家"精神内核"模仿 + 长篇项目管理（可复用）。
- 文宗：基于语料库的**可执行工艺系统**，四层工艺可拆解可校验，40+ 作家、20+ 流派、7 个时代、9 个国别学派。
- 建议：长篇项目管理流程用文豪，文本工艺根基用文宗。

## 依赖
- 语料库：`/Users/fred/Documents/重点文献/公有领域世界文学名著集/` 与 `/Users/fred/Documents/重点文献/诺贝尔文学奖作品集/`
- 依赖 _shared/core/safety-rules.md

## 参见
- [literary-ghostwriter](../literary-ghostwriter/README.md) — 长篇项目管理与精神内核模仿
- [humanizer](../humanizer/README.md) — AIGC 检测互补
- [brief-write](../brief-write/README.md) — 简洁口语风格互补

## 文件结构
```
skills/literary-master/
├── README.md
├── SKILL.md
└── rules/
    ├── corpus-guide.md        # 语料库索引与抽读方法
    ├── movements.md           # 流派工艺（20+）
    ├── eras.md                # 时代文法
    ├── national-schools.md    # 国别学派
    ├── voice-and-style.md     # 叙述声部与文体标记
    ├── character-building.md  # 人物建构机制
    ├── story-engineering.md   # 故事骨架目录
    ├── scene-dialogue.md      # 场景与对话技艺
    ├── author-signatures.md   # 40+ 大师签名档案
    └── anti-aigc.md           # 文学反 AIGC
```
