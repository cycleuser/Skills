#!/usr/bin/env python3
"""
humanize_lint.py — 人话技能的「AI 味」体检器（中英双语，纯标准库，只读）

它不修改文本，只做三件事：
  1. 量化：句长/段长波动、标点密度、版面痕迹密度、词汇多样性、名词化比例
  2. 命中：中英两套 AI 特征词表与句式模板，逐条给出位置与建议
  3. 打分：把上面两类合成 0-100 的「AI 味」分数与四维分项，供改写前后对比

用法:
  python3 humanize_lint.py check <文件|->  [--lang auto|zh|en] [--json]
                                      [--max-score 45] [--top 5] [--no-color]
  python3 humanize_lint.py score <文件|->  [--lang auto|zh|en] [--json]
  python3 humanize_lint.py rules             # 打印启用的检测项清单

退出码:
  0  分数 <= --max-score
  1  分数 >  --max-score（可作 CI / 改写循环的收敛判据）
  2  调用错误

设计约束（重要）:
  - 这是启发式体检，不是 AIGC 检测器。分数低不等于"人类写的"，分数高也不等于"AI 写的"。
  - 单个特征从不构成证据（见 rules/metrics.md 的误杀边界），报告里每项都标了置信度。
  - 阈值是经验值，来源见 references/ai-text-features-research.md；可按文体用 --profile 调整。
"""
from __future__ import annotations

import argparse
import itertools
import json
import math
import re
import sys
import unicodedata
from collections.abc import Iterable
from dataclasses import dataclass, field

# --------------------------------------------------------------------------
# 基础工具
# --------------------------------------------------------------------------

CJK_RE = re.compile(r"[\u4e00-\u9fff]")
LATIN_WORD_RE = re.compile(r"[A-Za-z][A-Za-z'’\-]*")
SENT_END_ZH = "。！？!?…"
SENT_END_EN = ".!?"


def is_cjk(ch: str) -> bool:
    return bool(CJK_RE.match(ch))


def detect_lang(text: str) -> str:
    cjk = len(CJK_RE.findall(text))
    latin = len(LATIN_WORD_RE.findall(text))
    if cjk == 0 and latin == 0:
        return "zh"
    return "zh" if cjk >= latin * 0.6 else "en"


EN_ABBREV = {"mr", "mrs", "ms", "dr", "prof", "e.g", "i.e", "vs", "etc", "fig", "no", "st", "jr", "sr", "inc", "ltd"}


def split_sentences(text: str, lang: str) -> list[str]:
    """切句。中文按句末标点；英文按标点+空格，并排除常见缩写。"""
    if lang == "zh":
        parts = re.split(r"(?<=[。！？!?…])|\n+", text)
        return [s.strip() for s in parts if s and s.strip()]

    parts = re.split(r"(?<=[.!?])\s+|\n+", text)
    out: list[str] = []
    buf = ""
    for s in parts:
        if not s:
            continue
        buf = (buf + " " + s).strip() if buf else s
        tail = re.sub(r"[^\w.]", "", buf.split()[-1]) if buf.split() else ""
        stem = tail.rstrip(".").lower()
        if tail.endswith(".") and (stem in EN_ABBREV or (len(stem) == 1 and stem.isalpha())):
            continue
        out.append(buf)
        buf = ""
    if buf.strip():
        out.append(buf.strip())
    return [s for s in out if s.strip()]


def paragraphs(text: str) -> list[str]:
    parts = re.split(r"\n\s*\n", text.strip())
    return [p.strip() for p in parts if p.strip()]


def length_of(s: str, lang: str) -> int:
    return len(CJK_RE.findall(s)) if lang == "zh" else len(LATIN_WORD_RE.findall(s))


def mean(xs: Iterable[float]) -> float:
    xs = list(xs)
    return sum(xs) / len(xs) if xs else 0.0


def stdev(xs: Iterable[float]) -> float:
    xs = list(xs)
    if len(xs) < 2:
        return 0.0
    m = mean(xs)
    return math.sqrt(sum((x - m) ** 2 for x in xs) / (len(xs) - 1))


def cv(xs: Iterable[float]) -> float:
    xs = list(xs)
    m = mean(xs)
    return stdev(xs) / m if m else 0.0


def per_k(x: float, total: float, k: float) -> float:
    return x / total * k if total else 0.0


def ramp_more_worse(value: float, low: float, high: float) -> float:
    """值越大越糟：<=low 得 0，>=high 得 100。"""
    if high <= low:
        return 0.0
    if value <= low:
        return 0.0
    if value >= high:
        return 100.0
    return (value - low) / (high - low) * 100.0


def ramp_more_better(value: float, low: float, high: float) -> float:
    """值越大越好（用于句长/段长波动）：>=high 得 0，<=low 得 100。"""
    if high <= low:
        return 0.0
    if value >= high:
        return 0.0
    if value <= low:
        return 100.0
    return (high - value) / (high - low) * 100.0


# --------------------------------------------------------------------------
# 词表与句式模板
# --------------------------------------------------------------------------

# ---- 中文 ----

ZH_HIGH = [
    "总的来看", "需要指出的是",
    "具有重要意义", "发挥重要作用", "起到了重要作用", "产生深远影响",
    "具有里程碑意义", "奠定了坚实基础", "提供了有力支撑", "标志着",
    "赋能", "闭环", "底层逻辑", "组合拳", "颗粒度", "范式转变",
    "全方位", "多维度", "深层次", "进一步", "不断地", "更好地", "有效地",
    "助力", "护航", "筑牢", "铸就", "谱写了",
]

