# `_shared/` — Skills 共享层

本目录**不是独立技能**。不含 `SKILL.md`，不被 skill-manager 注册。作用是存放多个技能共同依赖的参考内容，避免在不同技能目录中重复维护同一套材料。

同级技能通过 `manifest.yaml` 中的相对路径引用这里的文件：

```yaml
always_load:
  - ../_shared/core/safety-rules.md
  - ../_shared/core/anti-aigc.md
```

## 当前内容

| 文件 | 使用方 | 用途 |
|------|--------|------|
| `core/safety-rules.md` | 所有技能 | 通用 bash 安全规则，所有技能从 _shared 加载而非各自复制粘贴 |
| `core/anti-aigc.md` | 所有技能 | AIGC 检测反制通用规则，各技能在其 `rules/anti-aigc.md` 中扩展专属规则 |
| `core/design-principles.md` | 所有技能 | 共享设计原则：一手来源、显式胜过隐式、上下文感知、输出优先、可扩展 |
| `core/skill-template.md` | 新技能创建 | 技能创建模板、文件清单、状态标签规范 |
| `core/manifest-template.yaml` | 复杂技能 | 静态/动态分层 manifest 模板，声明 axes、always_load、references.on_demand |
| `memory/` | 所有技能 | **共享记忆系统** — per-skill 持久化 key-value 存储，跨会话状态保持。详见 `memory/README.md` |

## 何时放入 `_shared/`

仅当**两个或更多技能**需要复用同一份内容时，才放入 `_shared/`。单一技能的参考材料保留在技能自身的 `static/`、`references/` 或 `rules/` 目录中。

## 何时保持在技能内局部

`_shared/` 只放**定义和参考材料**（安全规则、设计原则、AIGC 反制规则、模板）。具体技能如何诊断、执行、输出，保留在各技能内部。
