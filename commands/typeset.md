---
description: Typeset - publication-grade book typesetting, Markdown chapters to PDF/DOCX, 11 hard quality gates
agent: build
---

Load the pai-ban skill and typeset: $ARGUMENTS

**Usage**: `/typeset <dir>`

**Subcommands**:
- `/typeset <dir>` - Build a PDF (and DOCX) from a Markdown chapter folder, auto-verify
- `/typeset init <dir>` - Scaffold a pai-ban.toml config + assets into a project
- `/typeset check <pdf|dir>` - Run the hard typography gates and report a pass/fail table
- `/typeset preview <dir>` - Compile a 2–3 chapter sample and render page PNGs for review
- `/typeset spec` - Print the authoritative design spec

**Examples**:
- `/typeset ~/books/llmap` - Build the whole book
- `/typeset init ~/books/llmap` - Initialize the project config
- `/typeset check ~/books/llmap/build/pai-ban/zh/<title>.pdf` - Re-run the audit

Core principle: declarative config + fixed pipeline + hard quality gates, reproducible and zero-tolerance (zero overflow, zero missing glyphs, zero LaTeX errors, zero Overfull ≥1pt). Requires TeX Live (xeCJK/listings/booktabs/fancyhdr/microtype/hyperref); missing packages are reported explicitly, never silently degraded. The PDF is the authoritative artifact, DOCX is the editable copy.
