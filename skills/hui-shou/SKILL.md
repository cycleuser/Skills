---
name: hui-shou
version: "1.0.0"
description: |
  File-operation logging and safe-recovery skill. Intercepts destructive file
  operations (rm/mv/truncate/overwrite) BEFORE they happen, moves the endangered
  content into a per-project trash with an append-only JSONL manifest, and
  restores deleted or overwritten files with SHA-256 integrity verification.

  Triggers when: User is about to delete/move/overwrite files, asks to recover a
  deleted file, wants a file-operation audit log, suspects accidental deletion,
  or needs to guard a destructive batch operation.

  Commands:
  - /回收 delete <路径> - 删除前先入回收站（防误删）
  - /回收 overwrite <路径> - 覆盖前先备份旧内容
  - /回收 move <src> <dst> - 移动/重命名并记录
  - /回收 list [过滤] - 列出回收站条目
  - /回收 log [N] - 查看最近 N 条操作日志
  - /回收 restore <id|路径|pattern> - 恢复到原位或指定位置
  - /回收 inspect <id> - 查看某条目的元数据与校验和
  - /回收 purge [天数] - 清理 N 天前的条目（需确认）
  - /回收 watch - 列出当前会话受守护的操作
  - /回收 guard on|off - 开关守护模式
  - /trash delete <path> - English command for safe delete
  - /trash list [filter] - List trash entries
  - /trash restore <id|path|pattern> - Restore deleted/overwritten file
  - /trash log [N] - Show recent N operation log entries
  - /trash purge [days] - Purge entries older than N days

  Capabilities: Pre-deletion interception with atomic move-to-trash, append-only
  JSONL manifest with SHA-256 checksums, stable recovery to original or custom
  location with integrity verification, overwrite snapshotting, move/rename
  logging, per-project isolation, configurable age-based purge with confirmation,
  guard-mode toggle for session-wide destructive-command routing.

author: cycleuser
license: MIT
status: Beta
---

## Safety Rules

参见 [_shared/core/safety-rules.md](../_shared/core/safety-rules.md) — 所有安全规则从共享层加载。

关键补充：**任何破坏性文件操作必须先入回收站，再执行**。本技能存在的意义就是让 `rm`、覆盖写、`mv` 覆盖都不再不可逆。守护模式开启时，禁止直接调用裸 `rm`/`mv -f`/`>` 截断。

# 回收 (HuiShou / File-Operation Logger & Safe Recovery)

文件操作日志与误删除恢复技能。核心原则：**先回收，后删除；有日志，可恢复**。

The one rule that matters: **no destructive file operation is irreversible. Move
endangered content into a per-project trash with a manifest FIRST, then execute.**

## Quick Commands

| Command | 说明 / Description |
|---------|-------------|
| `/回收 delete <路径>` | 删除前先入回收站（防误删）/ Safe delete via trash |
| `/回收 overwrite <路径>` | 覆盖写入前先备份旧内容 / Snapshot before overwrite |
| `/回收 move <src> <dst>` | 移动并记录 / Move with manifest entry |
| `/回收 list [过滤]` | 列出回收站条目 / List trash entries |
| `/回收 log [N]` | 查看最近 N 条操作日志 / Show recent N log entries |
| `/回收 restore <id\|路径\|pattern>` | 恢复到原位或指定位置 / Restore deleted/overwritten file |
| `/回收 inspect <id>` | 查看条目元数据与校验和 / Inspect entry metadata & checksum |
| `/回收 purge [天数]` | 清理 N 天前的条目（需确认）/ Purge old entries |
| `/回收 watch` | 列出本会话受守护的操作 / List guarded ops this session |
| `/回收 guard on\|off` | 开关守护模式 / Toggle guard mode |
| `/trash delete <path>` | Safe delete via trash |
| `/trash list [filter]` | List trash entries |
| `/trash restore <id\|path\|pattern>` | Restore deleted/overwritten file |
| `/trash log [N]` | Show recent N log entries |
| `/trash purge [days]` | Purge entries older than N days |

## 核心理念 / Core Philosophy

一次误删一个 `rm -rf` 就能让数小时的工作消失。本技能把"删除"变成两步可逆操作：

