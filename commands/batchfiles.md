---
description: Batch file pipeline — orient, rename, convert, dedupe, verify a batch of files (no-loss)
agent: build
---

Load the batch-file-pipeline skill and process: $ARGUMENTS

**Usage**: `/batchfiles <dir> <action>`

**Actions**:
- `/batchfiles <dir> orient` - Detect image rotation via OCR box geometry
- `/batchfiles <dir> rotate [angle]` - Batch rotate (auto-detect by default)
- `/batchfiles <dir> rename <mapping.csv>` - Batch rename with confirmation
- `/batchfiles <dir> convert <format>` - Batch convert
- `/batchfiles <dir> dedupe` - SHA-256 dedupe (report only)
- `/batchfiles <dir> verify <regex>` - Validate naming convention
