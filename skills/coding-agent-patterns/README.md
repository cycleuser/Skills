# 编程代理模式

## 状态：Beta

## 用途
基于Claude Code、Codex、Cline、Aider、OpenCode五款主流AI编程代理的核心模式分析，涵盖核心循环、上下文管理、工具安全、多供应商抽象、记忆系统和会话持久化。

## 快速命令
| 命令 | 说明 |
|------|------|
| `/agent-patterns` | 查看编程代理模式（核心循环、上下文管理、工具安全、多供应商、记忆系统） |

## 适用场景
- 构建AI编程代理或助手
- 实现工具调用循环
- 管理LLM上下文窗口
- 设计多供应商LLM抽象层
- 设置代理记忆和技能系统

## 依赖
- 依赖 _shared/core/safety-rules.md

## 参见
- python-project-developer — ToolResult模式集成
- master-architect — 代理系统架构分解
- skill-manager — 技能注册模式

## 文件结构
```
skills/coding-agent-patterns/
├── README.md
├── SKILL.md
└── rules/
    ├── context-management.md
    ├── tool-safety.md
    ├── multi-provider.md
    └── memory-systems.md
```
