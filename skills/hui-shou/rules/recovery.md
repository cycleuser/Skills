# 恢复策略 / Recovery Strategy

恢复是本技能的最终价值。核心：**校验通过才恢复，冲突不覆盖**。

## 恢复定位 / Locating Entry

支持三种定位方式，按优先级：

1. **精确 id**：`/回收 restore 20260729-1530-a1b2` —— 唯一定位
2. **原路径**：`/回收 restore ./src/old_module.py` —— 匹配 `src` 或 `src_rel`，取最近一条未 purge
3. **通配 pattern**：`/回收 restore 'tests/**'` —— glob 匹配 `src_rel`，批量恢复

> 同名文件多次删除：每次独立 `id`、独立 `entries` 子目录；按路径匹配取最近一条，按 `id` 精确定位。

## 校验流程 / Verification Flow

```
定位条目 / Locate entry
    ↓
读取 entries/<id>/<basename> / Read trash content
    ↓
计算 SHA-256 / Compute checksum
    ↓
与 manifest.jsonl 的 sha256 比对 / Compare with log
    ├─ 一致 → 继续 / Proceed
    └─ 不一致 → 拒绝恢复，报错"校验失败，可能损坏" / Refuse
    ↓
确定目标路径 / Resolve target path
    ↓
目标已存在? / Target exists?
    ├─ 是且无 --force → 拒绝覆盖，报错 / Refuse
    ├─ 是且有 --force → 先 delete 目标入站，再写恢复内容 / Snapshot then write
    └─ 否 → 直接写 / Write
    ↓
写入完成 / Write done
    ↓
append op=restored 记录 / Log restore
    ↓
--consume? 删除回收站原件 / Remove trash copy if consume
```

## 目标路径解析 / Target Resolution

- 默认：恢复到原 `src`（绝对路径）
  - 原 `src` 的父目录不存在 → 自动 `mkdir -p` 重建
- `--to <dest>`：恢复到指定位置
  - `<dest>` 是目录 → 写到 `<dest>/<basename>`
  - `<dest>` 是文件路径 → 写到 `<dest>`（父目录自动创建）
- 项目迁移后 `src` 绝对路径失效 → 优先用 `src_rel` 相对当前项目根恢复；`--to` 显式指定最稳

## 冲突处理 / Conflict Handling

| 情况 / Case | 行为 / Behavior |
|-------------|----------------|
| 目标已存在，无 `--force` | 拒绝覆盖，报错，提示加 `--force` |
| 目标已存在，有 `--force` | 先 `delete` 目标入站（保留旧版本可回滚），再写恢复内容 |
| 校验和失败 | 拒绝恢复，报错，建议从系统备份恢复 |
| 条目已被 purge（tombstone） | 报错"已清理，不可恢复" |
| `large=true` 但原位文件已不存在 | 报错"大文件内容已丢失" |
| 符号链接 | 重建同指向的符号链接（不恢复目标文件） |
| 目录树，目标已存在非空 | `--force` 合并（同名冲突拒绝）；无 `--force` 拒绝 |

## 恢复目录树 / Restoring Directory Trees

- 入站时用 `shutil.copytree` 保留树结构（含子目录、文件、元数据）
- 恢复时 `shutil.copytree(src=entries/<id>/<basename>, dst=target)`
  - 目标不存在 → 直接 copytree
  - 目标存在且 `--force` → 逐文件合并，同名冲突拒绝（除非再 `--force` 覆盖）
  - 目标存在且无 `--force` → 拒绝
- 保留原权限、时间戳（`copy2` 语义）

## 恢复符号链接 / Restoring Symlinks

- 入站：回收链接本身（不解析目标），记 `is_link=true`、`link_target=<指向>`
- 恢复：`os.symlink(link_target, target_path)`，重建同指向链接
- 若 `link_target` 已失效（悬空链接）→ 仍重建（保持原状），告警"目标已失效"

## 恢复后状态 / Post-Restore State

- 默认：回收站**保留**原件（`restored=true` 标记），可再次恢复
- `--consume`：恢复后**删除** `entries/<id>/`，但 manifest 行保留并标 `restored=true`（审计可查）
- 无论保留或 consume，都 `append` 一条 `op=restored` 记录到 manifest

## 批量恢复 / Batch Restore

`/回收 restore 'tests/**'`：
1. glob 匹配所有 `src_rel` 符合 pattern 且未 purge 的条目
2. 按时间倒序（最近优先）逐条恢复
3. 同名冲突（多条匹配同一 `src`）→ 默认取最近一条，其余跳过并报告
4. `--to <dir>` 批量恢复到统一目录，保持相对树结构
5. 输出汇总：成功 N 条、跳过 M 条、失败 K 条，逐条列 `id | src | status`

## 不可恢复情况 / Unrecoverable Cases

明确告知用户以下情况本技能无力回天：

- 守护模式关闭期间通过裸 `rm` 删除的文件
- 已被 `purge --confirm` 清理的条目（tombstone 存在但内容已删）
- `large=true` 且原位文件被外部删除/覆盖
- 回收站目录 `~/.opencode-trash/` 被外部整体删除
- 磁盘损坏导致 `entries/` 内容不可读

此时建议从 git / Time Machine / 系统快照 / 云备份恢复。