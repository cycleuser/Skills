---
name: an-jian
version: "1.0.0"
description: |
  安检 - Security review for skills before installation.
  
  触发条件/Triggers: 安装新技能前、定期审查已安装技能、或怀疑技能有安全问题。
  
  安全检查/Security Checks:
  - 危险命令/Dangerous Commands: rm -rf, sudo, curl|bash 等
  - 网络请求/Network Requests: 可能泄露数据
  - 文件写入/File Writes: 敏感位置写入
  - 凭证泄露/Credentials: API key/密码泄露风险
  - 资源耗尽/Resource Exhaustion: 无限循环
  - 权限提升/Privilege Escalation: 提权尝试
  - 外部依赖/External Dependencies: 可疑依赖
  
  命令/Commands:
  - /安检 <技能路径> - 审查技能安全
  - /安检 scan <路径> - 深度扫描
  - /安检 list - 列出已安装技能风险
  - /安检 fix <技能> - 修复安全问题
  - /security <skill-path> - English command
  
  处理方式/Actions:
  - 自动修复/Auto-fix: 移除或替换危险代码
  - 禁用部分/Disable: 禁用危险功能
  - 用户确认/User Confirm: 用户选择是否继续
  - 阻止安装/Block: 严重风险阻止安装
  
  能力/Capabilities: 静态代码分析、危险模式识别、风险评估、自动修复、用户交互决策。
author: cycleuser
license: MIT
---

# 安检 (Security Review)

技能安全审查技能。安装前审查，确保无安全隐患。
Security review for skills. Pre-installation check ensures no security risks.

## Quick Commands

| 命令/Command | 功能/Function |
|-------------|--------------|
| `/安检 <技能路径>` | 审查技能安全 |
| `/安检 scan <路径>` | 深度扫描 |
| `/安检 list` | 列出已安装技能风险 |
| `/安检 fix <技能>` | 修复安全问题 |
| `/security <path>` | Review skill security |
| `/security scan <path>` | Deep scan |
| `/security list` | List installed risks |
| `/security fix <skill>` | Fix security issues |

## 安全检查项/Security Checks

### 1. 危险命令/Dangerous Commands

```
【严重风险/Critical】
- rm -rf / - 删除根目录
- rm -rf ~ - 删除用户目录
- dd if=/dev/zero - 磁盘擦除
- :(){ :|:& };: - Fork bomb
- curl ... \| bash - 执行远程脚本
- wget ... \| sh - 执行远程脚本
- sudo rm -rf - 提权删除
- chmod 777 / - 开放所有权限
- mkfs - 格式化磁盘

【高风险/High】
- rm -rf (无确认)
- sudo (无必要)
- curl/wget 下载可执行文件
- nc -e /bin/sh - 反弹 shell
- base64 -d \| sh - 解码执行

【中风险/Medium】
- eval - 动态执行
- exec - 动态执行
- subprocess with shell=True
- os.system - 系统调用
```

### 2. 网络请求/Network Requests

```
【检查项/Checks】
- 是否发送数据到外部服务器
- 是否收集用户环境信息
- 是否上传代码或凭证
- 是否有硬编码的 URL
- 是否使用 HTTPS

【风险模式/Risk Patterns】
curl -X POST http://...  # 发送数据
requests.post(..., json={...})  # 发送 JSON
fetch('http://...', {...})  # 发送请求
```

### 3. 文件写入/File Writes

```
【敏感位置/Sensitive Locations】
- /etc/ - 系统配置
- /usr/ - 系统程序
- ~/.ssh/ - SSH 密钥
- ~/.bashrc - Shell 配置
- /tmp/ - 临时目录（可能被利用）
- 用户家目录/ - 用户文件

【检查项/Checks】
- 是否写入敏感位置
- 是否覆盖现有文件
- 是否创建隐藏文件
- 是否修改系统配置
```

### 4. 凭证泄露/Credentials

