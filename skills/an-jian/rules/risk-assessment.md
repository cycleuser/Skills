# 风险评估/Risk Assessment

## 风险等级/Risk Levels

```
┌─────────────────────────────────────────────────────────────────────┐
│                    风险等级/Risk Levels                              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  严重/Critical ████████░░ 80-100                                    │
│  ├── 系统损坏风险/System damage                                     │
│  ├── 数据丢失风险/Data loss                                         │
│  └── 凭证泄露风险/Credential leak                                   │
│  处理/Action: 阻止安装/Block install                                │
│                                                                      │
│  高/High        ██████░░░░ 60-79                                    │
│  ├── 危险命令执行/Dangerous command                                 │
│  ├── 敏感信息泄露/Sensitive info leak                               │
│  └── 权限提升/Privilege escalation                                  │
│  处理/Action: 需要用户确认/User confirm required                    │
│                                                                      │
│  中/Medium      ████░░░░░░ 40-59                                    │
│  ├── 潜在风险/Potential risk                                        │
│  ├── 需要特定条件/Needs specific condition                          │
│  └── 最佳实践问题/Best practice issue                               │
│  处理/Action: 建议修复/Suggest fix                                  │
│                                                                      │
│  低/Low         ██░░░░░░░░ 0-39                                     │
│  ├── 轻微风险/Minor risk                                            │
│  └── 代码质量问题/Code quality issue                                │
│  处理/Action: 可选改进/Optional improvement                         │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

## 风险计算公式/Risk Calculation

```python
def calculate_risk_score(risks: list[dict]) -> int:
    """Calculate overall risk score (0-100)."""
    
    # Risk level weights
    WEIGHTS = {
        "critical": 40,
        "high": 25,
        "medium": 10,
        "low": 2
    }
    
    score = 0
    for risk in risks:
        level = risk.get("risk_level", "low")
        score += WEIGHTS.get(level, 0)
    
    # Cap at 100
    return min(score, 100)


def get_risk_level(score: int) -> str:
    """Convert score to risk level."""
    
    if score >= 80:
        return "critical"
    elif score >= 60:
        return "high"
    elif score >= 40:
        return "medium"
    else:
        return "low"
```

## 风险矩阵/Risk Matrix

```
                    影响范围/Impact
                低       中       高
            ┌───────┬───────┬───────┐
          低│  低   │  中   │  高   │
            ├───────┼───────┼───────┤
可能性/     中│  中   │  高   │ 严重  │
Likelihood  ├───────┼───────┼───────┤
          高│  高   │ 严重  │ 严重  │
            └───────┴───────┴───────┘
```

## 风险决策/Risk Decision

```python
def make_decision(risk_level: str, user_preference: str) -> str:
    """Make installation decision based on risk level."""
    
    decisions = {
        "critical": {
            "default": "block",
            "with_confirm": "ask_user",
            "actions": ["fix", "disable", "cancel", "force_continue"]
        },
        "high": {
            "default": "ask_user",
            "with_confirm": "ask_user",
            "actions": ["fix", "review", "disable", "continue"]
        },
        "medium": {
            "default": "suggest_fix",
            "with_confirm": "continue",
            "actions": ["fix", "continue"]
        },
        "low": {
            "default": "pass",
            "with_confirm": "pass",
            "actions": ["continue"]
        }
    }
    
    return decisions.get(risk_level, {"default": "ask_user"})
```

## 审计报告模板/Audit Report Template

```markdown
# 安全审计报告/Security Audit Report

## 基本信息/Basic Info

| 项目/Item | 值/Value |
|----------|---------|
| 技能名称/Skill | {name} |
| 审查时间/Time | {timestamp} |
| 审查者/Reviewer | an-jian |
| 版本/Version | {version} |

## 风险摘要/Risk Summary

**总体风险/Overall Risk**: {level} ({score}/100)

| 风险等级/Level | 数量/Count | 占比/Percentage |
|---------------|-----------|----------------|
| 严重/Critical | {n} | {pct}% |
| 高/High | {n} | {pct}% |
| 中/Medium | {n} | {pct}% |
| 低/Low | {n} | {pct}% |

## 详细风险/Detailed Risks

### 严重风险/Critical Risks

| # | 位置/Location | 问题/Issue | 建议/Suggestion |
|---|--------------|-----------|----------------|
| 1 | {file}:L{n} | {issue} | {fix} |

### 高风险/High Risks

...

### 中风险/Medium Risks

...

### 低风险/Low Risks

...

## 修复建议/Fix Recommendations

### 必须修复/Must Fix

1. {critical_fix_1}
2. {critical_fix_2}

### 建议修复/Should Fix

1. {high_fix_1}
2. {high_fix_2}

### 可选修复/Optional Fix

1. {medium_fix_1}
2. {medium_fix_2}

## 决策/Decision

**用户选择/User Choice**: {choice}

**处理结果/Result**:
- 已修复/Fixed: {count}
- 已禁用/Disabled: {count}
- 已确认/Confirmed: {count}
- 剩余风险/Remaining: {count}

## 签名/Signature

**审查通过/Review Pass**: ✅/❌
**审查者/Reviewer**: an-jian
**时间/Time**: {timestamp}
```