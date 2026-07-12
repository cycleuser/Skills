---
description: Template-preserving form filler — copy original template, fill data, keep exact format
agent: build
---

Load the tianbiao skill and fill: $ARGUMENTS

**Usage**: `/tianbiao <template> <data>`

**Subcommands**:
- `/tianbiao <template> <data>` - Fill data into template, preserving fonts/borders/merged cells
- `/tianbiao convert <file>` - Convert .doc/.xls template to editable .docx/.xlsx (LibreOffice, high fidelity)
- `/tianbiao inspect <template>` - Map the template's tables/cells/fonts before filling
- `/tianbiao check <doc>` - Verify filled doc's format fidelity & data integrity

**Examples**:
- `/tianbiao quality-analysis.docx roster.xls` - Fill an exam analysis form
- `/tianbiao convert template.doc` - Convert a legacy template
- `/tianbiao inspect score-analysis.docx` - Inspect template structure

Core principle: fill the ORIGINAL template in place — never rebuild tables. Copy template → drop data into the right cells → keep original fonts, borders, merged cells and layout. Output to a NEW file, never overwrite the template.