```
【风险模式/Risk Patterns】
- API_KEY = "sk-..."  # 硬编码 API 密钥
- password = "..."  # 硬编码密码
- token = "..."  # 硬编码令牌
- AWS_SECRET_ACCESS_KEY  # AWS 凭证
- GITHUB_TOKEN  # GitHub 令牌

【环境变量/Env Vars】
- 是否读取敏感环境变量
- 是否泄露环境变量到日志
- 是否发送到外部服务器
```

### 5. 资源耗尽/Resource Exhaustion

```
【风险模式/Risk Patterns】
- while true: ...  # 无限循环
- for i in range(999999999): ...  # 大循环
- recursion without limit  # 无限递归
- 创建大量文件/进程
- 分配大量内存
```

### 6. 权限提升/Privilege Escalation

```
【风险模式/Risk Patterns】
- sudo - 提权执行
- setuid/setgid - 设置权限位
- chown root - 修改所有者
- 利用漏洞提权
```

### 7. 外部依赖/External Dependencies

```
【检查项/Checks】
- 依赖是否来自可信源
- 依赖是否有已知漏洞
- 依赖是否过多（供应链攻击）
- 是否有非常见依赖
```

## 风险评估/Risk Assessment

```
【风险等级/Risk Levels】

严重/Critical:
- 可能导致系统损坏
- 可能导致数据丢失
- 可能导致凭证泄露
处理：阻止安装，除非用户明确确认

高/High:
- 可能执行危险操作
- 可能泄露敏感信息
处理：需要用户确认，建议修复

中/Medium:
- 潜在风险
- 需要特定条件触发
处理：提示用户，可选修复

低/Low:
- 轻微风险
- 最佳实践问题
处理：建议改进，不影响安装
```

## 审查流程/Review Workflow

### Phase 1: 静态分析/Static Analysis

```markdown
## 静态分析报告/Static Analysis Report

**技能/Skill**: {skill_name}
**审查时间/Time**: {timestamp}

### 危险命令/Dangerous Commands
| 位置/Location | 命令/Command | 风险/Risk | 说明/Description |
|--------------|-------------|----------|-----------------|
| SKILL.md:L45 | rm -rf | 高/High | 无确认删除 |

### 网络请求/Network
| 位置/Location | URL | 方法/Method | 风险/Risk |
|--------------|-----|----------|----------|
| script.py:L20 | http://... | POST | 中/Medium |

### 文件操作/File Operations
| 位置/Location | 路径/Path | 操作/Operation | 风险/Risk |
|--------------|----------|-------------|----------|
| setup.sh:L10 | ~/.bashrc | Append | 高/High |

### 凭证/Credentials
| 位置/Location | 类型/Type | 风险/Risk |
|--------------|----------|----------|
| config.py:L5 | API_KEY | 严重/Critical |
```

### Phase 2: 风险评估/Risk Assessment

```markdown
## 风险评估/Risk Assessment

**总体风险/Overall Risk**: {Critical/High/Medium/Low}

### 风险汇总/Risk Summary
| 风险等级/Risk | 数量/Count | 处理/Action |
|--------------|-----------|------------|
| 严重/Critical | {n} | 必须修复/Must fix |
| 高/High | {n} | 建议修复/Should fix |
| 中/Medium | {n} | 可选修复/Optional |
| 低/Low | {n} | 建议改进/Suggest |
```

### Phase 3: 用户决策/User Decision

```markdown
## 安全审查决策/Security Decision

**技能/Skill**: {skill_name}
**总体风险/Overall Risk**: {level}

### 发现的风险/Risks Found
{risk_list}

### 建议操作/Recommended Actions
1. {action1}
2. {action2}

### 请选择/Please Choose:

[A] 自动修复/Auto-fix
    - 移除或替换危险代码
    - 禁用危险功能
    - 添加安全确认

[B] 手动审查/Manual Review
    - 查看具体风险位置
    - 逐项决定是否保留

[C] 禁用危险部分/Disable Dangerous Parts
    - 保留技能但禁用风险功能
    - 需要时手动启用

[D] 取消安装/Cancel Installation
    - 不安装此技能
    - 寻找替代方案

[E] 继续安装（风险自负）/Continue at Own Risk
    - 忽略所有警告
    - 用户承担全部责任

选择/Choice: [A/B/C/D/E]
```