1. **先回收，后删除**。任何 `rm`/`mv` 覆盖/`>` 截断之前，先把待破坏的内容原子地移进项目级回收站，并在 append-only 日志里登记一条。删除动作只在回收成功之后执行。
2. **日志即真相**。所有破坏性操作进 append-only JSONL 清单（`manifest.jsonl`），记录时间、原路径、操作类型、内容大小、SHA-256。日志永不原地改写，只能追加和 purge。
3. **恢复可验证**。恢复时按 SHA-256 校验内容完整性，写回原位或指定位置；原位已存在则拒绝覆盖，必须显式 `--force`。

三条铁律：

1. **不可逆操作前置守护**。守护模式（默认开）下，禁止裸 `rm`/`mv -f`/`>` 截断。一律走 `trash.py delete/overwrite/move` 子命令。
2. **回收站项目隔离**。每个项目（按 cwd 哈希）独立回收站目录，互不污染。回收站根：`~/.opencode-trash/<project-slug>/`。
3. **恢复优先于清理**。purge 必须二次确认，且默认只清 N 天前的条目；未指定天数则默认 30 天。永不自动 purge 未恢复且近期的条目。

## 回收站布局 / Trash Layout

```
~/.opencode-trash/
└── <project-slug>/                  # 按 cwd 的 SHA-1 前 12 位 + 末段目录名
    ├── manifest.jsonl               # append-only 操作日志，每行一条
    ├── entries/
    │   └── <id>/                    # id = 时间戳+短随机
    │       └── <basename>           # 被回收的内容（原文件名）
    └── guard.lock                   # 守护模式开关（存在=开）
```

- `manifest.jsonl` 每行一个 JSON 对象，字段见 [rules/manifest-format.md](rules/manifest-format.md)。
- 内容用**移动**（`rename`）入站，原子且免费；若跨设备则降级为复制+删除原文件，复制失败则拒绝删除并报错。
- 大文件（> `MAX_INLINE_BYTES`，默认 256 MiB）只在日志登记路径与校验和，内容留在原位并标记 `large=true`，恢复时按路径回拷；purge 时不删原文件。

## 工作流 / Workflow

```
Step 0  守护 Guard
  守护模式开（默认）→ 任何 rm/mv/truncate 前调用 trash.py 子命令
  守护模式关 → 裸命令可用，但仍建议走 trash.py（/回收 guard off 临时放行）

Step 1  回收 Collect（delete/overwrite/move）
  trash.py delete <path>:
    1) 校验 path 存在
    2) 生成 id，move path → entries/<id>/<basename>（跨设备则 copy+unlink）
    3) 计算 sha256、size，append 一行到 manifest.jsonl
    4) 原路径已不存在 → 删除完成；返回 id
  trash.py overwrite <path>:
    1) path 存在 → 先 delete 入站（同上）
    2) 返回 id；调用方随后可安全写入新内容
  trash.py move <src> <dst>:
    1) 若 dst 存在 → 先 delete dst 入站
    2) rename src→dst；记录 move 条目（src→dst，无内容回收）
    3) 失败回滚：从回收站还原 dst

Step 2  日志 Log（list/log/inspect）
  trash.py list [filter]  → 按 op/路径正则/天数过滤，打印表格
  trash.py log [N]        → 最近 N 条（默认 20）
  trash.py inspect <id>   → 单条元数据 + 校验和复核

Step 3  恢复 Restore
  trash.py restore <id|path|pattern> [--to <dest>] [--force]
    1) 在 manifest 中定位条目（精确 id / 原路径 / 通配 pattern）
    2) 校验 entries/<id>/<basename> 的 sha256 与日志一致
    3) 默认恢复到原 src 路径；--to 指定新位置
    4) 目标已存在且非 --force → 拒绝覆盖，报错
    5) 复制内容到目标，标记 restored=true，append 一条 restore 记录
    6) 默认不从回收站移除内容（可再次恢复）；--consume 则恢复后删除条目

Step 4  清理 Purge
  trash.py purge [days] [--confirm]
    1) days 默认 30；列出将删条目（id/原路径/时间/大小）
    2) 未带 --confirm → 只预览，不执行
    3) 带 --confirm → 删除 entries/<id> 与对应 manifest 行？
       注意：manifest.jsonl 是 append-only，purge 不改原文件，
       而是写一个 tombstone 行（op=purged），并物理删除 entries/<id>/ 内容
```

## 关键实现要点 / Key Implementation Notes

