# Tool Safety Patterns

## Three Safety Models

| Model | Implementation | Safety Level | User Experience |
|-------|---------------|--------------|-----------------|
| Hard sandbox | OS-level (Rust landlock) | Maximum | Seamless |
| Per-step approval | Popup for every action | High | Tedious |
| Tiered + hooks | Categorize tools, allow hooks | Balanced | Good |

## Tiered Tool System (Claude Code)

```python
from enum import Enum

class ToolTier(Enum):
    SAFE = "safe"              # Read-only, no approval needed
    MODERATE = "moderate"      # Write operations, optional approval
    DANGEROUS = "dangerous"    # Bash commands, strict controls

TOOL_TIERS = {
    "read": ToolTier.SAFE,
    "glob": ToolTier.SAFE,
    "grep": ToolTier.SAFE,
    "write": ToolTier.MODERATE,
    "edit": ToolTier.MODERATE,
    "bash": ToolTier.DANGEROUS,
}

def execute_tool(name: str, args: dict, config: dict) -> ToolResult:
    tier = TOOL_TIERS.get(name, ToolTier.MODERATE)

    if tier == ToolTier.DANGEROUS:
        # Check blacklist
        if is_blacklisted(args):
            return ToolResult(success=False, error="Command blocked")

        # Require approval unless in auto mode
        if not config.get("auto_approve_dangerous"):
            if not request_user_approval(name, args):
                return ToolResult(success=False, error="User cancelled")

    elif tier == ToolTier.MODERATE:
        # Run pre-write hooks
        if name in ("write", "edit"):
            hook_result = run_pre_write_hooks(args)
            if not hook_result.success:
                return hook_result

    return run_tool(name, args)
```

## Bash Command Blacklist

```python
BLACKLISTED_PATTERNS = [
    r"rm\s+-rf\s+/",
    r"rm\s+-rf\s+~",
    r">\s*/dev/sd",
    r"mkfs",
    r"dd\s+if=",
    r":()\s*{\s*:\|:&\s*}",  # Fork bomb
    r"curl.*\|\s*bash",
    r"wget.*\|\s*bash",
]

def is_blacklisted(args: dict) -> bool:
    command = args.get("command", "")
    for pattern in BLACKLISTED_PATTERNS:
        if re.search(pattern, command):
            return True
    return False
```

## Hooks System

```python
from typing import Callable
from dataclasses import dataclass

@dataclass
class HookResult:
    proceed: bool
    error: str | None = None
    modified_args: dict | None = None

HookFunction = Callable[[dict], HookResult]

class HookRegistry:
    def __init__(self):
        self.hooks: dict[str, list[HookFunction]] = {
            "pre_read": [],
            "pre_write": [],
            "pre_edit": [],
            "pre_bash": [],
            "post_tool": [],
        }

    def register(self, hook_name: str, func: HookFunction):
        self.hooks[hook_name].append(func)

    def run_hooks(self, hook_name: str, args: dict) -> HookResult:
        for hook in self.hooks.get(hook_name, []):
            result = hook(args)
            if not result.proceed:
                return result
            if result.modified_args:
                args = result.modified_args
        return HookResult(proceed=True)

# Example hook: Linter check before write
def lint_before_write(args: dict) -> HookResult:
    path = args.get("path", "")
    content = args.get("content", "")

    if path.endswith(".py"):
        import subprocess
        result = subprocess.run(
            ["ruff", "check", "--stdin-filename", path],
            input=content,
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            return HookResult(
                proceed=False,
                error=f"Linting failed:\n{result.stdout}"
            )

    return HookResult(proceed=True)

# Register
hooks = HookRegistry()
hooks.register("pre_write", lint_before_write)
```

## Git Protection

```python
PROTECTED_PATHS = [
    ".git/",
    ".gitignore",
    ".gitattributes",
]

def is_protected_path(path: str) -> bool:
    """Check if path is protected from modification."""
    path_lower = path.lower()
    for protected in PROTECTED_PATHS:
        if protected in path_lower:
            return True
    return False

def validate_write_path(path: str, work_dir: Path) -> bool:
    """Ensure write is within work directory and not protected."""
    abs_path = (work_dir / path).resolve()

    # Must be within work directory
    try:
        abs_path.relative_to(work_dir.resolve())
    except ValueError:
        return False  # Path traversal attempt

    # Must not be protected
    if is_protected_path(str(abs_path)):
        return False

    return True
```

## Doom Loop Detection (OpenCode)

Detect when agent is stuck repeating the same action.

```python
from dataclasses import dataclass
from typing import Any

@dataclass
class ToolCall:
    name: str
    args: dict[str, Any]

def detect_doom_loop(recent_calls: list[ToolCall], threshold: int = 3) -> bool:
    """Detect if agent is stuck in a loop."""
    if len(recent_calls) < threshold:
        return False

    last_n = recent_calls[-threshold:]

    # Check if all calls are identical
    first = last_n[0]
    for call in last_n[1:]:
        if call.name != first.name or call.args != first.args:
            return False

    return True  # Loop detected

# Usage in agent loop
class AgentLoop:
    def __init__(self):
        self.recent_calls: list[ToolCall] = []

    def run(self):
        while True:
            response = self.llm.chat(...)

            if response.tool_calls:
                for tc in response.tool_calls:
                    call = ToolCall(tc.name, tc.arguments)

                    # Track recent calls
                    self.recent_calls.append(call)
                    if len(self.recent_calls) > 10:
                        self.recent_calls.pop(0)

                    # Check for doom loop
                    if detect_doom_loop(self.recent_calls):
                        print("Warning: Agent appears stuck. Continue? [y/N]")
                        if input().lower() != "y":
                            return "cancelled"

                    result = self.execute_tool(tc.name, tc.arguments)
                    ...
```

## OS-Level Sandbox (Rust/Codex)

For maximum security, use OS-level isolation:

```rust
use landlock::*;
use seccompiler::*;

fn create_sandbox(allowed_paths: &[PathBuf]) -> Result<()> {
    // Landlock: restrict file access
    let rules = AccessFs::from_flags(
        AccessFs::ReadFile | AccessFs::ReadDir
    );

    let mut landlock = Landlock::new();
    for path in allowed_paths {
        landlock.add_rule(Rule::new(path, rules.clone())?);
    }
    landlock.restrict_self()?;

    // Seccomp: restrict syscalls
    let filter = SeccompFilter::new(
        vec![
            // Allow essential syscalls
            Allow::new("read"),
            Allow::new("write"),
            Allow::new("openat"),
            // Block dangerous ones
            Block::new("fork"),  // No new processes
        ]
    )?;
    filter.apply()?;

    Ok(())
}
```

## Command Timeout

```python
import subprocess
from typing import Optional

DEFAULT_TIMEOUT = 120  # seconds

def run_bash_safely(
    command: str,
    timeout: int = DEFAULT_TIMEOUT,
    cwd: Optional[Path] = None
) -> ToolResult:
    """Execute bash command with safety measures."""
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=cwd
        )
        return ToolResult(
            success=result.returncode == 0,
            data={"stdout": result.stdout, "stderr": result.stderr},
            metadata={"returncode": result.returncode}
        )
    except subprocess.TimeoutExpired:
        return ToolResult(
            success=False,
            error=f"Command timed out after {timeout}s"
        )
    except Exception as e:
        return ToolResult(success=False, error=str(e))
```

## Best Practices

1. **Default to safe** - When in doubt, require approval
2. **Layer defenses** - Blacklist + hooks + sandbox
3. **Log everything** - Audit trail for debugging
4. **Fail gracefully** - Don't crash on blocked operations
5. **User control** - Always let user override restrictions