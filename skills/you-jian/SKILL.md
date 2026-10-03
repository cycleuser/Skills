---
name: you-jian
version: "1.1.0"
description: |
  邮箱知识库（Mail Knowledge Base）：收取、阅读、检索邮件，并把邮件构建成可全文检索的本地知识库。
  支持多账号 IMAP 收信、读全文、下载附件、关键词检索、每日摘要分类。

  Triggers when: 需要收取/阅读/搜索邮件、把邮件归档成可检索知识库、按发件人/主题/日期归纳邮件、
  生成"今天要处理哪些邮件"的摘要、下载邮件附件归档。

  Commands:
  - /邮箱 fetch <账号|all> [--unread] [--limit N] - 收取邮件列表
  - /邮箱 read <账号> <uid> - 读某封邮件全文
  - /邮箱 search <账号|all> <关键词> - 按关键词检索邮件
  - /邮箱 kb <账号|all> [--dir 目录] - 把邮件构建成本地知识库
  - /邮箱 digest <账号|all> [--days N] - 每日摘要（分类+待办）
  - /邮箱 attach <账号> <uid> [--dir 目录] - 下载附件
  - /邮箱 send <账号> --to x --subject x --body x [--attach f] - 发送
  - /mail <subcommand> - English alias

  Capabilities: 多账号 IMAP 收信、中文乱码解码（gbk/gb18030/big5）、全文检索、
  邮件→Markdown+JSON 知识库、每日摘要分类
author: cycleuser
license: MIT
status: Beta
---

## Safety Rules

参见 [_shared/core/safety-rules.md](../_shared/core/safety-rules.md)

# 邮箱知识库 (Mail Knowledge Base)

把邮箱里的邮件变成可检索、可归档的本地知识库。三件事：**收与读 → 建库 → 检索**。
核心是 `scripts/mailbox.py`，agent 直接调用完成所有操作。

## 核心工作流

```
Step 1 收与读
   /邮箱 fetch all --unread            # 所有账号的未读列表（含 UID）
   /邮箱 fetch work --unread           # 单账号未读
   /邮箱 read work 42                  # 读第 42 封全文 + 附件清单

Step 2 建知识库
   /邮箱 kb work --dir ~/MailKB        # 把 work 邮箱邮件导出为 Markdown + index.json
   /邮箱 kb all --dir ~/MailKB --unread # 所有账号的未读邮件建库

Step 3 检索
   /邮箱 search all 发票               # 在所有邮箱按关键词检索（中文走客户端过滤）
   rg -l "关键词" ~/MailKB             # 在已建知识库里全文检索（Markdown 可被 rg/grep 检索）
   /邮箱 digest all --days 7           # 每日摘要：分类 + 高频发件人 + 待办

Step 4 附件与发送
   /邮箱 attach work 42 --dir ~/Downloads/发票
   /邮箱 send work --to a@b.com --subject 会议纪要 --body-file 纪要.txt --attach 纪要.pdf
```

## 知识库产物（/邮箱 kb）

对指定账号拉取邮件，导出到 `<dir>/<账号>/`：

```
<账号>/
├── index.json                        # 索引：uid/发件人/主题/日期/正文/附件清单
└── <uid>_<日期>_<主题>.md            # 每封一个 Markdown（front-matter + 正文 + 附件列表）
```

Markdown 带 YAML front-matter（uid/from/date/subject/attachments），可被 `rg`/`grep` 全文检索，
也可被 RAG 直接切片入库。

## Quick Commands

| 命令 | 说明 | 是否写操作 |
|------|------|-----------|
| `/邮箱 fetch <账号\|all> [--unread] [--limit] [--from] [--since]` | 收取邮件列表 | 只读 |
| `/邮箱 read <账号> <uid>` | 读全文 + 附件清单 | 只读 |
| `/邮箱 search <账号\|all> <关键词> [--folder] [--limit]` | 检索邮件 | 只读 |
| `/邮箱 kb <账号\|all> [--dir] [--folder] [--limit] [--unread]` | 构建邮件知识库 | 只读 |
| `/邮箱 digest <账号\|all> [--days N] [--folder]` | 每日摘要 | 只读 |
| `/邮箱 attach <账号> <uid> [--dir]` | 下载附件 | 只读 |
| `/邮箱 stats <账号\|all>` / `/邮箱 folders <账号>` | 统计 / 列文件夹 | 只读 |
| `/邮箱 send <账号> --to x [--cc] [--subject] [--body\|--body-file] [--attach]` | 发送 | 写（默认 DRY-RUN，需 --yes） |
| `/邮箱 mark/move/delete <账号> <uid> …` | 标记/移动/删除 | 写（默认 DRY-RUN，需 --yes） |

English 别名：`/mail fetch|read|search|kb|digest|attach|send|stats|folders|mark|move|delete`。

## 约定

- **读操作只读**：fetch / read / search / kb / digest / attach / stats / folders 不改变服务器状态。
- **写操作先 DRY-RUN**：send / mark / move / delete 默认打印将要执行的动作，加 `--yes` 才真正执行。
- **账号名传 `all`** 即遍历全部已配置邮箱，统一收/搜/建库/摘要。
- **邮件收发与授权**由独立的命令行程序负责（用户自建 CLI）；本技能只约定读写、建库、检索的用法，
  脚本支持环境变量 `YOUJIAN_PASS_<账号名>` 提供凭据，避免在技能/日志中泄露密码。

## 中文支持

- MIME 头部 RFC 2047 解码、正文 gbk/gb18030/big5 回退、HTML→纯文本。
- IMAP modified UTF-7 中文文件夹名；非 ASCII 关键词走客户端过滤搜索。
- 邮件主题/发件人里的中文正确解码为可检索文本。

## Anti-Patterns

| 违规 | 严重度 | 后果 |
|------|--------|------|
| 把授权码写进代码/日志/git | 高 | 密码泄露 |
| send/mark/move/delete 不加 --yes 直接假设已执行 | 高 | 误操作真实邮件 |
| 中文关键词硬塞进服务器端 SEARCH | 中 | 搜不到（应客户端过滤） |
| 读全文/附件前不 SELECT 文件夹 | 高 | IMAP 报 illegal in state AUTH |
| 用序号而非 UID 操作 | 中 | 并发/删除后错位 |

## 依赖

- Python ≥ 3.8，核心收发只用标准库（imaplib/smtplib/email）。
- 加密凭据库（可选）需 `cryptography`；不用它也可走环境变量提供凭据。

## 文件结构

```
skills/you-jian/
├── README.md              # 面向人的中文说明
├── SKILL.md               # 本文件
├── rules/
│   └── digest.md          # 摘要分类规则
├── scripts/
│   └── mailbox.py         # 多邮箱客户端（收/读/搜/建库/发）
└── tests/
    ├── test_mailbox.py    # 离线单测
    ├── mock_imap.py       # 极简 IMAP+SMTP 服务器（测试用）
    └── test_integration.py# 端到端集成测试
```

## 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| 1.1.0 | 2026-09 | 新增 kb 知识库构建；SKILL 聚焦读写/建库/检索 |
| 1.0.0 | 2026-09 | 初始版本：多账号 IMAP/SMTP、中文解码、摘要分类 |
