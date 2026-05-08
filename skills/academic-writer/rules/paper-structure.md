# Paper Structure Templates

Structures are starting points shaped by the argument, not rigid molds. Adjust section weights, ordering, and presence based on what the paper needs to say.

## Structure Principle

The paper's structure follows the argument:
1. Here is a real problem (Introduction)
2. Existing solutions fall short in this specific way (Related Work)
3. Here is our approach and why it should work (Method)
4. Here is evidence that it works and where it breaks (Experiments)
5. Here is what we learned (Conclusion)

Sections are weighted by contribution, not uniformly. The method and experiments sections should be the largest.

## IEEE Conference Paper (8 pages)

```
Title

Abstract (150-200 words)
   Single paragraph. Context → Gap → Approach → Key result. No citations.

Keywords (3-5 terms)
   Ordered by specificity, most specific first.

I. INTRODUCTION (1.0-1.2 pages)
   P1: Concrete problem with specific evidence (numbers, citations)
   P2: Why existing approaches cannot solve it (cite 3-5 papers with limits)
   P3: Our approach and its intuition (connect to the gap)
   P4: Contributions (numbered, concrete, falsifiable)
   [Optional P5: Paper organization — only if structure is non-standard]

II. RELATED WORK (0.7-1.0 pages)
   Paragraphs organized by IDEA, not by paper
   Each paragraph: what this family does, where it stops, 
   how it relates to our work
   End with explicit gap statement (1-2 sentences)

III. METHODOLOGY (2.0-2.8 pages)
   A. Problem Formulation
      - Formal definition with notation
      - Table of symbols if > 10
   
   B. Approach Overview
      - Figure + intuition paragraph (before diving into details)
      - Why this design, not just what the design is
   
   C-D. Key Components
      - Intuition first, then formal definition
      - Algorithm pseudocode if complex
   
   E. [Optional] Theoretical Analysis
      - Complexity, convergence guarantees
      - Only if it adds real value (reviewers check)

IV. EXPERIMENTS (2.0-2.8 pages)
   A. Setup
      - Datasets with statistics table
      - Baselines with citations and fairness note
      - Metrics with definitions
      - Implementation details: hardware, training time, hyperparameters
   
   B. Main Results
      - Comparison table with std dev
      - Statistical significance where appropriate
      - Key finding stated in text, not just in table
   
   C. Analysis
      - Ablation: which component matters most
      - Parameter sensitivity: how robust is it
      - [Optional] Case study or visualization
   
   D. Discussion
      - When the method fails and why
      - What the results mean beyond the numbers
      - [Important] This distinguishes thoughtful papers from AI papers

V. CONCLUSION (0.1-0.2 pages)
   What we did. Key finding. Honest limitation. 
   One concrete future step if it exists.
   NOT a summary of the paper. NOT "future work" wish list.

REFERENCES (0.8-1.0 page)
   20-35 references for 8-page paper. Quality over quantity.
```

## AAAI/IJCAI Format (8 pages)

Same structure as IEEE, but:
- Section numbering: "1 Introduction" not "I. INTRODUCTION"
- In-text citations: (Author, Year) not [1]
- Reference list: alphabetical by first author
- Tighter page limit: be ruthless with space

```
1 Introduction
2 Related Work
3 Preliminaries
   3.1 Problem Definition
   3.2 Notation
4 Method
   4.1 Overview
   4.2 [Component Name]
   4.3 [Component Name]
5 Experiments
   5.1 Setup
   5.2 Main Results
   5.3 Analysis
6 Conclusion
```

## CCF Chinese Journal (10-15 pages)

```
标题

摘要 (200-400字)
   研究背景(1句)→现有方法不足(1-2句)→本文方法(2-3句)→实验结果(1-2句)

关键词 (3-8个，分号分隔)

一、引言
   P1: 具体问题描述（用数据说话，不用"近年来"开头）
   P2: 现有方法的具体不足（逐条引用，说明每篇的局限）
   P3: 本文方法和直觉
   P4: 本文贡献
   本文的主要贡献包括：
   （1）提出了 XX 方法，解决了 XX 问题（具体、可验证）
   （2）在 XX 数据集上实现了 XX% 的提升
   （3）开源了 XX 代码/数据集

二、相关工作
   按研究思路组织，不按论文罗列
   （一）方向A的研究现状
   （二）方向B的研究现状
   （三）现有方法局限性分析（不是客套话，要具体指出来）

三、方法设计
   （一）问题定义与符号说明
       表1：符号表（超过10个符号时必须提供）
   （二）总体框架
       图1 + 直觉解释（先讲为什么这么做，再讲具体怎么做）
   （三）核心组件1
       数学推导 + 直觉说明交错
   （四）核心组件2
   （五）算法流程与复杂度分析

四、实验验证
   （一）实验环境与数据集
       数据集统计表 + 硬件/软件环境
   （二）对比方法与评价指标
       列出所有基线，标注是否原论文结果还是复现
   （三）主实验结果
       表格 + 具体分析（不只说"优于"，说为什么）
   （四）消融实验
       逐个去除组件，分析各自贡献
   （五）参数敏感性分析
       至少2个关键参数的变化曲线
   （六）案例分析（可选）
       展示实际案例，好案例和坏案例都要

五、结论与展望
   对应贡献逐条总结（1-2句/条）
   真实局限性（不是"未来将继续研究"客套话）
   如果有明确的下一步，具体说是什么问题和什么方向

参考文献（GB/T 7714-2015格式）
   30-50篇为宜，中文期刊引用占20-40%
```

## Page Allocation Guide

Section size should match contribution weight. Not all sections are equal:

| Section | 8-page paper | 10-page paper | Rationale |
|---------|-------------|---------------|-----------|
| Abstract | 0.1 | 0.1 | Fixed by format |
| Introduction | 1.0 | 1.2 | Problem + contribution |
| Related Work | 0.7 | 1.0 | Position, not survey |
| Method | 2.5 | 3.5 | Core contribution |
| Experiments | 2.5 | 3.5 | Evidence for claims |
| Conclusion | 0.1 | 0.2 | Brief |
| References | 0.8 | 0.5 | Squeezed for space |

## When to Break the Template

The templates above are defaults. Deviate when the argument demands it:

- No separate Related Work section if the intro covers it (short papers)
- Add a "Preliminaries" section when heavy notation is needed (AAAI style)
- Merge Method + Experiments for systems papers: "System Design" → "Evaluation"  
- Split Experiments into "Main Results" + "Analysis" when results are complex
- Add "Discussion" subsection when results are surprising or contradictory
- Remove "Conclusion" if it only repeats the abstract (some venues allow this)

## Organic Structure Checklist

- [ ] Each section has a clear purpose (not just "convention")
- [ ] Section sizes reflect contribution weights
- [ ] Argument flows without gaps between sections
- [ ] No section exists only because the template says so
- [ ] Reader can follow the logic by reading only first sentences
- [ ] Transitions between sections are natural, not mechanical