# Opencode Paper Writing Experience

Practical lessons learned from using opencode to write academic papers. These are not theoretical guidelines — they are hard-won techniques from actual paper writing sessions.

## Workflow Patterns

### Session Planning

A paper is too large for a single session. Plan multiple sessions with clear boundaries:

```
Session 1: Structure (/paper structure)
  → Define argument, contribution, outline
  → Output: detailed outline with page allocations

Session 2: Literature review (/paper search)
  → Build literature matrix
  → Identify must-cite papers
  → Output: 20-40 papers organized in a matrix

Session 3: Abstract + Introduction
  → Write these together — they form the paper's spine
  → Use /paper review after drafting

Session 4-N: One section per session
  → Method, Experiments, Related Work, Conclusion
  → Always /paper review after each section

Session M: Integration review
  → Check cross-references, smooth transitions
  → Final /paper detect for AIGC markers
  → Format check against venue requirements
```

### Section-by-Section Strategy

**Introduction is written LAST or revised LAST.** You cannot write a compelling intro until you know exactly what the paper delivers. Draft a placeholder, write the body, then rewrite the intro to match what you actually achieved.

**Method section benefits most from iterative refinement.** Write it once, then revise with:
- Did I explain WHY each design choice was made?
- Can a reader implement this from my description?
- Are notation definitions before first use?

**Experiments section needs real data.** Never fabricate results. If you don't have results yet, write the experiment setup and leave placeholders:
```
TODO: Run experiment with config X on dataset Y
Placeholder: [Results to be filled after experiment]
```

## Opencode-Specific Techniques

### Managing Context Window

A full paper (8+ pages) will overflow most model context windows. Strategies:

1. **Section-focused sessions**: Only provide the current section + the outline for context. Don't paste the entire paper.

2. **Literature in a matrix**: Don't paste 20 full abstracts. Use the literature matrix format:
   ```
   | Paper | Method | Dataset | Result | Limitation | Why Cite |
   |-------|--------|---------|--------|------------|----------|
   | Smith 2024 | Transformer-X | GLUE | 94.2% | O(n²) | Baseline |
   ```
   This compresses 20 papers into ~40 lines instead of ~200.

3. **Outline as context anchor**: Always include the current outline when drafting a section. This keeps the paper coherent without needing the full text.

4. **Previous section summary**: Before drafting Section 4, summarize Section 3 in 3-5 sentences instead of pasting the full text.

### Figure Generation Pipeline

When generating figures with opencode:

```
Step 1: Describe the figure in natural language
  "Scatter plot of embedding dimension vs retrieval accuracy, 
   with points colored by dataset, using viridis colormap."

Step 2: Generate the plotting script
  → Use the paper_style.py template from figure-quality.md
  → Always output SVG first, then PDF for LaTeX
  → Include reproduce script as supplementary

Step 3: Verify quality
  → Check font sizes (≥ 7pt at column width)
  → Check line widths (≥ 0.5pt for data, ≥ 0.75pt for axes)
  → Check color accessibility in grayscale
  → View SVG in browser before including in paper

Step 4: Caption writing
  → Caption describes what is shown AND what the takeaway is
  → NOT "Results of our method" but "Retrieval accuracy increases 
     with embedding dimension for all datasets, with the largest 
     gains observed for Domain B (▲12.3%)."
```

### Citation Management

```
# Adding citations dynamically during writing:
# 1. First pass: use [AUTHOR_YEAR] placeholders
# 2. When literature matrix is ready: replace with [X] numbered citations
# 3. Use BibTeX format for final compilation

# Example placeholder → real citation flow:
# Draft: "Previous work [SMITH_2024] shows..."
# Final: "Previous work [3] shows..." where [3] = Smith et al., "Title", CVPR 2024

# NEVER generate fake BibTeX entries. Only cite papers you have actually read.
# If you need a citation you haven't read:
#   1. Use /paper search to find the real paper
#   2. Read the abstract + key figures
#   3. Then cite with specific page/section references
```

### Avoiding AIGC Detection in Opencode-Generated Text

Opencode's output is particularly susceptible to certain AIGC patterns because:

1. **Repetitive sentence structure**: The model tends to produce sentences of similar length and structure within a section.

2. **Meta-commentary**: Phrases like "It is important to note that" or "We emphasize that" appear more frequently.

3. **Balanced arguments**: AI text tends to present exactly two sides with equal weight, then "our approach bridges both."

4. **Over-qualification**: Academic AI text overuses hedging: "might," "could," "suggests," "potentially" — sometimes in the same sentence.

**Counter-strategies for opencode sessions:**

```bash
# After generating a section, apply these checks:

# 1. Sentence length variance (target std/mean > 0.4)
python -c "
import re, statistics
text = open('section.md').read()
sentences = re.split(r'[.!?]+', text)
sentences = [s.strip() for s in sentences if len(s.strip()) > 5]
lengths = [len(s.split()) for s in sentences]
ratio = statistics.stdev(lengths) / (statistics.mean(lengths) + 0.01)
print(f'Length variance ratio: {ratio:.2f} (target > 0.4)')
"

# 2. Banned phrase count (target: 0)
# Check for: "comprehensive", "novel", "state-of-the-art" without citation,
# "It is worth noting", "It should be noted", "In recent years"

# 3. Hedging density (target: < 3% of sentences)
# Count sentences with "may/might/could/potentially/suggests/seems"
```

## Common Failure Modes

### Failure: The "AI Smooth" Paper

Symptom: Every paragraph is well-structured, logically clear, and completely forgettable. Reviewers say "well-written but marginal contribution."

Root cause: AI defaults to explanation mode — it explains what IS rather than arguing what SHOULD BE.

Fix: Every section needs a thesis, not just a description. Method section: WHY each choice, not just WHAT. Experiments: what SURPRISED you, not just what worked. Related work: WHERE each approach hits its boundary, not just what it does.

### Failure: The Citation-Free Zone

Symptom: Long paragraphs with no citations. Reviewers flag "unsupported claims."

Root cause: Opencode generates fluent text that sounds authoritative, making uncited claims feel natural.

Fix: After drafting, scan for any paragraph > 4 sentences without a citation. Every factual claim needs evidence. Rule: if you can add [X] after a sentence, you should.

### Failure: The "We Acknowledge But Don't Address" Limitations Section

Symptom: Limitations section lists things with "we leave this for future work."

Root cause: AI default is to politely acknowledge without confronting.

Fix: For each limitation, either (a) add an experiment that partially addresses it, or (b) explain specifically WHY it is hard and what the theoretical barrier is. "Future work" is acceptable only when the barrier is genuinely external.

### Failure: Perfect Diagrams, Terrible Caption

Symptom: Beautiful SVG figures with "Figure 3: Results" as caption.

Root cause: Opencode treats figure captions as afterthoughts.

Fix: Write captions FIRST, before generating the figure. A caption must state: (1) what is shown, (2) the key takeaway, (3) any non-obvious encoding (color = X, size = Y).

## Revision Request Checklist

Before submitting a revision:

- [ ] Every reviewer comment has a numbered response (R1.1, R1.2, R2.1...)
- [ ] Revised text is quoted in the response letter with line numbers
- [ ] New experiments/figures address the specific concern raised
- [ ] No reviewer comment is dismissed without evidence
- [ ] Response letter is professional, grateful, and specific
- [ ] PDF compiles cleanly with no undefined references
- [ ] All figures meet figure-quality.md standards
- [ ] AIGC detection patterns have been checked (see anti-ai-patterns.md)
- [ ] Co-author approval obtained for all changes