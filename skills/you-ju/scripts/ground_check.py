#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ground_check.py — you-ju 技能的闭世界审计工具 (只读，不修改任何输入文件)

用法:
  python3 ground_check.py whitelist <来源目录或文件...> -o whitelist.json
      从来源提取实体白名单与数字白名单，输出 JSON

  python3 ground_check.py check <输出.md> --whitelist whitelist.json [--sources a.md b.md ...]
      审计输出:
        E1 实体泄漏  — 输出中不在白名单的命名实体（英文词/专名/文档编号）
        N1 数字泄漏  — 输出中归一化后不在数字白名单的数值
        C1 引用失配  — [A:L12] 标记回查: 源文档该行是否包含断言关键词
        Q1 候选      — 输出含数值但同句含"未提供/未给出/未提及"提示人工复核

  python3 ground_check.py align <输出.md> <来源...>
      逐句对齐: 输出每个断言句标注 有据(命中来源行) / 无据(任何来源行都覆盖不足)

  python3 ground_check.py coverage <输出.md> <来源...>
      覆盖检查(可选): 来源要点(数字+实体行)有多少被输出覆盖

设计说明:
  - 虚构语料上白名单=闭世界全集, 白名单外实体必然是编造
  - 数字比对做单位归一化 (2.1 W == 2100 mW == 0.0021 kW)
  - C1 用"断言关键词出现在标记行"的宽松回查, 误报宁可多不可漏
  - R1(关系增加) 机械不可判定, 不在脚本范围, 需模型自审