- **原子性**：跨设备 `rename` 会 `EXDEV`，需降级为 `shutil.copy2` + `os.unlink`，且 copy 失败必须保留原文件并报错，绝不"删了再说"。
- **append-only 日志**：`manifest.jsonl` 只以 `a` 模式打开；purge/restore 不改写历史行，只追加新行（restore 加 `op=restored`，purge 加 `op=purged` tombstone）。查询时跳过 `purged` 行。
- **SHA-256 双向校验**：入站时算一次写入日志；恢复时再算一次比对，防回收站被外部篡改或磁盘损坏。
- **并发安全**：对 `manifest.jsonl` 的追加用 `fcntl.flock` 排他锁；跨进程可靠。
- **路径相对化**：日志里同时存 `src`（原始绝对路径）与 `src_rel`（相对项目根），便于项目迁移后恢复。
- **空目录与目录树**：`delete` 对目录用 `shutil.copytree` 入站（保留树结构），恢复时回建；空目录也要登记（size=0）。

详见 [scripts/trash.py](scripts/trash.py) —— 可复用的回收/恢复/日志/purge 工具。

## Rules

- [rules/workflow.md](rules/workflow.md) - 完整四步工作流与命令行操作
- [rules/manifest-format.md](rules/manifest-format.md) - manifest.jsonl 字段定义与 append-only 语义
- [rules/guard-patterns.md](rules/guard-patterns.md) - 守护模式：哪些命令必须先入回收站
- [rules/recovery.md](rules/recovery.md) - 恢复策略、冲突处理与校验流程
- [rules/anti-aigc.md](rules/anti-aigc.md) - 日志与恢复报告的反AIGC规则

## 使用示例 / Examples

### 示例 1：安全删除一个文件

```
用户/User: /回收 delete ./src/old_module.py

→ trash.py delete ./src/old_module.py
→ 已移动到回收站，id=20260729-1530-a1b2
→ manifest.jsonl 追加一条 delete 记录
→ 原路径已不存在，删除完成
→ 可用 /回收 restore 20260729-1530-a1b2 恢复
```

### Example 2: Recover a deleted file

```
用户/User: /回收 restore old_module

→ trash.py restore old_module
→ 匹配 1 条：id=20260729-1530-a1b2 src=./src/old_module.py
→ SHA-256 校验通过
→ 恢复到 ./src/old_module.py（已存在？否）
→ 完成；回收站保留原件可再次恢复
```

### 示例 3：覆盖前先备份

```
用户/User: 我要改写 config.yaml

→ 守护模式检测到覆盖写
→ trash.py overwrite ./config.yaml
  → 旧 config.yaml 入站，id=20260729-1600-c3d4
  → 返回 id，随后可安全写入新内容
→ 写入完成后，/回收 list 可见旧版本可随时回滚
```

### 示例 4：批量误删后整体恢复

```
用户/User: 我刚才 rm -rf 误删了整个 tests/ 目录！

→ 若守护模式曾开：/回收 list tests
  → 列出所有 src 含 tests/ 的条目
→ /回收 restore 'tests/**' --to ./restored_tests/
  → 逐条校验恢复到 restored_tests/ 保持原树结构
→ 若守护模式当时关：只能从 git/Time Machine 恢复（本技能无力回天）
```

## 边界情况 / Edge Cases

- **跨设备回收**：`rename` 抛 `EXDEV` → 降级 `copy2+unlink`；copy 失败则**保留原文件并报错**，绝不静默删除。
- **符号链接**：回收链接本身（不解析目标）；恢复时重建同指向的符号链接。
- **大文件（>256 MiB）**：内容留原位，日志记 `large=true` 与路径；purge 时不删原文件，只置 tombstone。
- **同名文件多次删除**：每次独立 id、独立 entries 子目录，互不覆盖；恢复按 id 精确定位，按路径则匹配最近一条。
- **目录树删除**：用 `copytree` 入站保留结构；恢复时 `copytree` 回建，目标已存在则 `--force` 合并或拒绝。
- **空文件/空目录**：照常登记（size=0），恢复时回建空文件/空目录。
- **权限/时间戳保留**：入站用 `shutil.copy2` 保留元数据；恢复同样 `copy2` 回写。
- **项目迁移后恢复**：`src` 是绝对路径可能失效，优先用 `src_rel` 相对项目根恢复；`--to` 显式指定最稳。
- **manifest 损坏行**：读取时跳过无法解析的行并记录告警，不中断整体恢复。
- **守护模式被关时的裸 rm**：本技能无法回溯；明确告知用户"守护模式关期间的裸删除不可恢复"，建议常开。

