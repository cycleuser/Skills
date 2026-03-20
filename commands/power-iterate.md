---
description: Power iterate - autonomous continuous work until time or token limit
agent: build
---

Load the power-iterate skill and start autonomous iteration on: $ARGUMENTS

Follow the power-iterate workflow:
1. Deep task decomposition
2. Create prioritized work queue
3. Execute continuously without user confirmation
4. Track time and token budgets
5. Report progress periodically
6. Save all progress when budget is exhausted

Budget options:
- --time <minutes>: Time limit (default: 30)
- --tokens <number>: Token limit (default: 100000)
- --budget <level>: Preset budget (tiny/small/medium/large/xlarge)

Example: /power-iterate Build a REST API --time 60 --tokens 100000