ZH_MID = [
    "此外", "同时", "然而", "因此", "另外", "总之", "由此可见",
    "一方面", "另一方面", "首先", "其次", "最后", "再者",
    "从某种意义上说", "在很大程度上", "在一定程度上", "某种程度上",
    "一般来说", "通常情况下", "毋庸置疑", "不难看出", "这意味着",
    "这表明", "这说明", "可以说是", "在此背景下", "随着……的发展",
]

ZH_ORAL_DEBRIS = [
    "说白了", "干货", "保姆级", "手把手", "划重点", "避坑", "踩坑",
    "一口气", "一次说清", "捋顺", "掰正", "定死", "有几个坑", "听我一句",
    "咱就是说", "家人们",
]

ZH_FAKE_CANDOR = ["说实话", "老实说", "坦白讲", "说真的", "不夸张地说", "讲真"]

ZH_NOMINAL_VERBS = [
    "进行", "开展", "实施", "推进", "加以", "予以",
    "加强", "提升", "优化", "完善", "构建", "打造", "实现", "促进", "推动",
]

# 常见四字格（够用来测密度，不求全）
ZH_IDIOMS = [
    "与时俱进", "因地制宜", "统筹兼顾", "多措并举", "标本兼治", "精准施策",
    "提质增效", "守正创新", "融会贯通", "相辅相成", "相得益彰", "一以贯之",
    "持之以恒", "久久为功", "行稳致远", "固本培元", "系统集成", "协同联动",
    "深耕细作", "夯基垒台", "立柱架梁", "靶向发力", "同频共振", "双向奔赴",
    "焕然一新", "生机勃勃", "井然有序", "错综复杂", "不可或缺", "举足轻重",
    "层出不穷", "日新月异", "潜移默化", "水到渠成", "有的放矢", "行之有效",
]

ZH_ANTHROPO = [
    "钉在", "钉死", "焊死", "塞进", "塞下", "喂给", "投喂", "吃掉", "吞下",
    "吐出来", "扛住", "硬扛", "榨干", "压榨", "吃满", "打满", "拉满", "跑满",
    "腾出来", "撑起", "支棱", "安家", "住进", "扎根", "搬运",
]

# 正则（中文）
ZH_PATTERNS = [
    ("Z01", "空话拔高", r"(具有|有着)[^，。\n]{0,12}(重要|深远|重大)[^，。\n]{0,8}(意义|影响|价值)",
     3, "高", "直接写发生了什么、改变了谁；意义留给读者判断"),
    ("Z02", "机械三段论", r"首先[，,][\s\S]{0,400}?其次[，,][\s\S]{0,400}?最后[，,]",
     3, "高", "删掉序数词，用内容本身的因果或时间顺序衔接"),
    ("Z03", "公式化收尾", r"(综上所述|总而言之|总的来说)[，,]",
     3, "高", "收尾说具体结论或下一步动作，不做总结陈词"),
    ("Z04", "对称并列", r"一方面[，,][\s\S]{0,200}?另一方面[，,]",
     2, "中", "改成主次分明的两句话，删掉对称框架"),
    ("Z05", "否定平行", r"不是[^。！？\n]{1,30}[，,]\s*(?:而|反)?是|不仅[^。！？\n]{1,24}[，,]\s*(?:更|还|也)|与其说[^。！？\n]{1,20}不如说",
     2, "高", "直接给结论；真需要纠正误解时保留一处"),
    ("Z06", "排比三项", r"[\u4e00-\u9fffA-Za-z0-9]{2,14}、[\u4e00-\u9fffA-Za-z0-9]{2,14}、[\u4e00-\u9fffA-Za-z0-9]{2,14}",
     2, "中", "三项并列改成两项或直接举例，打破三拍子"),
    ("Z09", "性化度后缀", r"[\u4e00-\u9fff]{1,4}性(?=[，。、；：的])",
     1, "低", "改回动词或具体名词：可用性→能用的程度"),
    ("Z10", "套话插入语", r"(值得注意的是|需要指出的是|不难看出|众所周知|毋庸置疑|值得一提的是)[，,]",
     2, "中", "删掉插入语，直接说事"),
    ("Z11", "泛人称代词", r"(我们|大家|你我|咱们)(来看|来看看|会发现|都知道|可能觉得)",
     2, "中", "说明文里省主语，或换成具体施事"),
    ("Z12", "寒暄式开头", r"^(最近|近来|常常?有人|经常有人|很多人)(问|说起|提到)|在当今[^。\n]{0,12}时代",
     3, "高", "删掉铺垫，第一句直接给事实、定义或现象"),
    ("Z13", "无据推演", r"(这意味着|这说明|这表明|由此可见|不难看出|可见)[，,]",
     2, "中", "补出推演链条，或删掉，让事实自己说话"),
    ("Z14", "劝诫式收尾", r"(我们应当|我们应该|需要各方|需要每个人|值得每个人|唯有……才能)",
     2, "中", "删掉号召；要提建议就写清谁在什么时候做什么"),
    ("Z16", "假坦白钩子", r"(说实话|老实说|坦白讲|说真的|不夸张地说)[，,]",
     2, "中", "要么直接说，要么删掉钩子"),
    ("Z19", "中英混杂", r"[\u4e00-\u9fff]{2,}(description|reference|frontmatter|fork|pipeline|workflow|prompt)",
     2, "中", "可译术语中文化，首次出现写「中文（English）」"),
    ("Z21", "模糊归属", r"(业界|业内|专家|学者|研究者|相关研究|有关部门)(普遍)?(认为|指出|表示|发现)[，,]?",
     3, "高", "点名来源；找不到来源就删"),
    ("Z22", "面面俱到", r"(既有[^。\n]{0,10}也有|既[^。\n]{0,8}又[^。\n]{0,8})|辩证(地)?看待|因人而异|见仁见智",
     2, "中", "给出取舍和条件，别用「两边都对」收场"),
    ("Z26", "连接词开场", r"^(此外|同时|然而|因此|另外|总之|再者|其次|最后)[，,]",
     1, "低", "删掉连接词，靠语序表达关系"),
]

