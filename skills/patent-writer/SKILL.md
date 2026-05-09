---
name: patent-writer
version: "2.0.0"
description: |
  Patent writing assistant for Chinese patents with search, disclosure document writing, workflow guidance, and strategic filing advice.

  Triggers when: Writing a patent application, creating a patent disclosure document, conducting patent search and analysis, planning patent filing strategy, or seeking guidance on the patent process timeline and requirements.

  Commands:
  - /patent search <keywords> - Conduct patent search with analysis framework
  - /patent disclosure <invention> - Write disclosure document with complete structure
  - /patent report <invention> - Generate self-search report with blocking risk assessment
  - /patent workflow - Show patent workflow with timeline and milestones
  - /patent strategy <invention> - Provide filing strategy advice
  - /patent check <document> - Check patent document compliance
  - /patent examples - Show patent writing examples and best practices

  Capabilities: Patent search platform guidance with analysis framework, disclosure document templates with complete structure, patent three-property analysis with blocking risk assessment, writing tips and best practices with quality checklist, workflow timeline estimation with strategic filing advice, self-search report generation, prior art analysis, novelty and inventiveness assessment, Chinese patent law compliance
author: cycleuser
license: MIT
---

## Safety Rules

**Critical**: Read and follow [global-rules/bash-safety.md](file:///Users/fred/.config/opencode/skills/global-rules/rules/bash-safety.md) for all bash/command execution.

Core rules:
1. **Always set explicit `timeout` on bash calls** — 30s for tests, 60s for installs, never default
2. **Never run unscoped full test suites** — use `-k` or file paths to limit scope
3. **Never use `rm -rf` without variable guards**, `curl|bash`, `sudo`, or `kill -9`
4. **Infinite loops must have hard timeout + budget limits** — no unbounded while(True)
5. **Redirect stdin** with `< /dev/null` for non-interactive commands

A bash timeout that triggers SIGKILL corrupts the terminal FD, crashes opencode's TUI, and forces a GUI restart.

# Patent Writer

Patent writing assistant for Chinese patent applications with comprehensive search, disclosure, and filing guidance.

## Quick Commands

| Command | Description |
|---------|-------------|
| `/patent search <keywords>` | Conduct patent search with analysis framework |
| `/patent disclosure <invention>` | Write disclosure document with complete structure |
| `/patent report <invention>` | Generate self-search report with blocking risk assessment |
| `/patent workflow` | Show patent workflow with timeline and milestones |
| `/patent strategy <invention>` | Provide filing strategy advice |
| `/patent check <document>` | Check patent document compliance |
| `/patent examples` | Show patent writing examples and best practices |

## Patent Process Overview

### Creation Phase (3-16 weeks)
- **Week 1-4**: Patent search & analysis
- **Week 2-8**: Write disclosure document
- **Week 3-12**: Agent drafts patent application
- **Week 4-16**: Review & revise

### Examination Phase (11-38 months)
- **<1 week**: Application & acceptance
- **3-18 months**: Preliminary review & publication
- **6-18 months**: Substantive examination
- **2 months**: Patent grant

**Total timeline**: 11-38 months

## Patent Search Methodology

### Search Strategy
1. **Define Search Scope**: Identify key technical terms, define technical field, list competitors, determine time range (usually last 20 years)
2. **Choose Search Platforms**: CNIPA (Chinese patents), Shanghai IP (Chinese), Google Patents (Global), USPTO (US), EPO Espacenet (European)
3. **Construct Search Queries**: Use Boolean operators `(keyword1 OR keyword2) AND (keyword3 OR keyword4)`, classification codes (CPC/IPC), assignee filters, date ranges
4. **Filter and Analyze**: Remove irrelevant results, categorize by relevance, identify closest prior art, document key findings

### Three-Property Check
- **Novelty**: Is the invention new? Has it been disclosed anywhere before?
- **Inventiveness**: Is it non-obvious? Would a skilled person easily derive it?
- **Utility**: Can it be manufactured? Does it solve a technical problem?

### Blocking Risk Assessment
- **HIGH**: Prior art covers key features, recommend abandoning or significantly modifying
- **MEDIUM**: Some overlap with prior art, possible design-around options
- **LOW**: Minimal overlap with prior art, proceed with filing

## Disclosure Document Structure

### Standard Template
```
1. 发明名称 (Title): [Concise, accurate reflection of technical solution]
2. 技术领域 (Technical Field): [Field of invention]
3. 背景技术 (Background Art): [Existing technology and its shortcomings]
4. 发明内容 (Invention Content):
   - 发明目的 (Purpose): [Problem to be solved]
   - 技术方案 (Technical Solution): [Detailed description of solution]
   - 有益效果 (Beneficial Effects): [Advantages over prior art]
5. 附图说明 (Drawing Description): [Brief description of figures]
6. 具体实施方式 (Detailed Description): [Specific implementation methods]
7. 权利要求概要 (Claims Outline): [Main claim points]
8. 关键词 (Keywords): [3-5 keywords]
```

### Writing Guidelines
- **Title**: Concise, accurate, specify method/system/device appropriately
- **Technical Field**: Start broad, narrow down to specific problem
- **Background**: Identify gap in current solutions, be specific about problems
- **Summary**: Three parts - purpose, solution with essential features, benefits with concrete improvements
- **Detailed Description**: Include references to drawings, step-by-step procedures, multiple embodiments with alternatives
- **Claims**: Independent claims with essential features, dependent claims for alternatives

## Key Principles

### When to Start Writing?
The optimal timing for patent filing is during project research when you can conduct patent search alongside research. File **before** implementation since patent protects ideas, not implementation. Most importantly, file **before any public announcement** since public disclosure before filing destroys novelty.

### Critical Timing Rules
1. **File Before Announcement**: Public disclosure before filing destroys novelty
2. **Don't Wait for Implementation**: File early in research, not after full implementation
3. **File Early in Research**: Consider filing at research milestones to secure broader scope

### Patent Three Properties (专利三性)
The three properties that define a patentable invention are:
- **Novelty (新颖性)**: Not publicly disclosed before filing
- **Inventiveness (创造性)**: Non-obvious to a skilled person
- **Utility (实用性)**: Can be made and used

## Patent Search Platforms

### Official Platform (国知局)
- URL: https://pss-system.cponline.cnipa.gov.cn/conventionalSearch
- Requires: ID card registration

### Shanghai IP Platform (上海知产平台)
- URL: https://www.shanghaiip.cn/search/#/home
- No login required

### International Platforms
- **Google Patents**: Global patent search
- **USPTO**: US patent database
- **EPO Espacenet**: European patent database

## Deliverables

### 1. Patent Disclosure Document (专利交底书)
The disclosure document is written by the inventor for the patent attorney. Key sections include title of invention, technical field, background art, summary of invention, detailed description, claims outline, drawings, and complete implementation examples.

### 2. Self-Search Report (自检索报告)
The self-search report checks if the patent has blocking risks. Its purpose is to clarify patent writing ideas, help the agent understand patent novelty, and improve the approval rate.

## Writing Best Practices

### Core Principles
1. **Clarity Over Complexity**: Use simple, direct language instead of technical jargon
2. **Specificity Over Generality**: Provide concrete parameters, ranges, and examples
3. **Completeness Over Brevity**: Include sufficient detail for a skilled person to reproduce

### Section-by-Section Tips
- **Title**: Specific, complete, concise (10-25 characters), avoid marketing language
- **Background**: Start broad, narrow down, identify actual problems, avoid being too long
- **Summary**: Three-part structure (purpose-solution-benefits), be specific about improvements
- **Detailed Description**: Reference drawings, step-by-step, multiple embodiments, working examples, alternatives

### Drawing Guidelines
- **Flowcharts**: For methods and processes, use standard symbols, number each step
- **Block Diagrams**: For systems, show connections, label each module
- **Structural Diagrams**: For devices, show physical components, include dimensions if relevant

## Filing Strategy

### Provisional vs. Non-provisional
- **Provisional**: Quick filing, 12-month priority, not examined, expires if not converted
- **Non-provisional**: Full examination, can mature to patent, higher cost, longer timeline

### Priority Claims
Within 12 months of first filing, you can claim priority to earlier applications and file in multiple countries. After 12 months, you cannot claim priority and may lose novelty if disclosed.

## Quality Assurance

### Common Mistakes to Avoid
1. **Insufficient Disclosure**: Don't use "conventional methods", provide specific details
2. **Missing Alternatives**: Always provide multiple implementation approaches
3. **Inconsistent Terminology**: Use same terms consistently throughout
4. **Ambiguous Language**: Avoid "approximately", "etc.", subjective statements
5. **Too Narrow/Narrow**: Balance scope breadth with supportable claims

### Quality Checklist
- Background covers relevant prior art
- Problem clearly identified  
- Solution fully described with specifics
- Advantages specific and convincing
- Multiple embodiments provided
- Drawings clear and complete
- Claims supported by description
- No undefined or inconsistent terms
- Clear, concise, and technically accurate

## Troubleshooting

### Search returns too many irrelevant results
- **Symptom**: `/patent search` returns broad results unrelated to the invention
- **Fix**: Narrow search with IPC classification codes; use `/patent search <keywords> --class <IPC>` to filter by technical field; add boolean operators (AND, NOT) in quotes

### Disclosure document rejected by patent agent
- **Symptom**: Patent agent returns disclosure for insufficient technical detail
- **Fix**: Use `/patent disclosure <invention> --detailed` for full technical specification; include best mode and alternative embodiments; add comparative data showing advantages over prior art

### Novelty search inconclusive
- **Symptom**: Can't determine if invention is novel from search results alone
- **Fix**: Use `/patent report <invention> --depth full` for comprehensive analysis; cross-search both patent databases and academic literature; consult patent classification definitions

### Filing timeline pressure
- **Symptom**: Invention already disclosed publicly, 12-month grace period running out
- **Fix**: Use `/patent strategy --urgent` for accelerated workflow; prioritize provisional application filing; flag all prior public disclosures with dates

## Edge Cases

- **Software patents**: Chinese patent law requires hardware + software combination; pure software methods may need different strategy — flag with `/patent strategy --software`
- **Design patents**: Design patent (外观设计) has different requirements than utility model (实用新型) or invention (发明专利) — use `/patent workflow --type design` for correct forms
- **Co-inventors from different organizations**: Ownership and filing rights need explicit assignment agreements before filing
- **Patent family strategy**: PCT vs Paris Convention routes — use `/patent strategy --international` for multi-country filing analysis
- **Pre-existing publications**: If the inventor published a paper before filing, check novelty grace period (6 months in China for certain exhibitions/conferences)
- **Employee invention**: If invention was made within scope of employment, employer typically owns rights unless contract states otherwise

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-04-01 | Initial version with search, disclosure, workflow |
| 2.0.0 | 2026-05-09 | Added strategy, check, examples commands; expanded from 128→212 lines; 4 rule files integrated |

## Rules
- [rules/patent-search.md](rules/patent-search.md) - Patent search methodology with analysis framework
- [rules/disclosure-document.md](rules/disclosure-document.md) - Complete disclosure document structure and examples  
- [rules/patent-workflow.md](rules/patent-workflow.md) - Full patent workflow with timeline and milestones
- [rules/writing-tips.md](rules/writing-tips.md) - Writing best practices with quality checklist

## Reference Standards
- Patent Law of the People's Republic of China
- Implementing Regulations of the Patent Law
- GB/T 7713-1987 Scientific and Technical Reports, Theses and Academic Papers

## Best Practices Summary
1. **Start Early**: File before public disclosure, begin during research phase
2. **Search Thoroughly**: Use multiple platforms, construct comprehensive queries
3. **Write Clearly**: Help agent understand your technical innovation with specifics
4. **Plan Strategically**: Consider filing timeline, priority claims, and scope breadth
5. **Iterate with Agent**: Review and refine together for optimal results

## See Also

- `/paper` from **academic-writer** — Literature search for prior art and novelty assessment
- `/人话` from **humanizer** — Humanize patent descriptions for broader readability