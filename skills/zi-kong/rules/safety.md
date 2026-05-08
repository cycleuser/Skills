# 安全层/Safety Layer for Autonomous Execution

## 变更审查规则/Change Review Rules

### 破坏性操作检测

```python
DESTRUCTIVE_PATTERNS = {
    "file_delete": [
        r'rm\s+-rf',
        r'shutil\.rmtree',
        r'os\.remove',
        r'os\.rmdir',
        r'Path.*\.unlink',
        r'Path.*\.rmdir',
    ],
    "data_loss": [
        r'DROP\s+TABLE',
        r'TRUNCATE',
        r'DELETE\s+FROM\s+\w+\s*;',
        r'\.truncate\s*\(',
        r'open\s*\([^)]*["\']w["\']',
    ],
    "system_modify": [
        r'sudo\s+',
        r'chmod\s+777',
        r'chown\s+',
        r'sysctl\s+',
        r'iptables\s+',
    ],
    "network_exposure": [
        r'0\.0\.0\.0\s*:\s*\d+',
        r'host\s*=\s*["\']0\.0\.0\.0["\']',
        r'bind\s*=\s*["\']0\.0\.0\.0["\']',
    ],
    "force_push": [
        r'git\s+push\s+.*--force',
        r'git\s+push\s+.*-f\b',
        r'git\s+reset\s+--hard',
    ],
}
```

### 破坏性操作安全替代/Safer Alternatives

```
┌─────────────────────────────────────────────────────────────────┐
│  破坏性操作                  →  安全替代                          │
├─────────────────────────────────────────────────────────────────┤
│  rm -rf /dir                 →  移到备份目录，确认后删除            │
│  DROP TABLE                  →  RENAME TABLE，确认后删除            │
│  DELETE FROM table;          →  SELECT COUNT 先确认，加 WHERE      │
│  git push --force            →  git push --force-with-lease        │
│  git reset --hard            →  git stash + git reset --soft       │
│  open(f, 'w')                →  open(f, 'w') + 先备份原文件        │
│  shutil.rmtree               →  移到 .zikong/trash/ 临时目录        │
│  sudo ...                    →  检查是否有非 sudo 替代方案          │
│  chmod 777                   →  chmod 755 或更严格权限              │
│  bind 0.0.0.0               →  bind 127.0.0.1 或指定接口           │
└─────────────────────────────────────────────────────────────────┘
```

### 安全替代代码示例

```python
def safe_delete(path: str) -> dict:
    """安全删除：移动到备份目录而非直接删除"""
    backup_dir = Path(".zikong/trash") / datetime.now().strftime("%Y%m%d")
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    src = Path(path)
    dst = backup_dir / src.name
    
    if dst.exists():
        dst = backup_dir / f"{src.name}_{int(time.time())}"
    
    shutil.move(str(src), str(dst))
    return {"action": "moved_to_trash", "original": str(src), "backup": str(dst)}


def safe_write(filepath: str, content: str) -> dict:
    """安全写入：先备份原文件"""
    path = Path(filepath)
    
    if path.exists():
        backup_dir = Path(".zikong/backups")
        backup_dir.mkdir(parents=True, exist_ok=True)
        backup = backup_dir / f"{path.name}_{int(time.time())}"
        shutil.copy2(str(path), str(backup))
    
    path.write_text(content, encoding="utf-8")
    return {"action": "safe_write", "backup_exists": path.exists()}
```

## 文件快照回滚/File Snapshot Rollback

### 快照机制

