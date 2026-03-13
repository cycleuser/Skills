# Multi-Provider LLM Abstraction

## The Problem

Each LLM provider has different APIs:

| Provider | Messages | Tool Calls | Streaming |
|----------|----------|------------|-----------|
| OpenAI | `content: string` | `tool_calls[].function` | `choices[0].delta` |
| Anthropic | `content: blocks[]` | `content[].type=="tool_use"` | `content_block_delta` |
| Google | `contents[].parts[]` | `parts[].functionCall` | Different events |
| Ollama | OpenAI-compatible | OpenAI-compatible | OpenAI-compatible |

## Solution 1: Use Vercel AI SDK (OpenCode approach)

```typescript
import { generateText } from 'ai';
import { openai } from '@ai-sdk/openai';
import { anthropic } from '@ai-sdk/anthropic';
import { google } from '@ai-sdk/google';

// Unified interface across providers
const result = await generateText({
  model: openai('gpt-4o'), // or anthropic('claude-3-5-sonnet')
  messages: [...],
  tools: {
    read: { ... },
    write: { ... },
  },
});
```

Benefits:
- 20+ providers supported
- Unified message format
- Built-in streaming
- Tool calling normalized

## Solution 2: Manual Adapters (Cline approach)

More control, supports 44 providers:

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Iterator

@dataclass
class ChatMessage:
    role: str
    content: str | list[dict]

@dataclass
class ToolCall:
    id: str
    name: str
    arguments: dict

@dataclass
class ChatResponse:
    content: str
    tool_calls: list[ToolCall] | None
    usage: dict

class BaseLLMClient(ABC):
    @abstractmethod
    def chat(
        self,
        messages: list[ChatMessage],
        tools: list[dict] | None = None,
        **kwargs
    ) -> ChatResponse:
        pass

    @abstractmethod
    def chat_stream(
        self,
        messages: list[ChatMessage],
        tools: list[dict] | None = None,
        **kwargs
    ) -> Iterator[str]:
        pass

    def count_tokens(self, messages: list[ChatMessage]) -> int:
        """Default token counting, override for accuracy."""
        return sum(len(m.content) // 4 for m in messages)
```

### OpenAI Adapter

```python
from openai import OpenAI

class OpenAIAdapter(BaseLLMClient):
    def __init__(self, model: str = "gpt-4o", api_key: str | None = None):
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def chat(self, messages, tools=None, **kwargs) -> ChatResponse:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[self._format_message(m) for m in messages],
            tools=tools,
            **kwargs
        )

        choice = response.choices[0]
        tool_calls = None
        if choice.message.tool_calls:
            tool_calls = [
                ToolCall(
                    id=tc.id,
                    name=tc.function.name,
                    arguments=json.loads(tc.function.arguments)
                )
                for tc in choice.message.tool_calls
            ]

        return ChatResponse(
            content=choice.message.content or "",
            tool_calls=tool_calls,
            usage={
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
            }
        )

    def _format_message(self, msg: ChatMessage) -> dict:
        if isinstance(msg.content, str):
            return {"role": msg.role, "content": msg.content}
        return {"role": msg.role, "content": msg.content}

    def chat_stream(self, messages, tools=None, **kwargs) -> Iterator[str]:
        stream = self.client.chat.completions.create(
            model=self.model,
            messages=[self._format_message(m) for m in messages],
            tools=tools,
            stream=True,
            **kwargs
        )
        for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
```

### Anthropic Adapter

```python
from anthropic import Anthropic

