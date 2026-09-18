# Terminal Crash Prevention

## The Problem

opencode's TUI uses raw mode on the terminal. Raw mode requires a valid file descriptor (FD) for stdin. When bash commands time out with SIGKILL, the stdin FD can become corrupted (bad FD), causing `setRawMode` to fail with `errno: 9 (EBADF)`.

## Prevention Checklist

Before running any bash command:
- [ ] Is there an explicit timeout set?
- [ ] Is the timeout appropriate for the operation?
- [ ] For test suites, is the scope limited with `-k` or file paths?
- [ ] For interactive commands, is stdin redirected with `< /dev/null`?
- [ ] For loops, is there a hard iteration limit and time budget?

## Safe Command Patterns

### Tests (scoped)
```bash
pytest tests/test_config.py -v -x          # Single file, stop on first failure
pytest -k "test_config" -v                 # By keyword
pytest tests/test_core/ -v --timeout=30    # Directory, with timeout
```

### Tests (NOT safe)
```bash
pytest                    # Unscoped, could run forever
pytest tests/             # All tests, no limit
```

### File Operations
```bash
rm file.txt                              # OK for single files
rm -rf "$DIR"  # ONLY if DIR is guarded   # Need variable guard
```

### Git Operations
```bash
git status                               # Safe, fast
git diff                                 # Safe, usually fast
git log --oneline -20                    # Safe, bounded
```

## What Gets Preserved

Even if the terminal crashes, the following are preserved:
- File modifications (the edits were already written)
- Git state (commits, stashes)
- Session logs in `~/.local/share/opencode/log/`

## What Gets Lost

- Current conversation context
- Unsaved tool state
- Active iteration progress
- Terminal display state

## Mitigation Strategy

1. **Prevention first**: Always set explicit timeouts
2. **Graceful degradation**: Use SIGTERM (timeout=30000) before SIGKILL (timeout=60000) for operations that could hang
3. **State persistence**: Use auto-save mechanisms for long-running work
4. **Check pointing**: Save progress periodically so crash recovery is faster
