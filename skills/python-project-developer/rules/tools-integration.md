# Function-Calling Patterns

## TOOLS Definition Format

Strict OpenAI API schema compliance:

```python
TOOLS: list[dict] = [
    {
        "type": "function",
        "function": {
            "name": "projectname_action_noun",
            "description": "Clear English description of what the tool does",
            "parameters": {
                "type": "object",
                "properties": {
                    "param_name": {
                        "type": "string",  # string | integer | number | boolean
                        "description": "Parameter description",
                    },
                    "optional_param": {
                        "type": "string",
                        "description": "Optional parameter",
                        "default": "default_value",
                    },
                    "enum_param": {
                        "type": "string",
                        "description": "Enum parameter",
                        "enum": ["option1", "option2", "option3"],
                    },
                },
                "required": ["param_name"],
            },
        },
    },
]
```

## Naming Convention

Pattern: `{projectname_lower}_{verb}_{noun}`

| Project | Tool Name |
|---------|-----------|
| chou | `chou_rename_papers` |
| huan | `huan_archive_site` |
| lapian | `lapian_transcode` |
| copytalker | `copytalker_translate` |

**Multi-word project names:** Keep lowercase and continuous (e.g., `copytalker`, not `copy_talker`).

## Dispatch Function

```python
import json
from typing import Any

def dispatch(name: str, arguments: dict[str, Any] | str) -> dict:
    """Dispatch tool call to appropriate API function.

    Args:
        name: Tool name from LLM response.
        arguments: Tool arguments (dict or JSON string).

    Returns:
        Dict representation of ToolResult.

    Raises:
        ValueError: Unknown tool name.
    """
    # Handle JSON string arguments
    if isinstance(arguments, str):
        arguments = json.loads(arguments)

    # Dispatch to API function
    if name == "projectname_action_noun":
        from .api import action_noun
        result = action_noun(**arguments)
        return result.to_dict()

    if name == "projectname_another_action":
        from .api import another_action
        result = another_action(**arguments)
        return result.to_dict()

    raise ValueError(f"Unknown tool: {name}")
```

## Usage Pattern

```python
from openai import OpenAI
from projectname.tools import TOOLS, dispatch

client = OpenAI()

# Create chat with tools
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "user", "content": "Process this file: data.txt"}
    ],
    tools=TOOLS,
)

# Handle tool calls
message = response.choices[0].message
if message.tool_calls:
    for tool_call in message.tool_calls:
        result = dispatch(
            tool_call.function.name,
            tool_call.function.arguments
        )

        # Feed result back to LLM
        messages.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": json.dumps(result)
        })

    # Continue conversation
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        tools=TOOLS,
    )
```

## Multiple Tools Example

```python
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "projectname_read_file",
            "description": "Read contents of a file",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "File path"}
                },
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "projectname_write_file",
            "description": "Write content to a file",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "File path"},
                    "content": {"type": "string", "description": "Content to write"},
                },
                "required": ["path", "content"],
            },
        },
    },
]

def dispatch(name: str, arguments: dict | str) -> dict:
    if isinstance(arguments, str):
        arguments = json.loads(arguments)

    if name == "projectname_read_file":
        from .api import read_file
        return read_file(**arguments).to_dict()

    if name == "projectname_write_file":
        from .api import write_file
        return write_file(**arguments).to_dict()

    raise ValueError(f"Unknown tool: {name}")
```

## Description Best Practices

- Write in English, even for Chinese projects
- Be specific about what the tool does
- Include what it returns
- Mention any side effects

**Good:**
```
"Read the contents of a file and return it as a string. Returns error if file does not exist."
```

**Bad:**
```
"Reads a file."
```