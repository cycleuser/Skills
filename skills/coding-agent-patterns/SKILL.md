---
name: coding-agent-patterns
version: "1.0.0"
description: |
  Core patterns for AI coding agents based on analysis of Claude Code, Codex, Cline, Aider, OpenCode.

  Triggers when: Building an AI coding agent or assistant, implementing tool-calling loops, managing context windows for LLMs, setting up agent memory or skill systems, or designing multi-provider LLM abstraction.

  Capabilities: Core agent loop with while(true) and tool execution, context management with pruning and compression and repo maps, tool safety with sandboxing and approval flows and doom loop detection, multi-provider abstraction with unified API for different LLMs, memory systems with project rules and auto-memory and skill loading, session persistence with SQLite vs JSONL patterns.
author: cycleuser
license: MIT
---

# Coding Agent Development Patterns

Core patterns distilled from Claude Code (70k stars), Codex (62k), Cline (58k), Aider (41k), and OpenCode (114k).

## The Core Loop: while(true)

All AI coding agents share the same fundamental loop. The loop follows the pattern: ask LLM if it needs tools, use them, feed results back, and repeat until done. The implementation builds context with tools and conversation history, calls the LLM with messages and tool definitions, checks for tool calls and returns content if none, executes tools and appends results to history, then loops back with tool results.

Core Tools: All agents have six fundamental tools. The `read` tool reads file contents. The `write` tool creates or overwrites files. The `edit` tool performs precise string replacement in files. The `bash` tool executes shell commands. The `glob` tool finds files by pattern. The `grep` tool searches file contents. A minimal viable agent requires approximately 1000-2000 lines with these six tools plus the loop.

## Challenge 1: Context Window Management

The biggest engineering challenge. A real project has thousands of files, but LLMs have limited context (128K - 2M tokens).

Strategies: Different agents use different strategies. Aider uses Repo Map with tree-sitter scanning that only passes signatures and loads details on demand. Claude Code uses Auto-compaction where the LLM summarizes history when context fills. OpenCode uses a two-level approach that prunes old tool results (keeping 40K recent) and then compresses.

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

Three safety models represent different trade-offs. The hard sandbox model used by Codex (Rust) provides maximum safety with OS-level isolation. The per-step approval model used by Cline is safe but tedious due to too many popups. The tiered plus hooks model used by Claude Code provides balance with read/write/execute tiers.

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

Each LLM provider has different APIs for message formats, tool calling, and streaming. OpenAI uses `content: string` with `function_call` for tools. Anthropic uses `content: blocks[]` with `tool_use` for tools. Google uses `parts[]` with `function_call` for tools. Ollama is OpenAI-compatible.

Two approaches exist for multi-provider abstraction. OpenCode uses the Vercel AI SDK which provides free abstraction for over 20 providers. Cline uses manual adapters which supports 44 providers with full control.

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

Different agents use different storage approaches. OpenCode uses SQLite which provides ACID guarantees and no corruption on crash. Other agents use JSONL which is simple and human-readable.

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

Different agents use different approaches for loading project rules. Claude Code uses `CLAUDE.md` plus `.claude/rules/` directory with auto-memory and per-file-type rules. OpenCode uses `.opencode/skills/` plus agents directory with on-demand skill loading and markdown agents. Cline uses `.clinerules` with 7 lifecycle hooks. Aider uses `CONVENTIONS.md` with simple `/read` loading. Codex uses `AGENTS.md` plus Skills for deterministic workflows.

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

Five key principles guide agent development. First, start with the loop by writing the while(true) first and getting tool calling working. Second, implement context management early since this is the number one cause of agent failures. Third, provider abstraction matters because locking into one LLM vendor creates vendor lock-in. Fourth, layer safety with sandbox plus approval plus detection. Fifth, recognize that memory equals context since rules are injected into prompts rather than being separate config.