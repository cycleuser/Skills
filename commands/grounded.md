---
description: Grounded generation - anti-hallucination strict paraphrasing with closed-world constraint and per-step audit
agent: build
---

Load the you-ju skill and run the task in grounded mode: $ARGUMENTS

**Usage**: `/grounded <task>`

**Examples**:
- `/grounded Summarize the key specs from these three documents` - grounded summary
- `/grounded audit summary.md` - audit existing output for hallucinations
- `/grounded align summary.md source_A.md` - sentence-level grounding alignment
- `/grounded experiment` - run baseline vs controlled comparison

**Workflow**:
Source manifest (IDs + whitelist) → recorded retrieval → closed-world paraphrase
(sentence-level citations [A:L12]) → per-sentence audit (entity/number/citation checks)
→ 3-round violation demotion → deliver with "uncovered by sources" list

**Rule**: Every entity, number, and logical relation in the output must be
traceable to source text; questions the source explicitly marks as "not
provided" must be reported as "not mentioned in sources" — never filled in.