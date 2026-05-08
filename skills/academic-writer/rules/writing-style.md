# Academic Writing Style Guidelines

## Natural Academic Voice

The goal is not "formal" writing — it is "researcher thinking on paper." Formality emerges from precision, not from stiffness.

### What Natural Academic Voice Sounds Like

```
A researcher explains their work to a colleague who works in a different 
subfield. Not overly casual, not overly stiff. Precise where precision 
matters, informal where formality adds nothing.
```

### Key Properties

1. Precision over verbosity: Every word earns its place. If deleting a word does not change the meaning, delete it.

2. Concrete over abstract: "5.2% improvement on SQuAD" beats "significant improvement."

3. Reasoning visible: Show why, not just what. The reader should be able to follow your thinking, not just your conclusion.

4. Honest hedging: When results are inconclusive, say so. "suggests" is not weakness — it is accuracy.

5. Active voice for methods: "We optimize" not "Optimization is performed."

6. Passive voice for established facts: "It is known that" not "We know that."

## Sentence Construction

### Sentence Length Variation

Critical for avoiding AI detection AND readability. Target:
- Short sentences (5-10 words): for observations, emphasis, transitions
- Medium sentences (15-25 words): for explanations, evidence
- Long sentences (30-45 words): for complex technical descriptions

Example mixing:
```
Standard cross-attention computes similarity across all token pairs. 
This is O(N²) and dominates memory usage for long sequences. To address 
this bottleneck, we factorize the attention computation into a local 
window component that processes adjacent tokens at O(Nk) cost and a global 
component that uses a fixed number of learned tokens to capture document-
level structure, resulting in overall O(N(k+g)) complexity where g is the 
number of global tokens.
```

### Hedging Language

Use hedging when appropriate — this is a sign of intellectual honesty, not weakness.

Appropriate hedging:
```
"Our results suggest that..." (when n=1 or limited datasets)
"This indicates..." (when causation is not proven)
"We hypothesize that..." (when proposing an explanation)
"It appears that..." (when observing a trend)
"Under these conditions, the method tends to..." (when results vary)
```

Inappropriate hedging:
```
"This may possibly potentially suggest that perhaps..." (stacking hedging is AI behavior)
"The method seems to perform somewhat reasonably..." (when you have clear numbers)
```

### Definite Claims

When you have evidence, be definite:
```
"Table 3 shows a 5.2% improvement." (not "approximately 5%")
"On the SQuAD dev set, F1 drops from 88.5 to 71.3." (not "significant degradation")
"Ablation confirms that removing the retrieval module reduces accuracy by 12.1%." 
```

## Paragraph Construction

### Not Every Paragraph Needs a Topic Sentence

AI writing advice insists on topic sentences for every paragraph. Real academic writing varies:

Pattern 1 — Topic-first (for introducing concepts):
```
The key challenge in cross-lingual transfer is the vocabulary gap. When 
the source and target languages share fewer than 20% of subword tokens, 
shared embeddings provide weak signal [1]. We address this by...
```

Pattern 2 — Evidence-first (for results):
```
On HotpotQA, our method achieves F1=71.3 compared to 65.8 for the 
strongest baseline [3]. This 5.5-point gap is larger than on SQuAD 
(where we gain only 0.3 points), suggesting that multi-hop reasoning 
benefits more from retrieval augmentation.
```

Pattern 3 — Question-first (for analysis):
```
Why does the global token count matter so little beyond g=8? Figure 4 
hints at the answer: with 8 global tokens, attention coverage already 
reaches 94% of the document. Additional tokens provide diminishing returns 
because they attend to overlapping content.
```

### Paragraph Length Varies

- 1-2 sentences: transitions, key observations, linking ideas
- 3-5 sentences: most paragraphs (normal length)
- 6-10 sentences: detailed technical explanations, thorough analysis
- Never force all paragraphs to similar length

## Section-Specific Styles

### Introduction

The introduction tells a story: why this problem matters, why it is not solved, what you did, what you found.

Opening: Start with the concrete problem, not the field's importance.

```
Bad: "Natural language processing is an important research area."
Good: "Extracting accurate answers from long documents (over 10K tokens) 
      remains challenging: even specialized models lose 15% accuracy when 
      document length exceeds their context window [1, 2]."
```

Contributions: Be concrete and falsifiable.

