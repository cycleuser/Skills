---
name: official-document-writer
version: "1.0.0"
description: |
  Official document writing assistant for Chinese government documents. Based on GB/T 9704-2012 standard.

  Triggers when: Writing Chinese official documents (公文), formatting documents according to national standards, reviewing document compliance, or creating notices, reports, requests, replies, letters, or minutes.

  Commands:
  - /gongwen notice <topic> - Write a notice (通知)
  - /gongwen report <topic> - Write a report (报告)
  - /gongwen request <topic> - Write a request (请示)
  - /gongwen reply <topic> - Write a reply (批复)
  - /gongwen letter <topic> - Write a letter (函)
  - /gongwen minutes <topic> - Write meeting minutes (纪要)
  - /gongwen check <document> - Check document compliance
  - /gongwen format - Show formatting rules

  Capabilities: 15 document types support, GB/T 9704-2012 compliance, hierarchy numbering rules, font and layout specifications, and document structure templates.
author: cycleuser
license: MIT
---

# Official Document Writer

Chinese official document writing assistant based on GB/T 9704-2012 national standard.

## Quick Commands

Eight commands correspond to the main document types. The `/gongwen notice <topic>` command writes a notice (通知). The `/gongwen report <topic>` command writes a report (报告). The `/gongwen request <topic>` command writes a request (请示). The `/gongwen reply <topic>` command writes a reply (批复). The `/gongwen letter <topic>` command writes a letter (函). The `/gongwen minutes <topic>` command writes meeting minutes (纪要). The `/gongwen check <document>` command checks document compliance. The `/gongwen format` command shows formatting rules.

## Document Types (公文种类)

According to "Regulations on the Handling of Official Documents of Party and Government Organs" (党政机关公文处理工作条例), there are 15 document types. Decision (决定) handles important matter deployment and rewards or punishments. Order (命令/令) publishes laws, appointments, removals, and commendations. Public Notice (公告) announces important matters domestically and internationally. Announcement (通告) publishes matters for general public knowledge. Notice (通知) handles approval and forwarding, deployment, and appointments. Circular (通报) praises excellence or criticizes mistakes. Proposal (议案) submits matters for deliberation. Report (报告) reports on work and responds to inquiries. Request (请示) requests instructions and approval. Reply (批复) responds to requests. Opinion (意见) provides insights and methods. Letter (函) handles work consultation and inquiry responses. Minutes (纪要) records main meeting circumstances.

## Document Structure (公文结构)

### Standard Format Elements

```
┌─────────────────────────────────────────────────────────────┐
│                        版头 (Header)                         │
├─────────────────────────────────────────────────────────────┤
│  份号 (保密件编号)                                           │
│  密级和保密期限 (如：机密★5年)                                │
│  紧急程度 (特急/加急)                                         │
│  发文机关标志 (红头)                                          │
│  发文字号 (如：国发〔2024〕1号)                               │
│  签发人 (上行文需标注)                                        │
├─────────────────────────────────────────────────────────────┤
│                        主体 (Body)                           │
├─────────────────────────────────────────────────────────────┤
│  标题 (居中，2号小标宋体)                                     │
│  主送机关 (顶格，3号仿宋)                                     │
│  正文 (3号仿宋)                                              │
│  附件说明                                                    │
│  发文机关署名                                                │
│  成文日期                                                    │
│  印章                                                        │
│  附注                                                        │
├─────────────────────────────────────────────────────────────┤
│                        版记 (Footer)                         │
├─────────────────────────────────────────────────────────────┤
│  抄送机关                                                    │
│  印发机关 / 印发日期                                         │
│  页码 (— 1 —)                                                │
└─────────────────────────────────────────────────────────────┘
```

### Letter Format Elements

