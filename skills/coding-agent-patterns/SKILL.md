---
name: coding-agent-patterns
version: "1.0.0"
description: |
  Core patterns for AI coding agents based on analysis of Claude Code, Codex, Cline, Aider, OpenCode.

  **Triggers when:**
  - Building an AI coding agent or assistant
  - Implementing tool-calling loops
  - Managing context windows for LLMs
  - Setting up agent memory or skill systems
  - Designing multi-provider LLM abstraction

  **Capabilities:**
  - Core agent loop: while(true) with tool execution
  - Context management: pruning, compression, repo maps
  - Tool safety: sandboxing, approval flows, doom loop detection
  - Multi-provider abstraction: unified API for different LLMs
  - Memory systems: project rules, auto-memory, skill loading
  - Session persistence: SQLite vs JSONL patterns
author: cycleuser
license: MIT
---

# Coding Agent Development Patterns

Core patterns distilled from Claude Code (70k stars), Codex (62k), Cline (58k), Aider (41k), and OpenCode (114k).

## The Core Loop: while(true)

All AI coding agents share the same fundamental loop:

```python
while True:
    # 1. Build context: tools + conversation history
    messages = build_messages(history, tools)

    # 2. Call LLM
    response = llm.chat(messages, tools=tool_definitions)

    # 3. Check for tool calls
    if not response.tool_calls:
        return response.content  # Done, return to user

    # 4. Execute tools
    for tool_call in response.tool_calls:
        result = execute_tool(tool_call.name, tool_call.arguments)
        history.append({"role": "tool", "content": result})

    # 5. Loop back with tool results
```

**Translation**: Ask LLM if it needs tools → use them → feed results back → repeat until done.

### Core Tools (all agents have these)

| Tool | Purpose |
|------|---------|
| `read` | Read file contents |
| `write` | Create/overwrite files |
| `edit` | Precise string replacement in files |
| `bash` | Execute shell commands |
| `glob` | Find files by pattern |
| `grep` | Search file contents |

A minimal viable agent: **~1000-2000 lines** with these 6 tools + the loop.

## Challenge 1: Context Window Management

The biggest engineering challenge. A real project has thousands of files, but LLMs have limited context (128K - 2M tokens).

### Strategies

| Agent | Strategy |
|-------|----------|
| **Aider** | Repo Map: tree-sitter scan, only pass signatures, load details on demand |
| **Claude Code** | Auto-compaction: LLM summarizes history when context fills |
| **OpenCode** | Two-level: prune old tool results (keep 40K recent), then compress |

### Compression Pattern

```python
def compress_context(history: list, budget: int) -> list:
    """Compress history when approaching context limit."""
    usage = count_tokens(history)

    if usage < budget * 0.8:
        return history

    # Keep recent turns, summarize older ones
    recent = history[-10:]  # Last 10 turns
    older = history[:-10]

    summary = llm.summarize(older)
    return [{"role": "system", "content": f"Previous context summary:\n{summary}"}] + recent
```

### Repo Map Pattern (Aider)

```python
def build_repo_map(repo_path: Path) -> str:
    """Build a 'map' of the codebase with just signatures."""
    import tree_sitter

    map_lines = []
    for file in repo_path.rglob("*.py"):
        # Parse and extract: class names, function signatures, imports
        signatures = extract_signatures(file)
        map_lines.append(f"{file}:\n{signatures}")

    return "\n".join(map_lines)  # Much smaller than full code
```

## Challenge 2: Tool Execution Safety

### Three Safety Models

| Model | Agent | Trade-off |
|-------|-------|-----------|
| **Hard sandbox** | Codex (Rust) | Maximum safety, OS-level isolation |
| **Per-step approval** | Cline | Safe but tedious (too many popups) |
| **Tiered + hooks** | Claude Code | Balanced: read/write/execute tiers |

### Sandboxing (Codex/Rust approach)

```rust
// Use landlock + seccomp for OS-level sandboxing
fn sandbox_restrict(allowed_paths: &[PathBuf]) -> Result<()> {
    // Limit file access to allowed paths
    // Block dangerous syscalls
    // Three modes: suggest-only, auto-edit, full-auto
}
```

### Tiered Tools (Claude Code approach)

```python
TOOL_TIERS = {
    "read": "safe",       # No approval needed
    "write": "needs_approval",  # User confirms
    "bash": "restricted", # Blacklist + approval
}

def execute_tool(name: str, args: dict) -> Result:
    tier = TOOL_TIERS.get(name, "safe")

    if tier == "needs_approval":
        if not user_approves(name, args):
            return Result(cancelled=True)

    if tier == "restricted":
        if is_dangerous(args):
            return Result(error="Command blocked")

    return run_tool(name, args)
```

### Doom Loop Detection (OpenCode unique feature)

```python
def detect_doom_loop(history: list) -> bool:
    """Detect if agent is stuck repeating the same action."""
    if len(history) < 3:
        return False

    last_three = history[-3:]
    # Check if same tool called 3 times with identical args
    if all_same_tool_and_args(last_three):
        return True  # Pause and ask user

    return False
```

## Challenge 3: Multi-Provider Abstraction

Each LLM provider has different APIs: message formats, tool calling, streaming.

| Provider | Message Format | Tool Field |
|----------|----------------|------------|
| OpenAI | `content: string` | `function_call` |
| Anthropic | `content: blocks[]` | `tool_use` |
| Google | `parts[]` | `function_call` |
| Ollama | OpenAI-compatible | OpenAI-compatible |

### Two Approaches

