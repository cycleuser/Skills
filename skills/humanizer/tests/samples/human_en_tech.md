## Install

Requires Python 3.10 or newer. Install from PyPI:

```bash
pip install humanize-lint
```

The CLI reads from a file or stdin and prints a JSON report:

- `--lang` forces zh or en; auto-detection is the default.
- `--profile` switches thresholds for prose, tech, or academic text.
- `--max-score` sets the exit-code threshold for CI.

Exit code is 1 when the score exceeds the threshold, 0 otherwise.
