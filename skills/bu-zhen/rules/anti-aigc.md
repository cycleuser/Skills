# 编排文档反AIGC检测规则

多agent编排文档(agent角色、委派契约、工作流阶段)面临独特的AIGC风险——它描述的是调度决策与角色边界,容易被写成正确的但放在任何编排框架都成立的泛泛之谈。好的编排文档读起来像调度器设计者在白板前讲解"为什么这个lane归这个agent";AI生成的读起来像分布式系统教科书的角色描述,空有术语没有取舍。

## 核心原则

编排文档反AIGC的关键是**委派理由充分**和**有边界取舍**。AI倾向生成"使用orchestrator协调专家"后列出多agent的一般性优点,而非针对本工作流的约束。人类写编排文档会写"为什么这个任务归fixer而非orchestrator",会写具体的token预算、时间预算、写范围冲突检测规则。

## 编排文档AIGC高发模式

### 1. 角色描述空洞(权重25%)

```
❌ AI模式:
"使用orchestrator协调多个专家agent"
"explorer负责代码库探索"
"oracle提供战略建议"
"fixer执行实现工作"

问题:这些描述放在任何编排框架都成立,没有具体委派条件。

✅ 专业写法:
"路由阈值:仅当满足(1)单个孤立动作(2)委派开销>执行开销(3)无合适专家,orchestrator才自己做。UI/设计工作永远路由designer——理由:designer模型(gpt-5.6-luna)在UI/UX任务上比orchestrator(gpt-5.6-terra)好10倍,但写范围与fixer重叠时必须串行。实测:terraform计划+委派+调和的延迟约3.2s,而orchestrator自己做一个20行单文件改动约8s——故<20行单文件自己做,>20行或多文件委派。"
```

### 2. 委派契约无对比(权重25%)

```
❌ AI模式:
"采用委派模式分配任务"
"使用后台任务并行执行"
"通过任务板跟踪状态"

✅ 专业写法:
"委派用background subagent而非同步task——理由:(1) 同步task阻塞orchestrator lane,3个并行fixer任务串行执行约90s,background并行约35s;(2) background任务通过任务板自动通知完成,orchestrator可继续独立工作。代价:background任务无法实时prompt子会话——task_message仅排队非打断通信,task_status只读检查。替代(同步task):适用场景是下一步强依赖结果时,如oracle审查必须等结果才能继续。"
```

### 3. 预算与限制缺失(权重20%)

```
❌ AI模式:
"对agent设置预算限制"
"实现doom loop检测"
"限制并行任务数量"

✅ 专业写法:
"预算上限(prompt层约束,配合opencode permission可升级为技术强制):subagent 50k token / 10min;orchestrator 500k token / 2h;council单次150k token / 30min。达80%警告,耗尽即冻结并报告'<scope>用<tokens>token / <time>'。预算不自动续期,用户显式批准才追加。doom-loop检测:同agent同参数连续3次即暂停(维护最近5次调用记录,比对agent名+工具名+参数哈希),触发后必须用户介入,技能不自行恢复——这是对'never stop'型上游(oh-my-openagent的ultrawork/boulder、slim的goal)失控风险的约束。诚实标注:未配合opencode permission配置前,这些靠agent遵守prompt,不构成系统级强制。"
```

### 4. 安全规则泛泛(权重15%)