## 常见问题排查 / Troubleshooting

- **恢复后内容对不上** → 校验和失败，回收站被外部改动或磁盘损坏；检查 `inspect <id>` 的 sha256，必要时从备份恢复。
- **manifest.jsonl 越来越大** → 用 `/回收 purge 30 --confirm` 清理 30 天前条目；purge 只加 tombstone 不改历史行，物理删内容。
- **跨项目误收** → 回收站按 cwd 隔离；若在错的项目下删除，去 `~/.opencode-trash/<其他project-slug>/` 找。
- **`rename` 报 EXDEV** → 回收站与项目不在同一卷；trash.py 已自动降级 copy+unlink，无需干预。
- **守护模式忘记开** → `/回收 guard on` 重开；本次会话内已生效。重启会话默认仍为开。
- **恢复目标已存在** → 默认拒绝覆盖防二次破坏；加 `--force` 覆盖（会先把目标也入回收站再写）。

## 配置选项 / Configuration

| 参数/Param | 默认值/Default | 说明/Description |
|-----------|---------------|-----------------|
| trash_root | `~/.opencode-trash` | 回收站根目录 / Trash root |
| guard_default | on | 守护模式默认开关 / Default guard state |
| max_inline_bytes | 268435456 | 超此大小不内联回收 / Large-file threshold (256 MiB) |
| purge_default_days | 30 | 默认清理天数 / Default purge age |
| keep_restored | true | 恢复后保留回收件 / Keep trash copy after restore |
| manifest_name | `manifest.jsonl` | 日志文件名 / Manifest filename |

## 集成 / Integration

### 与安全规则集成 / Safety Integration

```
任何破坏性文件操作 / Any destructive op:
    ↓
守护模式? / Guard on?
    ├─ 是 → 路由到 trash.py / Route to trash.py
    │       ↓
    │       回收+登记 → 执行删除 / Collect+log → execute
    └─ 否 → 警告后放行裸命令 / Warn then allow raw
    ↓
可恢复 / Recoverable
```

### 与其他技能集成 / Skill Integration

```
/安检 an-jian 检测到 rm -rf
    ↓
建议启用 /回收 guard on
    ↓
破坏性操作改走 /回收 delete
    ↓
误删后 /回收 restore
```

## Anti-Patterns

| 违规 / Violation | 严重度 / Severity | 后果 / Consequence |
|------|--------|------|
| 守护模式下裸 `rm` / Raw `rm` under guard | 高/High | 不可恢复，绕过日志 / Irreversible, bypasses log |
| 直接改写 `manifest.jsonl` 历史行 / Edit manifest history | 严重/Critical | 审计链断裂 / Audit chain broken |
| 恢复时不校验 SHA-256 / Skip checksum on restore | 高/High | 可能恢复损坏内容 / May restore corrupt content |
| purge 不带 `--confirm` 即执行 / Purge without confirm | 高/High | 误清近期可恢复件 / Wipes recent recoverable items |
| 跨设备 copy 失败仍删原文件 / Unlink after copy fail | 严重/Critical | 数据永久丢失 / Permanent data loss |
| 回收站与项目同卷却用 copy / Copy instead of rename | 低/Low | 浪费 IO / Wasted IO |

## AIGC检测意识 / AIGC-Aware Output

回收/恢复报告必须给出具体 id、路径、校验和、大小，不写"已安全处理"这类空话。参见 [rules/anti-aigc.md](rules/anti-aigc.md)。

核心要求：
- 不写"文件已恢复"，写"恢复 id=20260729-1530-a1b2 → ./src/old_module.py，SHA-256 `a1b2…` 校验通过，4287 字节"
- purge 预览必须列出具体 id 与原路径，不写"已清理旧条目"

## 版本历史 / Version History

| 版本 | 日期 | 变更 |
|------|------|------|
| 1.0.0 | 2026-07-29 | 初始版本：delete/overwrite/move 回收、append-only 日志、SHA-256 恢复、purge、守护模式 |

## See Also / 相关技能

- `/安检` from **an-jian** — 检测技能中的 `rm -rf` 等危险模式，建议配合本技能守护
- `/把关` from **ba-guan** — 发布前审查，破坏性操作应先过本技能
- `global-rules` — 通用 `rm -rf` 防护规则，本技能是其可逆化落地