---
name: an-jian
version: "1.1.0"
description: |
  Security review for skills before installation, detecting dangerous patterns and assessing risk levels.

  Triggers when: Installing a new skill, periodically reviewing installed skills, or suspecting security issues in a skill.

  Commands:
  - /安检 <技能路径> - Audit skill security
  - /安检 scan <路径> - Deep scan
  - /安检 list - List installed skill risks
  - /安检 fix <技能> - Fix security issues
  - /security <skill-path> - English command for skill security audit

  Capabilities: Static code analysis, dangerous pattern recognition, risk assessment, auto-fix, user interaction decisions
author: cycleuser
license: MIT
---

## Safety Rules

**Critical**: Read and follow [global-rules/bash-safety.md](file:///Users/fred/.config/opencode/skills/global-rules/rules/bash-safety.md) for all bash/command execution.

Core rules:
1. **Always set explicit `timeout` on bash calls** — 30s for tests, 60s for installs, never default
2. **Never run unscoped full test suites** — use `-k` or file paths to limit scope
3. **Never use `rm -rf` without variable guards**, `curl|bash`, `sudo`, or `kill -9`
4. **Infinite loops must have hard timeout + budget limits** — no unbounded while(True)
5. **Redirect stdin** with `< /dev/null` for non-interactive commands

A bash timeout that triggers SIGKILL corrupts the terminal FD, crashes opencode's TUI, and forces a GUI restart.

# 安检 (Security Review)

技能安全审查技能。安装前审查，确保无安全隐患。
Security review for skills. Pre-installation check ensures no security risks.

## Quick Commands

| Command | Description |
|---------|-------------|
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

## Performance & Resource Management / 性能与资源管理

### Scan Optimization / 扫描优化
- **Incremental scanning**: Only scan files changed since last audit; use `/安检 scan --incremental` for large projects
- **Pattern pre-filtering**: Skip binary files, minified code, and generated files (node_modules, __pycache__, .git) by default
- **Parallel file scanning**: Split file list across workers for repos with >100 files; max 4 parallel workers

### Caching Strategy / 缓存策略
- **Rule cache**: Pre-compiled regex patterns cached for 24 hours — avoids recompilation on re-scan
- **Result cache**: Identical files with same hash skip re-scanning; cache valid for 1 hour
- **Network call batching**: Group network dependency checks into batches of 10 to reduce API round trips

### Large Repository Handling / 大仓库处理
- **Depth-limited scanning**: `--depth 3` limits dependency tree analysis to 3 levels for npm/pip packages
- **Shard mode**: Repos >10,000 files split into shards of 1000; results aggregated after parallel scan
- **Timeout per file**: Each file limited to 30s analysis; files exceeding timeout flagged as "complex" for manual review

### Report Optimization / 报告优化
- **Risk aggregation**: Duplicate findings across files merged into single risk entry with file list
- **Priority filtering**: `--min-severity high` skips low/info findings for faster triage
- **Streaming output**: Long reports streamed as generated, not buffered in memory

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

## 常见问题与排查 / Troubleshooting

### 扫描结果过多 / Too many scan results
- **症状/Symptom**: `/安检 scan` 返回数百条警报，难以筛选 / Returns hundreds of alerts, hard to triage
- **解决/Fix**: 使用 `--min-severity high` 只显示高危；使用 `/安检 scan --priority network,credentials` 按类型过滤；分目录逐步扫描

### 误报率高 / High false positive rate
- **症状/Symptom**: 安全标记了无害代码 / Safe code flagged as dangerous
- **解决/Fix**: 使用 `/安检 fix --whitelist <pattern>` 添加白名单规则；检查规则匹配严格度 `--strictness moderate`

### 大仓库扫描超时 / Large repo scan timeout
- **症状/Symptom**: 超过10,000文件时扫描超时 / Scan times out on repos >10,000 files
- **解决/Fix**: 使用 `--shard` 分片扫描；排除 node_modules/.git/__pycache__ 目录；使用 `--incremental` 增量扫描

## 边界情况 / Edge Cases

- **自解压安装脚本**: 检测到 `curl|bash` 模式 → 标记为 `CRITICAL` 风险，要求手动审计
- **内嵌二进制**: 技能包含 base64 编码的二进制 → 标记为 `HIGH` 风险，要求声明用途
- **跨平台脚本**: 检测到 Windows 和 Unix 命令混用 → 标记为 `MEDIUM`，需确认兼容性
- **加密矿工程序**: 检测到 `stratum+tcp://` 或高CPU使用模式 → 标记为 `CRITICAL`，直接阻止
- **凭证泄露残留**: 检测到 API key 或 token 模式 → 标记为 `CRITICAL`，建议立即轮换密钥

## 版本历史 / Version History

| 版本 | 日期 | 变更 |
|------|------|------|
| 1.0.0 | 2026-04-01 | 初始版本，7项安全检查 |
| 1.1.0 | 2026-05-09 | 添加安全规则，集成，性能管理，排查，边界情况，audit-format.md |

## 相关技能

- `/把关` from **ba-guan** — 发布前审查中的安全审计层
- `/审视` from **shen-shi** — 仓库代码只读审计模式
- `/修炼` from **skill-refiner** — 修炼过程中修复安全缺陷
