# Bash Command Safety

## Core Rule: Always Set Explicit Timeout

Every bash call MUST have an explicit `timeout` parameter. Never rely on defaults.

```python
# CORRECT
await bash("pytest tests/test_module.py", timeout=30000)  # 30 seconds

# WRONG
await bash("pytest")  # No timeout — can hang forever
```

## Timeout Guidelines

| Operation Type | Recommended Timeout |
|---------------|-------------------|
| Simple commands (ls, grep, git status) | 5s (5000ms) |
| Single test file | 30s (30000ms) |
| Small test suite (<100 tests) | 60s (60000ms) |
| Package install | 60s (60000ms) |
| Large operations | 120s (120000ms), use background jobs |

## Dangerous Command Patterns (NEVER use)

### `rm -rf` without guards
```bash
# WRONG — can wipe entire system if variable is empty
rm -rf "$SOME_PATH"

# CORRECT — guard the variable
if [ -n "$SOME_PATH" ] && [ "$SOME_PATH" != "/" ]; then
    rm -rf "$SOME_PATH"
fi
```

### `curl | bash` (pipe to shell)
```bash
# WRONG — executes arbitrary code without inspection
curl https://example.com/install.sh | bash

# CORRECT — download, inspect, then run
curl -o install.sh https://example.com/install.sh
# Inspect install.sh manually
bash install.sh
```

### `sudo` without confirmation
- Only use sudo when explicitly requested by the user
- If unsure, ask the user before sudo

### `kill -9` (SIGKILL)
- **CRITICAL**: SIGKILL on bash timeout corrupts the terminal stdin FD
- This causes `setRawMode errno: 9 (EBADF)` — opencode TUI crashes
- Use `kill -15` (SIGTERM) instead, which allows graceful shutdown
- Only use SIGKILL as absolute last resort after SIGTERM fails

## Infinite Loop Prevention

Every while(true) loop MUST have:
1. A hard iteration limit (max 100 iterations)
2. A time budget (max 30 minutes)
3. An explicit exit condition

```python
# CORRECT
max_iterations = 100
start_time = time.time()
timeout_seconds = 1800  # 30 minutes

while True:
    if iterations >= max_iterations:
        break
    if time.time() - start_time > timeout_seconds:
        break
    # ... work ...
    iterations += 1
```

## Interactive Commands

Always redirect stdin for non-interactive commands:
```bash
command < /dev/null
```

## Terminal FD Corruption

**Root cause chain**: bash timeout → SIGKILL → stdin FD corrupted → `setRawMode errno: 9 (EBADF)` → opencode TUI shutdown

**Evidence**: `~/.local/share/opencode/log/2026-05-08T134431.log`

**Prevention**: Always set explicit timeouts. Never let bash commands hit the default timeout (which uses SIGKILL).
