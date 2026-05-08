# Reviewer Response Letter Guide

A response letter (rebuttal) is often more important than the paper revision itself. It determines whether reviewers accept your changes or dig in.

## Core Principles

1. **Every comment gets a response** — even "thank you for catching this."
2. **Be grateful, not defensive** — reviewers spent hours on your paper for free.
3. **Be specific** — "We revised Section 3.2, line 45" not "We improved the paper."
4. **Show, don't tell** — Quote the revised text, highlight the change.
5. **Honesty over spin** — If you couldn't address something, say why and what you did instead.

## Response Letter Structure

```
Dear Reviewers,

We thank all reviewers for their constructive feedback. We have carefully 
addressed each concern and believe the paper is significantly improved.

[Summary of major changes — 3-5 sentences max]

Below we respond to each comment point by point.

---

## Reviewer 1

**R1.1: [Quote reviewer's exact comment]**

[Your response]

**[After response]** We revised Line X in Section Y to read:
> "[Exact revised text]"

---

## Reviewer 2

**R2.1: [Quote]**

[Your response]
...
```

## Response Strategies by Comment Type

### Comments You Agree With

```
Pattern: Acknowledge → Revise → Quote revision → Quantify improvement

Example:
"We agree this was unclear. We have revised the formulation and added 
an intuitive explanation (Section 3.2). The revised text reads:

> 'Given a graph G = (V, E), we define the influence score I(v) as 
> the expected number of reachable nodes in t steps, where t follows 
> a geometric distribution with parameter p.'

We also conducted an ablation (Table 3, row 5) showing the revised 
formulation improves recall by 3.2%."
```

### Comments You Partially Agree With

```
Pattern: Acknowledge valid part → Explain constraint → Propose alternative

Example:
"We agree that evaluating on dataset D would strengthen the paper. 
However, D requires proprietary licenses that our institution cannot 
obtain within the revision period. Instead, we added experiments on 
dataset E (similar domain, public access), which shows consistent 
trends with our original results (Table 4). We note this limitation 
in Section 5.3."

Key: The reviewer sees you took it seriously, not that you dismissed it.
```

### Comments You Disagree With

```
Pattern: Respect the concern → Provide evidence → Offer minor concession

Example:
"We appreciate the reviewer's perspective on computational cost. 
However, our method's per-sample inference time (2.3ms on a single 
GPU, Table 5) is comparable to baseline methods (1.8ms for Model A, 
3.1ms for Model B). This is because our attention mechanism computes 
O(n) operations rather than the O(n²) assumed by the reviewer. We 
have clarified this in Section 4.3 and added a computational cost 
analysis table (Table 5)."

Key: Never say "the reviewer is wrong." Instead, show the evidence and 
let the reviewer reach that conclusion themselves.
```

### Ambiguous or Unclear Comments

```
Pattern: State your interpretation → Address that interpretation → 
         Invite clarification if wrong

Example:
"We interpret this comment as asking about the convergence guarantee 
of Algorithm 1. If our understanding is correct: yes, Algorithm 1 
converges because the loss function is Lipschitz continuous 
(Theorem 2, proof in Appendix A). We have added this clarification 
to Section 4.1. If the reviewer intended a different concern, we 
are happy to address it further."
```

### Dangerous Comments (Reviewer Misunderstood)

```
Pattern: Politely correct → Provide page/line reference → 
         Add clarification so others don't make same error

Example:
"We believe there may be a misunderstanding. The reviewer states 
that 'the method requires O(n³) time,' but our method uses a 
sparse attention mechanism that reduces this to O(n log n) 
(Section 3.3, Theorem 1). We have added a computational complexity 
analysis (Table 5) to make this clearer for all readers."
```

## Formatting Rules

1. **Color-code changes**: Purple/blue for reviewer comments, red for your changes in the paper.

2. **Quote exact text**: Always quote the specific text you changed, don't just say "we revised."

3. **Reference line/column numbers**: "Line 234 in the introduction" not "somewhere in the intro."

4. **Number every response**: R1.1, R1.2, R2.1, etc. Never leave a comment unnumbered.

5. **Separate major and minor responses**: Major concerns get full paragraphs. Minor concerns ("typo on line 5") can be grouped.

## Opencode-Specific Workflow

When using opencode to draft response letters:

1. **Paste reviewer comments** as structured input with reviewer IDs and comment numbers.

2. **Link to paper sections**: Reference exact sections, line numbers, and figure/table numbers.

3. **Generate SVG/PDF comparison figures** when showing revised results (use figure-quality.md standards).

4. **Track changes**: Use diff-style formatting to show what changed:
   ```
   OLD: "Our method achieves 95.3% accuracy."
   NEW: "Our method achieves 95.3% accuracy on Dataset A and 93.1% on Dataset B, 
         compared to baseline's 91.7% (Table 3)."
   ```

5. **Compile response** as Markdown first, then convert to PDF with proper formatting for submission.

## Phrases to Avoid

| Avoid | Use Instead |
|-------|-------------|
| "We disagree" | "We appreciate the concern, however..." |
| "The reviewer is wrong" | "We believe there may be a misunderstanding..." |
| "This is outside scope" | "While important, this falls beyond our current scope. We have added it as future work." |
| "We already said this" | "We have clarified this point in Section X to make it more explicit." |
| "This is obvious" | "We have added a brief explanation for readers less familiar with this concept." |
| "We don't have space" | "Due to space constraints, we have moved this analysis to Appendix X." |

## Time Budget

A response letter should receive 30-40% of the total revision effort:
- Reading comments carefully: 10%
- Planning responses: 10%
- Drafting responses: 15%
- Revising the paper itself: 50%
- Proofreading both: 15%