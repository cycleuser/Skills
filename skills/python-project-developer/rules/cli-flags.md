# CLI Implementation Details

## Required Flags Specification

### 1. Version (-V, --version)

```python
parser.add_argument(
    "-V", "--version",
    action="version",
    version=f"toolname {__version__}",
)
```

**Rules:**
- MUST use `action="version"`
- NEVER use `store_true` + manual print
- Version string should include tool name

### 2. Verbose (-v, --verbose)

```python
parser.add_argument(
    "-v", "--verbose",
    action="store_true",
    help="Verbose output",
)
```

**Exception:** If `-v` is used by another flag (e.g., `--voice`), use only `--verbose`.

### 3. Output (-o, --output)

```python
parser.add_argument(
    "-o", "--output",
    type=pathlib.Path,
    help="Output path",
)
```

### 4. JSON Output (--json)

```python
parser.add_argument(
    "--json",
    action="store_true",
    dest="json_output",  # REQUIRED: avoid conflict with json module
    help="Output results as JSON",
)
```

**Critical:** `dest="json_output"` is mandatory to avoid shadowing the `json` builtin.

### 5. Quiet (-q, --quiet)

```python
parser.add_argument(
    "-q", "--quiet",
    action="store_true",
    help="Suppress non-essential output",
)
```

## Help Formatter

Always use `RawDescriptionHelpFormatter` for proper epilog formatting:

```python
parser = argparse.ArgumentParser(
    prog="toolname",
    description="Tool description",
    formatter_class=argparse.RawDescriptionHelpFormatter,
    epilog="""
Examples:
  toolname input.txt
  toolname input.txt -o output.json
  toolname input.txt --json
""",
)
```

## Subcommands Pattern

For complex tools with multiple modes:

```python
subparsers = parser.add_subparsers(dest="command", required=True)

# Subcommand: search
search_parser = subparsers.add_parser("search", help="Search for items")
search_parser.add_argument("query", help="Search query")

# Subcommand: download
download_parser = subparsers.add_parser("download", help="Download items")
download_parser.add_argument("url", help="URL to download")
```

## Exit Code Contract

| Code | Meaning | When to Use |
|------|---------|-------------|
| 0 | Success | Operation completed |
| 1 | Runtime error | File not found, API error |
| 2 | Invalid args | argparse handles automatically |

## Logging Integration

```python
def setup_logging(verbose: bool, quiet: bool):
    level = logging.INFO
    if quiet:
        level = logging.WARNING
    elif verbose:
        level = logging.DEBUG

    logging.basicConfig(
        level=level,
        format="%(levelname)s: %(message)s",
    )
```

## Entry Point Pattern

```python
def main():
    args = parse_args()
    setup_logging(args.verbose, args.quiet)

    try:
        result = run_core_logic(args)
        if args.json_output:
            print(json.dumps(result.to_dict()))
        sys.exit(0)
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
```

## __main__.py

```python
# package_name/__main__.py
from .cli import main

main()
```

Enables: `python -m package_name`