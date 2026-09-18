# 回收工作流 / Trash Workflow

完整四步操作流程。核心：**先回收，后删除；有日志，可恢复**。

## Step 0 — 守护 Guard

守护模式决定破坏性命令是否自动路由到 `trash.py`。

```bash
# 查看当前状态
python3 scripts/trash.py guard status

# 开启（默认）
python3 scripts/trash.py guard on

# 临时关闭（不推荐，关期间的裸删除不可恢复）
python3 scripts/trash.py guard off
```

守护模式开启时，以下命令必须先经 `trash.py` 子命令，否则拒绝执行：

| 裸命令 / Raw | 替换为 / Replace with |
|--------------|---------------------|
| `rm <path>` | `/回收 delete <path>` |
| `rm -rf <dir>` | `/回收 delete <dir>` |
| `mv -f <src> <dst>`（覆盖） | `/回收 move <src> <dst>` |
| `> <path>`（截断） | `/回收 overwrite <path>` 再写 |
| `tee <path>`（覆盖） | 同上 |

> ⚠️ 守护模式只约束**通过本技能执行的**操作。用户在终端外手敲的 `rm` 本技能无法拦截，只能事后从 git/系统备份恢复——因此务必建议常开守护、常走 `/回收`。

## Step 1 — 回收 Collect

### 1a. 删除 delete

```bash
python3 scripts/trash.py delete <path>
```

流程：
1. 校验 `<path>` 存在，解析为绝对路径
2. 生成 `id`（格式 `YYYYMMDD-HHMM-xxxx`，4 位随机）
3. `move` 到 `entries/<id>/<basename>`；跨设备（`EXDEV`）降级 `copy2+unlink`
4. 计算 SHA-256 与 size，`append` 一行到 `manifest.jsonl`
5. 原路径已不存在 → 删除完成，返回 `id`

失败处理：
- `copy2` 失败 → **保留原文件，报错退出**，绝不 `unlink`
- 权限不足 → 报错，提示 `chmod` 或人工处理
- 路径不存在 → 报错（不创建空条目）

### 1b. 覆盖 overwrite

```bash
python3 scripts/trash.py overwrite <path>
# 返回 id 后，调用方可安全写入新内容
```

等价于：若 `<path>` 存在 → 先 `delete` 入站，返回 `id`；随后写入新内容即覆盖旧版本。若不存在则无操作（返回空 id），随后写入即新建。

### 1c. 移动 move

```bash
python3 scripts/trash.py move <src> <dst>
```

流程：
1. 若 `<dst>` 存在 → 先 `delete <dst>` 入站（保留可回滚）
2. `rename <src> → <dst>`
3. `append` 一条 `op=move` 记录（`src→dst`，**无内容回收**，只记路径变化）
4. `rename` 失败 → 从回收站还原 `<dst>`，回滚

## Step 2 — 日志 Log

```bash
# 最近 20 条
python3 scripts/trash.py log

# 最近 N 条
python3 scripts/trash.py log 50

# 列出回收站条目（全量）
python3 scripts/trash.py list

# 按路径正则过滤
python3 scripts/trash.py list 'src/.*\.py'

# 按操作类型过滤
python3 scripts/trash.py list --op delete

# 按天数过滤（近 7 天）
python3 scripts/trash.py list --days 7

# 单条详情
python3 scripts/trash.py inspect 20260729-1530-a1b2
```

输出表格字段：`id | op | src | size | sha256(前12) | time | restored?`

读取 `manifest.jsonl` 时：
- 跳过 `op=purged` 的 tombstone 行（条目已清理）
- `restored=true` 的行标记为"已恢复过"（仍可再次恢复，除非已 purge）

## Step 3 — 恢复 Restore

```bash
# 按 id 精确恢复
python3 scripts/trash.py restore 20260729-1530-a1b2

# 按原路径恢复（匹配最近一条）
python3 scripts/trash.py restore ./src/old_module.py

# 按通配 pattern 恢复
python3 scripts/trash.py restore 'tests/**'

# 恢复到指定位置（不改原路径）
python3 scripts/trash.py restore 20260729-1530-a1b2 --to ./restored/old_module.py

# 强制覆盖已存在的目标
python3 scripts/trash.py restore <id> --force

# 恢复后从回收站移除原件（不可再次恢复）
python3 scripts/trash.py restore <id> --consume
```

流程：
1. 在 `manifest.jsonl` 中定位条目（精确 `id` / 原路径 / 通配 `pattern`）
2. 读取 `entries/<id>/<basename>`，计算 SHA-256，与日志记录比对
   - 不一致 → **拒绝恢复**，报错"校验失败，可能损坏"
3. 默认恢复到原 `src` 路径；`--to` 指定新位置
4. 目标已存在且非 `--force` → **拒绝覆盖**，报错（防二次破坏）
5. `--force` → 先把目标 `delete` 入站，再写入恢复内容
6. 写入完成，`append` 一条 `op=restored` 记录
7. 默认保留回收站原件（可再恢复）；`--consume` 则删除 `entries/<id>/`

> 还原目录树时用 `shutil.copytree`，保留原结构；目标已存在则 `--force` 合并或拒绝。

## Step 4 — 清理 Purge

```bash
# 预览（默认 30 天前）
python3 scripts/trash.py purge

# 预览 N 天前
python3 scripts/trash.py purge 7

# 执行清理
python3 scripts/trash.py purge 30 --confirm
```

流程：
1. `days` 默认 30；列出将删条目（`id | src | time | size`）
2. 未带 `--confirm` → **只预览，不执行**
3. 带 `--confirm`：
   - 物理删除 `entries/<id>/` 内容
   - 在 `manifest.jsonl` 追加 `op=purged` tombstone（**不改历史行**）
   - `large=true` 的条目不删原文件（内容留原位），只置 tombstone

> 永不自动 purge 未恢复且近期的条目。purge 是显式、需确认的破坏性操作。

## 命令映射 / Command Mapping

| 命令 | 动作 |
|------|------|
| `/回收 delete <路径>` | Step 1a |
| `/回收 overwrite <路径>` | Step 1b |
| `/回收 move <src> <dst>` | Step 1c |
| `/回收 list [过滤]` | Step 2 |
| `/回收 log [N]` | Step 2 |
| `/回收 inspect <id>` | Step 2 |
| `/回收 restore <…>` | Step 3 |
| `/回收 purge [天数]` | Step 4 |
| `/回收 guard on\|off` | Step 0 |

英文命令 `/trash [delete|list|restore|log|purge] ...` 行为一致。