```
┌─────────────────────────────────────────────────────────────┐
│                     信函格式 (Letter Format)                  │
├─────────────────────────────────────────────────────────────┤
│  发文机关名称 (居中)                                          │
│  发文字号 (右上角)                                            │
│  标题 (居中)                                                  │
│  主送机关                                                     │
│  正文                                                         │
│  发文机关署名                                                 │
│  成文日期                                                     │
│  印章                                                         │
└─────────────────────────────────────────────────────────────┘
```

## Formatting Rules (格式规范)

### Hierarchy Numbering (层次序号)

According to GB/T 9704-2012, the four-level hierarchy numbering system uses distinct formats at each level. The first level uses Chinese numerals with a pause (一、二、三、……). The second level uses full-width parentheses with Chinese numerals（（一）（二）（三）……). The third level uses Arabic numerals with an English period (1. 2. 3. ……)。 The fourth level uses full-width parentheses with Arabic numerals（（1）（2）（3）……). Note: Do NOT use Roman numerals (I, II, III) or other formats.

### Font Specifications (字体规格)

Different document elements require specific fonts and sizes. The发文机关标志 uses small standard Song typeface in red. The 标题 uses small standard Song typeface in size 2. The 主送机关 uses Fang Song in size 3. The first level of 正文 uses Hei in size 3. The second level of 正文 uses Kai in size 3. The third and fourth levels of 正文 use Fang Song in size 3. The 发文字号 uses Fang Song in size 3. The 页码 uses Song in size 4.

### Page Layout (页面设置)

Page layout follows strict specifications. Paper size is A4 (210mm × 297mm). Margins are top 37mm, bottom 35mm, left 28mm, right 26mm. Line spacing is fixed 28 pounds (approximately 0.99cm). Page number format is — 1 — (one dash + page number + one dash). Page number position is bottom center, odd pages on right, even pages on left.

### Date Format (日期格式)

The correct format is 2024年3月15日. Common errors include 二〇二四年三月十五日 (Chinese era format), 2024.03.15 (dot notation), and 2024-03-15 (dash notation). Use the Chinese character 年月日 format.

### Document Number Format (发文字号格式)

The correct format is 国发〔2024〕1号 using Chinese brackets. Common errors include 国发[2024]1号 with square brackets, 国发[2024]第1号 with the extra 第 character, and 国发（2024）1号 with parentheses instead of brackets. Use the Chinese bracket character 〔〕 without any additional characters.

## Workflow

```
Step 1: 确定公文类型
├── 分析发文目的
├── 确定行文关系
└── 选择公文文种

Step 2: 收集基本信息
├── 发文机关
├── 主送机关
├── 公文主题
└── 相关背景

Step 3: 撰写公文
├── 拟定标题
├── 撰写正文
├── 添加附件说明
└── 确定落款

Step 4: 格式检查
├── 层次序号
├── 字体字号
├── 页面设置
└── 整体排版

Step 5: 合规审核
├── 内容合法性
├── 格式规范性
├── 语言得体性
└── 程序完整性
```

## Rules

- [rules/document-types.md](rules/document-types.md) - Document types and usage
- [rules/formatting-rules.md](rules/formatting-rules.md) - GB/T 9704-2012 formatting rules
- [rules/writing-guidelines.md](rules/writing-guidelines.md) - Writing guidelines
- [rules/templates.md](rules/templates.md) - Document templates

## Writing Principles

Five principles guide official document writing. First, 准确 means content must be accurate and factual. Second, 简洁 means express ideas concisely. Third, 规范 means follow national standards strictly. Fourth, 得体 means use appropriate tone and language. Fifth, 完整 means include all necessary elements.

## Common Mistakes to Avoid

Six common mistakes compromise official document quality. Wrong hierarchy numbering format violates the standard numbering rules. Missing document number or date makes the document incomplete. Incorrect font or size fails to meet formatting specifications. Missing stamp or signature invalidates the document. Wrong tone for document type inappropriate for the specific公文种类. Incomplete document structure violates the required format.

## Reference Standards

- GB/T 9704-2012 党政机关公文格式
- 党政机关公文处理工作条例 (2012)
- 标点符号用法 (GB/T 15834-2011)