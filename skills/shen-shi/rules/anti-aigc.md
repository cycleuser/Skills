# GitHub分析报告反AIGC检测规则

GitHub Issue/PR分析报告（问题分类、证据收集、优先级判定、修复建议）面临独特的AIGC风险——分析报告需要基于代码证据下判断，容易被写成正确的但无代码引用的泛泛之谈。好的分析报告读起来像代码审查意见，每句判断都有permalink支撑；AI生成的读起来像摘要，有结论无证据。

## 核心原则

GitHub分析报告反AIGC的关键是**证据链接必附**和**分类有判定边界**。AI倾向生成"这个Issue像是bug"的模糊判断。人类写分析报告会写具体的代码行号、复现步骤、证据permalink，会明确分类边界（bug还是feature、P1还是P2）。

## GitHub分析报告AIGC高发模式

### 1. 证据不足就下判断（权重25%）

```
❌ AI模式：
"这个Issue明显是一个bug"
"PR的代码质量很高"
"存在安全风险"

问题：没有代码证据支撑，判断无法验证。

✅ 专业写法：
"根据 src/auth.py:45 的代码，login() 函数在用户名为空时直接拼接SQL——这构成SQL注入漏洞（复现：curl -X POST /auth/login -d 'user=\x27OR\x201=1--'）。证据链接：https://github.com/org/repo/blob/abc123/src/auth.py#L45

进一步验证：src/auth.py:52 的register()函数使用了参数化查询（安全），但login()没有复用同一模式——这是一个疏忽而非系统性问题。"
```

### 2. 标签分类模糊（权重20%）

```
❌ AI模式：
"这个问题涉及多个方面"
"需要进一步讨论"
"可能是一个bug或feature"
"优先级较高"

✅ 专业写法：
"分类：bug（不是feature-request）
理由：Issue标题写'report not loading'，复现步骤明确（步骤3/3必现），代码根因是core/report.py:89 的NoneType错误——这是运行时错误不是需求不满足。
优先级：P1（不是P2/P3）
理由：(1)有workaround（手动刷新页面），但UX极差（用户需操作3次才能看到报告）；(2)影响面：所有查看报告的用户（约60%日活用户）；(3)无数据丢失风险→不升级P0。
指派建议：@auth-team（认证模块负责人，过去3个类似bug都是此团队修复的）"
```

### 3. PR审查流于表面（权重20%）

```
❌ AI模式：
"PR的代码整体质量不错"
"建议增加一些测试"
"代码风格需要改进"

✅ 专业写法：
"PR #127 审查（+89 -34，修改文件5个）：
严重问题（1项）：
- src/api.py:45 新增的get_user()缺少认证装饰器@require_auth——当前任何匿名请求都能获取用户信息（信息泄露风险）。对比：同文件get_settings()有装饰器（第38行）。修复：在44行添加@require_auth。
建议改进（2项）：
- tests/test_api.py 缺少get_user的测试——当前覆盖率从92%降至88%（新增代码无测试）
- src/api.py:67 的f-string中有3个变量插值，建议用.format()提升可读性（低优先级）
肯定（1项）：
- src/api.py:52 的错误处理是本PR最佳实践——使用了自定义异常UserNotFoundError而非通用Exception，保持了异常层级一致性。"

### 4. 分析报告无复现路径（权重15%）

```
❌ AI模式：
"问题出现在用户登录时"
"当数据量较大时会触发"
"特定条件下会发生错误"

✅ 专业写法：
"复现路径（3步必现）：
1. POST /auth/login -d '{"user":"test","pass":"test"}' （返回token: abc123）
2. DELETE /auth/user/test -H 'Authorization: Bearer abc123' （返回200 OK）
3. GET /auth/user/test -H 'Authorization: Bearer abc123' （返回500 Internal Server Error）

根因：DELETE操作软删除用户（deleted_at字段），但GET查询没有过滤deleted_at IS NULL——SQL：src/auth.py:89 `SELECT * FROM users WHERE username='test'`应为`SELECT * FROM users WHERE username='test' AND deleted_at IS NULL`。"

### 5. 修复建议不具体（权重10%）

```
❌ AI模式：
"建议修复这个安全漏洞"
"应该添加适当的错误处理"
"需要完善输入验证"

✅ 专业写法：
"修复方案（2行代码）：
文件：src/auth.py
行号：第45行
修改前：`query = f"SELECT * FROM users WHERE username='{username}'"`
修改后：`query = "SELECT * FROM users WHERE username=%s"; cursor.execute(query, (username,))`

影响范围：仅影响login()函数（1处），register()函数已使用参数化查询（第52行）。
测试：需新增 test_auth.py::test_sql_injection_empty_username 和 test_auth.py::test_sql_injection_or_1_1 两个用例。回归风险：低——参数化查询是标准模式，同文件已有使用先例。"

### 6. 趋势分析无数据（权重10%）

```
❌ AI模式：
"近期bug报告有所增加"
"代码质量保持稳定"
"社区反馈整体积极"

✅ 专业写法：
"Issue趋势分析（近30天）：
- bug类Issue：12个（前30天：7个，+71%），根因分布：认证模块4个（+300%）、数据模块3个（+0%）、UI模块5个（+67%）
- 认证模块bug激增原因：v2.3.0重构（commit abc123）引入了4个regression——均有对应PR修复中
- 平均Issue关闭时间：3.2天（前30天：4.1天，-22%）
- P0 Issue：0个（前30天：1个）→系统稳定性改善

预测：若认证模块4个regression在3天内修复，bug类Issue将回落至7-8个/月（正常水平）。"
```

## GitHub分析报告反AIGC六原则

### 1. 每个判断附代码证据和permalink

不写"明显是bug"，写"src/auth.py:45 直接拼接SQL，permalink: ..."。

### 2. 分类有判定边界

不写"可能是bug"，写"分类：bug（不是feature），理由：[具体]"。

### 3. PR审查分严重/建议/肯定三级

不写"代码质量不错"，写"严重问题1项（第X行缺少装饰器），建议2项，肯定1项"。

### 4. 复现路径精确到curl命令

不写"登录时出错"，写"3步curl复现路径"。

### 5. 修复建议精确到文件行号和代码diff

不写"应该修复"，写"文件:行号，修改前→修改后，影响1处"。

### 6. 趋势分析配具体数据

不写"bug有所增加"，写"bug 12个（前30天7个，+71%），根因分布：..."。

## AIGC率检测清单

### 内容检测
- [ ] 每个判断是否有代码证据（文件:行号）？→无证据=AI
- [ ] 分类是否有判定边界（A不是B）？→模糊分类=AI
- [ ] PR审查是否有严重/建议/肯定分级？→全是建议=AI
- [ ] 复现路径是否精确到curl/API调用？→笼统描述=AI
- [ ] 修复建议是否有代码diff？→只有"应该X"=AI
- [ ] 趋势分析是否有具体数字和前值？→只有结论=AI

### 语言检测
- [ ] 是否出现"明显/可能/需要进一步讨论"等模糊判断？→大量出现=AI
- [ ] 是否有permalink或具体代码行号？→无=AI
- [ ] 优先级是否有P0/P1/P2/P3标签？→无=AI
- [ ] 分类是否包含排除理由（bug不是feature）？→无排除=AI

### AIGC率评分标准

- 0-15%：像资深工程师的code review，每个判断有证据
- 16-30%：合格，有少量可优化项
- 31-50%：需修改，像摘要而非分析
- 51-70%：需重写，有结论无证据
- 71-100%：纯AI模板，每个判断都似是而非