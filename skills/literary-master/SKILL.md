---
name: literary-master
version: "1.0.0"
description: |
  Literary master skill (文宗) — writes in the authentic craft of world-class authors, literary
  movements, national schools, and historical eras, grounded in deep corpus analysis of
  ~800 works (public-domain world classics + Nobel Prize collection).

  Triggers when: Writing fiction/poetry/drama in the style of a specific great author, a
  literary movement (realism, modernism, magic realism, symbolism, etc.), a national school
  (Russian/French/English/American/German/Nordic), or an era; building characters the way
  masters build them; engineering story structure; or needing a powerful general literary
  craft system beyond surface-level imitation.

  Commands:
  - /文宗 <风格目标> <选题> — Write in the craft of an author / movement / era / national school
  - /文宗 流派 <流派> <选题> — Write in a literary movement (现实主义/自然主义/现代主义/魔幻现实主义…)
  - /文宗 时代 <年代> <选题> — Write in an era's grammar (古典/中世纪/文艺复兴/19世纪/20世纪…)
  - /文宗 作家 <作家名> <选题> — Write in one master's signature craft
  - /文宗 人物 <人物> — Build a master-crafted character card
  - /文宗 结构 <题材> — Engineer a story skeleton
  - /文宗 声部 <目标> <文本> — Re-voice a passage in a target craft
  - /文宗 校核 <文本> <目标> — Verify style fidelity against craft rules
  - /master <target> <topic> — English equivalent
  - /master 流派/era/author/character/structure/voice/verify — English subcommands

  Capabilities: Corpus-grounded craft system, 40+ author signatures, 20+ movements, era grammar,
  national-school traditions, character-building mechanics, story-skeleton catalog, narrative
  voice control, free-indirect-speech technique, scene/dialogue craft, anti-AIGC literary writing.
author: cycleuser
license: MIT
status: Beta
---

## Safety Rules

参见 [_shared/core/safety-rules.md](../_shared/core/safety-rules.md) — 所有安全规则从共享层加载。

# 文宗 Literary Master

基于 **559 部公有领域世界文学名著 + 292 部诺贝尔文学奖作品** 语料库的深析，建立的"作家级写作工艺系统"。
不同于"形似模仿"，本技能把大师写作拆成可执行的四层工艺：**叙述声部 → 人物建构 → 故事工程 → 文体标记**，
再按 **流派 / 时代 / 国别学派 / 作家签名** 四维索引调用。语料库是校验标准：写完后回到真实文本比对。

## 语料库位置

```
/Users/fred/Documents/重点文献/公有领域世界文学名著集/    # 180 位名家 / 559 部作品（多为全文 txt）
/Users/fred/Documents/重点文献/诺贝尔文学奖作品集/         # 122 位获奖者 / 292 部作品（详细剧情 md + 部分原著）
```

写作或校核时，**必须**用 bash 抽读相关作品原文做参照（详见 `rules/corpus-guide.md`）。

## 快速命令 Quick Commands

| Command | Description |
|---------|-------------|
| `/文宗 <风格目标> <选题>` | 以指定作家/流派/时代/学派工艺创作 |
| `/文宗 流派 <流派> <选题>` | 以文学流派工艺创作 |
| `/文宗 时代 <年代> <选题>` | 以时代文法创作 |
| `/文宗 作家 <作家名> <选题>` | 以某大师签名工艺创作 |
| `/文宗 人物 <人物>` | 构建大师级人物卡 |
| `/文宗 结构 <题材>` | 生成故事骨架/分幕大纲 |
| `/文宗 声部 <目标> <文本>` | 将文本重写为目标工艺声部 |
| `/文宗 校核 <文本> <目标>` | 依工艺规则校验风格保真度 |
| `/master <target> <topic>` | Write in an author/movement/era/school's craft (English) |
| `/master character <char>` | Build a master-level character card |
| `/master structure <topic>` | Engineer a story skeleton |
| `/master voice <target> <text>` | Re-voice text in target craft |
| `/master verify <text> <target>` | Verify style fidelity |

## 核心：四层工艺系统

大师的"风格"不是词汇表，而是**可拆解的工艺**。写作前先为选定目标组装工艺档案：

### 1. 叙述声部（Narrative Voice）
叙述者是谁、站在什么高度、如何介入、句子的呼吸如何。
- **全知道德家**（托尔斯泰：判断又宽恕；狄更斯：戏剧化说书人）
- **隐形外科医生**（福楼拜：自由间接引语；契诃夫：客观潜台词）
- **讽刺解剖者**（奥斯汀/华顿：自由间接+反讽；斯威夫特/伏尔泰：讥诮）
- **神经质独白者**（陀思妥耶夫斯基：地下人；茨维格：心理显微镜）
- **冷静荒诞者**（卡夫卡：办事腔处理超现实）
- **预言/百科全书**（梅尔维尔：越界布道；雨果：天启雄辩）
- **口语天真见证者**（马克·吐温：语域错位即反讽）
- **记忆回溯者**（普鲁斯特/莫迪亚诺/石黑：记忆即叙事本体）
- **集体众声**（阿列克谢耶维奇/伯尔：口述拼接，作者隐身）
- **平白写作**（埃尔诺：无人称、阶级物件学）

