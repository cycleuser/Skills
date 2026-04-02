---
description: 启动项目重建流程
agent: build
---

Load the project-rebuilder skill and execute: analyze reference project "$ARGUMENTS", create rebuild plan, start team review process, and begin ralph persistent execution mode.

**用法**: `/rebuild <参考项目> <目标>`

**示例**:
- `/rebuild https://github.com/apache/flink 流处理核心引擎`
- `/rebuild vscode 轻量级代码编辑器`

**功能**: 分析参考项目，提取核心特性，制定重建计划，启动 team 并行审查和 ralph 持久执行。
