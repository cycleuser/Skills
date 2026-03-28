---
name: literary-ghostwriter
version: "2.0.0"
description: |
  文豪代笔技能 - 模仿七位文学大师的写作风格
  
  触发条件: 需要以特定作家风格创作文章或作品，文学创作、剧本写作、小说创作，或风格模仿练习。
  
  命令:
  - /文豪 <作家> <选题> - 中文创作
  - /literary <author> <topic> - English writing
  
  支持七位作家: 西方三位是shakespeare/莎士比亚、zweig/茨维格、calvino/卡尔维诺。中国四位是luxun/鲁迅、laoshe/老舍、jinyong/金庸、gulong/古龙。
  
  能力: 深度分析作家风格特征，中英双语创作支持，多种体裁支持，遵循用户提供的选题和剧情。
author: cycleuser
license: MIT
---

# Literary Ghostwriter 文豪代笔

模仿文学大师风格的创作技能，支持七位作家：莎士比亚、茨维格、卡尔维诺、鲁迅、老舍、金庸、古龙。

## Quick Commands

Fourteen commands cover writing in the style of seven literary masters. For Chinese commands: `/文豪 莎士比亚 <选题>` for Shakespeare style, `/文豪 茨维格 <选题>` for Zweig style, `/文豪 卡尔维诺 <选题>` for Calvino style, `/文豪 鲁迅 <选题>` for Lu Xun style, `/文豪 老舍 <选题>` for Lao She style, `/文豪 金庸 <选题>` for Jin Yong style, `/文豪 古龙 <选题>` for Gu Long style. For English commands: `/literary shakespeare <topic>`, `/literary zweig <topic>`, `/literary calvino <topic>`, `/literary luxun <topic>`, `/literary laoshe <topic>`, `/literary jinyong <topic>`, `/literary gulong <topic>`.

---

## 七位大师概览

### 西方作家

#### 威廉·莎士比亚 (William Shakespeare, 1564-1616)

莎士比亚是英国文艺复兴时期的戏剧家和诗人，代表作品包括《哈姆雷特》《罗密欧与朱丽叶》《麦克白》《李尔王》。风格要点包括诗意语言与散文交织，深刻的人性洞察，五幕戏剧结构，以及大量独白与隐喻。

#### 斯蒂芬·茨维格 (Stefan Zweig, 1881-1942)

茨维格是奥地利20世纪上半叶的作家，代表作品包括《一个陌生女人的来信》《象棋的故事》《昨日的世界》。风格要点包括细腻的心理描写，优雅流畅的长句，命运的偶然与必然，以及怀旧与末世情怀。

#### 伊塔洛·卡尔维诺 (Italo Calvino, 1923-1985)

卡尔维诺是意大利20世纪下半叶的作家，代表作品包括《看不见的城市》《如果在冬夜，一个旅人》《树上的男爵》。风格要点包括轻逸与精确，奇幻与现实交织，结构实验，以及哲学寓言性。

### 中国作家

#### 鲁迅 (1881-1936)

鲁迅原名周树人，浙江绍兴人，代表作品包括《狂人日记》《阿Q正传》《祝福》《野草》。风格要点包括简洁有力的短句，冷峻的批判精神，白描手法，以及深刻的社会关怀。

#### 老舍 (1899-1966)

老舍原名舒庆春，北京人，代表作品包括《骆驼祥子》《四世同堂》《茶馆》。风格要点包括京味儿语言，幽默讽刺，口语化叙事，以及关注底层市民。

#### 金庸 (1924-2018)

金庸原名查良镛，浙江海宁人，代表作品包括《射雕英雄传》《天龙八部》《笑傲江湖》《鹿鼎记》。风格要点包括文白相间，章回体结构，家国情怀，以及人物成长弧线。

#### 古龙 (1938-1985)

古龙原名熊耀华，江西南昌人，代表作品包括《多情剑客无情剑》《楚留香传奇》《陆小凤传奇》。风格要点包括极简主义语言，诗化意境，短句为主，以及悬念反转。

---

## 风格速查表

七位作家的风格对比：莎士比亚以诗意和隐喻著称，采用五幕戏剧结构，核心主题围绕命运、爱情和权力。茨维格以优雅细腻见长，使用框架叙事，主题聚焦命运偶然与怀旧。卡尔维诺追求精确轻盈，采用实验结构，探讨存在与可能性。鲁迅风格简洁犀利，以短篇为主创作，深刻批判国民性。老舍语言富有京味儿，带有幽默讽刺，采用生活流结构，关注底层命运与市民生活。金庸文白相间，使用章回体结构，核心主题是家国与侠义。古龙追求极简诗意，采用蒙太奇手法，主题围绕孤独与友情。

---

## 创作流程

```
1. 确认作家风格
   ↓
2. 理解选题要求
   ↓
3. 应用风格特征
   ├── 语言风格
   ├── 结构模式
   ├── 人物塑造
   └── 主题表达
   ↓
4. 完成创作
   ↓
5. 风格审校
```

---

## Rules

西方作家:
- [rules/shakespeare-style.md](rules/shakespeare-style.md) - 莎士比亚风格详解
- [rules/zweig-style.md](rules/zweig-style.md) - 茨维格风格详解
- [rules/calvino-style.md](rules/calvino-style.md) - 卡尔维诺风格详解

中国作家:
- [rules/luxun-style.md](rules/luxun-style.md) - 鲁迅风格详解
- [rules/laoshe-style.md](rules/laoshe-style.md) - 老舍风格详解
- [rules/jinyong-style.md](rules/jinyong-style.md) - 金庸风格详解
- [rules/gulong-style.md](rules/gulong-style.md) - 古龙风格详解

通用:
- [rules/vocabulary.md](rules/vocabulary.md) - 风格词汇库