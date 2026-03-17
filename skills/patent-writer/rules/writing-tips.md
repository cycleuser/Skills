# Patent Writing Tips

## Core Principles

### 1. Clarity Over Complexity

```
❌ The aforementioned apparatus is configured to facilitate the 
   transmission of electromagnetic signals through a predetermined
   medium characterized by specific permittivity values.

✓ The device sends radio signals through air.
```

### 2. Specificity Over Generality

```
❌ A suitable amount of material is used.

✓ 10-50 grams of catalyst is used, preferably 25-30 grams.
```

### 3. Completeness Over Brevity

```
❌ The data is processed.

✓ The data is processed by:
   1. Removing noise using a median filter
   2. Normalizing to zero mean and unit variance
   3. Encoding using a pre-trained transformer model
```

## Section-by-Section Tips

### Title (发明名称)

```
Good titles:
- Specific: "一种基于注意力机制的文本分类方法"
- Complete: Includes method/system/device as appropriate
- Concise: Usually 10-25 characters

Avoid:
- Marketing language: "一种革命性的..."
- Too broad: "一种处理方法"
- Too narrow: "一种用Python实现的..."
```

### Background Art (背景技术)

```
Structure:
1. Start broad - What is the technical field?
2. Narrow down - What is the specific problem?
3. Identify gap - What is missing in current solutions?

Common mistakes:
- Too long (should be 1-2 pages)
- Missing prior art
- Not identifying actual problems
- Too promotional
```

### Summary (发明内容)

```
Three parts:

1. Purpose (发明目的)
   "本发明要解决的技术问题是提供一种..."

2. Solution (技术方案)
   "为解决上述技术问题，本发明提供..."
   - List all essential features
   - Include optional improvements
   - Cover all alternatives

3. Benefits (有益效果)
   "与现有技术相比，本发明具有以下有益效果："
   - Be specific: "accuracy improved by 15%"
   - Be comparative: "faster than existing methods"
   - Be complete: list all benefits
```

### Detailed Description (具体实施方式)

```
Essential elements:

1. Reference to drawings
   "如图1所示，..."
   "参考图2，..."

2. Step-by-step description
   "步骤S101：数据输入模块接收用户输入的文本数据"
   "具体地，文本数据可以是..."

3. Multiple embodiments
   "实施例1：..."
   "实施例2：与实施例1的区别在于..."

4. Working examples
   Provide actual parameters, conditions, results

5. Alternatives
   "可选地，也可以使用..."
   "在其他实施例中，..."
```

### Claims Drafting Tips (权利要求撰写技巧)

```
Independent claims (独立权利要求):
- Include only essential features
- Start with "一种..."
- End with structural/functional elements

Dependent claims (从属权利要求):
- Add non-essential features
- Provide alternatives
- Create fallback positions

Claim language:
- Use "所述" to reference earlier elements
- Use "其特征在于" to introduce features
- Use "包括" not "由...组成"
```

## Drawing Guidelines

### Types of Drawings

```
1. Flowcharts (流程图)
   - For methods/processes
   - Use standard symbols
   - Number each step

2. Block Diagrams (框图)
   - For systems
   - Show connections
   - Label each module

3. Structural Diagrams (结构图)
   - For devices
   - Show physical components
   - Include dimensions if relevant
```

### Drawing Rules

```
1. Number consistently
   - Figure numbers: 图1, 图2
   - Element numbers: 10, 20, 21, 22

2. Label clearly
   - Chinese preferred
   - Consistent terminology

3. Reference in text
   - "如图1所示"
   - "参见图2中的元件10"

4. Sufficient detail
   - Enough to understand
   - Not overly complex
```

## Common Mistakes

### Technical Mistakes

```
1. Insufficient disclosure
   ❌ "使用常规方法处理"
   ✓ "使用X方法处理，具体包括..."

2. Missing alternatives
   ❌ Only one way described
   ✓ Multiple alternatives provided

3. Inconsistent terminology
   ❌ "模块"、"单元"、"组件" used interchangeably
   ✓ One term used consistently
```

### Language Mistakes

```
1. Ambiguous language
   ❌ "大约"、"左右"、"等"
   ✓ Specific ranges, concrete lists

2. Future tense
   ❌ "将要处理"
   ✓ "处理"

3. Subjective statements
   ❌ "这个方法很好"
   ✓ "该方法准确率达到95%"
```

### Strategic Mistakes

```
1. Too narrow
   ❌ Only one specific implementation
   ✓ Broader scope with specific examples

2. Too broad
   ❌ Claims that cannot be supported
   ✓ Supported by detailed description

3. Missing fallback
   ❌ Only independent claim
   ✓ Dependent claims as backup
```

## Quality Checklist

```
Content Quality:
□ Background covers relevant prior art
□ Problem clearly identified
□ Solution fully described
□ Advantages are specific and convincing
□ Multiple embodiments provided
□ Drawings are clear and complete

Technical Quality:
□ Technical details sufficient
□ Parameters specified
□ Alternatives provided
□ No inconsistent terminology

Legal Quality:
□ Claims supported by description
□ Essential features in independent claims
□ Optional features in dependent claims
□ No undefined terms

Language Quality:
□ Clear and concise
□ No ambiguous terms
□ Consistent terminology
□ Correct grammar
```

## Writing Process

```
Step 1: Outline (30 min)
- Write section headers
- List key points for each section

Step 2: Draft (2-4 hours)
- Fill in each section
- Don't worry about perfection

Step 3: Draw (1-2 hours)
- Create necessary drawings
- Reference in text

Step 4: Review (1 hour)
- Check against checklist
- Fix obvious issues

Step 5: Revise (1-2 hours)
- Improve clarity
- Add missing details

Step 6: Final review (30 min)
- Read as if you're the examiner
- Check completeness
```