# ---- 英文 ----

EN_AI_WORDS = {
    # 高置信度（多份研究共同指认）
    "delve": 3, "tapestry": 3, "intricate": 3, "intricacies": 3, "underscore": 3,
    "underscores": 3, "underscoring": 3, "pivotal": 3, "testament": 3,
    "camaraderie": 3, "palpable": 3, "meticulous": 3, "meticulously": 3,
    # 中置信度
    "leverage": 2, "seamless": 2, "seamlessly": 2, "vibrant": 2, "robust": 2,
    "realm": 2, "showcase": 2, "showcasing": 2, "foster": 2, "fostering": 2,
    "garner": 2, "garnered": 2, "multifaceted": 2, "holistic": 2, "nuanced": 2,
    "myriad": 2, "plethora": 2, "crucial": 2, "enduring": 2, "interplay": 2,
    "amidst": 2, "solace": 2, "fleeting": 2, "unravel": 2, "cacophony": 2,
    # 低置信度（本身正常，密集出现才算）
    "utilize": 1, "utilizing": 1, "facilitate": 1, "comprehensive": 2,
    "notably": 1, "additionally": 1, "moreover": 1, "furthermore": 1,
    "ensure": 1, "enhance": 1, "enhancing": 1, "align": 1, "landscape": 1,
    "insights": 1, "profound": 1, "vital": 1, "key": 0,
}

EN_PATTERNS = [
    ("E01", "意义拔高", r"\b(stands? as|serves? as|is a testament to|a testament to|plays? a (?:crucial|pivotal|vital|key|significant) role|underscore[sd]? the (?:importance|significance)|reflects? (?:a )?broader|marks? a (?:pivotal|turning) (?:moment|point)|indelible mark|setting the stage for)\b",
     3, "high", "replace with what actually happened; drop the significance claim"),
    ("E02", "回避系动词", r"\b(serves? as|functions? as|operates? as|stands? as|represents?|boasts?|features?|maintains?)\b(?!\s+(?:that|to)\b)",
     2, "medium", "use is/are/has; 'serves as a hub' -> 'is a hub'"),
    ("E04", "-ing 尾巴分析", r",\s+\w+ing\b[^.;]{0,80}[.;]",
     2, "high", "split into a real clause with a subject, or delete"),
    ("E05", "否定平行", r"\bnot (?:just|only|merely|simply)\b[^.]{0,80}\bbut\b|\bit'?s not\b[^.]{0,60}\bit'?s\b|\brather than\b",
     2, "high", "state the claim; keep at most one contrast per page"),
    ("E06", "三项并列", r"\b\w+(?:, \w+){2},? (?:and|or) \w+|\b\w+, \w+, and \w+",
     2, "medium", "cut to two items or give one concrete example"),
    ("E07", "名词化堆叠", r"\b\w+(?:tion|sion|ment|ness|ity|ance|ence)\b",
     1, "medium", "turn nominalizations back into verbs"),
    ("E09", "套话开场", r"\b(In today'?s (?:fast-paced|ever-changing|digital) world|In an era of|Let'?s dive in|Let'?s explore|Great question|In the realm of)\b",
     3, "high", "delete; start with the fact"),
    ("E10", "助手残留", r"\b(Certainly[!,. ]|Of course[!,. ]|Here'?s (?:a|an|the|what|how)|I hope this helps|Let me know if|Would you like me to|As an AI)\b",
     3, "high", "remove chat framing entirely"),
    ("E11", "免责声明", r"\b(it is important to note|it'?s worth noting|it should be noted|while specific details|based on available information|not widely (?:documented|available)|should not be confused with)\b",
     2, "high", "say the thing or say you don't know, once"),
    ("E12", "模糊归属", r"\b(experts (?:argue|say|believe)|industry reports|observers have|studies (?:show|suggest)|some critics|many (?:experts|scholars))\b",
     3, "high", "name the source or cut the sentence"),
    ("E13", "挑战与展望段", r"\b(Despite (?:its|these|their)[^.]{0,60}(?:challenges|success|promise)|faces? (?:several|numerous|many) challenges|Challenges and (?:Future|Legacy)|Future (?:Outlook|Prospects))\b",
     3, "high", "delete the formula; mention a concrete constraint if it matters"),
    ("E15", "粗体标签列表", r"^\s*[-*•]\s+\*\*[^*\n]{2,40}\*\*\s*[:：]",
     2, "medium", "write it as a sentence; bold labels are slideware"),
    ("E16", "破折号", "—|--",
     2, "medium", "use a comma, colon, or full stop"),
    ("E21", "表格化散文", r"^\s*\|.+\|\s*$",
     1, "low", "prose beats a two-row table"),
    ("E23", "拉丁词膨胀", r"\b(utilize[sd]?|facilitate[sd]?|endeavor|ascertain|commence|terminate|implement(?:ation)? of)\b",
     1, "low", "use the short verb: use, help, try, find out, start, end"),
    ("E24", "列表化", r"^\s*(?:[-*•]|\d+[.)])\s+",
     1, "medium", "turn the list into sentences unless it is genuinely a list"),
    ("E25", "伪具体引用", r"\b(doi:\s*10\.\d{4,}/\S+|et al\.,? \d{4})\b",
     0, "low", "verify every DOI; fabricated refs resolve to unrelated papers"),
]