### Phase 4: 执行决策/Execute Decision

```markdown
## 决策执行/Decision Execution

**用户选择/User Choice**: {choice}

### 执行结果/Execution Result

#### 自动修复/Auto-fix
| 原代码/Original | 修复后/Fixed | 状态/Status |
|---------------|------------|------------|
| rm -rf {dir} | rm -rf {dir} && confirm() | ✅ |

#### 禁用部分/Disabled
| 功能/Feature | 状态/Status |
|------------|------------|
| network_upload | 已禁用/Disabled |

#### 安装确认/Installation Confirm
- [ ] 用户已确认风险/User confirmed risks
- [ ] 已记录审计日志/Audit logged
- [ ] 已创建回滚方案/Rollback ready
```

## 审计报告/Audit Report

```markdown
## 安全审计报告/Security Audit Report

**技能/Skill**: {skill_name}
**审查者/Reviewer**: an-jian
**时间/Time**: {timestamp}
**版本/Version**: {version}

### 审查摘要/Summary
- 检查项/Checks: {total}
- 发现风险/Risks: {count}
- 已修复/Fixed: {count}
- 剩余风险/Remaining: {count}

### 风险详情/Risk Details
{detailed_risks}

### 修复记录/Fix Records
{fix_records}

### 用户确认/User Confirmation
- 已告知风险/Risks disclosed: ✅
- 用户确认/User confirmed: ✅
- 确认时间/Time: {timestamp}

### 建议/Recommendations
{recommendations}
```

## 使用示例/Examples

### 示例 1：审查新技能

```
用户/User: /安检 ./skills/new-skill

→ Phase 1: 静态分析/Static analysis
→ Phase 2: 风险评估/Risk assessment
→ Phase 3: 用户决策/User decision
→ Phase 4: 执行决策/Execute decision
→ 输出审计报告/Output audit report
```

### Example 2: List Installed Risks

```
用户/User: /security list

→ 扫描已安装技能/Scan installed skills
→ 列出所有风险/List all risks
→ 提供修复建议/Provide fix suggestions
```

### 示例 3：修复安全问题

```
用户/User: /安检 fix <技能名>

→ 分析安全问题/Analyze security issues
→ 生成修复方案/Generate fix plan
→ 执行修复/Execute fixes
→ 验证修复结果/Verify fixes
```

## Rules

- [rules/dangerous-patterns.md](rules/dangerous-patterns.md) - 危险模式/Dangerous Patterns
- [rules/risk-assessment.md](rules/risk-assessment.md) - 风险评估/Risk Assessment
- [rules/fix-strategies.md](rules/fix-strategies.md) - 修复策略/Fix Strategies
- [rules/audit-format.md](rules/audit-format.md) - 审计格式/Audit Format

## 配置选项/Configuration

| 参数/Param | 默认值/Default | 说明/Description |
|-----------|---------------|-----------------|
| auto_block_critical | true | 自动阻止严重风险/Auto-block critical |
| require_confirm_high | true | 高风险需要确认/Confirm high risk |
| audit_log_enabled | true | 启用审计日志/Enable audit log |
| max_risk_level | high | 最大允许风险/Max allowed risk |

## 集成/Integration

### 与安装流程集成/Install Integration

```
安装技能/Install Skill:
    ↓
调用 /安检/Call /security
    ↓
风险审查/Risk Review
    ↓
┌─────────────────────────────────────┐
│ 风险等级/Risk Level                 │
├─────────────────────────────────────┤
│ 严重/Critical → 阻止 (用户确认例外)  │
│ 高/High → 需要用户确认              │
│ 中/Medium → 提示，可选修复          │
│ 低/Low → 通过                       │
└─────────────────────────────────────┘
    ↓
通过/Pass → 继续安装/Continue
    ↓
失败/Fail → 取消安装/Cancel
```