```python
class SnapshotManager:
    def __init__(self, workspace: str):
        self.workspace = Path(workspace)
        self.snapshot_dir = self.workspace / ".zikong" / "snapshots"
        self.snapshot_dir.mkdir(parents=True, exist_ok=True)
    
    def create_snapshot(self, name: str) -> str:
        """创建工作区文件快照"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        snapshot_name = f"{name}_{timestamp}"
        snapshot_path = self.snapshot_dir / snapshot_name
        
        changed_files = get_changed_files(str(self.workspace))
        snapshot_meta = {
            "name": snapshot_name,
            "timestamp": timestamp,
            "files": changed_files,
            "git_head": get_git_head(),
        }
        
        for filepath in changed_files:
            src = self.workspace / filepath
            dst = snapshot_path / filepath
            dst.parent.mkdir(parents=True, exist_ok=True)
            if src.exists():
                shutil.copy2(str(src), str(dst))
        
        meta_path = snapshot_path / "_meta.json"
        meta_path.write_text(json.dumps(snapshot_meta, indent=2))
        
        return snapshot_name
    
    def rollback_to_snapshot(self, name: str) -> dict:
        """回滚到指定快照"""
        snapshot_path = self.snapshot_dir / name
        meta_path = snapshot_path / "_meta.json"
        
        if not meta_path.exists():
            return {"success": False, "error": f"Snapshot not found: {name}"}
        
        meta = json.loads(meta_path.read_text())
        restored = []
        
        for filepath in meta["files"]:
            src = snapshot_path / filepath
            dst = self.workspace / filepath
            if src.exists():
                shutil.copy2(str(src), str(dst))
                restored.append(filepath)
        
        return {"success": True, "restored_files": restored}
    
    def list_snapshots(self) -> list:
        """列出所有快照"""
        snapshots = []
        for d in self.snapshot_dir.iterdir():
            if d.is_dir() and (d / "_meta.json").exists():
                meta = json.loads((d / "_meta.json").read_text())
                snapshots.append(meta)
        return sorted(snapshots, key=lambda x: x["timestamp"], reverse=True)
```

### 快照触发规则

```
触发快照的条件：
1. 每次执行破坏性操作前
2. 每 5 轮自动快照
3. 重构操作前
4. 批量文件修改前
5. 用户暂停前
```

## 硬超时守卫/Hard Timeout Guard

### 超时层级

```
┌────────────────────────────────────────────────────────────────┐
│  层级/Level      超时/Timeout     触发动作/Action               │
├────────────────────────────────────────────────────────────────┤
│  软超时          预算 80%         停止接受新任务，只完成当前任务    │
│  硬超时          预算 95%         强制收尾，保存状态，停止执行      │
│  绝对超时        预算 100% + 5min 紧急保存所有状态，强制退出      │
└────────────────────────────────────────────────────────────────┘
```

### 超时守卫实现

```python
import signal
import threading

class TimeoutGuard:
    def __init__(self, time_budget_sec: int, token_budget: int):
        self.time_budget = time_budget_sec
        self.token_budget = token_budget
        self.start_time = time.time()
        self.hard_timeout = time_budget_sec + 300  # 绝对超时 = 预算 + 5分钟
        self._setup_signal_handler()
    
    def _setup_signal_handler(self):
        """设置 SIGALRM 处理器"""
        def handler(signum, frame):
            raise TimeoutError("Absolute timeout reached")
        signal.signal(signal.SIGALRM, handler)
        signal.alarm(self.hard_timeout)
    
    def check_soft_timeout(self) -> bool:
        """检查是否到达软超时"""
        elapsed = time.time() - self.start_time
        return elapsed >= self.time_budget * 0.80
    
    def check_hard_timeout(self) -> bool:
        """检查是否到达硬超时"""
        elapsed = time.time() - self.start_time
        return elapsed >= self.time_budget * 0.95
    
    def force_save_and_exit(self):
        """强制保存并退出"""
        try:
            save_current_state()
            create_emergency_snapshot()
            write_progress_report()
        except Exception:
            pass
        finally:
            signal.alarm(0)
    
    def cancel(self):
        """取消超时守卫"""
        signal.alarm(0)
```

### 操作级超时

```python
OPERATION_TIMEOUTS = {
    "perceive": 60,        # 感知阶段最多 60 秒
    "decide": 30,          # 决策阶段最多 30 秒
    "execute": 300,        # 执行阶段最多 300 秒
    "review": 120,         # 审查阶段最多 120 秒
    "save": 30,            # 保存阶段最多 30 秒
    "file_read": 10,       # 读文件最多 10 秒
    "file_write": 30,      # 写文件最多 30 秒
    "test_run": 120,       # 测试运行最多 120 秒
    "git_operation": 60,   # Git 操作最多 60 秒
    "web_search": 30,      # 网页搜索最多 30 秒
}
```

## 安全检查清单/Safety Checklist

### 每次迭代前检查

```
□ 预算是否足够完成当前任务？
□ 当前操作是否为破坏性操作？
□ 是否已创建快照？
□ 测试是否处于通过状态？
□ 是否有 safer alternative？
```

### 执行破坏性操作前检查

```
□ 是否有非破坏性替代方案？
□ 是否已创建快照？
□ 是否已通知用户？
□ 影响范围是否已评估？
□ 回滚方案是否就绪？
```