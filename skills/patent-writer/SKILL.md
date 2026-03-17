---
name: patent-writer
version: "1.0.0"
description: |
  Patent writing assistant for Chinese patents. Helps with patent search, disclosure document writing, and patent workflow guidance.

  **Triggers when:**
  - Writing a patent application
  - Creating a patent disclosure document
  - Conducting patent search and analysis
  - Planning patent strategy for a project

  **Commands:**
  - `/patent search <keywords>` - Conduct patent search
  - `/patent disclosure <invention>` - Write disclosure document
  - `/patent report <invention>` - Generate self-search report
  - `/patent workflow` - Show patent workflow

  **Capabilities:**
  - Patent search platform guidance
  - Disclosure document templates
  - Patent three-property analysis
  - Writing tips and best practices
  - Workflow timeline estimation
author: cycleuser
license: MIT
---

# Patent Writer

Patent writing assistant for Chinese patent applications.

## Quick Commands

| Command | Description |
|---------|-------------|
| `/patent search <keywords>` | Patent search guidance |
| `/patent disclosure <invention>` | Write disclosure document |
| `/patent report <invention>` | Generate self-search report |
| `/patent workflow` | Show patent workflow |

## Patent Workflow

```
┌─────────────────────────────────────────────────────────────────────┐
│                      PATENT WRITING WORKFLOW                         │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐          │
│  │    SEARCH    │───▶│    WRITE     │───▶│   SUBMIT     │          │
│  │   检索分析   │    │   撰写交底书 │    │   代理提交   │          │
│  │   1-4 weeks  │    │   1-4 weeks  │    │   1-4 weeks  │          │
│  └──────────────┘    └──────────────┘    └──────────────┘          │
│                                                                      │
│                           ▼                                          │
│                   ┌──────────────┐                                   │
│                   │    REVIEW    │                                   │
│                   │   国知局审查 │                                   │
│                   │  11-38 months│                                   │
│                   └──────────────┘                                   │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

## Timeline Estimation

| Phase | Task | Duration |
|-------|------|----------|
| Creation | Patent search & analysis | 1-4 weeks |
| | Patent writing | 1-4 weeks |
| | Agent drafting | 1-4 weeks |
| | Review & revision | 0-4 weeks |
| **Subtotal** | | **3-16 weeks** |
| Examination | Application & acceptance | < 1 week |
| | Preliminary review & publication | 3-18 months |
| | Substantive examination | 6-18 months |
| | Patent grant | 2 months |
| **Total** | | **11-38 months** |

## Key Principles

### When to Start Writing?

1. **During project research** - Conduct patent search alongside research
2. **Before implementation** - Patent protects ideas, not implementation
3. **Before announcement** - File patent before any public disclosure

### Patent Three Properties (专利三性)

1. **Novelty (新颖性)** - Not publicly disclosed before
2. **Inventiveness (创造性)** - Non-obvious to skilled person
3. **Utility (实用性)** - Can be made and used

### Common Mistakes to Avoid

- ❌ Waiting until project completion
- ❌ Public announcement before filing
- ❌ Insufficient prior art search
- ❌ Poor technical description

## Patent Search Platforms

### Official Platform (国知局)
- URL: https://pss-system.cponline.cnipa.gov.cn/conventionalSearch
- Requires: ID card registration

### Shanghai IP Platform (上海知产平台)
- URL: https://www.shanghaiip.cn/search/#/home
- No login required

## Deliverables

### 1. Patent Disclosure Document (专利交底书)

The disclosure document is written by the inventor for the patent attorney.

**Key sections:**
- Title of invention
- Technical field
- Background art
- Summary of invention
- Detailed description
- Claims outline
- Drawings

### 2. Self-Search Report (自检索报告)

Self-search report checks if the patent has blocking risks.

**Purpose:**
- Clarify patent writing ideas
- Help agent understand patent novelty
- Improve approval rate

## Writing Tips

1. **Draw more diagrams** - A picture is worth a thousand words
2. **Provide examples** - Help agent and examiner understand
3. **Emphasize advantages** - Clear benefits over prior art
4. **Be specific** - Avoid vague descriptions

## Rules

- [rules/patent-search.md](rules/patent-search.md) - Patent search methodology
- [rules/disclosure-document.md](rules/disclosure-document.md) - Disclosure document writing
- [rules/patent-workflow.md](rules/patent-workflow.md) - Patent workflow details
- [rules/writing-tips.md](rules/writing-tips.md) - Writing best practices

## Reference

- [Patent Writing Guide](https://github.com/yufeiminds/patent-writing-guide)
- [USTC Disclosure Template](https://iat.ustc.edu.cn/u/cms/xjjs/202203/29084743bh3k.doc)

## Best Practices

1. Start early - Patent protects ideas, file before public disclosure
2. Search thoroughly - Understand prior art landscape
3. Write clearly - Help agent understand your invention
4. Iterate with agent - Review and refine together