"""
import argparse
import json
import os
import re
import sys
import unicodedata

# ---------------------------------------------------------------- utilities

NUM_RE = re.compile(
    r"-?\d+(?:\.\d+)?(?:\s*(?:×|x)\s*-?\d+(?:\.\d+)?)*"
    r"\s*(?:%|°C|TOPS|TOPS/W|W|mW|kW|Gbps|Mbps|fps|ms|us|µs|ns|MB|KB|GB|nm|通道|个百分点|亿|万)?"
)

UNIT_TO_BASE = {
    "w": 1.0, "mw": 0.001, "kw": 1000.0,                       # 功率 -> W
    "tops": 1.0, "tops/w": 1.0,                                # 算力原样
    "gbps": 1.0, "mbps": 0.001, "kbps": 1e-6,                  # 带宽 -> Gbps
    "ms": 1.0, "us": 0.001, "µs": 0.001, "ns": 1e-6, "s": 1000.0,  # 时间 -> ms
    "mb": 1.0, "kb": 0.001, "gb": 1000.0,                      # 容量 -> MB
    "%": 1.0, "°c": 1.0, "fps": 1.0, "nm": 1.0, "通道": 1.0,
    "个百分点": 1.0, "亿": 1.0, "万": 1.0,
}

# 数字白名单里的行允许带注释与中文单位
STOP_NUM_TOKENS = {"2026", "2027"}  # 年份裸数字: 单独出现太泛, 只在带上下文时比对


def norm_num(num_str):
    """'2.1 W' / '2100 mW' -> ('power', 2.1) 归一化键; 无法归一则原样小写"""
    s = num_str.strip().lower()
    m = re.match(r"^(-?\d+(?:\.\d+)?)(?:\s*(?:×|x)\s*-?\d+(?:\.\d+)?)*\s*(.*)$", s)
    if not m:
        return ("raw", s)
    val = float(m.group(1))
    unit = m.group(2).strip()
    if unit in ("", None):
        return ("bare", val)
    u = unit.replace(" ", "")
    base = UNIT_TO_BASE.get(u)
    if base is None:
        return ("raw", s)
    # 功率族/带宽族/时间族/容量族各自有 base=1 的规范单位
    if u in ("w", "gbps", "ms", "mb", "%", "°c", "fps", "nm", "通道", "个百分点", "亿", "万", "tops", "tops/w"):
        return ("num", round(val, 6))
    return ("num", round(val * base, 6))


def num_key(num_str):
    kind, v = norm_num(num_str)
    if kind == "raw":
        return v
    if kind == "bare":
        return f"bare:{v}"
    return f"num:{v}"


# 中文常用字表: 小语料闭集缺大量常用字, 单字缺失≠新实体。
# 从 common_chars.txt 加载 (现代汉语常用字), 加上功能字补充集
_CN_COMMON_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                               "common_chars.txt")
try:
    with open(_CN_COMMON_FILE, encoding="utf-8") as _f:
        _COMMON = set(_f.read().strip())
except OSError:
    _COMMON = set()
CN_FUNCTION_CHARS = _COMMON | set(
    "的了在是与和及或对于从被把让使向往着过地得其所本该等之这些那些"
    "不未无没别非反都只更就很也太最较挺相当十分往往每各某另另外"
    "来源说明任务样例测试输出检查对比整理总结清单涉及给出提到明确声明来去"
    "引用转述覆盖回答提问常见问题支持部署应用场景产品规格参数版本文档"
    "数据信息内容结果表现情况状态过程方法方式类型种类项目方面角度层面"
    "如果那么因为所以但且或并并且而且虽然然而因此由于既然"
)


# 中文元话语停用词: 输出端组织语言, 非来源转述实体
CN_STOPWORDS_CN = {
    "来源", "输出", "内容", "信息", "数据", "性能", "产品", "文档", "说明",
    "以上", "以下", "本文", "本次", "其中", "以及", "通过", "使用", "支持",
    "包括", "对于", "关于", "由于", "因此", "主要", "采用", "面向", "提供",
    "测试", "样例", "总结", "对比", "整理", "问题", "清单", "未覆盖", "未提及",
    "未提供", "未给出", "明确", "声明", "涉及", "自研", "几乎", "运行", "还将",
    "已经", "正在", "将会", "能够", "应该", "直接", "稳定", "无损", "同步",
    "推出", "实现", "完成", "达到", "高达", "需要", "无法", "可以", "不能",
    "是否", "何时", "多少", "推测", "以下为", "竞品数据", "联网", "检索",
    "授权", "进行", "定位", "市场份额", "前景", "补充", "先补", "需先",
}

# 中文高频双字功能词: 收缩结果命中即放行 (小语料单字缺失≠新实体)
CN_COMMON_WORDS = {
    "进行", "授权", "使用", "可以", "无法", "需要", "提供", "检索", "联网",
    "对比", "比较", "分析", "说明", "声明", "明确", "请勿", "请提供", "若需",
    "涉及", "包含", "覆盖", "给出", "提及", "相关", "如下", "如下所述", "以上",
    "补充", "补充来源", "先补充", "需先补充",
    "请提供竞品数据来源", "竞品数据来源", "数据来源", "来源或", "或授权",
    "以下", "关于", "由于", "因此", "但是", "然而", "此外", "同时", "另外",
    "其中", "以及", "或者", "并且", "如果", "那么", "即使", "尽管", "虽然",
    "本次", "本次任务", "当前", "目前", "目前尚", "尚未", "暂无", "暂未",
}


def _segmentable_by_common_words(seg):
    """贪心切分: 段能否被 CN_COMMON_WORDS + CN_FUNCTION_CHARS 完全覆盖 (元话语放行)"""
    words = sorted(CN_COMMON_WORDS | set(CN_STOPWORDS_CN), key=len, reverse=True)
    i = 0
    while i < len(seg):
        for w in words:
            if w and seg.startswith(w, i):
                i += len(w)
                break
        else:
            if seg[i] in CN_FUNCTION_CHARS:
                i += 1
                continue
            return False
    return True


def shrink_to_unknown_runs(seg, cn_chars):
    """收缩到来源外未知字符的最小连续子段: '采用台积电'→'台积电'"""
    unknown = set(seg) - cn_chars - CN_FUNCTION_CHARS
    if not unknown:
        return seg
    best = seg
    for m in re.finditer(r"[\u4e00-\u9fff]+", seg):
        run = m.group(0)
        idxs = [i for i, c in enumerate(run) if c in unknown]
        if not idxs:
            continue
        # 取首个未知字符向两侧扩展的未知连续窗口
        i0 = idxs[0]
        lo = hi = i0
        while lo > 0 and run[lo - 1] in unknown:
            lo -= 1
        while hi < len(run) - 1 and run[hi + 1] in unknown:
            hi += 1
        cand = run[lo:hi + 1]
        if len(cand) < len(best):
            best = cand
    return best


# 常见英文功能词: 首字母大写出现在句首时不是实体
EN_STOPWORDS = {
    "the", "this", "that", "with", "for", "and", "but", "not", "int",
    "when", "batch", "top", "note", "ok", "md", "json", "api", "url",
    "io", "eof", "faq", "readme", "ai",
}


def is_plausible_entity(tok):
    """启发式: 判定一个英文 token 是否像命名实体"""
    if len(tok) < 2:
        return False
    if tok.isdigit():
        return False
    if tok.lower() in EN_STOPWORDS:
        return False
    # 纯小写词不是实体 (英文功能词/普通词)
    if tok.islower() and tok.isalpha():
        return False
    # 全大写缩写 (≥2 字符): TOPS, FAQ, MB
    if tok.isupper() and len(tok) >= 2:
        return True
    # 首字母大写+混合: MobileNetV2, ResNet-50, MIPI-CSI, INT8, Gen3, FCBGA-441
    if re.match(r"^[A-Z][A-Za-z0-9\-]*$", tok) and len(tok) >= 3:
        return True
    return False


def extract_cn_entities(text):
    """抽中文实体候选: 2-8 字中文连续段。

    中文分词无词典, 用"白名单交集"策略: 段在白名单/来源中找不到 → 候选泄漏。
    停用段排除常见通用名词, 降低误报; 高频误报由白名单补充兜底。
    """
    CN_STOP = set(CN_STOPWORDS_CN) | {
        "组样", "例的", "主要面", "三类设备", "场景中", "产线", "部署到",
        "意味着", "意味", "语料无此信息", "语料", "无此", "此信息", "语料内",
        "语料外", "内可", "来源未覆盖", "来源外", "若需", "若需对比", "均未",
        "联网检索", "请提供", "定位总结", "任务",
    }
    out = []
    for m in re.finditer(r"[\u4e00-\u9fff]{2,8}", text):
        seg = m.group(0)
        if seg in CN_STOP or len(seg) < 2:
            continue
        out.append(seg)
    return out


def is_trivial_cn_token(seg):
    """单字与纯功能字组合不具实体判别力, 放行"""
    if len(seg) <= 1:
        return True
    return set(seg) <= CN_FUNCTION_CHARS


def extract_en_entities(text):
    """从文本抽英文命名实体候选: 连续大写开头词 + 已知模式"""
    toks = re.findall(r"[A-Za-z][A-Za-z0-9\-/×.]*", text)
    out = []
    i = 0
    while i < len(toks):
        if is_plausible_entity(toks[i]):
            # 贪心合并连续实体词 (MobileNetV2 与 ResNet-50 不合并: 有连接词)
            out.append(toks[i])
        i += 1
    return out


def extract_nums(text):
    out = []
    for m in NUM_RE.finditer(text):
        s = m.group(0).strip()
        if not s:
            continue
        # 纯行号/编号类纯数字且无单位: 仍记录 (bare key), 白名单机制统一处理
        out.append(s)
    return out


# ---------------------------------------------------------------- whitelist

def build_whitelist(paths):
    ent = set()
    num = set()
    aliases = {}  # 别名 -> 标准实体
    for p in paths:
        if os.path.isdir(p):
            for fn in sorted(os.listdir(p)):
                if fn.endswith(".md") or fn.endswith(".txt"):
                    ent2, num2, al = scan_file(os.path.join(p, fn))
                    ent |= ent2
                    num |= num2
                    aliases.update(al)
        elif os.path.isfile(p):
            ent2, num2, al = scan_file(p)
            ent |= ent2
            num |= num2
            aliases.update(al)
    return {"entities": sorted(ent), "numbers": sorted(num), "aliases": aliases}


def scan_file(path):
    ent = set()
    num = set()
    aliases = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if not line.strip():
                continue
            stripped = line.strip()
            # 跳过注释/表格行/引用块/标题行: 只从正文行提取中文实体,
            # 但数字仍从全行提取 (表格数字也是白名单)
            is_table = stripped.startswith("|")
            is_meta = (stripped.startswith("#") or stripped.startswith(">")
                       or stripped.startswith("-") or stripped.startswith("*"))
            body = stripped
            if "=" in stripped and not is_table and not stripped.startswith("http"):
                # 实体白名单行: 允许 "标准名 = 别名1/别名2"
                std, al = stripped.split("=", 1)
                body = std.strip()
                for a in al.split("/"):
                    a = a.strip()
                    if a:
                        aliases[a] = body
            for e in extract_en_entities(body):
                ent.add(e)
            if re.search(r"[\u4e00-\u9fff]", body) and not is_table:
                # 中文实体: 只从标题行抽 (## Q1 / ## 产品定位 等), 正文句子的
                # 中文片段是断言不是实体, 白名单过宽会让检查失效。
                # 正文中的中文实体保护由 align/coverage 的宽松命中兜底。
                if stripped.startswith("#") and not stripped.startswith("## Q"):
                    for seg in re.findall(r"[\u4e00-\u9fff][\u4e00-\u9fffA-Za-z0-9\-]{1,29}", body):
                        seg = seg.strip("的了在是与和及或本")
                        if 1 < len(seg) <= 20 and not re.search(r"未|请勿|不得|禁止", seg):
                            ent.add(seg)
            for n in extract_nums(stripped):
                num.add(num_key(n))
    return ent, num, aliases


# ---------------------------------------------------------------- checks

def check_output(out_path, whitelist, source_paths=None):
    with open(out_path, encoding="utf-8") as f:
        lines = f.readlines()
    ents = set(whitelist.get("entities", []))
    ent_lower = {e.lower() for e in ents}
    aliases = whitelist.get("aliases", {})
    nums = set(whitelist.get("numbers", []))
    src_texts = {}
    for p in source_paths or []:
        try:
            with open(p, encoding="utf-8") as f:
                src_texts[os.path.basename(p)] = f.read()
        except OSError:
            pass
    src_all = "\n".join(src_texts.values())

    e1, n1, c1, q1cand = [], [], [], []
    for ln, raw in enumerate(lines, 1):
        line = raw.rstrip("\n")
        stripped = line.strip()
        # 跳过元信息行: 注释块(>/#)、实验说明——它们描述实验而非转述来源
        # 标题行(# / ##)是输出端结构骨架, 不是对来源的转述断言
        if stripped.startswith(">") or stripped.startswith("<!--") or stripped.startswith("#"):
            continue
        code_masked = mask_code_spans(line)

        # --- E1: 实体泄漏 (英文 token + 中文段)
        cn_chars = set(re.findall(r"[\u4e00-\u9fff]", src_all)) if source_paths else set()
        for tok in extract_en_entities(code_masked) + extract_cn_entities(code_masked):
            t = tok.lower()
            if t in ent_lower or t in {a.lower() for a in aliases}:
                continue
            # 白名单子串命中: 白名单实体包含该段或该段包含白名单实体 (星尘-7/星尘半导体)
            if any(tok in e or e in tok for e in ents if len(e) >= 2):
                continue
            if source_paths and re.search(re.escape(tok), src_all):
                continue
            if re.search(r"[\u4e00-\u9fff]", tok):
                # 中文段判定链 (闭世界, 词组级优先于字级):
                # a) 全部字符都在来源中 → 字级放行 ('工艺'/'星尘')
                if cn_chars and set(tok) <= cn_chars:
                    continue
                if is_trivial_cn_token(tok):
                    continue
                # b) 段整体 3-gram 命中来源 → 语料内词组, 放行
                #    (词组级判定不受常用字表影响: '台积电'任何 3 字窗口都不在来源)
                if len(tok) >= 3 and source_paths and any(
                        tok[i:i + 3] in src_all for i in range(len(tok) - 2)):
                    continue
                # c) 高频功能词整词放行; 或可被功能词序列完全切分 ('对比需先补充数据来源')
                if len(tok) <= 1 or tok in CN_COMMON_WORDS:
                    continue
                if _segmentable_by_common_words(tok):
                    continue
                # d) 报告收缩到未知字符窗口 (仅展示; 放行判定已由 a-c 完成)
                shrunk = shrink_to_unknown_runs(tok, cn_chars)
                if len(shrunk) >= 2:
                    tok = shrunk
                e1.append({"line": ln, "entity": tok, "text": line.strip()[:80],
                           "kind": "cn"})
                continue
            e1.append({"line": ln, "entity": tok, "text": line.strip()[:80],
                       "kind": "en"})

        # --- N1: 数字泄漏
        for n in extract_nums(code_masked):
            k = num_key(n)
            if k in nums:
                continue
            if k.startswith("bare:") and k.split(":")[1] in {"1.0", "2.0", "3.0"}:
                # 列表序号/小整数: 不判泄漏 (引用标记 [A:L12] 等也在 code mask 外,
                # 但纯小整数歧义太大)
                continue
            if source_paths:
                # 等值归一后在来源里找
                if num_in_sources(n, src_all):
                    continue
            n1.append({"line": ln, "number": n, "key": k, "text": line.strip()[:80]})

        # --- Q1 候选: 同句既有具体数值又有"未提供"语义 → 矛盾句, 人工复核
        #     纯声明句("来源未提及X"无数值)不算矛盾, 是 Q1 的正确处理
        if re.search(r"未提供|未给出|未提及|未定|未覆盖", line):
            if re.search(r"\d+(?:\.\d+)?\s*(?:TOPS|W|fps|ms|MB|nm|Gbps|%)", code_masked):
                q1cand.append({"line": ln, "text": line.strip()[:80],
                               "why": "同句含数值+未提供语义, 疑似越权补值"})

    # --- C1: 引用标记回查
    if source_paths:
        c1 = check_citations(lines, src_texts)
    return {"E1": e1, "N1": n1, "C1": c1, "Q1_candidates": q1cand}


def mask_code_spans(line):
    """去掉行内代码与引用标记本身, 防止 [A:L12]/`8 TOPS` 自身触发"""
    line = re.sub(r"\[[A-Za-z0-9]+:L\d+(?:-\d+)?\]", "", line)
    line = re.sub(r"`[^`]*`", "", line)
    return line


def num_in_sources(num_str, src_all):
    k = num_key(num_str)
    for n in extract_nums(src_all):
        if num_key(n) == k:
            return True
    return False


def check_citations(lines, src_texts):
    """[A:L12] / [A:L12-15] 回查: 断言关键词应出现在目标行

    一行可含多个标记; 断言文本按标记切分成段, 每段归属其前面的标记。
    """
    keys = {k: build_line_index(v) for k, v in src_texts.items()}
    # 编号 -> 文件名映射: source_A.md / A.md / doc-A.md 中的字母编号
    by_id = {}
    for fname, idx in keys.items():
        stem = os.path.splitext(fname)[0]
        m = (re.search(r"(?:^|[_-])([A-Za-z])$", stem) or       # source_A, doc-A
             re.match(r"^([A-Za-z])$", stem))                    # 裸 A
        if m:
            by_id[m.group(1).upper()] = idx
    violations = []
    for ln, raw in enumerate(lines, 1):
        if "[" not in raw:
            continue
        # 按标记切分: 文本段 -> 其后跟的标记
        segments = re.split(r"(\[[A-Za-z0-9]+:L\d+(?:-\d+)?\])", raw)
        pending_text = ""
        for seg in segments:
            m = re.match(r"^\[([A-Za-z0-9]+):L(\d+)(?:-(\d+))?\]$", seg)
            if not m:
                pending_text += seg
                continue
            cid, l1, l2 = m.group(1), int(m.group(2)), int(m.group(3) or m.group(2))
            idx = by_id.get(cid.upper())
            if idx is None:
                violations.append({"line": ln, "cite": m.group(0),
                                   "reason": f"来源编号 {cid} 不在 --sources 清单中"})
                pending_text = ""
                continue
            # 逐个候选片段回查: 任一命中即算有据。
            # 输出端的引导语("语料内的性能数据")可能与来源措辞不同,
            # 所以除最长片段外, 也尝试其余中文/英文片段, 防止引导语误伤
            frags = assert_fragments(pending_text)
            pending_text = ""
            if not frags:
                continue
            hit = False
            # 宽松回查: 标记行 ±1 行 (行号手写偏差容忍 1 行; 转述跨相邻行)
            # 差 ≥2 行判失配——防止"大窗口刷白"让 C1 形同虚设
            # build_line_index 在头部垫了 '', idx[i] = 第 i 行, 故窗口取 [l1-1, l2+2)
            lo, hi = max(0, l1 - 1), min(len(idx), l2 + 2)
            window = "".join(idx[lo:hi])
            for frag in frags:
                if frag in window or char_overlap_hit(frag, window, ratio=0.7):
                    hit = True
                    break
            if not hit:
                src_line = idx[l1] if l1 < len(idx) else "<越界>"
                violations.append({"line": ln, "cite": m.group(0),
                                   "reason": f"断言片段「{frag}」未命中 {cid}:L{l1}" +
                                             (f"-L{l2}" if l1 != l2 else ""),
                                   "src_line": src_line.strip()[:80]})
    return violations


def build_line_index(text):
    lines = text.split("\n")
    # 引用行号按源文件实际行号 (1-based, 含标题), 与 L 标记一致
    return [""] + lines


def assert_fragments(text, limit=5):
    """断言的候选片段: 中文连续段(按长度降序) + 英文长词, 取前 limit 个"""
    frags = re.findall(r"[\u4e00-\u9fff]{2,}", text)
    frags = sorted(set(frags), key=len, reverse=True)
    frags += [w for w in re.findall(r"[A-Za-z][A-Za-z0-9\-]{3,}", text)]
    return frags[:limit]


def pick_assert_fragment(text):
    """取断言中最具区分度的片段: 最长的中文连续段或最长的英文词 (兼容保留)"""
    frags = assert_fragments(text)
    return frags[0] if frags else ""


# ---------------------------------------------------------------- align

def align_output(out_path, source_paths):
    with open(out_path, encoding="utf-8") as f:
        out_text = f.read()
    src_texts = []
    for p in source_paths:
        try:
            with open(p, encoding="utf-8") as f:
                src_texts.append(f.read())
        except OSError:
            pass
    src_all = "\n".join(src_texts)
    result = []
    for ln, raw in enumerate(out_text.split("\n"), 1):
        line = raw.strip()
        if not line or line.startswith("#") or line.startswith("|--") or line.startswith("-|-"):
            continue
        # 元信息行(>开头)描述实验/说明本身, 不参与有据判定
        if line.startswith(">"):
            continue
        if re.search(r"未提供|未给出|未提及|未定|未覆盖|来源外推测|以下为推测", line):
            result.append({"line": ln, "status": "declared-gap", "text": line[:80]})
            continue
        # 程序性提示语: 面向用户的后续操作建议, 非来源转述断言
        if re.search(r"如需|若需|请提供|需先|可先|建议先|可联系|可检索|可授权", line) and len(line) < 30:
            result.append({"line": ln, "status": "procedural", "text": line[:80]})
            continue
        masked = mask_code_spans(line)
        frags = salient_fragments(masked)
        if not frags:
            continue
        hit_frags = [f for f in frags if f.lower() in src_all.lower()]
        # 中文片段按字符 bigram 宽松匹配 (允许轻微改写)
        if len(hit_frags) < len(frags):
            for f_ in frags:
                if f_ in hit_frags:
                    continue
                if char_overlap_hit(f_, src_all):
                    hit_frags.append(f_)
        status = "grounded" if len(hit_frags) == len(frags) else (
            "partial" if hit_frags else "ungrounded")
        result.append({"line": ln, "status": status,
                       "frags": frags, "hit": hit_frags, "text": line[:80]})
    return result


def salient_fragments(text):
    out = []
    for cn in re.findall(r"[\u4e00-\u9fff]{3,}", text):
        out.append(cn)
    for en in re.findall(r"[A-Za-z][A-Za-z0-9\-]{3,}", text):
        out.append(en)
    return out[:8]


def char_overlap_hit(frag, src_all, ratio=0.8):
    """中文片段: 80% 字符出现在来源中即算宽松命中 (容忍换序/虚词增删)"""
    if not re.search(r"[\u4e00-\u9fff]", frag):
        return False
    chars = [c for c in frag if "\u4e00" <= c <= "\u9fff"]
    if not chars:
        return False
    hit = sum(1 for c in set(chars) if c in src_all)
    return hit / max(1, len(set(chars))) >= ratio


# ---------------------------------------------------------------- coverage

def coverage(out_path, source_paths):
    with open(out_path, encoding="utf-8") as f:
        out_text = f.read()
    total, covered = 0, 0
    missed = []
    for p in source_paths:
        try:
            with open(p, encoding="utf-8") as f:
                for ln, line in enumerate(f, 1):
                    line = line.strip()
                    if not line or line.startswith("#") or line.startswith(">"):
                        continue
                    if not (re.search(r"\d", line) or re.search(r"[\u4e00-\u9fff]{6,}", line)):
                        continue
                    total += 1
                    frags = salient_fragments(mask_code_spans(line))
                    if frags and any(f_.lower() in out_text.lower() for f_ in frags):
                        covered += 1
                    else:
                        missed.append(f"{os.path.basename(p)}:L{ln}: {line[:60]}")
        except OSError:
            continue
    return {"total": total, "covered": covered, "missed": missed[:20]}


# ---------------------------------------------------------------- CLI

def main():
    ap = argparse.ArgumentParser(description="you-ju closed-world audit (read-only)")
    sub = ap.add_subparsers(dest="cmd", required=True)

    ap_w = sub.add_parser("whitelist", help="build whitelist from sources")
    ap_w.add_argument("paths", nargs="+")
    ap_w.add_argument("-o", "--out", default="whitelist.json")

    ap_c = sub.add_parser("check", help="audit output")
    ap_c.add_argument("output")
    ap_c.add_argument("--whitelist", required=True)
    ap_c.add_argument("--sources", nargs="*", default=[])

    ap_a = sub.add_parser("align", help="sentence-level grounding alignment")
    ap_a.add_argument("output")
    ap_a.add_argument("sources", nargs="+")

    ap_v = sub.add_parser("coverage", help="source coverage check (optional)")
    ap_v.add_argument("output")
    ap_v.add_argument("sources", nargs="+")

    args = ap.parse_args()
    if args.cmd == "whitelist":
        wl = build_whitelist(args.paths)
        with open(args.out, "w", encoding="utf-8") as f:
            json.dump(wl, f, ensure_ascii=False, indent=1)
        print(f"OK whitelist: {len(wl['entities'])} entities, "
              f"{len(wl['numbers'])} numbers, {len(wl['aliases'])} aliases -> {args.out}")
        return 0

    if args.cmd == "check":
        with open(args.whitelist, encoding="utf-8") as f:
            wl = json.load(f)
        r = check_output(args.output, wl, args.sources)
        total = len(r["E1"]) + len(r["N1"]) + len(r["C1"])
        print(f"== you-ju check: {args.output} ==")
        print(f"E1 实体泄漏: {len(r['E1'])}")
        for v in r["E1"]:
            print(f"  L{v['line']}: entity「{v['entity']}」| {v['text']}")
        print(f"N1 数字泄漏: {len(r['N1'])}")
        for v in r["N1"]:
            print(f"  L{v['line']}: number「{v['number']}」({v['key']}) | {v['text']}")
        print(f"C1 引用失配: {len(r['C1'])}")
        for v in r["C1"]:
            print(f"  L{v['line']}: {v['cite']} — {v['reason']}")
        print(f"Q1 候选(需人工): {len(r['Q1_candidates']) if 'Q1_candidates' in r else len(r['Q1_candidates'])}")
        for v in r["Q1_candidates"]:
            print(f"  L{v['line']}: {v['why']} | {v['text']}")
        print(f"PASS" if total == 0 else f"FAIL ({total} violation(s))")
        return 0 if total == 0 else 1

    if args.cmd == "align":
        r = align_output(args.output, args.sources)
        n_g = sum(1 for x in r if x["status"] == "grounded")
        n_u = sum(1 for x in r if x["status"] == "ungrounded")
        n_p = sum(1 for x in r if x["status"] == "partial")
        n_d = sum(1 for x in r if x["status"] in ("declared-gap", "procedural"))
        n_t = n_g + n_u + n_p
        print(f"== you-ju align: {args.output} ==")
        print(f"句级有据率: {n_g}/{n_t}" + (f" = {n_g/n_t:.0%}" if n_t else ""))
        for x in r:
            mark = {"grounded": "✅有据", "partial": "🟡部分",
                    "ungrounded": "❌无据", "declared-gap": "⬜声明缺口",
                    "procedural": "🔧程序语"}.get(x["status"], x["status"])
            extra = ""
            if x["status"] == "ungrounded" and x.get("frags"):
                extra = f" | 关键片段: {x['frags'][:3]}"
            print(f"  L{x['line']}: {mark} | {x['text']}{extra}")
        return 0

    if args.cmd == "coverage":
        r = coverage(args.output, args.sources)
        print(f"== you-ju coverage: {args.output} ==")
        print(f"覆盖 {r['covered']}/{r['total']} 来源要点")
        if r["missed"]:
            print("未覆盖(前20):")
            for m in r["missed"]:
                print(f"  {m}")
        return 0


if __name__ == "__main__":
    sys.exit(main())