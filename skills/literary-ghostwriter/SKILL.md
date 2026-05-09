---
name: literary-ghostwriter
version: "2.1.0"
description: |
  Literary ghostwriter skill that mimics the writing style of seven literary masters for creative writing.

  Triggers when: Writing in a specific author's style, creative writing, script writing, novel writing, or style imitation exercises.

  Commands:
  - /文豪 <作家> <选题> - Write in Chinese with a master's style
  - /literary <author> <topic> - Write in English with a master's style

  Capabilities: Deep analysis of author's spiritual core, providing concrete methods for authentic imitation, bilingual Chinese-English creation, multiple genre support, following user-provided topics and plot
author: cycleuser
license: MIT
---

## Safety Rules

**Critical**: Read and follow [global-rules/bash-safety.md](file:///Users/fred/.config/opencode/skills/global-rules/rules/bash-safety.md) for all bash/command execution.

Core rules:
1. **Always set explicit `timeout` on bash calls** — 30s for tests, 60s for installs, never default
2. **Never run unscoped full test suites** — use `-k` or file paths to limit scope
3. **Never use `rm -rf` without variable guards**, `curl|bash`, `sudo`, or `kill -9`
4. **Infinite loops must have hard timeout + budget limits** — no unbounded while(True)
5. **Redirect stdin** with `< /dev/null` for non-interactive commands

A bash timeout that triggers SIGKILL corrupts the terminal FD, crashes opencode's TUI, and forces a GUI restart.

# Literary Ghostwriter 文豪代笔

模仿文学大师风格的创作技能，支持七位作家：莎士比亚、茨维格、卡尔维诺、鲁迅、老舍、金庸、古龙。

## Quick Commands

| Command | Description |
|---------|-------------|
| `/文豪 <作家> <选题>` | Write in Chinese with a master's style (莎士比亚/茨维格/卡尔维诺/鲁迅/老舍/金庸/古龙) |
| `/literary <author> <topic>` | Write in English with a master's style (shakespeare/zweig/calvino/luxun/laoshe/jinyong/gulong) |

---

## 核心原则：神似而非形似

### 形似 vs 神似

形似是表面模仿：使用作家的标志性词汇、句式、风格特征。

神似是内核把握：理解作家的精神世界，像他一样思考，用他的方式追问人生。

```
【形似示例】鲁迅风格（形似）：
"我翻开历史一查，发现这历史里写的都是欺骗。"
→ 只是模仿句式，没有鲁迅的精神内核

【神似示例】鲁迅风格（神似）：
"那本书躺在旧书摊的角落，封面已经泛黄。
他翻了几页，看到的是一个又一个熟悉的名字——
曾经意气风发的改革者，如今都在体制里找到了安稳的位置。
他没有说话，只是把书放回去，走了。

这沉默里有什么？失望？理解？还是习惯了？

他说不上来。他只知道，那些曾经批判的人，
后来都成了被批判的对象。批判者和被批判者，原来只隔着一层窗户纸。"

→ 不只是句式，是对"批判者变成被批判者"这一现象的追问
→ 这是鲁迅式的社会观察和精神拷问
```

### 神似的三层境界

```
第一层：语言特征
- 词汇、句式、节奏
- 这是表层的模仿，容易做到

第二层：精神内核
- 作家的核心价值观
- 他追问什么问题？他如何回答？
- 这是中层的把握，需要深入理解

第三层：创作机制
- 他如何观察世界？
- 他如何处理素材？
- 他如何构建意义？
- 这是深层的掌握，需要反复练习

【核心原则】
真正神似的作品，读者感受到的是"这很像他写的"，
而不是"这是在模仿他的风格"。
```

---

## 七位大师的精神内核

### 西方作家

#### 威廉·莎士比亚 (William Shakespeare, 1564-1616)

**精神内核**：对人性的深刻洞察，追问"人是什么？"

**核心母题**：人是矛盾的——伟大与渺小、理性与疯狂、爱与恨并存。

**神似要点**：不评判只展示矛盾；用独白追问存在问题；诗意语言触及真相而非装饰。

**创作机制**：确定核心矛盾 → 通过人物选择展示 → 让命运体现选择的代价 → 结尾不留答案。

#### 斯蒂芬·茨维格 (Stefan Zweig, 1881-1942)

**精神内核**：对人类情感的极致探索，追问"在命运面前，人能做什么？"

**核心母题**：命运的偶然性与人的尊严。

**神似要点**：心理描写如显微镜剥开表层；用克制表达最强烈的情感；长句累积情感最后释放。

#### 伊塔洛·卡尔维诺 (Italo Calvino, 1923-1985)

**精神内核**：对存在的轻盈追问，"如何用轻逸面对沉重？"

**核心母题**：存在的可能性与不可能性。

**神似要点**：精确描述奇幻意象；数学逻辑与想象结合；结构实验打破线性。

### 中国作家

#### 鲁迅 (1881-1936)

**精神内核**：对国民性的诊断，追问"中国人是什么？病在哪里？"

**核心母题**：中国人的精神困境——麻木、自欺、看客心态。

**神似要点**：批判来自悲悯不是优越；白描不加形容词和解释；反语让对方的话杀死对方；冷的表面下是深切的热。

#### 老舍 (1899-1966)

**精神内核**：对小人物的悲悯，追问"底层人如何活着？"

**核心母题**：小人物的挣扎与无奈。

**神似要点**：京味儿语言是身份不是装饰；幽默来自对生活的观察；口语化叙事像聊天；议论穿插叙事。

#### 金庸 (1924-2018)

**精神内核**：用江湖写人生，追问"人如何选择？选择的代价是什么？"

**核心母题**：侠义、命运、选择。

**神似要点**：武功是性格的延伸不是技能；家国情怀通过选择体现；文白相间创造距离感；四字词语服务于意境。

#### 古龙 (1938-1985)

**精神内核**：对孤独的书写，追问"人活着为了什么？"

**核心母题**：孤独、友情、选择。

**神似要点**：极简不是目的是留白；短句控制节奏和情绪；不写武功过程只写结果；孤独中寻找温暖。

---

## 创作流程

### 第一步：理解选题

在开始创作前，必须深入理解：选题的核心情感是什么？哪位作家的精神内核最契合？用什么体裁最合适？

### 第二步：深入作家

不只是阅读规则文件，而是：阅读作家的代表作感受他的节奏；理解他的精神内核——他追问什么？他如何回答？分析他的创作机制——他如何处理素材？

### 第三步：神似创作

核心原则：不是使用作家的词汇，是像他一样思考；不是模仿句式，是追问同类问题；不是堆砌意象，是让意象服务于主题。

### 第四步：自我审视

完成初稿后：这段文字，读者能感受到"像某位作家"吗？是形似还是神似？精神内核是否准确？创作机制是否运用得当？

---

## Rules

西方作家:
- [rules/shakespeare-style.md](rules/shakespeare-style.md) - 莎士比亚风格详解（含神似创作方法）
- [rules/zweig-style.md](rules/zweig-style.md) - 茨维格风格详解
- [rules/calvino-style.md](rules/calvino-style.md) - 卡尔维诺风格详解

中国作家:
- [rules/luxun-style.md](rules/luxun-style.md) - 鲁迅风格详解（含神似创作方法）
- [rules/laoshe-style.md](rules/laoshe-style.md) - 老舍风格详解
- [rules/jinyong-style.md](rules/jinyong-style.md) - 金庸风格详解（含神似创作方法）
- [rules/gulong-style.md](rules/gulong-style.md) - 古龙风格详解（含神似创作方法）

通用:
- [rules/vocabulary.md](rules/vocabulary.md) - 风格词汇库