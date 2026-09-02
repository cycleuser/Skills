---
description: Inventory & report — inventory materials from a directory, cross-verify sources, output table + summary
agent: build
---

Load the inventory-report skill and inventory: $ARGUMENTS

**Usage**: `/inventory <dir> [topic]`

**Subcommands**:
- `/inventory <dir> [topic]` - Define taxonomy, search, cross-verify, output xlsx + summary
- `/inventory verify <list>` - Cross-verify an existing list with evidence chain
- `/inventory report` - Generate a docx report

**Examples**:
- `/inventory ~/Current 成果` - Inventory achievements
- `/inventory verify 我的获奖清单` - Verify an award list