EN_CONNECTIVES = [
    "however", "moreover", "furthermore", "additionally", "therefore",
    "consequently", "nevertheless", "in addition", "overall", "in conclusion",
    "firstly", "secondly", "thirdly", "finally", "thus",
]

# 版面与残留
RE_MARKDOWN_BOLD = re.compile(r"\*\*[^*\n]+\*\*")
RE_MARKDOWN_HEAD = re.compile(r"^\s{0,3}#{1,6}\s", re.MULTILINE)
RE_MARKDOWN_CODE = re.compile(r"```")
RE_BULLET = re.compile(r"^\s*(?:[-*•]|\d+[.)])\s+", re.MULTILINE)
RE_TABLE = re.compile(r"^\s*\|.+\|\s*$", re.MULTILINE)
RE_EMOJI = re.compile(
    "[" "\U0001F300-\U0001FAFF" "\U00002600-\U000027BF" "\U0001F000-\U0001F0FF"
    "\u2705\u274c\u26a0\u2b50\ufe0f" "]"
)
RE_KEYCAP = re.compile(r"[0-9]\ufe0f?\u20e3")
RE_EM_DASH = re.compile(r"——|—")
RE_QUOTE_CN = re.compile(r"「[^」\n]{1,20}」")
RE_CURLY = re.compile(r"[“”‘’]")
RE_UNUSUAL_UNICODE = re.compile(r"[─≈→←≥≤★☆※§¶•◦▪▫]")


# --------------------------------------------------------------------------
# 统计
# --------------------------------------------------------------------------

@dataclass
class Hit:
    id: str
    name: str
    count: int
    weight: int
    conf: str
    advice: str
    samples: list[str] = field(default_factory=list)
    lines: list[int] = field(default_factory=list)


@dataclass
class Report:
    lang: str
    chars: int
    words: int
    score: float
    band: str
    subscores: dict
    metrics: dict
    hits: list[Hit]
    notes: list[str]

    def to_dict(self) -> dict:
        d = {
            "lang": self.lang,
            "chars": self.chars,
            "words": self.words,
            "score": round(self.score, 1),
            "band": self.band,
            "subscores": {k: round(v, 1) for k, v in self.subscores.items()},
            "metrics": {k: (round(v, 3) if isinstance(v, float) else v)
                        for k, v in self.metrics.items()},
            "hits": [
                {
                    "id": h.id, "name": h.name, "count": h.count,
                    "weight": h.weight, "confidence": h.conf,
                    "advice": h.advice, "samples": h.samples[:5],
                    "lines": sorted(set(h.lines))[:8],
                }
                for h in self.hits
            ],
            "notes": self.notes,
        }
        return d


def line_no(text: str, pos: int) -> int:
    return text.count("\n", 0, pos) + 1


def sniff_fragment(text: str, start: int, end: int, pad: int = 14) -> str:
    a = max(0, start - 2)
    b = min(len(text), end + pad)
    frag = text[a:b].replace("\n", " ")
    return re.sub(r"\s+", " ", frag).strip()


def scan_patterns(text: str, patterns, lang: str) -> list[Hit]:
    hits: list[Hit] = []
    for pid, name, rx, weight, conf, advice in patterns:
        flags = re.MULTILINE | (re.IGNORECASE if lang == "en" else 0)
        found: list[re.Match] = list(re.finditer(rx, text, flags))
        if not found:
            continue
        hits.append(Hit(
            id=pid, name=name, count=len(found), weight=weight, conf=conf,
            advice=advice,
            samples=[sniff_fragment(text, m.start(), m.end()) for m in found[:5]],
            lines=[line_no(text, m.start()) for m in found[:5]],
        ))
    return hits


def scan_words(text: str, table: dict[str, int], pid: str, name: str, advice: str) -> Hit | None:
    low = text.lower()
    total = 0
    samples: list[str] = []
    lines: list[int] = []
    maxw = max(table.values())
    for w, weight in table.items():
        if weight <= 0:
            continue
        for m in re.finditer(r"\b" + re.escape(w) + r"\b", low):
            total += 1
            if len(samples) < 5:
                samples.append(sniff_fragment(text, m.start(), m.end()))
                lines.append(line_no(text, m.start()))
    if total == 0:
        return None
    return Hit(id=pid, name=name, count=total, weight=maxw, conf="high",
               advice=advice, samples=samples, lines=lines)


def scan_zh_lexicon(text: str) -> list[Hit]:
    out: list[Hit] = []

    def tally(words: list[str], pid: str, name: str, weight: int, conf: str, advice: str):
        total = 0
        samples, lines = [], []
        for w in words:
            for m in re.finditer(re.escape(w), text):
                total += 1
                if len(samples) < 5:
                    samples.append(sniff_fragment(text, m.start(), m.end()))
                    lines.append(line_no(text, m.start()))
        if total:
            out.append(Hit(pid, name, total, weight, conf, advice, samples, lines))

    tally(ZH_HIGH, "Z01", "空话/拔高/官腔词", 3, "高",
          "换成具体动作与结果；官腔词一个不留")
    tally(ZH_ORAL_DEBRIS, "Z18", "口播/带货腔", 3, "高",
          "平实表达或直接删掉")
    tally(ZH_FAKE_CANDOR, "Z16", "假坦白钩子", 2, "中",
          "直接说，不要铺垫")
    tally(ZH_ANTHROPO, "Z23", "拟人/动作隐喻", 3, "高",
          "换平实动词：放、装、存、读、占、不够")
    return out


def count_zh_idioms(text: str) -> int:
    return sum(text.count(w) for w in ZH_IDIOMS)