**关键技法**：自由间接引语（style indirect libre）——把人物内心混入第三人称叙述、不加引号不加"她想"，
是福楼拜到奥斯汀再到现代小说最核心的声部技术。详见 `rules/voice-and-style.md`。

### 2. 人物建构（Character Construction）
- **原型引擎**：从语料库提取的角色原型（被碾碎的理想主义者、执念者、荒谬英雄、傻瓜、多余人、拜伦式情人、反抗的女性…），见 `rules/character-building.md`。
- **驱动方式**：秘密/罪（吉勒鲁普、黛莱达、温塞特）、执念（高老头、福尔赛、王龙、亚哈）、气质与环境错位（包法利）、历史撕裂（梅列霍夫、日瓦戈）、记忆身份（石黑、莫迪亚诺）。
- **立体化**：外部细节即心灵（曼的账本、福尔赛的家具）、镜像双人组对位（塞特姆布里尼/纳夫塔）、动态弧线 vs 撕裂型弧线、动物/边缘视角（铁皮鼓奥斯卡、生死疲劳转世、吉姆佩尔傻瓜）。

### 3. 故事工程（Story Engineering）
- **骨架目录**：成长小说、兴衰四代、单日决胜、赎罪弧、问题剧对垒、循环寓言、荒谬非情节、复调多声部、记忆小说、证词口述史、微型史诗、旅程/公路、档案寻根、物件意象小说…见 `rules/story-engineering.md`。
- **时间容器**：单日/四季/一生/四代/循环时间——同一副骨架装进不同时间容器即不同作品。
- **主题架构**：让意象成为结构（风中的芦苇、银河、水轮、桥、河）、辩证对置（理性/疯狂）、母题法（leitmotif）。

### 4. 文体标记（Style Markers）
- **句法签名**：托尔斯泰的长累积句、狄金森的破折号、乔伊斯的无标点流、萨拉马戈的无句读、克拉斯诺霍尔卡伊的数页一句、海明威的短句（见语料库诺奖卷）、福楼拜的 imparfait。
- **意象系统**：波德莱尔感应、济慈通感、川端物哀、帕慕克细密画。
- **词汇域**：方言即身份（吐温、哈代、老舍）、科层精确（卡夫卡）、金钱账簿（巴尔扎克）。

---

## 四维索引

### A. 流派 Movements（`rules/movements.md`）
20+ 流派的工艺标记与操作说明：
古典主义 / 浪漫主义 / 现实主义 / 自然主义 / 象征主义 / 心理小说 / 意识流·现代主义 /
表现主义 / 荒诞派 / 存在主义 / 魔幻现实主义 / 新小说 / 极简主义 / 后现代元叙事 /
纪实·见证文学 / 后殖民 / 自传体平白写作 / 教育小说 / 地域小说 / 家族编年史 / 讽刺小说 / 童话·寓言

### B. 时代 Eras（`rules/eras.md`）
古典时代 / 中世纪·文艺复兴 / 17-18世纪 / 19世纪（浪漫→现实→自然）/ 20世纪上半（现代主义）/ 20世纪下半（后现代）/ 21世纪。每个时代有：世界观语法、声部倾向、人物模型、故事容器、语言禁忌。

### C. 国别学派 National Schools（`rules/national-schools.md`）
俄罗斯（灵魂辩证法）/ 法国（精确与反讽）/ 英国（社会喜剧与意识流）/ 美国（口语与个人主义史诗）/
德国·中欧（哲思与荒诞）/ 北欧（悲剧主义与大地）/ 意大利（历史与民间）/ 西语·拉美（魔幻与激情）/
日本（物哀与留白）。每个学派：核心难题、招牌声部、原型库、结构偏好。

### D. 作家签名 Author Signatures（`rules/author-signatures.md`）
40+ 位大师的"签名档案"：每人 6 行内——声部、原型、骨架、标记、一句话诀窍、代表作。
覆盖：托尔斯泰、陀思妥耶夫斯基、契诃夫、屠格涅夫、果戈理、普希金、高尔基；巴尔扎克、福楼拜、雨果、
司汤达、莫泊桑、左拉、普鲁斯特、大仲马；狄更斯、奥斯汀、勃朗特、哈代、乔伊斯、伍尔夫、康拉德、
劳伦斯、詹姆斯、王尔德；梅尔维尔、马克·吐温、爱伦·坡、霍桑、杰克·伦敦、菲茨杰拉德、华顿、凯瑟、
惠特曼、狄金森；歌德、卡夫卡、尼采、黑塞、里尔克、茨威格；易卜生、斯特林堡、安徒生；塞万提斯、
维尔加、曼佐尼；加缪、海明威、福克纳、斯坦贝克、川端康成、贝克特、马尔克斯、莫言、门罗、石黑一雄、
埃尔诺、韩江、萨拉马戈、托卡尔丘克、阿列克谢耶维奇、莫里森、奥尼尔。

