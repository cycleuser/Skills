# 流程文档反AIGC检测规则

同 he-bing/rules/anti-aigc.md 的流程文档反AIGC规则。

安全审计报告补充特有规则：

## 安全审计特有AIGC模式

### 风险等级无依据

```
❌ AI模式：
"此风险等级为高"
"建议修复"

✅ 专业写法：
"风险等级：HIGH。依据：curl|bash 模式可在任意目标主机执行代码，影响范围100%用户（未安装前），CVSS评分9.8。修复方案：下载脚本到/tmp后用less查看再执行，修改后CVE编号待定。"
```

### 修复建议笼统

```
❌ AI模式：
"建议修复此安全问题"
"建议移除危险代码"

✅ 专业写法：
"修复方案：将 quick-install.sh 中第3行：
  curl -fsSL $URL | bash
改为：
  curl -fsSL $URL -o /tmp/install.sh && less /tmp/install.sh && bash /tmp/install.sh
此修改保留功能但增加人工审查环节。"
```

## 检测标准同 he-bing/rules/anti-aigc.md