def detect_short_opener_paragraphs(text: str, lang: str) -> tuple[int, list[int]]:
    """段首 3-12 字孤立判断句。"""
    n = 0
    lines: list[int] = []
    cursor = 0
    for para in paragraphs(text):
        idx = text.find(para, cursor)
        if idx < 0:
            continue
        cursor = idx + len(para)
        sents = split_sentences(para, lang)
        if len(sents) >= 2:
            first = len(CJK_RE.findall(sents[0])) if lang == "zh" else len(LATIN_WORD_RE.findall(sents[0]))
            lim = 12 if lang == "zh" else 7
            if 0 < first <= lim:
                n += 1
                if len(lines) < 5:
                    lines.append(line_no(text, idx))
    return n, lines


def detect_short_burst(text: str, lang: str) -> int:
    """连续 3 句以上极短句。"""
    sents = split_sentences(text, lang)
    lim = 8 if lang == "zh" else 5
    run = 0
    best = 0
    for s in sents:
        n = len(CJK_RE.findall(s)) if lang == "zh" else len(LATIN_WORD_RE.findall(s))
        if 0 < n <= lim:
            run += 1
            best = max(best, run)
        else:
            run = 0
    return best if best >= 3 else 0


def detect_uniform_runs(text: str, lang: str) -> int:
    """连续 3 句以上句长几乎相同（±12%）。"""
    lens = [len(CJK_RE.findall(s)) if lang == "zh" else len(LATIN_WORD_RE.findall(s))
            for s in split_sentences(text, lang)]
    lens = [n for n in lens if n > 0]
    run = 1
    worst = 0
    for a, b in itertools.pairwise(lens):
        if a and abs(a - b) <= max(2, 0.12 * a):
            run += 1
            worst = max(worst, run)
        else:
            run = 1
    return worst if worst >= 3 else 0


def connective_initial_ratio(text: str, lang: str) -> float:
    sents = split_sentences(text, lang)
    if not sents:
        return 0.0
    if lang == "zh":
        pat = re.compile(r"^(此外|同时|然而|因此|另外|总之|再者|其次|最后|首先|综上|不仅如此)")
    else:
        pat = re.compile(r"^(" + "|".join(EN_CONNECTIVES) + r")\b", re.IGNORECASE)
    n = sum(1 for s in sents if pat.match(s.strip()))
    return n / len(sents)


def ngram_repetition(text: str, lang: str, n: int = 4) -> float:
    """重复 n-gram 占比（论元/短语复用的代理指标）。"""
    if lang == "zh":
        seq = re.sub(r"[^\u4e00-\u9fff]", "", text)
    else:
        seq = re.sub(r"[^A-Za-z\s]", " ", text.lower()).split()
    if len(seq) < n * 3:
        return 0.0
    grams = ["".join(seq[i:i + n]) if isinstance(seq, str) else " ".join(seq[i:i + n])
             for i in range(len(seq) - n + 1)]
    uniq = len(set(grams))
    return 1 - uniq / len(grams)


def ttr(text: str, lang: str) -> float:
    if lang == "zh":
        chars = CJK_RE.findall(text)
        return len(set(chars)) / len(chars) if chars else 0.0
    words = [w.lower() for w in LATIN_WORD_RE.findall(text)]
    return len(set(words)) / len(words) if words else 0.0


# --------------------------------------------------------------------------
# 主分析
# --------------------------------------------------------------------------

PROFILES = {
    # 散文/公众号/博客：版面与套话要求最严
    "prose": {
        "bold": (1.0, 3.0), "dash": (1.0, 3.0), "list_ratio": (0.06, 0.15),
        "triad": (0.4, 1.2), "triad_en": (0.8, 2.2), "score_cap": 45,
        "allow": {"bold": 1, "dash": 1, "list": 1},
        "sent_cv": (0.32, 0.55), "para_cv": (0.20, 0.55),
    },
    # 技术文档：列表与表格是正当的
    "tech": {
        "bold": (2.0, 6.0), "dash": (1.0, 3.0), "list_ratio": (0.15, 0.35),
        "triad": (0.8, 2.0), "triad_en": (1.2, 3.0), "score_cap": 55,
        "allow": {"bold": 3, "dash": 2, "list": 8},
        "sent_cv": (0.25, 0.48), "para_cv": (0.20, 0.55),
    },
    # 学术：允许工整结构，重点看空话与词汇
    "academic": {
        "bold": (0.5, 2.0), "dash": (1.0, 3.0), "list_ratio": (0.05, 0.20),
        "triad": (0.5, 1.5), "triad_en": (0.8, 2.0), "score_cap": 50,
        "allow": {"bold": 0, "dash": 2, "list": 2},
        "sent_cv": (0.18, 0.38), "para_cv": (0.15, 0.45),
    },
}