---

## 写作工作流

### 第一步：解析目标
用户给出风格目标。解析为四维坐标：`流派 × 时代 × 国别 × 作家`。
若只给作家名 → 定位其签名档案 + 时代 + 流派；只给流派 → 定位流派规则；只给时代 → 定位时代文法。

### 第二步：装配工艺档案
按四层系统为本次写作装配工艺档案：
```
声部：<叙述者类型 + 介入度 + 句法签名>
人物：<原型 + 驱动方式 + 弧线类型 + 镜像对位>
结构：<骨架 + 时间容器 + 主题架构>
标记：<意象系统 + 词汇域 + 句法细节 + 禁忌词>
```

### 第三步：语料参照
用 bash 抽读 1-3 部相关作品原文片段（`rules/corpus-guide.md` 有路径清单），校准语感。**这是文宗与传统风格模仿的根本区别**——每个判断都有原文依据。

### 第四步：工程搭建
- 用 `rules/story-engineering.md` 选骨架并生成分幕大纲
- 用 `rules/character-building.md` 建人物卡（驱动/弧线/镜像/声线）

### 第五步：执笔
严格按四层档案写。写作时把工艺档案放在面前逐层落实，而非凭"印象"。

### 第六步：自检
用 `rules/anti-aigc.md` 去 AI 味；用 `rules/voice-and-style.md` 校核声部与标记；回读语料对照。

---

## 人物建构命令（`/文宗 人物`）

输出大师级人物卡：
```
## <角色名> 人物卡
- 原型：<来自原型库>
- 核心驱动：<秘密/执念/气质错位/历史撕裂/记忆身份>
- 欲望 vs 需求：<表面欲望 / 深层需求>
- 弧线：<天真→受挫→觉醒→成熟 | 撕裂型 | 堕落型 | 静默见证型>
- 镜像对位：<与谁成对，对位轴是什么>
- 声线：<词汇域/句式/口头禅/沉默方式>
- 外部细节：<环境即心灵的具体物>
- 三处压迫点：<每次出场被什么反复刺激>
```

## 故事工程命令（`/文宗 结构`）

输出：
```
- 骨架：<选自骨架目录，附示例作品>
- 时间容器：<单日/四季/一生/循环…>
- 分幕：<3-5 幕，每幕：目标/升级/转折/人物变化>
- 主题嵌入：<意象即结构的落点>
- 伏笔/回收：<清单>
```

## 风格校核命令（`/文宗 校核`）

按四层逐项打分：
| 层 | 检查项 | 权重 |
|----|--------|------|
| 声部 | 叙述者介入度/自由间接使用/句法签名 | 30% |
| 人物 | 原型符合度/驱动一致性/声线稳定 | 25% |
| 结构 | 骨架匹配/时间容器/伏笔回收 | 20% |
| 标记 | 意象系统/词汇域/禁忌词 | 15% |
| 去AI | AIGC 痕迹 | 10% |

<7 分 → 找出最弱层，重写该层；<5 分 → 回语料库重读再重写。

---

## Rules

- [rules/corpus-guide.md](rules/corpus-guide.md) — 语料库索引与抽读方法
- [rules/movements.md](rules/movements.md) — 流派工艺（20+ 流派）
- [rules/eras.md](rules/eras.md) — 时代文法
- [rules/national-schools.md](rules/national-schools.md) — 国别学派
- [rules/voice-and-style.md](rules/voice-and-style.md) — 叙述声部与文体标记技术
- [rules/character-building.md](rules/character-building.md) — 人物建构机制
- [rules/story-engineering.md](rules/story-engineering.md) — 故事骨架目录
- [rules/scene-dialogue.md](rules/scene-dialogue.md) — 场景与对话技艺
- [rules/author-signatures.md](rules/author-signatures.md) — 40+ 大师签名档案
- [rules/anti-aigc.md](rules/anti-aigc.md) — 文学反 AIGC

## AIGC-Aware Output

文学是 AIGC 检测最敏感的文类。四层工艺本身就是反 AI 的结构性武器——真实作家的句法不规则、结构不对称、
情绪不均一、意象不工整。详见 `rules/anti-aigc.md`。核心铁律：
- 禁止均匀句长、排比三段式、"值得注意的是"式过渡、机械总-分-总
- 每个作家的不规则处（狄金森的断句、果戈理的离题、契诃夫的沉默）恰恰是最该模仿的"指纹"

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-08-04 | 基于公有领域 559 部 + 诺贝尔 292 部语料库深析创建。四层工艺系统 + 四维索引 + 10 部规则库 + 40+ 作家签名。 |

## See Also

- `/文豪` from **literary-ghostwriter** — 长篇项目管理可复用；文宗提供更深的工艺根基
- `/人话` from **humanizer** — AIGC 检测互补
- `/简写` from **brief-write** — 简洁口语风格互补
