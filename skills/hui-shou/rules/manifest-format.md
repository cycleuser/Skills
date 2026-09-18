# manifest.jsonl 字段定义 / Manifest Format

`manifest.jsonl` 是 append-only 操作日志，每行一个 JSON 对象。**永不原地改写**，只能追加；purge/restore 也只追加新行（tombstone / restored 记录），不删历史行。

## Append-only 语义

- 文件只以 `a` 模式打开，追加时用 `fcntl.flock` 排他锁
- 查询时按行解析，跳过 `op=purged` 的 tombstone
- `restored=true` 表示已恢复过（仍可再恢复，除非已 purge）
- 损坏行（JSON 解析失败）跳过并记录告警，不中断整体

## 字段定义 / Fields

每条记录的 JSON 字段：

| 字段 / Field | 类型 | 必填 | 说明 / Description |
|--------------|------|------|---------------------|
| `id` | string | 是 | 条目 ID，`YYYYMMDD-HHMM-xxxx`（4 位随机） |
| `op` | string | 是 | 操作类型：`delete`/`overwrite`/`move`/`restore`/`purged` |
| `src` | string | 是 | 原始绝对路径（`move` 记 `src→dst`） |
| `src_rel` | string | 是 | 相对项目根的路径，便于迁移后恢复 |
| `dst` | string | 否 | `move` 操作的目标路径 |
| `trash_path` | string | 是 | 回收站内内容路径 `entries/<id>/<basename>` |
| `sha256` | string | 是 | 内容 SHA-256（hex，64 字符） |
| `size` | int | 是 | 内容字节数（目录树为总字节数） |
| `mtime` | float | 是 | 原文件修改时间戳 |
| `time` | string | 是 | 操作时间 ISO-8601 |
| `is_dir` | bool | 是 | 是否目录 |
| `is_link` | bool | 是 | 是否符号链接 |
| `link_target` | string | 否 | 符号链接指向（`is_link=true` 时） |
| `large` | bool | 否 | 大文件标记，内容留原位 |
| `large_path` | string | 否 | `large=true` 时的原位绝对路径 |
| `restored` | bool | 否 | 是否已恢复过（默认 false） |
| `restore_time` | string | 否 | 恢复时间（`restored=true` 时） |
| `restore_to` | string | 否 | 恢复到的目标路径 |
| `purged` | bool | 否 | 是否已清理（tombstone 标记） |
| `project_slug` | string | 是 | 项目标识（cwd SHA-1 前 12 位 + 末段目录名） |
| `cwd` | string | 是 | 操作时的项目根绝对路径 |

## op 类型 / Operation Types

| op | 含义 | 是否回收内容 | 日志追加时机 |
|----|------|------------|-------------|
| `delete` | 删除（先入站） | 是 | 内容入站后 |
| `overwrite` | 覆盖写（先备份旧内容） | 是（旧内容） | 旧内容入站后 |
| `move` | 移动/重命名 | 否（只记路径变化） | rename 成功后 |
| `restore` | 恢复 | 否（原件保留） | 内容写回后 |
| `purged` | 清理 tombstone | —（物理删内容已执行） | 物理删除后 |

## 示例记录 / Example Entries

```jsonl
{"id":"20260729-1530-a1b2","op":"delete","src":"/proj/src/old.py","src_rel":"src/old.py","trash_path":"entries/20260729-1530-a1b2/old.py","sha256":"a1b2c3...","size":4287,"mtime":1753789800.0,"time":"2026-07-29T15:30:12+08:00","is_dir":false,"is_link":false,"project_slug":"a1b2c3d4e5f6-proj","cwd":"/proj"}
{"id":"20260729-1600-c3d4","op":"overwrite","src":"/proj/config.yaml","src_rel":"config.yaml","trash_path":"entries/20260729-1600-c3d4/config.yaml","sha256":"e5f6...","size":1024,"mtime":1753791600.0,"time":"2026-07-29T16:00:45+08:00","is_dir":false,"is_link":false,"project_slug":"a1b2c3d4e5f6-proj","cwd":"/proj"}
{"id":"20260729-1610-eeee","op":"move","src":"/proj/a.txt","dst":"/proj/b.txt","src_rel":"a.txt","time":"2026-07-29T16:10:01+08:00","project_slug":"a1b2c3d4e5f6-proj","cwd":"/proj"}
{"id":"20260729-1530-a1b2","op":"restore","src":"/proj/src/old.py","restore_to":"/proj/src/old.py","time":"2026-07-29T17:00:00+08:00","restored":true,"project_slug":"a1b2c3d4e5f6-proj"}
{"id":"20260601-1200-0000","op":"purged","time":"2026-07-29T18:00:00+08:00","purged":true,"project_slug":"a1b2c3d4e5f6-proj"}
```

## 校验和计算 / Checksum

- 入站时：流式读取内容算 SHA-256，写入 `sha256` 字段
- 恢复时：再算一次，与日志记录比对，不一致则拒绝恢复
- 目录树：对树内所有文件内容 concatenated 算总 SHA-256（用于整体一致性校验），同时记录 `size` 为树总字节

## project_slug 生成 / Project Slug

```python
import hashlib, os
cwd = os.getcwd()
h = hashlib.sha1(cwd.encode()).hexdigest()[:12]
tail = os.path.basename(cwd.rstrip('/')) or 'root'
slug = f"{h}-{tail}"
```

回收站路径：`~/.opencode-trash/<project_slug>/`