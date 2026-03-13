# Academic Writing Style Guidelines

## Core Principles

### 1. Formal Academic Tone

**Correct:**
```
The proposed method achieves significant improvement over existing approaches.
```

**Incorrect:**
```
Our method is really good and works much better than others!
```

### 2. Complete Sentences

**Correct:**
```
The system consists of three modules. The first module processes input data. 
The second module extracts features, and the third module generates predictions.
```

**Incorrect:**
```
The system: three modules. First: process input. Second: extract features. 
Third: generate predictions.
```

### 3. Proper Transitions

```
- "Furthermore, ..."
- "In addition to ..."
- "Building upon ..."
- "In contrast to ..."
- "To address this limitation, ..."
- "Consequently, ..."
```

## Sentence Patterns

### Describing Method

```
We propose [method name], a [type] approach for [task].

The proposed framework consists of [number] main components.

Formally, let X denote the input and Y denote the output.

Given the input sequence, we first apply [operation] to obtain...

The objective function is defined as...
```

### Describing Results

```
Experimental results demonstrate that...

As shown in Table X, our method outperforms...

The improvement is particularly significant in...

We observe a X% improvement over the strongest baseline.
```

### Citing Work

```
Recent studies [1, 2, 3] have shown that...

Following the approach of [4], we...

Unlike previous work [5, 6], our method...

This is consistent with findings from [7].
```

## Language Patterns to Avoid

### Colon-Separated Headings

**Avoid:**
```
Architecture: The system uses a transformer-based encoder.
Training: We use Adam optimizer with learning rate 1e-4.
```

**Use:**
```
The system uses a transformer-based encoder. We use Adam optimizer 
with learning rate 1e-4 for training.
```

### Bullet Point Paragraphs

**Avoid:**
```
Our contributions are:
• We propose a new method
• We conduct experiments
• We achieve state-of-the-art results
```

**Use:**
```
Our contributions are as follows. First, we propose a new method 
for text classification. Second, we conduct extensive experiments 
on multiple benchmarks. Third, we achieve state-of-the-art results 
with significant improvements.
```

### Emoji and Decorative Symbols

**Avoid:**
```
Our method achieves 🎯 95% accuracy! 
Key features: ✅ Fast ✅ Accurate ✅ Scalable
```

**Use:**
```
Our method achieves 95% accuracy. The key features include 
fast inference, high accuracy, and good scalability.
```

## Vocabulary Choice

### Prefer Specific over Vague

| Vague | Specific |
|-------|----------|
| good performance | 95.3% accuracy |
| many methods | over 20 approaches |
| significant improvement | 12.5% improvement |
| recent years | 2020-2024 |

### Prefer Active over Passive (when appropriate)

| Passive | Active |
|---------|--------|
| It was observed that... | We observe that... |
| The data was processed by... | The system processes the data using... |

### Technical Terms

```
Use standard terminology:
- "neural network" not "brain-like network"
- "attention mechanism" not "focus mechanism"
- "embedding" not "vector representation" (in context)
- "baseline" not "comparison method"
```

## Mathematical Writing

### Inline vs Display

```
Inline for simple expressions: The loss function L = ...

Display for important equations:
$$
L = \frac{1}{N} \sum_{i=1}^{N} \ell(y_i, \hat{y}_i)
$$
```

### Equation Introductions

```
The loss function is defined as follows:

$$
L = \frac{1}{N} \sum_{i=1}^{N} \ell(y_i, \hat{y}_i)
$$

where N denotes the number of samples and \ell is the cross-entropy loss.
```

### Notation Consistency

```
Define once, use consistently:
- Bold capital for matrices: X, W
- Bold lowercase for vectors: x, w
- Italic for scalars: x, w, n
- Calligraphic for sets: \mathcal{D}, \mathcal{X}
```

## Common Mistakes

### 1. Overusing "Novel" and "State-of-the-art"

**Avoid:**
```
We propose a novel state-of-the-art approach with novel architecture...
```

**Use:**
```
We propose an approach with a transformer-based architecture that 
achieves competitive performance...
```

### 2. Informal Expressions

| Avoid | Use |
|-------|-----|
| huge | significant |
| a lot of | numerous |
| very big | substantial |
| pretty good | promising |

### 3. First Person Overuse

**Limit:**
```
We propose... We design... We implement... We evaluate...
```

**Vary with:**
```
This paper presents... The proposed method... 
Our experiments demonstrate... The results indicate...
```

## Paragraph Structure

### Topic Sentence Pattern

```
[Topic sentence stating main point]
[Supporting evidence or explanation]
[Examples or details]
[Transition to next point]
```

### Example

```
The attention mechanism is crucial for capturing long-range dependencies 
in text. By computing attention weights between all token pairs, the model 
can directly access relevant context regardless of distance. For example, 
in the sentence "The bank announced that it would raise interest rates," 
the pronoun "it" can be correctly linked to "bank" through attention. 
This capability distinguishes transformers from traditional recurrent models.
```

## Revision Checklist

- [ ] No colon-separated headings in paragraphs
- [ ] No emoji or decorative symbols
- [ ] Complete sentences throughout
- [ ] Proper transitions between paragraphs
- [ ] Specific quantitative claims
- [ ] Consistent mathematical notation
- [ ] Formal academic vocabulary
- [ ] No repetitive sentence structures
- [ ] Citations properly integrated
- [ ] No informal expressions