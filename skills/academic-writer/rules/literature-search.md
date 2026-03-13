# Literature Search Protocol

## Search Strategy

### Step 1: Keyword Expansion

Before searching, expand your keywords:

```python
def expand_keywords(primary_topic: str) -> dict:
    """Generate comprehensive search keywords."""
    return {
        "primary": [primary_topic],
        "synonyms": get_synonyms(primary_topic),
        "related_methods": get_related_methods(primary_topic),
        "applications": get_applications(primary_topic),
        "variations": get_variations(primary_topic),
    }
```

### Step 2: Multi-Source Search

Execute parallel searches across multiple databases:

| Database | Search Query Example | Priority |
|----------|---------------------|----------|
| Google Scholar | `"exact phrase" AND keyword` | High |
| arXiv | `cat:cs.AI AND keyword` | High |
| DBLP | `title:keyword OR abstract:keyword` | Medium |
| Semantic Scholar | `keyword + field:Computer Science` | High |

### Step 3: Filter and Rank

Filter results by:

1. **Relevance** - Match with research question
2. **Recency** - Prefer papers from last 5 years
3. **Venue** - Prioritize top-tier venues
4. **Citations** - Highly cited papers (but check recency)

## Search Templates

### For Method Papers

```
"[method name]" OR "[method abbreviation]"
"[core technique]" AND "[domain]"
"[problem]" AND "[solution approach]"
```

### For Survey Papers

```
"[domain]" AND ("survey" OR "review" OR "tutorial")
"[topic]" AND ("recent advances" OR "comprehensive review")
```

### For Comparative Studies

```
"[task]" AND ("benchmark" OR "comparison" OR "evaluation")
"[method A]" vs "[method B]" comparison
```

## Paper Collection Template

For each relevant paper found:

```markdown
## [ID] Author et al. (Year) - Short Title

### Metadata
- **Full Title**: [complete title]
- **Authors**: [author list]
- **Venue**: [conference/journal name, year]
- **URL**: [link to paper]
- **DOI**: [if available]
- **arXiv**: [if preprint]

### Summary
- **Problem**: What problem does it solve?
- **Method**: What is the proposed approach?
- **Results**: What are the main findings?
- **Contribution**: What is novel?

### Relevance
- **Why relevant**: Connection to your work
- **Cite as**: [X] for what specific claim
- **Comparison point**: How does it compare to your method?

### Notes
- Key equations or algorithms
- Datasets used
- Limitations mentioned
```

## Organizing Literature

### By Theme

```
literature/
├── surveys/
│   ├── survey_001.md
│   └── survey_002.md
├── methods/
│   ├── method_001.md
│   └── method_002.md
├── applications/
│   ├── app_001.md
│   └── app_002.md
└── baselines/
    ├── baseline_001.md
    └── baseline_002.md
```

### By Relation

```
references/
├── must_cite/           # Essential papers
├── related_work/        # Related but not core
├── baselines/           # Methods to compare against
└── background/          # Foundational papers
```

## Citation Extraction

### From Paper Text

```python
def extract_citations(paper_text: str) -> list:
    """Extract citations from paper text."""
    patterns = [
        r'\[(\d+)\]',                          # [1]
        r'\((\w+,\s*\d{4}[a-z]?)\)',           # (Author, 2024)
        r'(\w+)\s+et\s+al\.\s*\((\d{4})\)',    # Author et al. (2024)
    ]
    return find_all_matches(paper_text, patterns)
```

### Building Reference List

```python
def build_reference(citation_info: dict, style: str = "ieee") -> str:
    """Build formatted reference string."""
    if style == "ieee":
        return f"[{citation_info['id']}] {citation_info['authors']}, " \
               f"\"{citation_info['title']},\" {citation_info['venue']}, " \
               f"{citation_info['year']}, pp. {citation_info['pages']}."
    elif style == "acm":
        return f"{citation_info['authors']}. {citation_info['year']}. " \
               f"{citation_info['title']}. In {citation_info['venue']}. " \
               f"ACM, {citation_info['pages']}."
```

## Literature Matrix

Create a comparison matrix for related work:

| Paper | Year | Problem | Method | Dataset | Metric | Strength | Limitation |
|-------|------|---------|--------|---------|--------|----------|------------|
| [1] | 2024 | X | A | D1 | M1 | S1 | L1 |
| [2] | 2023 | Y | B | D2 | M2 | S2 | L2 |

## Quality Assessment

### Conference Ranking (CS)

| Tier | Examples |
|------|----------|
| A* | AAAI, IJCAI, NeurIPS, ICML, CVPR, ACL |
| A | ICDM, CIKM, ECML, COLING |
| B | Others with reasonable reputation |

### Journal Ranking

| Tier | Examples |
|------|----------|
| CCF-A | TPAMI, TKDE, TOIS |
| CCF-B | TNNLS, TMM, IPM |
| SCI | Various indexed journals |

## Citation Tracking

### Forward Citations

Find papers that cite a key paper:

1. Google Scholar: "Cited by" link
2. Semantic Scholar: "Citations" section
3. Web of Science: Citation report

### Backward Citations

Follow references in a paper to find foundational work.

## Search Log Template

```markdown
# Literature Search Log

## Date: YYYY-MM-DD

### Search 1: [Keywords]
- **Database**: Google Scholar
- **Query**: "keyword1" AND "keyword2"
- **Results**: 150
- **Relevant**: 12
- **Saved**: [paper IDs]

### Search 2: [Keywords]
- **Database**: arXiv
- **Query**: cat:cs.AI AND keyword
- **Results**: 45
- **Relevant**: 8
- **Saved**: [paper IDs]

### Summary
- Total papers found: X
- Total relevant: Y
- Key papers identified: [list]
```