def analyze(text: str, lang: str = "auto", profile: str = "prose") -> Report:
    if lang == "auto":
        lang = detect_lang(text)
    p = PROFILES.get(profile, PROFILES["prose"])
    notes: list[str] = []

    if lang == "zh":
        total = len(CJK_RE.findall(text)) or 1
        words = total
    else:
        words = len(LATIN_WORD_RE.findall(text)) or 1
        total = words

    sents = split_sentences(text, lang)
    slens = [length_of(s, lang) for s in sents]
    paras = paragraphs(text)
    plens = [length_of(x, lang) for x in paras]

    sent_cv = cv(slens)
    para_cv = cv(plens)

    # ---- 版面
    bold = len(RE_MARKDOWN_BOLD.findall(text))
    heads = len(RE_MARKDOWN_HEAD.findall(text))
    fences = len(RE_MARKDOWN_CODE.findall(text)) // 2
    bullets = len(RE_BULLET.findall(text))
    tables = len(RE_TABLE.findall(text))
    emoji = len(RE_EMOJI.findall(text)) + len(RE_KEYCAP.findall(text))
    dash = len(RE_EM_DASH.findall(text))
    quotes_cn = len(RE_QUOTE_CN.findall(text))
    curly = len(RE_CURLY.findall(text))
    unusual = len(RE_UNUSUAL_UNICODE.findall(text))
    list_lines = bullets + tables
    total_lines = max(1, text.count("\n") + 1)

    bold_pk = per_k(bold, total, 1000)
    dash_pk = per_k(dash, total, 1000)
    list_ratio = list_lines / total_lines

    # ---- 词汇
    hits: list[Hit] = scan_patterns(text, ZH_PATTERNS if lang == "zh" else EN_PATTERNS, lang)
    if lang == "zh":
        hits += scan_zh_lexicon(text)
        nominal = sum(text.count(w) for w in ZH_NOMINAL_VERBS)
        nominal_rate = per_k(nominal, total, 1000)          # 次/千字
        idiom_rate = per_k(count_zh_idioms(text), total, 1000)
        ai_vocab_rate = per_k(sum(h.count for h in hits if h.id == "Z01"), total, 1000)
        nom_lo, nom_hi = 8.0, 18.0
    else:
        wh = scan_words(text, EN_AI_WORDS, "E03", "AI vocabulary", "swap for plain words")
        if wh:
            hits.append(wh)
        nom_words = len(re.findall(r"\b\w+(?:tion|sion|ment|ness|ity|ance|ence)\b", text, re.IGNORECASE))
        nominal_rate = nom_words / total                      # 占比
        idiom_rate = 0.0
        ai_vocab_rate = per_k(wh.count if wh else 0, total, 1000)
        nom_lo, nom_hi = 0.045, 0.10

    # ---- 句式
    conn_ratio = connective_initial_ratio(text, lang)
    triad = sum(h.count for h in hits if h.id in ("Z06", "E06"))
    neg_par = sum(h.count for h in hits if h.id in ("Z05", "E05"))
    triad_pk = per_k(triad, total, 1000)
    neg_pk = per_k(neg_par, total, 1000)
    short_open, _ = detect_short_opener_paragraphs(text, lang)
    burst = detect_short_burst(text, lang)
    uniform = detect_uniform_runs(text, lang)
    rep = ngram_repetition(text, lang, 4 if lang == "zh" else 5)
    diversity = ttr(text, lang)

    # ---- 分项打分（0-100，越高越像 AI）
    # 少量出现属于正常写作，只有数量超过"容忍额度"才按密度计分（误杀边界）
    allow = p["allow"]
    bold_eff = bold_pk if bold > allow["bold"] else 0.0
    dash_eff = dash_pk if dash > allow["dash"] else 0.0
    list_eff = list_ratio if list_lines > allow["list"] else 0.0

    items = [
        ramp_more_better(sent_cv, p["sent_cv"][0], p["sent_cv"][1]),
        ramp_more_worse(bold_eff, p["bold"][0], p["bold"][1]),
        ramp_more_worse(list_eff, p["list_ratio"][0], p["list_ratio"][1]),
        ramp_more_worse(dash_eff, p["dash"][0], p["dash"][1]),
    ]
    # 段落少于 4 段时段长方差没有统计意义
    if len(paras) >= 4:
        items.append(ramp_more_better(para_cv, p["para_cv"][0], p["para_cv"][1]))
    s_structure = mean(items)
    s_lexicon = mean([
        ramp_more_worse(ai_vocab_rate, 3.0, 15.0),
        ramp_more_worse(nominal_rate, nom_lo, nom_hi),
        ramp_more_worse(idiom_rate, 25.0, 60.0) if lang == "zh" else 0.0,
    ])
    s_syntax = mean([
        ramp_more_worse(conn_ratio, 0.10, 0.35),
        ramp_more_worse(triad_pk, *(p["triad_en"] if lang == "en" else p["triad"])),
        ramp_more_worse(neg_pk, 0.3, 1.5),
        ramp_more_worse(float(short_open), 0.3, 2.0),
        ramp_more_worse(float(max(burst, 0)), 0.0, 1.0),
        ramp_more_worse(float(max(uniform, 0)), 3.0, 5.0),
        ramp_more_worse(rep, 0.06, 0.22),
    ])
    s_residue = mean([
        ramp_more_worse(per_k(heads, total, 1000), 0.5, 4.0),
        ramp_more_worse(per_k(fences, total, 1000), 0.0, 2.0),
        ramp_more_worse(per_k(emoji, total, 1000), 0.0, 1.5),
        # 中文里的 “” 是规范标点，不构成痕迹；英文里弯引号才是 ChatGPT/DeepSeek 特征
        ramp_more_worse(per_k(curly, total, 1000), 0.0, 6.0) if lang == "en" else 0.0,
        ramp_more_worse(per_k(unusual, total, 1000), 0.2, 2.0),
        ramp_more_worse(per_k(quotes_cn, total, 1000), 0.5, 4.0),
    ])

    # 独立信号数：命中多少个不同的高置信度检测项。人写文本很少同时踩 4 项以上。
    sig = sum(1.0 if h.conf in ("高", "high") else 0.5
              for h in hits if h.weight >= 2)
    s_signals = ramp_more_worse(sig, 0.0, 4.0)

    score = (0.20 * s_structure + 0.22 * s_lexicon + 0.20 * s_syntax
             + 0.08 * s_residue + 0.30 * s_signals)

    # 少量"硬信号"提权：助手残留、模糊归属、公式化收尾、假引用
    hard = [h for h in hits if h.id in ("E10", "E12", "E13", "Z02", "Z03", "Z12", "Z21")
            and h.conf in ("高", "high")]
    if hard:
        boost = min(12.0, sum(h.weight for h in hard) * 1.5)
        score = min(100.0, score + boost)
        notes.append("硬信号命中：" + "、".join(f"{h.id}{h.name}" for h in hard))

    if lang == "zh" and total < 180:
        notes.append("样本偏短（<180 字），句长与段落统计不可靠")
    if lang == "en" and words < 120:
        notes.append("sample short (<120 words); sentence-length stats unreliable")

    band = ("低（人味较足）" if score < 15 else
            "轻（有 AI 痕迹）" if score < 40 else
            "中（明显 AI 味）" if score < 62 else
            "高（一眼 AI）")

    metrics = {
        "sentences": len(sents),
        "avg_sent_len": mean(slens),
        "sent_cv": sent_cv,
        "para_cv": para_cv,
        "bold_per_k": bold_pk,
        "em_dash_per_k": dash_pk,
        "list_line_ratio": list_ratio,
        "ai_vocab_per_k": ai_vocab_rate,
        "nominal_rate": nominal_rate,
        "idiom_per_k": idiom_rate,
        "connective_initial_ratio": conn_ratio,
        "triad_per_k": triad_pk,
        "neg_parallel_per_k": neg_pk,
        "short_opener_paras": short_open,
        "short_burst_max": burst,
        "uniform_run_max": uniform,
        "repeated_ngram_ratio": rep,
        "type_token_ratio": diversity,
        "emoji": emoji,
        "curly_quotes": curly,
    }
    hits.sort(key=lambda h: (-h.weight * min(h.count, 6), h.id))
    return Report(lang=lang, chars=len(text), words=words, score=score, band=band,
                  subscores={"structure": s_structure, "lexicon": s_lexicon,
                             "syntax": s_syntax, "residue": s_residue,
                             "signals": s_signals},
                  metrics=metrics, hits=hits, notes=notes)


