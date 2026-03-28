---
name: academic-writer
version: "1.0.0"
description: |
  Academic paper writing assistant for top-tier conferences (AAAI, IJCAI, IEEE).

  Triggers when: Writing academic papers or articles, needing literature search and citation formatting, preparing manuscripts for conference submission, or creating paper structure and organization.

  Commands:
  - /paper new <topic> - Start new paper with topic
  - /paper search <keywords> - Search and collect literature
  - /paper cite - Format citations properly
  - /paper structure - Generate paper outline
  - /paper review - Review and polish text

  Capabilities: Literature search from Google Scholar, arXiv, DBLP, standard citation formatting (IEEE, ACM, APA), paper structure generation for AAAI/IJCAI format, natural academic writing without AI markers, and mathematical notation and figure descriptions.
author: system
license: MIT
---

# Academic Writer

Professional academic paper writing assistant for top-tier conference submissions.

## Quick Commands

Five commands support the academic writing workflow. The `/paper new <topic>` command starts a new paper with topic analysis. The `/paper search <keywords>` command searches and collects relevant literature. The `/paper cite` command formats citations in standard format. The `/paper structure` command generates a paper outline. The `/paper review` command reviews and polishes the paper for submission.

## Paper Structure Templates

### IEEE Conference Format

```
Title

Abstract (150-200 words)
Keywords (3-5 terms)

I. INTRODUCTION
   - Background and motivation
   - Problem statement
   - Contributions summary

II. RELATED WORK
   - Literature review
   - Gap identification

III. METHODOLOGY / APPROACH
   A. Problem Formulation
   B. Algorithm/Model Design
   C. Theoretical Analysis

IV. EXPERIMENTS
   A. Experimental Setup
   B. Datasets
   C. Baselines
   D. Results and Analysis
   E. Ablation Studies

V. CONCLUSION

REFERENCES
```

### AAAI/IJCAI Format

```
Title

Abstract
Keywords

1 Introduction

2 Related Work

3 Preliminaries
   3.1 Problem Definition
   3.2 Notations

4 Method
   4.1 Overview
   4.2 Component Details
   4.3 Algorithm

5 Experiments
   5.1 Setup
   5.2 Main Results
   5.3 Analysis

6 Conclusion

References
```

### Chinese Article Format

```
标题

摘要
关键词

一、引言

二、相关工作

三、方法设计
   （一）问题定义
   （二）技术方案
   （三）算法流程

四、实验验证
   （一）实验设置
   （二）结果分析
   （三）对比讨论

五、结论

参考文献
```

## Writing Guidelines

### Language Style

**DO:**
- Use formal academic language
- Write complete sentences with proper transitions
- Use passive voice where appropriate
- Include specific technical terms with definitions
- Provide numerical evidence for claims

**DO NOT:**
- Use emoji or decorative symbols
- Use colon-separated headings (e.g., "Architecture: The system uses...")
- Write fragmented bullet points as paragraphs
- Use informal expressions
- Overuse adjectives like "novel", "state-of-the-art"

### Section Writing Patterns

#### Introduction Pattern

```
[Context] In recent years, [domain] has attracted significant attention 
due to [reason].

[Problem] However, existing approaches suffer from [limitation], which 
hinders their application in [scenario].

[Solution] To address this challenge, we propose [method name], a 
[brief description of the approach].

[Contribution] The main contributions of this paper are as follows:
(1) We propose...
(2) We design...
(3) We conduct extensive experiments...
```

#### Method Section Pattern

```
[Overview] Figure X illustrates the overall architecture of [method].

[Component 1] Given input X, we first compute Y through Z process.
Formally, let f denote the mapping function:
    [mathematical formulation]

[Component 2] Building upon the intermediate representation, we then...

[Algorithm] Algorithm 1 presents the detailed procedure.
```

#### Experiments Pattern

```
[Setup] We evaluate [method] on [dataset] benchmark.

[Baseline] We compare against the following methods: [list].

[Main Results] Table X shows the comparison results. Our method 
achieves [metric] improvement over the strongest baseline.

[Analysis] To understand the contribution of each component, we conduct 
ablation studies on [aspect].
```

