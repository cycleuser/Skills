# 技能创建模板 (Skill Creation Template)

以下是最小可工作技能的文件清单和模板。

---

## 目录结构

### 简单技能（规则 < 200 行）
```
skills/<name>/
├── README.md          # 面向人的中文说明（必需）
└── SKILL.md           # 技能定义，含 frontmatter + 规则 + 工作流（必需）
```

### 复杂技能（规则 > 200 行 / 有多维变体）
```
skills/<name>/
├── README.md          # 面向人的中文说明
├── SKILL.md           # 精简路由器（50-80行），声明路由协议
├── manifest.yaml      # 声明 axes、always_load、references.on_demand
├── static/
│   ├── core/          # 核心立场、工作流、输出格式
│   └── fragments/     # 按 axis value 加载的片段
└── references/        # 深层参考资料，按需加载
```

---

## SKILL.md 模板

### 简单技能

```markdown
---
name: <name>
version: "1.0.0"
description: |
  <一句话说明这个技能做什么、何时触发、主要输出格式和核心场景>

  Triggers when: <英文触发条件>

  Commands:
  - /command <args> - <说明>

  Capabilities: <能力列表>
author: cycleuser
license: MIT
status: Beta
---

## Safety Rules

参见 [_shared/core/safety-rules.md](../_shared/core/safety-rules.md)

# <技能标题>

<技能指令内容>

## Quick Commands

| Command | Description |
|---------|-------------|
| ... | ... |

## Anti-Patterns

| 违规 | 严重度 | 后果 |
|------|--------|------|
| ... | ... | ... |
```

### 路由器风格技能

```markdown
---
name: <name>
version: "1.0.0"
description: |
  <说明>
author: cycleuser
license: MIT
status: Beta
---

# <技能标题> — Router

This skill is split into two layers:
- **static layer**: 通过 manifest.yaml 声明的可复用内容片段
- **dynamic layer**: 本文件和 manifest.yaml，检测请求的轴并只加载当前任务需要的片段

Do not apply logic from memory. Always load fragments from disk.

## Routing Protocol

### 1. Load manifest and core layer
Read [manifest.yaml](manifest.yaml). Also read every file under `always_load`.

### 2. Detect axis values
For each axis in manifest, decide the value from user input.

### 3. Load matching fragments
For each axis value, Read the mapped file. Do NOT read every fragment.

### 4. Execute using loaded material
Apply loaded fragments in priority order.

### 5. Reach for references only when needed
Open `references/` files on demand per the `references.on_demand` table.
```

---

## manifest.yaml 模板

```yaml
name: <name>
version: 1.0.0
description: >
  Declarative manifest for the static/dynamic split.

always_load:
  - ../_shared/core/safety-rules.md
  - ../_shared/core/anti-aigc.md
  # Skill-local core
  - static/core/stance.md
  - static/core/workflow.md

axes:
  axis_name:
    detect: |
      How to detect the value from user input.
    values:
      value_a: static/fragments/axis_name/value_a.md
      value_b: static/fragments/axis_name/value_b.md
    default: value_a
    multi: false

references:
  on_demand:
    - condition: when to load
      path: references/file.md
    - condition: when to load
      path: references/another-file.md
```

---

## 状态标签

| 标签 | 含义 |
|------|------|
| `Draft` | 规则已定义，尚未在真实案例上测试 |
| `Beta` | 已在示例上测试，仍可能存在边界问题 |
| `Stable` | 已在真实内容上验证，规则相对稳定 |
| `Deprecated` | 不再推荐使用，将被移除或合并 |

---

## 文件清单

| 文件 | 是否必需 | 用途 |
|------|----------|------|
| `SKILL.md` | 必需 | frontmatter（name、description、status）+ 规则 + 工作流 |
| `README.md` | 必需 | 面向人的中文说明文档 |
| `manifest.yaml` | 复杂技能推荐 | 静态/动态分层声明 |
| `static/core/*.md` | 复杂技能推荐 | 核心立场、工作流、输出格式 |
| `static/fragments/**/*.md` | 复杂技能推荐 | 按轴值加载的片段 |
| `references/*.md` | 复杂技能推荐 | 深层参考材料，按需加载 |
| `rules/*.md` | 简单技能推荐 | 详细规则和模式，与 SKILL.md 并列 |

## 新技能创建流程

1. 在 `skills/` 下创建目录 `skills/<name>/`
2. 按上表创建必需文件
3. 更新 `skills.json` 中的技能注册表
4. 更新 `README.md` 中的技能索引表
5. 设置 `status: Draft` 直到真实验证
