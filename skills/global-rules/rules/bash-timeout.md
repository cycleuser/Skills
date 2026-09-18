# Bash Timeout Safety

## The Default Timeout Problem

When a bash command times out with the default timeout (2 minutes without an explicit value), the system sends SIGKILL. This is a hard kill that:

1. Does not allow the process to clean up
2. Can corrupt file descriptors
3. Can corrupt the terminal stdin FD specifically

## The Terminal Crash Chain

```
bash command runs > 2 minutes
→ Default timeout triggers
→ SIGKILL sent to process
→ Stdin file descriptor corrupted (FD becomes bad)
→ opencode TUI tries to setRawMode on the bad FD
→ setRawMode errno: 9 (EBADF — Bad file descriptor)
→ TUI crashes, all state lost
→ opencode GUI must be restarted
```

## Timeout Values

### Always use these explicit timeouts:

| Duration | Timeout (ms) | Examples |
|----------|-------------|----------|
| Trivial | 5000 | `ls`, `echo`, `grep`, `git status` |
| Quick | 10000 | `git diff`, simple bash, file reads |
| Standard | 30000 | `pytest tests/test_file.py`, `pip install -q` |
| Extended | 60000 | `pytest tests/` (small suite), `npm install` |
| Long | 120000 | Full builds, large test suites |

### Never:
- Run commands without a timeout parameter
- Run `pytest` without `-k` or file path limiting
- Run full test suites in a single bash call
- Use timeout > 120000 without splitting into smaller units

## Terminal Recovery

If a terminal crash occurs:
1. Restart opencode GUI
2. Check `~/.local/share/opencode/log/` for the crash log
3. Verify the last command's timeout was too short
4. Add explicit timeout to the failing command
5. Re-run with proper timeout

## Session Integrity

- Bash timeouts preserve non-stdin state (file writes, data in memory)
- Only the terminal connection is affected
- Work done before the timeout is preserved
- Use background processes for long-running tasks when possible