```
❌ AI模式:
"采用多层安全机制确保编排安全"
"对敏感操作进行审批和限制"
"实现路径隔离"

✅ 专业写法:
"编排层安全硬化(10条prompt层约束,配合opencode permission配置可升级为技术强制):
1. 敏感目录禁区:对~/.ssh、~/.aws、~/.config/opencode、.git/、.env*、*.key、*.pem禁写禁删禁移动——解析目标绝对路径(含symlink跟随)比对13个glob,命中即拒绝并报告。
2. 路径白名单:所有写在PROJECT_ROOT(首次/布阵时readlink -f cwd锁定)内,每写前解析绝对路径+symlink跟随检查前缀。
3. 预算上限:见上,达80%警告,耗尽冻结。并行subagent≤8(参考真原版team-core max_members硬上限)。
4. doom-loop:3次相同调用暂停。
5. 禁远程脚本:扫描命令文本,命中curl|bash/wget|bash/eval/node -e/python -c/npx install/pip/npm/brew/go/cargo install/docker pull等14+模式即拒绝,展示命令等用户确认。
6. 无OAuth透传:不读auth.json/credentials.json,不调OAuth端点,不在日志含key片段。
7. subagent隔离:独立会话,不直接互调,跨subagent数据经orchestrator调和。
8. 审查预算:每gate 1+2=3次,超出拒绝。
9. 并行写冲突检测:派发前收集写所有权,重叠即拒绝。
10. 审计日志:所有委派/预算/拦截记JSONL到.bu-zhen/audit.jsonl,不含key不含内容片段。
诚实标注:未配合opencode permission配置前,这些靠agent遵守prompt;配置后(见safety-hardening.md末尾示例)由opencode在工具执行前拦截,升级为系统级强制。"
```

### 5. 工作流阶段无方案对比(权重15%)

```
❌ AI模式:
"采用五阶段工作流"
"先理解再规划再执行"
"最后验证"

✅ 专业写法:
"五阶段:理解→路径选择→委派检查→规划并行化→验证。为何不是三阶段(规划→执行→验证):三阶段在'执行'阶段把委派决策混入实现,实测在多专家场景下orchestrator会串行执行本应并行的lane——拆出'委派检查'独立阶段后,并行率从40%升到75%(20个多文件任务样本)。为何不是七阶段(加'风险评估'与'成本核算'独立阶段):这两步在路径选择阶段已隐含,独立阶段增加orchestrator token开销约8k/任务而无决策质量提升——故合并入路径选择。deepwork协议在五阶段上加门控:每阶段后强制@oracle审查,但仅用于高风险多阶段工作,常规任务用五阶段即可。"
```

## 编排文档反AIGC五原则

### 1. 每个委派决策标注排除理由

不写"用X agent",写"委派给X而非Y,因为Y在本工作流场景下有[具体问题]"。

### 2. 所有预算/限制配数字

不写"设置预算",写"subagent 50k token / 10min,达80%警告,耗尽冻结"。

### 3. 安全规则写具体而非口号

不写"多层安全",写"7个正则比对敏感目录+PROJECT_ROOT前缀检查+预算计数器+doom-loop 5次记录"。

### 4. 委派写约束而非通用优点

不写"background任务高效",写"background并行35s vs 同步串行90s,代价是无法实时prompt子会话"。

### 5. 标注替代方案和折衷

不写确定语气,写"代价是X"、"替代方案Y的劣势是Z"、"为何不是N阶段"。

## AIGC率检测清单

### 内容检测
- [ ] 每个委派决策是否有排除理由?→无理由=AI
- [ ] 预算/限制是否有具体数字(token、分钟、百分比)?→无数字=AI
- [ ] 安全规则是否有具体实现(正则条数、路径检查方式、计数器逻辑)?→口号式=AI
- [ ] 工作流阶段是否有方案对比(为何不是N阶段)?→直接定论=AI
- [ ] 是否有替代方案和折衷说明?→全确定=AI

### 语言检测
- [ ] 是否出现"采用X模式"而无具体委派条件?→有=AI
- [ ] 是否出现"高效/安全/可靠"等空洞形容词?→有=AI
- [ ] 预算描述是否有具体数值?→无=AI
- [ ] 角色描述是否可映射到具体工具调用与权限?→不可映射=AI

### AIGC率评分标准

- 0-15%:像调度器设计文档,每个委派决策有数据支撑
- 16-30%:合格,有少量可优化项
- 31-50%:需修改,像分布式系统教科书
- 51-70%:需重写,空有术语没有取舍
- 71-100%:纯AI模板,正确但无用