```
Bad: "We make comprehensive contributions to the field of X."
Good: "(1) We release LongDocQA, a benchmark of 2,400 question-answer pairs 
      over documents averaging 32K tokens. (2) We propose windowed 
      retrieval-augmented generation, which improves accuracy from 71% to 
      83% on LongDocQA. (3) We show that current models fail primarily on 
      questions requiring cross-section reasoning (Section 5.3)."
```

### Method

Write method sections as design decisions with rationale, not as feature descriptions.

```
Bad: "We use a transformer encoder with 12 layers and 768 hidden dimensions."
Good: "We need a model that handles sequences up to 4K tokens. Standard 
      BERT supports only 512 tokens [1]; Longformer extends to 4K by 
      replacing full attention with local windows [2]. We adopt Longformer's 
      architecture but add task-specific adapters (Section 3.2) to reduce 
      fine-tuning cost from 1.2GB to 14MB of trainable parameters."
```

Interleave intuition and formal definition:

```
"Intuitively, sparse attention selects which tokens to attend to rather 
than attending to everything. Formally, given input X ∈ ℝ^{n×d}, we 
compute a binary mask M ∈ {0,1}^{n×n} where M_{ij} = 1 if token i should 
attend to token j. The attention then becomes:
    A = softmax((XW_Q)(XW_K)^T ⊙ M / √d) (XW_V)
where ⊙ denotes element-wise multiplication."
```

### Experiments

Report with honesty and detail:

```
Good practices:
- Report mean and standard deviation across 3-5 runs
- Include p-values or confidence intervals for main claims  
- Show failure cases (Table 4, "Error Analysis")
- Compare fairly: same data, same tuning protocol, same hardware
- State training time and computational cost
- Discuss when and why the method does NOT work
```

### Related Work

Organize by ideas, not by papers. Each paragraph should have a thesis about the category:

```
Bad: "[1] proposed X. [2] proposed Y. [3] proposed Z."
Good: "Retrieval-based methods [1, 2] achieve high precision by grounding 
      answers in evidence, but require domain-specific indexes. Generation-
      based methods [3, 4, 5] are more flexible but cannot verify factual 
      accuracy. Recent work combines both [6, 7], though verification remains 
      the bottleneck (we address this in Section 3.3)."
```

### Conclusion

Brief and honest. No padded future work lists.

```
Good structure:
1. What we did (2-3 sentences matching contributions)
2. Key finding (1 sentence)
3. Limitation (1-2 sentences, specific)
4. One concrete next step (optional, must be specific)
```

## Language Precision

### Numbers

```
Always: "95.3% accuracy" not "about 95%"  
Always: "768-dimensional embeddings" not "high-dimensional embeddings"
Always: "12-layer transformer" not "deep transformer"
Always: "training took 4.2 hours on 8×A100" not "extensive training"
```

### Comparisons

```
Be specific about the comparison:
"outperforms BERT-base by 5.2 F1 on SQuAD" ✓
"outperforms BERT-base" ✗ (by how much?)
"achieves competitive results" ✓ (only when the difference is not significant)
"significantly outperforms" ✓ (only with p < 0.05)
```

### Technical Terms

Define on first use, then use consistently:
```
"We use sparse attention (where each token attends to at most k other 
tokens) throughout the encoder. Unless noted, k=256."
```

## Chinese Academic Style

中文论文的写作风格需要注意：

### 用词规范

- 使用"本文"代替"我们"（部分期刊要求）
- 数学符号首次出现时用中文解释
- 图表标题用中文，英文可附于括号内
- 参考文献中英文混排按GB/T 7714-2015

### 避免的中式AI痕迹

```
禁忌：
- "对...进行了深入的研究" → "研究了..."
- "起到了积极的作用" → "提高了X%，详见Y表"
- "具有重要的理论意义和实践价值" → 删除，或说出具体是什么意义
- "得到了广泛的关注" → "被引用N次"或"在X、Y、Z等领域应用"
- "取得了良好的效果" → "准确率达到X%"
```

## Revision Protocol

After completing a draft, apply this order:

1. Logic check: Does each section's argument flow without gaps?
2. Evidence check: Does every claim have a number, citation, or experiment?
3. AI pattern check: Scan for banned patterns in anti-ai-patterns.md
4. Precision pass: Replace vague words with specific ones
5. Length pass: Cut any sentence that survives deletion
6. Format check: Against target venue requirements