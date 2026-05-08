# Anti-AI-Patterns for Academic Text

Academic papers face the highest AIGC scrutiny: Turnitin, GPTZero, conference reviewer heuristics, and journal editorial checks. Academic text has a unique challenge — it is formal and structured by nature, which overlaps with some AI patterns. The key is to preserve formality while adding the intellectual texture that AI smooths away.

## Core Principle

AI text is statistically predictable. Real academic text shows: intellectual struggle in reasoning, hedging at uncertainty boundaries, specific implementation details, and natural sentence-level variation. The goal is not to "fool" detectors — it is to write like a researcher who actually did the work.

## Critical Detection Vectors for Academic Text

### 1. Structural Symmetry (Weight: 30%)

AI papers have suspiciously balanced sections. Real papers have heavy methodology and experiments, lighter related work and conclusion.

Detection signals:
- Paragraph lengths within a section have low variance
- Each subsection is similar length (AI loves symmetry)
- Related work reviews exactly 3 papers per paragraph

Counter-measures:
- Vary paragraph length: 2-sentence observations next to 15-sentence technical explanations
- Make some subsections deliberately short when the point is simple
- Give more space to what matters more (usually your method and key results)

### 2. Transition Patterns (Weight: 25%)

AI uses the same transitions everywhere. Real researchers vary based on the logical relationship.

High-risk transitions (avoid or limit to 1x per paper):
```
中文：首先...其次...再次...最后...
中文：一方面...另一方面...
中文：综上所述...

English: Firstly, Secondly, Thirdly
English: On the one hand, On the other hand
English: It is worth noting that / It should be noted that
```

Natural academic transitions:
```
Causal: Since X holds, we can ...
Contrast: Unlike X which assumes Y, our approach ...
Build: Extending the framework of [1], we add ...
Concession: While X achieves Y, it does not address Z.
Detail: Concretely, ...
Evidence: As Table 2 shows, ...
Reference: Following [3], we define ...
```

### 3. Vacuous Modifiers (Weight: 20%)

AI inflates. Real researchers are precise.

Banned (0 occurrences):
- "comprehensive" (unless literally everything is covered)
- "novel" (unless truly no prior work exists — cite to prove it)
- "state-of-the-art" (unless #1 on the leaderboard — cite the benchmark)
- "significant" without a p-value or confidence interval
- "widely used" without citation count or deployment evidence
- "recent years" — use the actual year range: "2020-2024"
- "extensive experiments" — say how many: "12 ablation configurations across 4 datasets"

Replacement strategy:
```
Instead of "novel", write: "To our knowledge, no prior work has addressed X in the context of Y."
Instead of "significant improvement", write: "5.2% improvement over [baseline] (p < 0.01)"
Instead of "extensive experiments", write: "experiments on 3 benchmarks with 4 ablation settings"
Instead of "widely adopted", write: "used in [1], [2], [3] for task X"
```

### 4. Formulaic Openings (Weight: 15%)

The "In recent years, X has attracted significant attention" opening is the single most AI-detected pattern in academic papers.

Banned openings:
```
"In recent years, [domain] has attracted significant attention..."
"With the rapid development of [technology]..."
"[Domain] plays an important role in [field]..."
"In the era of [buzzword]..."
"As [technology] continues to evolve..."
"近年 来，[领域] 受到了广泛关注..."
"随着[技术]的快速发展..."
```

Natural openings (start with the actual problem):
```
"Deploying language models on edge devices requires models under 500MB, 
yet current quantization methods degrade accuracy below 90% for models 
smaller than 200MB [1, 2]."

"When the training distribution differs from the test distribution — as 
in medical imaging where scanner types vary across hospitals [3] — standard 
empirical risk minimization fails (accuracy drops from 94% to 71% in our 
experiments)."

"知识库检索的维度不匹配问题在实际部署中频繁出现：当 embedding 模型从 
1024 维切换到 768 维时，现有的 155 个文档集合全部无法检索，但没有
工具能在索引前检测或索引后自适应这一问题。"
```

### 5. Reasoning Depth (Weight: 10%)

AI states conclusions. Researchers show work.

AI pattern:
```
"We propose an attention mechanism that captures long-range dependencies.
Our method outperforms baselines by 3.2%."
```

Researcher pattern:
```
"Standard self-attention computes all N² token pairs, which is unnecessary 
when most pairs are irrelevant (Section 4.2 shows only 12% of attention 
weights exceed 0.01 on Longformer-style documents). We therefore restrict 
attention to local windows of size k, with learned global tokens bridging 
windows. This captures local structure exactly while approximating global 
dependencies, at O(Nk) cost. Table 3 confirms that k=256 recovers 97% of 
full-attention accuracy on documents up to 4K tokens."
```

## Academic-Specific Counter-Patterns

### For Method Sections

AI writes method sections as a feature list. Researchers write them as design decisions.

AI:
```
Our method consists of three modules: encoder, aggregator, and decoder.
The encoder extracts features. The aggregator combines them. The decoder 
generates output.
```

Researcher:
```
We need to map variable-length input sequences to fixed-size representations. 
A natural choice is recurrent encoding [1], but this processes tokens 
sequentially and cannot leverage GPU parallelism. We therefore use a 
transformer encoder (Section 3.2), which processes all positions in parallel 
at the cost of O(N²) attention computation. For our task, input sequences 
average 128 tokens (Table 1), making this cost acceptable.
```

### For Experiments

AI presents experiments as a victory lap. Researchers present them as an investigation.

AI:
```
We conduct extensive experiments. Our method achieves the best results on 
all datasets, demonstrating its effectiveness.
```

Researcher:
```
We evaluate on three benchmarks of increasing difficulty: SQuAD (single-span, 
short answers), HotpotQA (multi-hop, requires reasoning across documents), 
and our newly collected MedQA (domain-specific, requiring expert knowledge). 
Table 2 shows that our method matches the state of the art on SQuAD (F1: 
88.2 vs. 88.5 [3]) but substantially improves on HotpotQA (F1: 71.3 vs. 
65.8) and MedQA (EM: 54.1 vs. 42.7). The larger gaps on harder benchmarks 
suggest that cross-document reasoning benefits most from our retrieval 
augmentation. However, on very short questions (under 5 tokens), our 
retrieval adds noise and slightly hurts performance (Section 5.4).
```

### For Related Work

AI summarizes. Researchers position.

AI:
```
[1] proposed method A for task X. [2] proposed method B for task X. [3] 
proposed method C for task X.
```

Researcher:
```
Existing approaches to task X fall into two families. Retrieval-based methods 
[1, 2] achieve high precision on factual queries but require a curated 
knowledge base, which limits coverage. Generation-based methods [3, 4] 
have broader coverage but suffer from hallucination when training data is 
sparse. Our work inhabits the space between these families: we retrieve 
passages (for grounding) but generate answers (for coverage), with a 
verification step that catches hallucination (Section 3.3).
```

## Chinese Academic AI Patterns

Chinese academic papers have their own AI detection vectors:

### 高风险中文模式

```
禁忌：
- "本文首先介绍了...，然后分析了...，最后总结了..."
- "具有重要的理论意义和实际应用价值"
- "在...领域得到了广泛应用"
- "取得了显著的成果"
- "为...提供了新的思路和方法"
- "目前已有大量研究..."（不说具体数量）
```