| Approach | Agent | Pros |
|----------|-------|------|
| **Use Vercel AI SDK** | OpenCode | Free abstraction for 20+ providers |
| **Manual adapters** | Cline | 44 providers, full control |

### Unified Client Pattern

```python
class BaseLLMClient(ABC):
    @abstractmethod
    def chat(self, messages: list, tools: list) -> Response: ...

    @abstractmethod
    def chat_stream(self, messages: list, tools: list) -> Iterator[Chunk]: ...

class OpenAIClient(BaseLLMClient):
    def chat(self, messages, tools):
        return self.client.chat.completions.create(
            model=self.model, messages=messages, tools=tools
        )

class AnthropicClient(BaseLLMClient):
    def chat(self, messages, tools):
        return self.client.messages.create(
            model=self.model, messages=messages, tools=tools
        )

def get_client(provider: str, model: str) -> BaseLLMClient:
    clients = {
        "openai": OpenAIClient,
        "anthropic": AnthropicClient,
        "ollama": OllamaClient,
    }
    return clients[provider](model)
```

## Challenge 4: Error Recovery

Long execution chains fail often: API limits, expired keys, network, context overflow.

### Layered Retry Pattern

```python
async def agent_loop_with_retry(max_retries: int = 32):
    for attempt in range(max_retries):
        try:
            return await agent_loop()
        except RateLimitError:
            await sleep(60 * (2 ** attempt))  # Exponential backoff
        except AuthError:
            rotate_api_key()  # Inner retry
        except ContextOverflowError:
            compress_context()  # Middle retry
        except NetworkError:
            continue  # Immediate retry
        except FatalError:
            rebuild_session()  # Outer retry
```

## Challenge 5: Session Persistence

| Agent | Storage | Pros |
|-------|---------|------|
| **OpenCode** | SQLite | ACID, no corruption on crash |
| **Others** | JSONL | Simple, human-readable |

### JSONL Pattern

```python
def save_session(session_id: str, event: dict):
    """Append event to session log file."""
    log_file = Path.home() / ".agent" / "sessions" / f"{session_id}.jsonl"
    with open(log_file, "a") as f:
        f.write(json.dumps(event) + "\n")

def load_session(session_id: str) -> list:
    """Load all events from session."""
    log_file = Path.home() / ".agent" / "sessions" / f"{session_id}.jsonl"
    events = []
    with open(log_file) as f:
        for line in f:
            events.append(json.loads(line))
    return events
```

### Shadow Git Pattern (Cline unique)

```python
def init_shadow_git(project_path: Path):
    """Create hidden git repo for undo history."""
    shadow_path = project_path / ".agent-shadow-git"
    run(["git", "init"], cwd=shadow_path)

def snapshot_after_tool(shadow_path: Path):
    """Auto-commit after each tool execution."""
    run(["git", "add", "-A"], cwd=shadow_path)
    run(["git", "commit", "-m", "snapshot"], cwd=shadow_path)

def undo_to_snapshot(shadow_path: Path, commit_hash: str):
    """Restore to any previous state."""
    run(["git", "checkout", commit_hash], cwd=shadow_path)
```

## Memory Systems

### Project Rules Loading

| Agent | File | Features |
|-------|------|----------|
| **Claude Code** | `CLAUDE.md` + `.claude/rules/` | Auto-memory, per-file-type rules |
| **OpenCode** | `.opencode/skills/` + agents/ | On-demand skill loading, markdown agents |
| **Cline** | `.clinerules` | 7 lifecycle hooks |
| **Aider** | `CONVENTIONS.md` | Simple `/read` loading |
| **Codex** | `AGENTS.md` + Skills | Deterministic workflows |

### Skill System Pattern (OpenCode)

```
.opencode/
├── skills/
│   ├── git-release/
│   │   └── SKILL.md
│   └── code-review/
│       └── SKILL.md
└── agents/
    └── reviewer.md   # Specialized agent definition
```

```markdown
<!-- .opencode/agents/reviewer.md -->
---
description: Code review agent, read-only
mode: subagent
tools:
  write: false
  edit: false
---
You are a code review expert. Analyze code, suggest improvements, never modify files.
```

### Auto-Memory Pattern (Claude Code)

```python
def learn_from_correction(user_feedback: str, context: dict):
    """Store user corrections for future reference."""
    memory_file = Path.home() / ".claude" / "auto_memory.json"

    memories = json.loads(memory_file.read_text())
    memories.append({
        "feedback": user_feedback,
        "context": context,
        "timestamp": datetime.now().isoformat(),
    })

    memory_file.write_text(json.dumps(memories, indent=2))

def build_system_prompt() -> str:
    """Include learned preferences in system prompt."""
    memory_file = Path.home() / ".claude" / "auto_memory.json"
    if memory_file.exists():
        memories = json.loads(memory_file.read_text())
        return f"User preferences:\n{format_memories(memories)}"
    return ""
```

## Rules

- [rules/context-management.md](rules/context-management.md) - Context window strategies
- [rules/tool-safety.md](rules/tool-safety.md) - Security patterns
- [rules/multi-provider.md](rules/multi-provider.md) - LLM abstraction
- [rules/memory-systems.md](rules/memory-systems.md) - Agent memory patterns

## Key Takeaways

1. **Start with the loop** - Write the while(true) first, get tool calling working
2. **Context management early** - This is the #1 cause of agent failures
3. **Provider abstraction matters** - Don't lock into one LLM vendor
4. **Safety in layers** - Sandbox + approval + detection
5. **Memory = context** - Rules are injected into prompts, not separate config