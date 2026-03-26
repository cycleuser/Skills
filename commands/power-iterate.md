---
description: Power iterate - autonomous continuous work until budget exhausted
agent: build
---

Load the power-iterate skill and start autonomous iteration on: $ARGUMENTS

**Usage**: `/power-iterate <task> [options]`

**Examples**:
- `/power-iterate Build a REST API --time 60`
- `/power-iterate Develop complete feature --budget large`

**Budget options**:
- `--time <minutes>`: Time limit (default: 30)
- `--tokens <number>`: Token limit (default: 100000)
- `--budget <level>`: Preset budget (tiny/small/medium/large/xlarge)

**Features**: Autonomous execution, no confirmation needed, continuous work until budget exhausted.