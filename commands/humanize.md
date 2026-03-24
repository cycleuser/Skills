# Humanize Command

Entry point for the humanizer skill to convert AI-generated text into more natural human language.

## Usage

```bash
/humanize <text or file path>
/humanize --style formal <text>     # Formal humanization
/humanize --style casual <text>     # Casual humanization
/humanize --target <target_rate> <text>
/humanize --demo                    # Demo mode
```

## Execution Flow

```
1. Input → Receive text or file from user
2. Style Detection → Determine formal or casual
3. AI Detection → Analyze AI features, calculate AIGC rate
4. Strategy Selection → Choose rewriting strategy based on detection
5. Iterative Rewriting → Multiple rounds until target reached
6. Output → Display comparison and report
```

## Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| --style | auto | Style: auto/formal/casual |
| --target | 30 | Target AIGC rate (%) |
| --max-iter | 10 | Maximum iterations |
| --demo | false | Generate demo sample |

## Formal Humanization (--style formal)

**Use cases:** Papers, reports, commentary articles, professional documents

**Core Strategies:**
1. **Focused Selection** — Don't be comprehensive; focus on core issues
2. **Position Expression** — Express clear judgments, have definite views
3. **Deep Analysis** — Raise questions, analyze essence
4. **Evidence Support** — Cite specific data, cases, studies
5. **Thinking Traces** — Show reasoning process, acknowledge uncertainty

**Example:**
```
Input (AI Rate 93%):
Artificial intelligence has revolutionized the way we live
and work. Firstly, in the healthcare sector, AI enables
more accurate diagnosis. Secondly, in the financial industry...
In conclusion, the impact of AI is profound and far-reaching.

Output (AI Rate 18%):
AI's Social Impact: Beyond the Revolutionary Rhetoric

The claim that artificial intelligence "revolutionizes"
society has become a commonplace, but what precisely is
being revolutionized, and how?

In healthcare, the impact is real but uneven. AI systems
have achieved diagnostic accuracy that matches or exceeds
human experts in specific tasks. Yet clinical integration
remains frustratingly slow. The bottleneck is not technical
but institutional: liability frameworks are unclear.

What emerges from this analysis is a pattern: AI's impact
is significant but differentiated. The technology works best
in bounded, well-defined tasks; it struggles with open-ended
problems requiring contextual judgment.
```

## Casual Humanization (--style casual)

**Use cases:** Blogs, comments, social media, informal articles

**Core Strategies:**
1. **Structure Disruption** — Remove formal structure, shuffle order
2. **Colloquialism** — Replace formal words, add conversational markers
3. **Personalization** — Add personal experiences and feelings
4. **Imperfection** — Vary sentence length, add natural jumps

**Example:**
```
Input (AI Rate 91%):
This product is an intelligent learning assistant designed
to help users improve learning efficiency. The product has
the following core functions: intelligent learning plan
formulation, personalized content recommendation...

Output (AI Rate 24%):
This app is all about helping you learn more efficiently.
Features are pretty standard: planning, recommendations,
progress tracking, Q&A.

Honestly, there are tons of these apps now. Their main pitch
is AI-powered personalization—pushing content based on your
learning style. Sounds good in theory, but after using it...
it's just okay. Sometimes the recommendations hit, sometimes
they're totally off.
```

## Execution Steps

### Step 1: Style Detection

Auto-detect or use specified style:
- Analyze vocabulary formality
- Analyze sentence complexity
- Determine text context

### Step 2: AI Feature Detection

```
Structural Features:
- Paragraph uniformity
- List patterns
- Transition frequency

Linguistic Features:
- AI vocabulary matching
- Sentence pattern recognition
- Empty expression detection

Content Features:
- Position/stance
- Analysis depth
- Evidence support
- Thinking traces
```

### Step 3: Strategy Selection

```
Formal Strategies:
├── AI rate > 70%: Focus + Position + Deep analysis
├── AI rate 50-70%: Evidence + Thinking traces
└── AI rate 30-50%: Detail polishing

Casual Strategies:
├── AI rate > 70%: Structure disruption + Colloquialism + Personalization
├── AI rate 50-70%: Imperfection + Emotion
└── AI rate 30-50%: Detail addition
```

### Step 4: Iterative Rewriting

```
while not converged:
    1. Apply current strategy
    2. Detect new AIGC rate
    3. Evaluate effectiveness
    4. Check quality metrics
    5. Adjust strategy
    6. Check convergence
```

### Step 5: Output Results

Generate report containing:
- Original vs. final AI rate
- Iteration summary
- Key changes
- Humanized text
- Quality assessment

## Notes

1. **Preserve Meaning**: Don't change the main message
2. **Style Consistency**: Keep style uniform throughout
3. **Moderation**: Below 30% is usually sufficient
4. **Human Review**: Final results should be verified

## Related Rules

- rules/ai-features.md - AI feature detection rules
- rules/formal-humanization.md - Formal humanization strategies
- rules/humanization.md - Casual humanization strategies
- rules/iteration.md - Iteration optimization flow
- rules/examples.md - Processing examples