### Mathematical Notation

Use standard LaTeX notation:

```
Inline: Let $f: \mathcal{X} \to \mathcal{Y}$ be the mapping function.

Display:
$$
\mathcal{L} = \sum_{i=1}^{N} \ell(y_i, \hat{y}_i) + \lambda \|\theta\|_2^2
$$

Algorithm:
\begin{algorithm}
\caption{Algorithm Name}
\begin{algorithmic}
\STATE Input: data $\mathcal{D}$
\STATE Output: result $R$
\STATE 1: Initialize parameters
\STATE 2: for iteration $t = 1$ to $T$ do
\STATE 3:   Update $\theta$ using gradient descent
\STATE 4: end for
\end{algorithmic}
\end{algorithm}
```

## Citation Formatting

### IEEE Style

```
[1] A. Author and B. Author, "Title of the paper," in Proc. Conf. Name, 
    Year, pp. 1-10.

[2] C. Author, D. Author, and E. Author, "Paper title," Journal Name, 
    vol. X, no. Y, pp. 1-20, Year.
```

### ACM Style

```
[1] Author, A. and Author, B. 2024. Paper title. In Proceedings of 
    Conference Name (Conference '24). ACM, New York, NY, USA, 1-10.
```

### APA Style

```
Author, A. A., & Author, B. B. (2024). Title of the paper. Journal Name, 
Volume(Issue), page-range.
```

## Literature Search

### Search Sources

Six search sources provide literature for academic writing. Google Scholar at scholar.google.com is best for general academic papers. arXiv at arxiv.org is best for preprints and CS/AI papers. DBLP at dblp.org provides computer science bibliography. Semantic Scholar at semanticscholar.org offers AI-powered paper discovery. ACM DL at dl.acm.org covers computing literature. IEEE Xplore at ieeexplore.ieee.org provides engineering papers.

### Search Keywords Template

```
Primary: [main topic]
Secondary: [specific aspect], [method name], [application domain]
Alternative: [related concepts], [synonyms]
```

### Literature Organization

For each collected paper:

```markdown
## [Author et al., Year] - Title

**Venue**: Conference/Journal (Year)

**Key Contribution**: One sentence summary

**Method**: Brief description of approach

**Results**: Main findings

**Relevance**: How it relates to your work

**Citation**: [X] A. Author et al., "Title," Venue, Year.
```

## Figure and Table Guidelines

### Figure Caption Format

```
Fig. 1. Description of the figure content. The x-axis represents...
and the y-axis shows...

Fig. 2. Architecture of the proposed method. The system consists of
three main components: encoder, processor, and decoder.
```

### Table Format

```
TABLE I
COMPARISON WITH STATE-OF-THE-ART METHODS

| Method | Accuracy | F1-Score | Time (ms) |
|--------|----------|----------|-----------|
| Baseline A | 85.2 | 0.83 | 120 |
| Baseline B | 87.1 | 0.85 | 150 |
| Ours | 91.3 | 0.90 | 100 |
```

## Review Checklist

### Before Submission

- [ ] Abstract within word limit (150-200)
- [ ] Keywords 3-5 terms
- [ ] All figures have captions
- [ ] All tables have titles
- [ ] All citations are formatted consistently
- [ ] No undefined references
- [ ] Mathematical notation is consistent
- [ ] No grammatical errors
- [ ] Page limit is respected

### Quality Check

- [ ] Contribution is clearly stated
- [ ] Experiments are reproducible
- [ ] Baselines are fair comparisons
- [ ] Results are statistically significant
- [ ] Limitations are discussed

## Rules

- [rules/literature-search.md](rules/literature-search.md) - Literature search protocol
- [rules/citation-format.md](rules/citation-format.md) - Citation formatting rules
- [rules/paper-structure.md](rules/paper-structure.md) - Paper structure templates
- [rules/writing-style.md](rules/writing-style.md) - Academic writing guidelines