class AnthropicAdapter(BaseLLMClient):
    def __init__(self, model: str = "claude-3-5-sonnet-20241022", api_key: str | None = None):
        self.client = Anthropic(api_key=api_key)
        self.model = model

    def chat(self, messages, tools=None, **kwargs) -> ChatResponse:
        # Anthropic requires separate system message
        system = None
        filtered_messages = []
        for m in messages:
            if m.role == "system":
                system = m.content
            else:
                filtered_messages.append(m)

        response = self.client.messages.create(
            model=self.model,
            max_tokens=kwargs.get("max_tokens", 4096),
            system=system,
            messages=[self._format_message(m) for m in filtered_messages],
            tools=self._format_tools(tools) if tools else None,
        )

        # Extract content and tool calls
        content = ""
        tool_calls = []
        for block in response.content:
            if block.type == "text":
                content += block.text
            elif block.type == "tool_use":
                tool_calls.append(ToolCall(
                    id=block.id,
                    name=block.name,
                    arguments=block.input
                ))

        return ChatResponse(
            content=content,
            tool_calls=tool_calls if tool_calls else None,
            usage={
                "prompt_tokens": response.usage.input_tokens,
                "completion_tokens": response.usage.output_tokens,
            }
        )

    def _format_message(self, msg: ChatMessage) -> dict:
        return {"role": msg.role, "content": msg.content}

    def _format_tools(self, tools: list[dict]) -> list[dict]:
        return [
            {
                "name": t["function"]["name"],
                "description": t["function"]["description"],
                "input_schema": t["function"]["parameters"]
            }
            for t in tools
        ]
```

### Ollama Adapter

```python
import httpx

class OllamaAdapter(BaseLLMClient):
    """Ollama uses OpenAI-compatible API."""

    def __init__(self, model: str = "llama3.2", base_url: str = "http://localhost:11434"):
        self.model = model
        self.base_url = base_url

    def chat(self, messages, tools=None, **kwargs) -> ChatResponse:
        # Use OpenAI-compatible endpoint
        response = httpx.post(
            f"{self.base_url}/v1/chat/completions",
            json={
                "model": self.model,
                "messages": messages,
                "tools": tools,
            },
            timeout=120.0
        )
        data = response.json()

        choice = data["choices"][0]
        return ChatResponse(
            content=choice["message"]["content"],
            tool_calls=self._parse_tool_calls(choice["message"]),
            usage=data.get("usage", {})
        )
```

## Client Factory

```python
class LLMClientFactory:
    PROVIDERS = {
        "openai": OpenAIAdapter,
        "anthropic": AnthropicAdapter,
        "google": GoogleAdapter,
        "ollama": OllamaAdapter,
        "deepseek": DeepSeekAdapter,  # OpenAI-compatible
    }

    @classmethod
    def create(cls, provider: str, model: str, **kwargs) -> BaseLLMClient:
        if provider not in cls.PROVIDERS:
            raise ValueError(f"Unknown provider: {provider}")

        return cls.PROVIDERS[provider](model=model, **kwargs)

    @classmethod
    def auto_detect(cls) -> list[str]:
        """Detect available providers."""
        available = []
        for provider in cls.PROVIDERS:
            try:
                if provider == "ollama":
                    resp = httpx.get("http://localhost:11434/api/tags", timeout=2)
                    if resp.status_code == 200:
                        available.append(provider)
                elif os.getenv(f"{provider.upper()}_API_KEY"):
                    available.append(provider)
            except:
                pass
        return available
```

## Provider Aliases

```python
ALIASES = {
    "claude": "anthropic",
    "gpt": "openai",
    "gemini": "google",
    "local": "ollama",
}

def resolve_provider(name: str) -> str:
    return ALIASES.get(name.lower(), name.lower())
```

## Usage

```python
# Create client
client = LLMClientFactory.create("openai", "gpt-4o")

# Use unified interface
response = client.chat(
    messages=[ChatMessage(role="user", content="Hello")],
    tools=TOOLS
)

if response.tool_calls:
    for tc in response.tool_calls:
        result = dispatch(tc.name, tc.arguments)
        # ...
```

## Best Practices

1. **Don't hardcode providers** - Use factory pattern
2. **Abstract message format** - Normalize before sending
3. **Handle streaming differently** - Each provider has unique event format
4. **Token counting varies** - Use provider-specific counters when available
5. **Rate limits differ** - Implement per-provider retry logic