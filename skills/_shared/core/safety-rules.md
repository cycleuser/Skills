# 通用安全规则 (Shared Safety Rules)

**所有技能继承此文件的安全规则。** 各技能 SKILL.md 中引用本文件而非重复粘贴。

---

## Bash 执行安全规则

**Critical**: 所有 bash/命令执行必须遵循以下规则。

1. **Always set explicit `timeout` on bash calls** — 30s for tests, 60s for installs, never default
2. **Never run unscoped full test suites** — use `-k` or file paths to limit scope
3. **Never use `rm -rf` without variable guards**, `curl|bash`, `sudo`, or `kill -9`
4. **Infinite loops must have hard timeout + budget limits** — no unbounded while(True)
5. **Redirect stdin** with `< /dev/null` for non-interactive commands

## 关键警告

- Bash timeout that triggers SIGKILL corrupts the terminal FD, crashes opencode's TUI, and forces a GUI restart.
- `curl|bash` 是安全风险 — 必须先下载脚本检查后再执行。
- `git` 操作（commit、push、checkout）仅在用户明确要求时执行。

## 引用方式

各技能 SKILL.md 在 frontmatter 后添加一行引用即可：

```markdown
## Safety Rules

参见 [_shared/core/safety-rules.md](../_shared/core/safety-rules.md) — 所有安全规则从此文件加载，避免跨技能重复维护。
```
