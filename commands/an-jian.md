---
description: 安全审查技能/Security review for skills
agent: build
---

Load the an-jian skill and review skill security: $ARGUMENTS

**用法/Usage**: `/安检 <技能路径>` or `/security <skill-path>`

**示例/Examples**:
- `/安检 ./skills/new-skill` - 审查新技能/Review new skill
- `/安检 scan <路径>` - 深度扫描/Deep scan
- `/安检 list` - 列出已安装风险/List installed risks
- `/security <path>` - English command
- `/security scan <path>` - Deep scan

**功能/Function**: 技能安全审查，检测危险命令、网络请求、凭证泄露等/Security review detects dangerous commands, network requests, credential leaks, etc.

**处理方式/Actions**:
- 自动修复/Auto-fix
- 禁用危险部分/Disable dangerous parts
- 用户确认/User confirm
- 阻止安装/Block installation
