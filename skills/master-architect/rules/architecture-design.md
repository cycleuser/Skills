# Architecture Design Patterns

## Architectural Styles

### 1. Layered Architecture

```
┌─────────────────────────────────┐
│        Presentation Layer       │
├─────────────────────────────────┤
│        Business Logic Layer     │
├─────────────────────────────────┤
│        Data Access Layer        │
├─────────────────────────────────┤
│        Database Layer           │
└─────────────────────────────────┘
```

**Use When:** Traditional enterprise applications

### 2. Modular Architecture

```
┌─────────┐  ┌─────────┐  ┌─────────┐
│ Module A│  │ Module B│  │ Module C│
└────┬────┘  └────┬────┘  └────┬────┘
     │            │            │
     └────────────┼────────────┘
                  │
           ┌──────▼──────┐
           │    Core     │
           └─────────────┘
```

**Use When:** Tools with CLI/GUI/Web interfaces

### 3. Microservices Architecture

```
┌─────────┐  ┌─────────┐  ┌─────────┐
│ Service │  │ Service │  │ Service │
│    A    │  │    B    │  │    C    │
└────┬────┘  └────┬────┘  └────┬────┘
     │            │            │
     └────────────┼────────────┘
                  │
           ┌──────▼──────┐
           │ API Gateway │
           └─────────────┘
```

**Use When:** Large-scale distributed systems

## Module Design Principles

### Single Responsibility Principle

Each module should have one reason to change.

```
Good:
- cli.py: Only handles command-line parsing
- core.py: Only contains business logic
- api.py: Only provides API wrapper

Bad:
- main.py: Handles CLI, business logic, and API
```

### Interface Segregation

Define minimal, focused interfaces.

```python
# Good: Focused interface
class FileReader:
    def read(self, path: str) -> str: ...

# Bad: Bloated interface
class FileHandler:
    def read(self, path: str) -> str: ...
    def write(self, path: str, content: str): ...
    def delete(self, path: str): ...
    def move(self, src: str, dst: str): ...
```

### Dependency Inversion

Depend on abstractions, not concretions.

```python
# Good: Depend on abstraction
class DataProcessor:
    def __init__(self, storage: StorageInterface):
        self.storage = storage

# Bad: Depend on concrete implementation
class DataProcessor:
    def __init__(self):
        self.storage = SQLDatabase()  # Hardcoded dependency
```

## Interface Design

### API Design Pattern

```python
# Standard API function signature
def module_action_noun(
    *,
    required_param: str,
    optional_param: str = "default",
) -> ToolResult:
    """
    Perform action on noun.
    
    Args:
        required_param: Description
        optional_param: Description
        
    Returns:
        ToolResult with success status
    """
    pass
```

### CLI Design Pattern

```python
# Standard CLI argument structure
def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(...)
    
    # Unified flags (required)
    parser.add_argument("-V", "--version", ...)
    parser.add_argument("-v", "--verbose", ...)
    parser.add_argument("-o", "--output", ...)
    parser.add_argument("--json", ...)
    parser.add_argument("-q", "--quiet", ...)
    
    # Module-specific arguments
    parser.add_argument("--specific-option", ...)
    
    return parser
```

## Architecture Decision Records

### ADR Template

```markdown
# ADR-NNN: [Decision Title]

## Status
[Proposed | Accepted | Deprecated | Superseded]

## Context
[What is the issue that we're seeing that motivates this decision?]

## Decision
[What is the change that we're proposing and/or doing?]

## Consequences
[What becomes easier or more difficult because of this change?]

## Alternatives Considered
[What other options were considered?]
```

## Architecture Review Checklist

- [ ] All modules have single responsibility
- [ ] All interfaces are minimal and focused
- [ ] All dependencies are explicit
- [ ] No circular dependencies
- [ ] Clear layer boundaries
- [ ] Error handling strategy defined
- [ ] Logging strategy defined
- [ ] Configuration management defined
- [ ] Security considerations documented
- [ ] Performance requirements addressed