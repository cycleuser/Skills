---
name: official-document-writer
version: "1.0.0"
description: |
  Official document writing assistant for Chinese government documents. Based on GB/T 9704-2012 standard.

  **Triggers when:**
  - Writing Chinese official documents (公文)
  - Formatting documents according to national standards
  - Reviewing document compliance
  - Creating notices, reports, requests, replies, letters, or minutes

  **Commands:**
  - `/gongwen notice <topic>` - Write a notice (通知)
  - `/gongwen report <topic>` - Write a report (报告)
  - `/gongwen request <topic>` - Write a request (请示)
  - `/gongwen reply <topic>` - Write a reply (批复)
  - `/gongwen letter <topic>` - Write a letter (函)
  - `/gongwen minutes <topic>` - Write meeting minutes (纪要)
  - `/gongwen check <document>` - Check document compliance
  - `/gongwen format` - Show formatting rules

  **Capabilities:**
  - 15 document types support
  - GB/T 9704-2012 compliance
  - Hierarchy numbering rules
  - Font and layout specifications
  - Document structure templates
author: cycleuser
license: MIT
---

# Official Document Writer

Chinese official document writing assistant based on GB/T 9704-2012 national standard.

## Quick Commands

| Command | Document Type |
|---------|---------------|
| `/gongwen notice <topic>` | 通知 |
| `/gongwen report <topic>` | 报告 |
| `/gongwen request <topic>` | 请示 |
| `/gongwen reply <topic>` | 批复 |
| `/gongwen letter <topic>` | 函 |
| `/gongwen minutes <topic>` | 纪要 |
| `/gongwen check <document>` | 合规检查 |
| `/gongwen format` | 格式规范 |

## Document Types (公文种类)

According to "Regulations on the Handling of Official Documents of Party and Government Organs" (党政机关公文处理工作条例):

| Type | Chinese | Purpose |
|------|---------|---------|
| Decision | 决定 | 重要事项部署、奖惩 |
| Order | 命令（令） | 公布法规、任免、嘉奖 |
| Public Notice | 公告 | 向国内外宣布重要事项 |
| Announcement | 通告 | 公布社会各界周知事项 |
| Notice | 通知 | 批转、转发、部署、任免 |
| Circular | 通报 | 表彰先进、批评错误 |
| Proposal | 议案 | 提请审议事项 |
| Report | 报告 | 汇报工作、回复询问 |
| Request | 请示 | 请求指示、批准 |
| Reply | 批复 | 答复请示事项 |
| Opinion | 意见 | 提出见解和办法 |
| Letter | 函 | 商洽工作、询问答复 |
| Minutes | 纪要 | 记载会议主要情况 |

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

According to GB/T 9704-2012:

```
第一层：一、二、三、……（中文数字+顿号）
第二层：（一）（二）（三）……（全角括号+中文数字）
第三层：1. 2. 3. ……（阿拉伯数字+英文句点）
第四层：（1）（2）（3）……（全角括号+阿拉伯数字）
```

**Note:** Do NOT use Roman numerals (I, II, III) or other formats.

### Font Specifications (字体规格)

| Element | Font | Size |
|---------|------|------|
| 发文机关标志 | 小标宋体 | 红色 |
| 标题 | 小标宋体 | 2号 |
| 主送机关 | 仿宋 | 3号 |
| 正文第一层 | 黑体 | 3号 |
| 正文第二层 | 楷体 | 3号 |
| 正文第三、四层 | 仿宋 | 3号 |
| 发文字号 | 仿宋 | 3号 |
| 页码 | 宋体 | 4号 |

### Page Layout (页面设置)

- **Paper size:** A4 (210mm × 297mm)
- **Margins:** Top 37mm, Bottom 35mm, Left 28mm, Right 26mm
- **Line spacing:** Fixed 28 pounds (约0.99cm)
- **Page number format:** — 1 — (一字线+页码+一字线)
- **Page number position:** Bottom center, odd right, even left

### Date Format (日期格式)

```
正确格式：2024年3月15日
错误格式：二〇二四年三月十五日
错误格式：2024.03.15
错误格式：2024-03-15
```

### Document Number Format (发文字号格式)

```
正确格式：国发〔2024〕1号
错误格式：国发[2024]1号
错误格式：国发[2024]第1号
错误格式：国发（2024）1号
```

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

1. **准确** - Content must be accurate and factual
2. **简洁** - Express ideas concisely
3. **规范** - Follow national standards strictly
4. **得体** - Use appropriate tone and language
5. **完整** - Include all necessary elements

## Common Mistakes to Avoid

- ❌ Wrong hierarchy numbering format
- ❌ Missing document number or date
- ❌ Incorrect font or size
- ❌ Missing stamp or signature
- ❌ Wrong tone for document type
- ❌ Incomplete document structure

## Reference Standards

- GB/T 9704-2012 党政机关公文格式
- 党政机关公文处理工作条例 (2012)
- 标点符号用法 (GB/T 15834-2011)