# 修复策略/Fix Strategies

## 修复类型/Fix Types

### 1. 自动修复/Auto-Fix

适用于/For:
- 可识别的危险模式
- 有明确替代方案
- 不需要业务逻辑理解

```python
def auto_fix(code: str, risk_type: str) -> tuple[str, bool]:
    """
    Attempt to automatically fix security issues.
    Returns: (fixed_code, success)
    """
    
    fixes = {
        "rm_rf_no_confirm": fix_rm_rf,
        "curl_bash": fix_curl_bash,
        "hardcoded_key": fix_hardcoded_key,
        "shell_injection": fix_shell_injection,
    }
    
    fix_func = fixes.get(risk_type)
    if fix_func:
        return fix_func(code)
    
    return code, False
```

### 2. 禁用功能/Disable Feature

适用于/For:
- 非核心功能
- 风险过高无法修复
- 用户选择保留但禁用

```python
def disable_feature(code: str, feature_name: str) -> str:
    """Disable a specific feature."""
    
    # Comment out the feature
    code = code.replace(
        f"def {feature_name}",
        f"# DISABLED for security\ndef _disabled_{feature_name}"
    )
    
    # Add warning
    warning = f'''
# WARNING: {feature_name} has been disabled for security reasons.
# To enable, remove this warning and rename function back.
'''
    
    return warning + code
```

### 3. 添加确认/Add Confirmation

适用于/For:
- 危险但必要的操作
- 需要用户知情同意
- 一次性操作

```python
def add_confirmation(code: str, dangerous_op: str) -> str:
    """Add user confirmation for dangerous operations."""
    
    confirmation_template = '''
def confirm_action(action: str) -> bool:
    """Require user confirmation for dangerous actions."""
    print(f"WARNING: About to perform dangerous action: {action}")
    response = input("Are you sure? Type 'yes' to confirm: ")
    return response.lower() == 'yes'

# Usage:
if not confirm_action("{action}"):
    print("Action cancelled by user.")
    sys.exit(0)
'''
    
    # Insert confirmation function
    code = confirmation_template + "\n" + code
    
    # Add check before dangerous operation
    code = code.replace(
        dangerous_op,
        f'if confirm_action("{dangerous_op}"):\n    {dangerous_op}'
    )
    
    return code
```

## 具体修复/Specific Fixes

### 修复 rm -rf 无确认

```bash
# Before
rm -rf "$BUILD_DIR"

# After
safe_rm_rf() {
    local dir="$1"
    
    # Validate path
    if [ -z "$dir" ]; then
        echo "Error: Directory not specified"
        return 1
    fi
    
    # Check not system directory
    case "$dir" in
        /|/etc|/usr|/bin|/sbin|/boot|/dev|/proc|/sys)
            echo "Error: Cannot remove system directory: $dir"
            return 1
            ;;
        $HOME)
            echo "Error: Cannot remove home directory"
            return 1
            ;;
    esac
    
    # Confirm
    if [ ! -d "$dir" ]; then
        echo "Warning: Directory does not exist: $dir"
        return 0
    fi
    
    echo "Warning: Removing directory: $dir"
    read -p "Are you sure? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Cancelled."
        return 0
    fi
    
    rm -rf "$dir"
}

# Usage
safe_rm_rf "$BUILD_DIR"
```

### 修复 curl | bash

```bash
# Before
curl -fsSL https://example.com/install.sh | bash

# After
# REMOVED: Downloading and executing remote scripts is not allowed
# Security risk: Remote script could contain malicious code
#
# Alternative: Install through package manager or download and review first

# Option 1: Package manager (recommended)
# apt-get install package-name
# brew install package-name

# Option 2: Download and review
# curl -fsSL https://example.com/install.sh -o install.sh
# # REVIEW install.sh manually
# bash install.sh

echo "Please install dependencies manually and review code first."
```

### 修复硬编码凭证

```python
# Before
API_KEY = "sk-abc123xyz789"

# After
import os

# Get API key from environment variable
# Set it with: export API_KEY="your-key-here"
API_KEY = os.environ.get("API_KEY")

if not API_KEY:
    raise ValueError(
        "API_KEY environment variable not set. "
        "Please set it with: export API_KEY='your-key-here'"
    )
```

### 修复 Shell 注入

```python
# Before
import os
os.system(f"ls -la {user_input}")

# After
import subprocess
import shlex

def safe_list_directory(path: str) -> str:
    """Safely list directory contents."""
    # Validate path
    if not os.path.isdir(path):
        raise ValueError(f"Not a directory: {path}")
    
    # Use subprocess with list args (no shell)
    result = subprocess.run(
        ["ls", "-la", path],
        capture_output=True,
        text=True,
        check=True,
        timeout=30
    )
    
    return result.stdout

# Usage
output = safe_list_directory(user_input)
```

## 修复验证/Fix Verification

```python
def verify_fix(original: str, fixed: str, risk_type: str) -> dict:
    """Verify that the fix resolves the security issue."""
    
    # Re-scan fixed code
    risks_after = scan_for_risks(fixed)
    
    # Check if original risk is gone
    original_risks = [r for r in risks_after if r["type"] == risk_type]
    
    return {
        "original_risk": risk_type,
        "fix_applied": True,
        "risk_resolved": len(original_risks) == 0,
        "new_risks": len(risks_after),
        "verification_passed": len(original_risks) == 0
    }
```