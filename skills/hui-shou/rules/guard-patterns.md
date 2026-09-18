# 守护模式规则 / Guard Patterns

守护模式拦截破坏性文件操作，强制其先入回收站。核心：**不可逆操作必须可逆化**。

## 守护范围 / Guarded Operations

守护模式开启时，以下操作必须改走 `/回收`（`trash.py`）：

### 必须拦截 / Must Intercept

| 模式 / Pattern | 拦截动作 / Action |
|---------------|------------------|
| `rm <path>` | `/回收 delete <path>` |
| `rm -rf <dir>` | `/回收 delete <dir>` |
| `rm -fr <dir>` | 同上 |
| `mv -f <src> <dst>`（dst 存在，覆盖） | `/回收 move <src> <dst>` |
| `mv <src> <dst>`（dst 存在） | 同上（静默覆盖也拦） |
| `> <path>`（截断清空） | `/回收 overwrite <path>` |
| `>| <path>` | 同上 |
| `tee <path>`（无 -a，覆盖） | `/回收 overwrite <path>` |
| `cp -f <src> <dst>`（dst 存在，覆盖） | `/回收 overwrite <dst>` |
| `shutil.rmtree(...)` | `/回收 delete <dir>` |
| `os.unlink(...)` / `os.remove(...)` | `/回收 delete <path>` |
| `Path.unlink()` | `/回收 delete <path>` |
| `open(path, 'w')`（path 存在，覆盖） | `/回收 overwrite <path>` |
| `git clean -fd` / `git checkout -- <file>` | 警告：会丢弃工作区改动，建议先 `/回收 delete` 受影响文件 |

### 不拦截 / Not Intercepted

- `mkdir`、`touch`（新建，非破坏）
- `mv <src> <dst>`（dst 不存在，纯移动）
- `cp <src> <new_dst>`（新建副本）
- `git rm`（git 有自己的历史，可 `git checkout` 恢复；但建议提示用户）
- 在 `.git/` 内部的操作（git 自己管，本技能不介入）
- 回收站内部操作（`~/.opencode-trash/` 内，避免递归）

## 判定流程 / Decision Flow

```
检测到文件操作命令 / File op detected
    ↓
目标在 .git/ 内? → 放行（git 自管）
    ↓ 否
目标在回收站内? → 放行（避免递归）
    ↓ 否
是新建操作（dst 不存在）? → 放行
    ↓ 否（会破坏已有内容）
守护模式开? 
    ├─ 是 → 路由到 trash.py 子命令 → 回收 → 执行
    └─ 否 → 警告"守护已关，此操作不可恢复" → 放行
```

## 守护锁 / Guard Lock

- 回收站根下 `guard.lock` 文件存在 = 守护开
- `/回收 guard on` 创建该文件；`off` 删除
- `/回收 guard status` 读取状态
- 每个会话启动时读 `guard.lock` 决定默认行为；文件不存在视为开（安全优先）

## 跨技能协作 / Cross-Skill Coordination

- **an-jian（安检）**：检测到 `rm -rf` 等危险模式时，建议启用 `/回收 guard on`，并将破坏性命令改走 `/回收 delete`
- **ba-guan（把关）**：发布前审查的破坏性操作应先过本技能
- **global-rules**：通用 `rm -rf` 防护规则，本技能是其"可逆化"的落地实现

## 边界 / Boundaries

- 守护**只约束通过本技能/bash 工具执行的操作**；用户在终端外手敲或外部程序直接 syscall 的删除本技能无法拦截
- 守护不替代系统备份（Time Machine/snapshot），而是提供"操作级"可逆性
- 守护关期间的裸删除**不可恢复**，必须明确告知用户