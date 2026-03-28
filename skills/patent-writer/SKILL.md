---
name: patent-writer
version: "1.0.0"
description: |
  Patent writing assistant for Chinese patents. Helps with patent search, disclosure document writing, and patent workflow guidance.

  Triggers when: Writing a patent application, creating a patent disclosure document, conducting patent search and analysis, or planning patent strategy for a project.

  Commands:
  - /patent search <keywords> - Conduct patent search
  - /patent disclosure <invention> - Write disclosure document
  - /patent report <invention> - Generate self-search report
  - /patent workflow - Show patent workflow

  Capabilities: Patent search platform guidance, disclosure document templates, patent three-property analysis, writing tips and best practices, and workflow timeline estimation.
author: cycleuser
license: MIT
---

# Patent Writer

Patent writing assistant for Chinese patent applications.

## Quick Commands

Four commands support the patent writing workflow. The `/patent search <keywords>` command provides patent search guidance. The `/patent disclosure <invention>` command writes a disclosure document. The `/patent report <invention>` command generates a self-search report. The `/patent workflow` command shows the patent workflow.

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

The patent process has two main phases. The creation phase includes patent search and analysis (1-4 weeks), patent writing (1-4 weeks), agent drafting (1-4 weeks), and review and revision (0-4 weeks), totaling 3-16 weeks. The examination phase includes application and acceptance (under 1 week), preliminary review and publication (3-18 months), substantive examination (6-18 months), and patent grant (2 months). The total timeline ranges from 11-38 months.

## Key Principles

### When to Start Writing?

The optimal timing for patent filing is during project research when you can conduct patent search alongside research. File before implementation since patent protects ideas, not implementation. Most importantly, file before any public announcement since public disclosure before filing destroys novelty.

### Patent Three Properties (专利三性)

The three properties that define a patentable invention are novelty (新颖性), which means not publicly disclosed before; inventiveness (创造性), which means non-obvious to a skilled person; and utility (实用性), which means can be made and used.

### Common Mistakes to Avoid

Four common mistakes compromise patent applications. Waiting until project completion delays filing unnecessarily. Making a public announcement before filing destroys novelty. Conducting insufficient prior art search weakens the application's novelty claim. Providing poor technical description makes it difficult for the patent attorney and examiner to understand the invention.

## Patent Search Platforms

### Official Platform (国知局)
- URL: https://pss-system.cponline.cnipa.gov.cn/conventionalSearch
- Requires: ID card registration

### Shanghai IP Platform (上海知产平台)
- URL: https://www.shanghaiip.cn/search/#/home
- No login required

## Deliverables

### 1. Patent Disclosure Document (专利交底书)

The disclosure document is written by the inventor for the patent attorney. Key sections include title of invention, technical field, background art, summary of invention, detailed description, claims outline, and drawings.

### 2. Self-Search Report (自检索报告)

The self-search report checks if the patent has blocking risks. Its purpose is to clarify patent writing ideas, help the agent understand patent novelty, and improve the approval rate.

## Writing Tips

Four tips improve patent disclosure quality. First, draw more diagrams since a picture is worth a thousand words. Second, provide examples to help the agent and examiner understand the invention. Third, emphasize advantages with clear benefits over prior art. Fourth, be specific and avoid vague descriptions.

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