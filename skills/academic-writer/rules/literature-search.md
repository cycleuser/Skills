# Literature Search Protocol

## Iterative Search Strategy

Real literature search is not one query — it is iterative mining. You search broadly, read deeply, then search specifically based on what you learned.

### Phase 1: Broad Survey (1-2 hours)

Goal: Understand the landscape — key surveys, foundational papers, active directions.

```bash
# Semantic Scholar — best for overview + citation graph
curl -s "https://api.semanticscholar.org/graph/v1/paper/search?query=TOPIC&limit=20&fields=title,authors,year,abstract,citationCount,influentialCitationCount" | python3 -m json.tool

# arXiv — latest preprints, often before peer review
curl -s "http://export.arxiv.org/api/query?search_query=all:TOPIC&max_results=20&sortBy=submittedDate" | python3 -c "
import sys, xml.etree.ElementTree as ET
tree = ET.parse(sys.stdin)
ns = {'a': 'http://www.w3.org/2005/Atom'}
for entry in tree.findall('.//a:entry', ns):
    title = entry.find('a:title', ns).text.strip().replace('\n',' ')
    year = entry.find('a:published', ns).text[:4]
    print(f'{year} | {title}')
"

# Google Scholar (via webfetch tool)
# webfetch https://scholar.google.com/scholar?q=TOPIC
```

### Phase 2: Citation Mining (2-3 hours)

Goal: From 5-10 key papers, mine their references AND who cited them.

For each key paper:
1. Read abstract + introduction + related work + conclusion
2. Extract cited papers that appear in multiple key papers (these are must-cites)
3. Follow "cited by" forward citations (Semantic Scholar API)
4. Check recent citations (last 2 years) for latest baselines

```bash
# Forward citations from a paper
curl -s "https://api.semanticscholar.org/graph/v1/paper/PAPER_ID/citations?fields=title,authors,year,citationCount&limit=50"
```

### Phase 3: Targeted Search (1-2 hours)

Goal: Find specific baselines, datasets, and venue-specific references.

```bash
# Search for specific methods
curl -s "https://api.semanticscholar.org/graph/v1/paper/search?query=METHOD_NAME+TASK&limit=10&fields=title,year,venue"

# Search specific venue proceedings
# DBLP is best for venue-specific search
curl -s "https://dblp.org/search/publ/api?q=TOPIC+venue:AAAI&format=json&h=20"
```

### Phase 4: Must-Cite Verification

Before writing, check that your reference list includes:
- 2-3 papers from the target venue (last 2 years)
- Foundational papers that any reviewer would expect
- Papers from potential reviewers (if known)
- Baseline papers you compare against
- The paper that introduced each dataset you use

## Search Keywords Strategy

Do not search a single keyword. Expand systematically:

```
Start: "retrieval augmented generation"

Expansion:
1. Core synonyms: "RAG", "retrieval-augmented", "knowledge-augmented generation"
2. Components: "dense retrieval" + "generation", "retriever-reader"
3. Related tasks: "open-domain QA", "knowledge-grounded dialogue"  
4. Benchmarks: "NaturalQuestions", "HotpotQA", "MS MARCO"
5. Limitations: "hallucination" + "retrieval", "retrieval noise"
6. Alternatives: "parametric knowledge", "in-context learning"
```

## Literature Matrix

Build a structured matrix, not a flat reference list:

| ID | Paper | Year | Problem | Method | Key Result | Limitation | Your Use |
|----|-------|------|---------|--------|------------|------------|----------|
| R1 | Lewis et al. | 2020 | Open-domain QA | RAG (retriever+generator) | EM: 44.5 on NQ | Fixed retriever | Primary baseline |
| R2 | Izacard et al. | 2022 | Same | FiD (inter-doc attention) | EM: 51.4 on NQ | Memory-heavy | Architecture comparison |
| R3 | Gao et al. | 2024 | Same | Self-RAG (adaptive retrieval) | EM: 56.1 on NQ | Training cost | Related approach |

The "Limitation" column is critical — it is where your gap identification comes from.

## Paper Reading Protocol

For each paper, extract in order:
1. Abstract (1 min) — what is this about?
2. Contribution claim (30 sec) — what did they say they did?
3. Method figure (1 min) — how does it work?
4. Results table (1 min) — how well does it work?
5. Limitations section (30 sec) — where does it break?
6. Related work (2 min) — what else should I read?

Time budget: 5-6 minutes per paper for triage, 30-60 minutes for papers you will cite.

## Literature Organization

### By Relevance Level

```
references/
├── must_cite/       # 5-10 papers: foundational + baselines + target venue
├── related_work/    # 10-20 papers: related approaches
├── background/      # 5-10 papers: foundational concepts
└── optional/        # 5-10 papers: marginally related, cite if space allows
```

### By Argument Role

```
references/
├── gap_papers/      # Papers whose limitations define your gap
├── baseline_papers/ # Methods you compare against
├── foundation/       # Core techniques you build upon
└── context/         # Domain papers that establish importance
```

## Chinese Academic Sources

For Chinese CCF journal submissions:

```bash
# 知网 CNKI — primary Chinese academic database
# (requires subscription, typically via university)
# URL: cnki.net

# 万方数据 — alternative Chinese database
# URL: wanfangdata.com.cn

# 百度学术 — aggregated search, free
# URL: xueshu.baidu.com
```

CCF ranking reference for Chinese CS submissions:
- CCF-A journals: 计算机学报, 软件学报, 计算机研究与发展
- CCF-A conferences: (use international conferences like AAAI, NeurIPS)
- CCF-B journals: 计算机科学, 模式识别与人工智能

## Citation Tracking

### Forward Citation Chain

When you find a key paper from 2020:
1. Semantic Scholar: find papers citing it (2021-2024)
2. These papers likely improved upon it or identified its limitations
3. Read the 3 most-cited forward citations — they define the current state

### Backward Citation Chain

When you find a new 2024 paper:
1. Read its reference list carefully
2. Papers it cites heavily (3+ mentions) are likely foundational
3. Check if those foundational papers have newer/improved versions

## Search Log Template

Keep a log to avoid re-searching:

```markdown
# Literature Search Log

## Project: [title]

### Session: YYYY-MM-DD

**Round 1: Broad**
- Query: "TOPIC"
- Sources: Semantic Scholar, arXiv
- Results: 40 found, 8 relevant, 3 saved
- Key papers: [R1] Lewis et al. 2020, [R2] Izacard 2022

**Round 2: Citation Mining from [R1]**
- Forward citations: 12 relevant (2022-2024)
- Backward refs: 5 foundational
- New must-cites: [R3] Gao 2024

**Round 3: Targeted**
- Query: "self-adaptive retrieval generation"
- New baselines: [R4] Asai 2024

**Total**: 23 papers collected, 12 must-cite, 11 related work
```