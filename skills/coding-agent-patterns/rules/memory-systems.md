# Agent Memory Systems

## Memory System Comparison

| Agent | Project Rules | Auto Memory | Skills | Hooks |
|-------|--------------|-------------|--------|-------|
| Claude Code | CLAUDE.md + rules/ | Yes | No | Yes |
| OpenCode | SKILL.md | No | Yes | No |
| Cline | .clinerules | No | No | Yes (7) |
| Aider | CONVENTIONS.md | No | No | No |
| Codex | AGENTS.md + Skills | No | Yes | No |

## Claude Code: CLAUDE.md + Auto-Memory

### Project Instructions

```markdown
<!-- CLAUDE.md -->
# Project Instructions

## Build Commands
- Run tests: `pytest tests/`
- Lint: `ruff check .`
- Build: `python -m build`

## Code Style
- Line length: 100 characters
- Use type hints for all functions
- Follow Google docstring style

## Architecture
- API routes in `src/api/`
- Core logic in `src/core/`
- Tests mirror source structure
```

### Per-File-Type Rules

```
.claude/rules/
├── python.md      # Loaded when editing .py files
├── typescript.md  # Loaded when editing .ts files
└── rust.md        # Loaded when editing .rs files
```

### Auto-Memory Implementation

```python
from pathlib import Path
import json
from datetime import datetime

MEMORY_FILE = Path.home() / ".claude" / "auto_memory.json"

def learn_preference(feedback: str, context: dict):
    """Store user correction for future reference."""
    if not MEMORY_FILE.exists():
        MEMORY_FILE.parent.mkdir(parents=True, exist_ok=True)
        MEMORY_FILE.write_text("[]")

    memories = json.loads(MEMORY_FILE.read_text())
    memories.append({
        "feedback": feedback,
        "context": context,
        "timestamp": datetime.now().isoformat(),
        "project": context.get("project"),
    })

    MEMORY_FILE.write_text(json.dumps(memories, indent=2))

def get_learned_preferences() -> list[str]:
    """Retrieve stored preferences."""
    if not MEMORY_FILE.exists():
        return []

    memories = json.loads(MEMORY_FILE.read_text())
    return [m["feedback"] for m in memories]

def build_system_prompt() -> str:
    """Include learned preferences."""
    preferences = get_learned_preferences()
    if preferences:
        return "User preferences learned from previous sessions:\n" + "\n".join(f"- {p}" for p in preferences)
    return ""
```

## OpenCode: Skill System + Markdown Agents

### Skill Structure

```
.opencode/skills/
├── git-release/
│   ├── SKILL.md
│   └── rules/
│       └── version-bump.md
└── code-review/
    └── SKILL.md
```

### Skill Definition

```markdown
<!-- .opencode/skills/git-release/SKILL.md -->
---
name: git-release
description: Create a new git release with version bump and changelog.
triggers:
  - "release version"
  - "create release"
  - "publish new version"
---

# Git Release Skill

## Steps
1. Determine version bump type (major/minor/patch)
2. Update version in pyproject.toml
3. Generate changelog from commits
4. Create git tag
5. Push tag to origin

## Rules
- Never release on dirty working tree
- Always run tests before release
...
```

### On-Demand Skill Loading

```python
class SkillLoader:
    def __init__(self, skills_dir: Path):
        self.skills_dir = skills_dir
        self.cache: dict[str, dict] = {}

    def list_available(self) -> list[dict]:
        """List all available skills with metadata."""
        skills = []
        for skill_dir in self.skills_dir.iterdir():
            skill_file = skill_dir / "SKILL.md"
            if skill_file.exists():
                frontmatter = self._parse_frontmatter(skill_file)
                skills.append({
                    "name": frontmatter.get("name", skill_dir.name),
                    "description": frontmatter.get("description", ""),
                    "path": str(skill_dir),
                })
        return skills

    def load(self, skill_name: str) -> str:
        """Load skill content on demand."""
        if skill_name in self.cache:
            return self.cache[skill_name]["content"]

        skill_dir = self.skills_dir / skill_name
        skill_file = skill_dir / "SKILL.md"
        content = skill_file.read_text()

        # Remove frontmatter, keep content
        _, body = self._split_frontmatter(content)
        self.cache[skill_name] = {"content": body}
        return body

    def should_load(self, user_message: str, skill: dict) -> bool:
        """Determine if skill should be loaded based on triggers."""
        triggers = skill.get("triggers", [])
        message_lower = user_message.lower()
        return any(trigger in message_lower for trigger in triggers)
```

### Markdown Agent Definition

```markdown
<!-- .opencode/agents/reviewer.md -->
---
description: Code review specialist - analyzes code, suggests improvements
mode: subagent
tools:
  read: true
  write: false
  edit: false
  bash: false
---

You are a senior code reviewer. Your role:
- Identify bugs and potential issues
- Suggest improvements for readability
- Check for security vulnerabilities
- Recommend best practices

You analyze code but never modify it.
```

