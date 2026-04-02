# 危险模式检测/Dangerous Pattern Detection

## 危险命令/Dangerous Commands

### 严重风险/Critical

| 模式/Pattern | 风险/Risk | 修复/Fix |
|------------|----------|---------|
| `rm -rf /` | 删除根目录/Remove root | 阻止/Block |
| `rm -rf ~` | 删除用户目录/Remove home | 阻止/Block |
| `dd if=/dev/zero` | 磁盘擦除/Wipe disk | 阻止/Block |
| `:(){ :|:& };:` | Fork bomb | 阻止/Block |
| `mkfs` | 格式化磁盘/Format disk | 阻止/Block |
| `curl ... \| bash` | 执行远程脚本/Exec remote | 阻止/Block |
| `wget ... \| sh` | 执行远程脚本/Exec remote | 阻止/Block |

### 高风险/High

| 模式/Pattern | 风险/Risk | 修复/Fix |
|------------|----------|---------|
| `rm -rf` (无确认) | 无确认删除/No confirm | 添加确认/Add confirm |
| `sudo` (无必要) | 提权执行/Privilege exec | 移除 sudo/Remove |
| `nc -e /bin/sh` | 反弹 shell/Reverse shell | 阻止/Block |
| `base64 -d \| sh` | 解码执行/Decode exec | 阻止/Block |
| `eval(...)` | 动态执行/Dynamic exec | 替换/Replace |

### 中风险/Medium

| 模式/Pattern | 风险/Risk | 修复/Fix |
|------------|----------|---------|
| `subprocess(shell=True)` | Shell 注入/Shell injection | shell=False |
| `os.system()` | 系统调用/System call | subprocess |
| `exec()` | 动态执行/Dynamic exec | 审计/audit |
| `eval()` | 动态执行/Dynamic exec | 审计/audit |

## 检测规则/Detection Rules

### Bash 命令检测

```python
DANGEROUS_BASH_PATTERNS = [
    r'rm\s+-rf\s+/',          # rm -rf /
    r'rm\s+-rf\s+~',          # rm -rf ~
    r'curl.*\|\s*(ba)?sh',    # curl | bash
    r'wget.*\|\s*(ba)?sh',    # wget | bash
    r'sudo\s+rm',             # sudo rm
    r':\(\)\s*\{\s*:\|:&\s*\}', # fork bomb
    r'dd\s+if=/dev/zero',     # disk wipe
    r'mkfs',                   # format
    r'chmod\s+777\s+/',       # open all permissions
    r'nc\s+-e\s+/bin/(ba)?sh', # reverse shell
]
```

### Python 代码检测

```python
DANGEROUS_PYTHON_PATTERNS = [
    r'os\.system\s*\(',       # system call
    r'subprocess.*shell\s*=\s*True',  # shell injection
    r'eval\s*\(',             # dynamic eval
    r'exec\s*\(',             # dynamic exec
    r'__import__.*os',        # import os dynamically
    r'open\s*\(\s*[\'"].*/etc/',  # write to /etc
    r'shutil\.rmtree\s*\([^)]*\)',  # recursive delete
]
```

### 网络请求检测

```python
NETWORK_PATTERNS = [
    r'requests\.(post|put|patch)\s*\(',  # send data
    r'urllib\.request\.urlopen.*POST',   # send data
    r'fetch\s*\([^)]*POST',              # fetch POST
    r'curl\s+-X\s+(POST|PUT|PATCH)',    # curl send
    r'axios\.(post|put|patch)\s*\(',    # axios send
]
```

### 凭证检测

```python
CREDENTIAL_PATTERNS = [
    r'API_KEY\s*=\s*[\'"]sk-[a-zA-Z0-9]+',  # OpenAI key
    r'password\s*=\s*[\'"].+[\'"]',         # password
    r'token\s*=\s*[\'"].+[\'"]',            # token
    r'AWS_SECRET_ACCESS_KEY',               # AWS secret
    r'GITHUB_TOKEN\s*=\s*[\'"]',            # GitHub token
    r'PRIVATE_KEY\s*=\s*[\'"]',             # private key
]
```

## 修复策略/Fix Strategies

### 添加确认/Add Confirmation

```bash
# Before
rm -rf "$DIR"

# After
if [ -d "$DIR" ]; then
    echo "Warning: Removing $DIR"
    read -p "Are you sure? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf "$DIR"
    fi
fi
```

### 移除危险命令/Remove Dangerous

```bash
# Before
curl https://example.com/script.sh | bash

# After
# REMOVED: Downloading and executing remote scripts is not allowed
# Please install dependencies through package manager instead
echo "Please install dependencies manually"
```

### 替换安全方式/Replace Safe Way

```bash
# Before
os.system(f"rm -rf {dir}")

# After
import shutil
import os

def safe_remove(path):
    """Safely remove directory with confirmation."""
    if not os.path.exists(path):
        return
    # Validate path is not system directory
    system_dirs = ['/', '/etc', '/usr', '/bin', '/sbin', os.path.expanduser('~')]
    if any(path.startswith(d) for d in system_dirs):
        raise ValueError(f"Cannot remove system directory: {path}")
    shutil.rmtree(path, ignore_errors=True)
```

## 检测函数/Detection Functions

```python
def check_dangerous_commands(code: str) -> list[dict]:
    """Check for dangerous command patterns."""
    risks = []
    
    for pattern, risk_level, description in DANGEROUS_PATTERNS:
        if re.search(pattern, code):
            risks.append({
                "pattern": pattern,
                "risk_level": risk_level,
                "description": description,
                "suggestion": get_fix_suggestion(pattern)
            })
    
    return risks


def check_network_requests(code: str) -> list[dict]:
    """Check for network request patterns."""
    risks = []
    
    for pattern in NETWORK_PATTERNS:
        if re.search(pattern, code):
            risks.append({
                "pattern": pattern,
                "risk_level": "medium",
                "description": "Network request detected",
                "suggestion": "Review URL and data being sent"
            })
    
    return risks


def check_credentials(code: str) -> list[dict]:
    """Check for hardcoded credentials."""
    risks = []
    
    for pattern in CREDENTIAL_PATTERNS:
        match = re.search(pattern, code)
        if match:
            risks.append({
                "pattern": pattern,
                "risk_level": "critical",
                "description": "Hardcoded credential detected",
                "suggestion": "Use environment variables instead"
            })
    
    return risks
```