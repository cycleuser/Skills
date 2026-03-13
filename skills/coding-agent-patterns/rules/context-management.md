# Context Window Management Strategies

## The Problem

- Real projects: thousands of files, hundreds of thousands of lines
- LLM context limits: 128K - 2M tokens
- Each tool call adds to context (grep can return 500+ lines)
- Context overflow = agent failure

## Strategy 1: Pruning

Remove old, less relevant content while keeping recent context.

```python
def prune_context(history: list, keep_recent: int = 40000) -> list:
    """Prune old tool results while keeping recent turns."""
    pruned = []
    current_tokens = 0

    for message in reversed(history):
        msg_tokens = count_tokens(message)

        if current_tokens + msg_tokens > keep_recent:
            # Replace old tool results with summary
            if message.get("role") == "tool":
                pruned.append({
                    "role": "tool",
                    "content": "[Previous tool output truncated]"
                })
            else:
                break
        else:
            pruned.append(message)
            current_tokens += msg_tokens

    return list(reversed(pruned))
```

## Strategy 2: Compression (Auto-Compaction)

Let the LLM summarize its own history.

```python
def compress_history(history: list, model: str = "gpt-4o-mini") -> str:
    """Use LLM to compress history into summary."""
    compression_prompt = """Summarize the following conversation history.
Keep:
- Key decisions made
- Important context discovered
- Current task status
- Files modified

History:
{history}
"""
    response = client.chat.completions.create(
        model=model,
        messages=[{
            "role": "user",
            "content": compression_prompt.format(
                history=json.dumps(history[-20:])  # Last 20 turns
            )
        }]
    )
    return response.choices[0].message.content

def manage_context(history: list, max_tokens: int) -> list:
    current = count_tokens(history)
    if current < max_tokens * 0.8:
        return history

    # Compress older history
    summary = compress_history(history[:-5])
    return [
        {"role": "system", "content": f"Previous context:\n{summary}"}
    ] + history[-5:]  # Keep last 5 turns intact
```

## Strategy 3: Repo Map (Aider)

Instead of loading entire files, create a "map" with just signatures.

```python
def build_repo_map(repo_path: Path) -> str:
    """Build lightweight map of codebase structure."""
    import tree_sitter_python as tspython
    from tree_sitter import Language, Parser

    parser = Parser(Language(tspython.language()))

    map_lines = []
    for py_file in repo_path.rglob("*.py"):
        if ".venv" in str(py_file) or "__pycache__" in str(py_file):
            continue

        content = py_file.read_text()
        tree = parser.parse(bytes(content, "utf8"))

        signatures = []
        for node in tree.root_node.children:
            if node.type == "class_definition":
                name = node.child_by_field_name("name")
                if name:
                    signatures.append(f"class {name.text.decode()}")
            elif node.type == "function_definition":
                name = node.child_by_field_name("name")
                if name:
                    signatures.append(f"def {name.text.decode()}")

        if signatures:
            map_lines.append(f"{py_file.relative_to(repo_path)}:\n  " + "\n  ".join(signatures))

    return "\n\n".join(map_lines)
```

## Strategy 4: Two-Level Management (OpenCode)

Combine pruning + compression:

```python
class ContextManager:
    def __init__(self, max_tokens: int = 128000):
        self.max_tokens = max_tokens
        self.pruned_recent = 40000  # Keep 40K tokens of recent

    def manage(self, history: list) -> list:
        tokens = count_tokens(history)

        # Level 1: Prune old tool results
        if tokens > self.max_tokens * 0.6:
            history = self.prune_tool_results(history)

        # Level 2: Compress if still over
        tokens = count_tokens(history)
        if tokens > self.max_tokens * 0.8:
            history = self.compress_older(history)

        return history

    def prune_tool_results(self, history: list) -> list:
        """Remove old tool results, keep structure."""
        # Keep last N tokens of tool outputs
        ...

    def compress_older(self, history: list) -> list:
        """LLM summarization of old turns."""
        ...
```

## Context Budget Tracking

```python
class TokenBudget:
    def __init__(self, max_tokens: int):
        self.max_tokens = max_tokens
        self.used = 0
        self.tool_outputs = []

    def add_message(self, message: dict):
        tokens = count_tokens(message)
        self.used += tokens

        if message.get("role") == "tool":
            self.tool_outputs.append(tokens)

    def should_compress(self) -> bool:
        return self.used > self.max_tokens * 0.8

    def compression_target(self) -> int:
        # Target: reduce to 60% of max
        return int(self.max_tokens * 0.6)
```

## Model Context Sizes

| Model | Context Window |
|-------|---------------|
| GPT-4o | 128K |
| Claude 3.5 Sonnet | 200K |
| Gemini 2.0 Flash | 1M |
| Gemini 1.5 Pro | 2M |
| DeepSeek R1 | 64K |

## Best Practices

1. **Track tokens continuously** - Don't wait for overflow
2. **Trigger at 80% capacity** - Before it's too late
3. **Preserve recent turns** - Most relevant for current task
4. **Summarize, don't delete** - Keep key decisions
5. **Test with real projects** - Context behavior differs by workload