# 安全审计报告格式/Security Audit Report Format

## JSON 结构化报告/JSON Structured Report

### 报告顶层结构

```json
{
  "report_meta": {
    "skill_name": "string",
    "skill_version": "string",
    "audit_timestamp": "ISO8601",
    "auditor": "an-jian",
    "audit_id": "string"
  },
  "summary": {
    "overall_risk_level": "critical|high|medium|low",
    "overall_risk_score": 0,
    "total_findings": 0,
    "findings_by_severity": {
      "critical": 0,
      "high": 0,
      "medium": 0,
      "low": 0
    },
    "decision": "block|confirm|suggest|pass",
    "auto_fixed": 0,
    "requires_review": 0
  },
  "findings": [],
  "risk_calculation": {},
  "remediation": []
}
```

### 单条发现结构/Per-Finding Detail

```json
{
  "finding_id": "ANJ-001",
  "severity": "critical|high|medium|low",
  "category": "dangerous_command|credential_leak|network_request|file_write|privilege_escalation|resource_exhaustion|dependency",
  "title": "string",
  "description": "string",
  "location": {
    "file_path": "string",
    "line_start": 0,
    "line_end": 0,
    "snippet": "string"
  },
  "pattern_matched": "string",
  "evidence": "string",
  "remediation": {
    "type": "auto_fix|disable|confirm|block",
    "suggestion": "string",
    "fixed_code": "string|null"
  },
  "references": ["string"]
}
```

### 严重等级定义/Severity Levels

```
┌──────────────────────────────────────────────────────────────────┐
│  Level      Score  Action                                        │
├──────────────────────────────────────────────────────────────────┤
│  critical   80-100 Block install, require manual override       │
│  high       60-79  Require user confirmation before install     │
│  medium     40-59  Suggest fix, allow install with warning      │
│  low        0-39   Optional improvement, no blocking            │
└──────────────────────────────────────────────────────────────────┘
```

## 风险评分计算/Risk Score Calculation

```json
{
  "risk_calculation": {
    "formula": "sum(weight(severity) * count) capped at 100",
    "weights": {
      "critical": 40,
      "high": 25,
      "medium": 10,
      "low": 2
    },
    "raw_score": 0,
    "capped_score": 0,
    "risk_level": "critical|high|medium|low",
    "deductions": {
      "critical_findings": 0,
      "high_findings": 0,
      "medium_findings": 0,
      "low_findings": 0
    },
    "adjustments": {
      "multi_file_pattern": -5,
      "repeated_pattern": -3,
      "network_exfiltration": -10,
      "dependency_vulnerability": -5
    }
  }
}
```

### 评分示例

| 场景 | 计算 | 得分 | 等级 |
|------|------|------|------|
| 1 个 critical | 40×1 | 40 | medium |
| 2 个 critical | 40×2 | 80 | critical |
| 1 critical + 2 high | 40+25×2 | 90 | critical |
| 3 medium + 2 low | 10×3+2×2 | 34 | low |
| 1 high + 5 medium | 25+10×5 | 75 | high |

## 修复建议结构/Remediation Suggestions

```json
{
  "remediation": [
    {
      "finding_id": "ANJ-001",
      "priority": "must_fix|should_fix|optional",
      "action_type": "auto_fix|manual_fix|disable|confirm",
      "description": "string",
      "before_code": "string",
      "after_code": "string",
      "verification_steps": ["string"]
    }
  ],
  "fix_summary": {
    "total_fixes": 0,
    "auto_fixable": 0,
    "manual_fix_required": 0,
    "fix_order": ["string"]
  }
}
```

## Markdown 人类审查报告/Markdown Human Review Format

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

## 详细发现/Detailed Findings

### 严重/Critical

| # | 文件:行号 | 问题 | 模式 | 修复建议 |
|---|----------|------|------|---------|
| 1 | {file}:L{n} | {title} | {pattern} | {suggestion} |

### 高/High

| # | 文件:行号 | 问题 | 模式 | 修复建议 |
|---|----------|------|------|---------|
| ... |

### 中/Medium

...

### 低/Low

...

## 修复建议/Fix Recommendations

### 必须修复/Must Fix (Priority: P0)

1. **{finding_id}**: {description}
   - 位置/Location: `{file}:L{line}`
   - 修复/Fix: {suggestion}

### 建议修复/Should Fix (Priority: P1)

1. **{finding_id}**: {description}

### 可选修复/Optional (Priority: P2)

1. **{finding_id}**: {description}

## 决策/Decision

**安装决策**: {decision}
- 已自动修复/Auto-fixed: {n}
- 需要确认/Requires review: {n}
- 剩余风险/Remaining risk: {n}

**签名/Signature**: an-jian @ {timestamp}
```

## 报告生成规则/Report Generation Rules

1. JSON 报告必须包含所有字段，空值填 `null` 或空数组
2. Markdown 报告省略无发现的等级分区
3. 行号从 1 开始，范围包含起止行
4. snippet 最多 3 行，用 `...` 标记截断
5. 修复代码必须可直接替换原代码
6. 评分精确到整数，不四舍五入
7. 验证步骤必须可操作，不写"检查代码"等模糊描述