# --------------------------------------------------------------------------
# 输出
# --------------------------------------------------------------------------

def render(report: Report, top: int = 5, color: bool = True) -> str:
    def c(code: str, s: str) -> str:
        return f"\033[{code}m{s}\033[0m" if color else s

    score_color = "32" if report.score < 15 else "33" if report.score < 40 else "31"
    L = []
    L.append(f"语言 {report.lang}   字符 {report.chars}   计量单位 {report.words}")
    L.append(f"AI 味 {c(score_color, f'{report.score:.1f}/100')}   {report.band}")
    L.append("")
    L.append("分项：结构 {structure:.0f}  词汇 {lexicon:.0f}  句式 {syntax:.0f}  残留 {residue:.0f}  信号 {signals:.0f}".format(
        **report.subscores))
    L.append("")
    m = report.metrics
    L.append("指标：")
    L.append(f"  句数 {m['sentences']}  平均句长 {m['avg_sent_len']:.1f}  句长CV {m['sent_cv']:.2f}  段长CV {m['para_cv']:.2f}")
    L.append(f"  加粗 {m['bold_per_k']:.1f}/千  破折号 {m['em_dash_per_k']:.1f}/千  列表行占比 {m['list_line_ratio']:.0%}")
    nom_txt = f"{m['nominal_rate']:.1f}/千" if report.lang == "zh" else f"{m['nominal_rate']:.1%}"
    L.append(f"  AI词 {m['ai_vocab_per_k']:.1f}/千  名词化 {nom_txt}  三项并列 {m['triad_per_k']:.2f}/千  否定平行 {m['neg_parallel_per_k']:.2f}/千")
    L.append(f"  连接词开场句 {m['connective_initial_ratio']:.0%}  段首短句 {m['short_opener_paras']} 处  重复n-gram {m['repeated_ngram_ratio']:.2f}  TTR {m['type_token_ratio']:.2f}")
    L.append("")
    if report.hits:
        L.append(f"命中（按严重度，最多 {top} 类）：")
        for h in report.hits[:top]:
            where = ",".join(str(x) for x in sorted(set(h.lines))[:4]) or "-"
            L.append(f"  [{h.id}] {h.name} ×{h.count}  权重{h.weight}/{h.conf}  行 {where}")
            L.append(f"        → {h.advice}")
            for s in h.samples[:2]:
                L.append(f"        例：{s[:60]}")
    else:
        L.append("命中：无")
    if report.notes:
        L.append("")
        for n in report.notes:
            L.append(f"注：{n}")
    return "\n".join(L)


DIFF_METRICS = [
    ("sent_cv", "句长CV", "higher"),
    ("para_cv", "段长CV", "higher"),
    ("bold_per_k", "加粗/千", "lower"),
    ("em_dash_per_k", "破折号/千", "lower"),
    ("list_line_ratio", "列表行占比", "lower"),
    ("ai_vocab_per_k", "AI词/千", "lower"),
    ("nominal_rate", "名词化", "lower"),
    ("triad_per_k", "三项并列/千", "lower"),
    ("connective_initial_ratio", "连接词开场", "lower"),
]


def _disp_width(text: str) -> int:
    """终端显示宽度：CJK 与全角字符按 2 计。"""
    return sum(2 if unicodedata.east_asian_width(ch) in "WF" else 1 for ch in text)


def _pad(text: str, width: int, align: str = "left") -> str:
    gap = max(0, width - _disp_width(text))
    return (" " * gap + text) if align == "right" else (text + " " * gap)


