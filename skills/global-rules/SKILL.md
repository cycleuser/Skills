---
name: global-rules
version: "1.0.0"
description: |
  Global safety and operational rules for opencode sessions. Auto-loaded with highest priority on every session.

  Contains critical rules learned from incidents to prevent system crashes and data loss.
auto_load: true
load_priority: -100
author: cycleuser
license: MIT
---

## Safety Rules

**Critical**: Read and follow all rules in this directory for every bash/command execution.

Core rules:
1. **Always set explicit `timeout` on bash calls** — 30s for tests, 60s for installs, never default
2. **Never run unscoped full test suites** — use `-k` or file paths to limit scope
3. **Never use `rm -rf` without variable guards**, `curl|bash`, `sudo`, or `kill -9`
4. **Infinite loops must have hard timeout + budget limits** — no unbounded while(True)
5. **Redirect stdin** with `< /dev/null` for non-interactive commands

## Rules

- [rules/bash-safety.md](rules/bash-safety.md) - Bash command safety patterns and dangerous operations
- [rules/bash-timeout.md](rules/bash-timeout.md) - Timeout safety and terminal FD corruption prevention
- [rules/terminal-safety.md](rules/terminal-safety.md) - Terminal crash prevention and recovery

## Incident Record

| Date | Incident | Root Cause | Prevention |
|------|----------|------------|------------|
| 2026-05-08 | opencode TUI crash | bash timeout → SIGKILL → stdin FD corrupted → `setRawMode errno: 9` | Always set explicit timeout; never SIGKILL |

## See Also

- `/安检` from **an-jian** — Security audit for dangerous patterns
- `/skills` from **skill-manager** — Browse all installed skills
