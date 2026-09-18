# 回收 (HuiShou)

## 状态：Beta

## 用途

文件操作日志与误删除恢复技能。任何破坏性文件操作（`rm`/`mv` 覆盖/`>` 截断）执行前，先把待破坏内容原子地移入项目级回收站并登记 append-only 日志（含 SHA-256），让删除变成可逆的两步操作。误删后可按 id/路径/通配符恢复，校验和验证完整性。

核心一句话：先回收，后删除；有日志，可恢复。

## 快速命令

| 命令 | 说明 |
|------|------|
| `/回收 delete <路径>` | 删除前先入回收站（防误删） |
| `/回收 overwrite <路径>` | 覆盖写入前先备份旧内容 |
| `/回收 move <src> <dst>` | 移动/重命名并记录 |
| `/回收 list [过滤]` | 列出回收站条目 |
| `/回收 log [N]` | 查看最近 N 条操作日志 |
| `/回收 restore <id\|路径\|pattern>` | 恢复到原位或指定位置 |
| `/回收 inspect <id>` | 查看条目元数据与校验和 |
| `/回收 purge [天数]` | 清理 N 天前条目（需 `--confirm`） |
| `/回收 guard on\|off` | 开关守护模式 |
| `/trash delete <path>` | Safe delete via trash (English) |
| `/trash restore <id\|path\|pattern>` | Restore deleted/overwritten file |
| `/trash list [filter]` | List trash entries |
| `/trash log [N]` | Show recent N log entries |
| `/trash purge [days]` | Purge old entries |

## 适用场景

- 任何需要执行 `rm`/`mv -f`/`>` 覆盖写之前，确保可回滚
- 误删文件后立即恢复（守护模式曾开过）
- 批量重构/重命名时保留旧版本审计链
- 需要文件操作可追溯、可审计的项目
- 防止 `rm -rf` 一次误删清空工作

## 为什么需要它

一次裸 `rm -rf` 就能让数小时工作消失。本技能把"删除"变成两步可逆：先入回收站登记（SHA-256），再执行删除。恢复时校验完整性，写回原位或指定位置；目标已存在默认拒绝覆盖防二次破坏。append-only 日志永不改写历史，purge 只加 tombstone。

## 四步工作流

1. **守护** Guard：守护模式（默认开）下破坏性命令改走 `/回收`
2. **回收** Collect：`delete`/`overwrite`/`move` 把内容原子移入回收站并登记日志
3. **日志** Log：`list`/`log`/`inspect` 查询条目与校验和
4. **恢复** Restore：按 id/路径/通配符恢复，SHA-256 校验，冲突不覆盖
5. **清理** Purge：`purge [天数]` 预览 + `--confirm` 执行（默认 30 天）

## 回收站布局

```
~/.opencode-trash/<project-slug>/
├── manifest.jsonl      # append-only 操作日志
├── entries/<id>/<name> # 被回收的内容
└── guard.lock          # 守护模式开关
```

项目隔离：每个项目（按 cwd 的 SHA-1 前 12 位 + 末段目录名）独立回收站。

## 依赖

- Python 3.8+（仅标准库，无第三方依赖）
- 依赖 `_shared/core/safety-rules.md`

## 安全原则

- **任何破坏性操作必须先入回收站，再执行**；守护模式禁止裸 `rm`/`mv -f`/`>` 截断
- **append-only 日志永不改写**；purge/restore 只追加新行
- **恢复时必须校验 SHA-256**，不一致拒绝恢复
- **恢复冲突默认不覆盖**，需显式 `--force`（会先把目标也入站）
- **跨设备 copy 失败绝不删原文件**
- **purge 需二次确认**（`--confirm`），默认只清 30 天前条目
- 大文件（>256 MiB）内容留原位，只登记路径与校验和

## 文件结构

```
skills/hui-shou/
├── README.md
├── SKILL.md
├── rules/
│   ├── workflow.md          # 四步工作流与命令行操作
│   ├── manifest-format.md   # manifest.jsonl 字段定义与 append-only 语义
│   ├── guard-patterns.md    # 守护模式：哪些命令必须先入回收站
│   ├── recovery.md          # 恢复策略、冲突处理与校验流程
│   └── anti-aigc.md         # 日志与恢复报告反AIGC规则
└── scripts/
    └── trash.py            # 回收/恢复/日志/purge 工具（纯标准库）
```

## 参见

- `/安检` from **an-jian** — 检测危险 `rm -rf` 模式，建议配合本技能守护
- `/把关` from **ba-guan** — 发布前审查，破坏性操作应先过本技能
- `global-rules` — 通用 `rm -rf` 防护规则，本技能是其可逆化落地