def render_diff(before: Report, after: Report, color: bool = True) -> str:
    def c(code: str, s: str) -> str:
        return f"\033[{code}m{s}\033[0m" if color else s

    delta = after.score - before.score
    head = "下降" if delta < 0 else ("上升" if delta > 0 else "持平")
    lines = [
        f"改写前 {before.score:.1f} → 改写后 {after.score:.1f}（{head} {abs(delta):.1f}）",
        f"档位：{before.band} → {after.band}",
        "",
        _pad("指标", 12) + _pad("前", 8, "right") + _pad("后", 8, "right") + _pad("变化", 10, "right"),
    ]
    for key, label, direction in DIFF_METRICS:
        b = before.metrics.get(key, 0.0)
        a = after.metrics.get(key, 0.0)
        is_ratio = key in ("list_line_ratio", "connective_initial_ratio")
        fb, fa = (f"{b:.0%}", f"{a:.0%}") if is_ratio else (f"{b:.2f}", f"{a:.2f}")
        d = (a - b) * 100 if is_ratio else a - b
        good = (d > 0) if direction == "higher" else (d < 0)
        dtxt = f"{d:+.1f}pp" if is_ratio else f"{d:+.2f}"
        dtxt = c("32", dtxt) if good and abs(d) > 1e-9 else dtxt
        lines.append(_pad(label, 12) + _pad(fb, 8, "right")
                     + _pad(fa, 8, "right") + _pad(dtxt, 10, "right")
                     + (" " * max(0, 8 - len(dtxt))))

    b_ids = {h.id: h.count for h in before.hits}
    a_ids = {h.id: h.count for h in after.hits}
    gone = [i for i in b_ids if i not in a_ids]
    left = [(i, a_ids[i]) for i in b_ids if i in a_ids and a_ids[i] < b_ids[i]]
    new = [(i, n) for i, n in a_ids.items() if i not in b_ids]
    if gone:
        lines += ["", "已清除：" + "、".join(gone)]
    if left:
        lines.append("仍有残留：" + "、".join(f"{i}×{n}" for i, n in left))
    if new:
        lines.append("新增命中（改写引入）：" + "、".join(f"{i}×{n}" for i, n in new))
    return "\n".join(lines)


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(
        description="AI 味体检器（中英双语，只读，不修改文本）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="例：python3 humanize_lint.py check draft.md --lang zh --profile prose",
    )
    ap.add_argument("action", nargs="?", default="check",
                    choices=["check", "score", "rules", "diff"],
                    help="check=详细报告 score=一行摘要 rules=检测项清单 diff=前后对比")
    ap.add_argument("path", nargs="?", default="-", help="文本文件，或 - 表示 stdin")
    ap.add_argument("path2", nargs="?", default=None, help="diff 模式的改写后文件")
    ap.add_argument("--lang", default="auto", choices=["auto", "zh", "en"])
    ap.add_argument("--profile", default="prose", choices=list(PROFILES))
    ap.add_argument("--json", action="store_true", help="输出 JSON")
    ap.add_argument("--max-score", type=float, default=None,
                    help="超过该分数时退出码 1（默认取 profile 的阈值）")
    ap.add_argument("--top", type=int, default=5)
    ap.add_argument("--no-color", action="store_true")
    args = ap.parse_args(argv)

    if args.action == "rules":
        print("中文检测项：")
        for pid, name, *_ in ZH_PATTERNS:
            print(f"  {pid}  {name}")
        print("  词表  Z01 空话官腔 / Z18 口播腔 / Z16 假坦白 / Z23 拟人隐喻")
        print("  结构  Z29 段首短判断句 / 连续短句轰炸 / 句式同构 / 连接词开场率")
        print("英文检测项：")
        for pid, name, *_ in EN_PATTERNS:
            print(f"  {pid}  {name}")
        print(f"  词表  E03 AI vocabulary （{len(EN_AI_WORDS)} 词）")
        return 0

    if args.action == "diff":
        if not args.path2:
            print("diff 需要两个文件：diff <改写前> <改写后>", file=sys.stderr)
            return 2
        try:
            with open(args.path, encoding="utf-8") as f:
                before_text = f.read()
            with open(args.path2, encoding="utf-8") as f:
                after_text = f.read()
        except OSError as e:
            print(f"读取失败：{e}", file=sys.stderr)
            return 2
        before = analyze(before_text, args.lang, args.profile)
        after = analyze(after_text, args.lang, args.profile)
        cap = args.max_score if args.max_score is not None else PROFILES[args.profile]["score_cap"]
        if args.json:
            print(json.dumps({"before": before.to_dict(), "after": after.to_dict(),
                              "delta": round(after.score - before.score, 1),
                              "pass": after.score <= cap}, ensure_ascii=False, indent=2))
        else:
            print(render_diff(before, after, color=not args.no_color))
            print(f"\n阈值 {cap:.0f}：" + ("通过" if after.score <= cap else "未通过"))
        return 0 if after.score <= cap else 1

    if args.path == "-":
        text = sys.stdin.read()
    else:
        try:
            with open(args.path, "r", encoding="utf-8") as f:
                text = f.read()
        except OSError as e:
            print(f"读取失败：{e}", file=sys.stderr)
            return 2

    if not text.strip():
        print("输入为空", file=sys.stderr)
        return 2

    rep = analyze(text, args.lang, args.profile)
    cap = args.max_score if args.max_score is not None else PROFILES[args.profile]["score_cap"]

    if args.json:
        out = rep.to_dict()
        out["max_score"] = cap
        out["pass"] = rep.score <= cap
        print(json.dumps(out, ensure_ascii=False, indent=2))
    elif args.action == "score":
        print(f"{rep.score:.1f}\t{rep.band}\t{rep.lang}\t{args.path}")
    else:
        print(render(rep, top=args.top, color=not args.no_color))
        print(f"\n阈值 {cap:.0f}：" + ("通过" if rep.score <= cap else "未通过，按上面命中的前 3 类先改"))

    return 0 if rep.score <= cap else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