```python
def load_agent(agent_path: Path) -> dict:
    """Load markdown agent definition."""
    content = agent_path.read_text()
    frontmatter, body = parse_frontmatter(content)

    return {
        "description": frontmatter.get("description", ""),
        "mode": frontmatter.get("mode", "subagent"),
        "tools": frontmatter.get("tools", {}),
        "system_prompt": body,
    }
```

## Cline: .clinerules + Hooks

### Project Rules

```
# .clinerules
Use pnpm instead of npm.
Run tests with: pnpm test
Max line length: 100 characters.
```

### 7 Lifecycle Hooks

| Hook | When Fired | Use Case |
|------|-----------|----------|
| `PreTask` | Before agent starts | Load project context |
| `PostTask` | After agent finishes | Cleanup, notifications |
| `PreToolUse` | Before tool execution | Validation, approval |
| `PostToolUse` | After tool execution | Logging, side effects |
| `PreCompact` | Before context compression | Save important context |
| `PostCompact` | After context compression | Verify summary quality |
| `Checkpoint` | Periodic state save | Recovery points |

### Hook Implementation

```typescript
// .cliner/hooks/pre-tool-use.ts
export default async function hook(args: {
  tool: string;
  args: Record<string, any>;
}): Promise<{ cancel?: boolean; message?: string }> {
  // Block writes to protected paths
  if (args.tool === 'write' || args.tool === 'edit') {
    if (args.args.path.includes('.git/')) {
      return {
        cancel: true,
        message: 'Cannot modify files in .git directory'
      };
    }
  }

  // Require approval for bash commands
  if (args.tool === 'bash') {
    const dangerous = ['rm -rf', 'sudo', 'chmod'];
    if (dangerous.some(cmd => args.args.command.includes(cmd))) {
      // Will prompt user for approval
      return { /* proceed with approval flow */ };
    }
  }

  return {}; // Proceed
}
```

## Aider: CONVENTIONS.md

Simplest approach - just load a markdown file:

```markdown
<!-- CONVENTIONS.md -->
# Coding Conventions

## Python
- Use httpx instead of requests
- All functions need type hints
- Prefer dataclasses over dicts

## Testing
- Use pytest
- One test class per source class
- Mock external dependencies

## Git
- Conventional commits: feat/fix/docs/refactor
- Reference issue numbers in commits
```

```python
# Load with /read command
# User: /read CONVENTIONS.md
# Then it becomes part of context
```

## Three-Tier Memory Architecture

For sophisticated agents:

```python
from dataclasses import dataclass
from pathlib import Path
import json
from datetime import datetime

@dataclass
class Memory:
    """Three-tier memory system."""

    # Tier 1: Persistent KV (facts, preferences)
    kv_path: Path = Path.home() / ".agent" / "memory.json"

    # Tier 2: Session logs (full history)
    log_path: Path = Path.home() / ".agent" / "logs"

    # Tier 3: Vector search (semantic retrieval)
    vector_path: Path = Path.home() / ".agent" / "chroma"

    def get_fact(self, key: str) -> str | None:
        """Retrieve persistent fact."""
        if not self.kv_path.exists():
            return None
        data = json.loads(self.kv_path.read_text())
        return data.get(key)

    def set_fact(self, key: str, value: str):
        """Store persistent fact."""
        self.kv_path.parent.mkdir(parents=True, exist_ok=True)
        data = json.loads(self.kv_path.read_text()) if self.kv_path.exists() else {}
        data[key] = value
        self.kv_path.write_text(json.dumps(data, indent=2))

    def log_interaction(self, role: str, content: str):
        """Log interaction to JSONL."""
        self.log_path.mkdir(parents=True, exist_ok=True)
        log_file = self.log_path / f"{datetime.now().strftime('%Y-%m-%d')}.jsonl"
        with open(log_file, "a") as f:
            f.write(json.dumps({
                "timestamp": datetime.now().isoformat(),
                "role": role,
                "content": content
            }) + "\n")

    def search_related(self, query: str, k: int = 5) -> list[str]:
        """Semantic search over past interactions."""
        # Requires ChromaDB or similar
        try:
            import chromadb
            client = chromadb.PersistentClient(str(self.vector_path))
            collection = client.get_or_create_collection("memory")
            results = collection.query(query_texts=[query], n_results=k)
            return results["documents"][0]
        except ImportError:
            return []
```

## Best Practices

1. **Rules are context, not config** - Inject into prompts, don't parse
2. **Specificity wins** - "Use pnpm not npm" beats "use modern tools"
3. **Auto-memory needs limits** - Don't accumulate forever
4. **Skills load on demand** - Don't bloat initial context
5. **Version control rules** - Team shares via git