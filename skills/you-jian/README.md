# 邮箱知识库 (Mail Knowledge Base / you-jian)

## 状态：Beta

## 用途

收取、阅读、检索邮件，并把邮件构建成可全文检索的本地知识库。三件事：**收与读 → 建库 → 检索**。

- 多账号 IMAP 收信（Gmail / Outlook / QQ / 163 / 126 / 新浪 / iCloud / 139 / Zoho 及自建服务器）
- 读全文、下载附件、中文关键词检索
- 把邮件批量导出为 **Markdown + index.json** 的本地知识库（可被 `rg`/`grep` 检索，可被 RAG 切片入库）
- 每日摘要（紧急/待办/验证码/通知/营销/普通 分类 + 高频发件人）

## 快速上手

```bash
python scripts/mailbox.py fetch work --unread              # 收取未读
python scripts/mailbox.py read work 42                     # 读全文
python scripts/mailbox.py search work 发票                 # 关键词检索（中文）
python scripts/mailbox.py kb work --dir ~/MailKB           # 构建知识库
python scripts/mailbox.py digest work --days 7             # 每日摘要
python scripts/mailbox.py attach work 42 --dir ~/Downloads # 下载附件
```

## 命令一览

| 命令 | 说明 |
|------|------|
| `fetch <账号\|all> [--unread] [--limit] [--from] [--since]` | 收取邮件列表 |
| `read <账号> <uid>` | 读全文 + 附件清单 |
| `search <账号\|all> <关键词>` | 检索邮件 |
| `kb <账号\|all> [--dir] [--limit] [--unread]` | 构建邮件知识库 |
| `digest <账号\|all> [--days N]` | 每日摘要 |
| `attach <账号> <uid> [--dir]` | 下载附件 |
| `stats <账号\|all>` / `folders <账号>` | 统计 / 列文件夹 |
| `send <账号> --to x --subject x --body x [--attach f]` | 发送 |

账号名传 `all` 即遍历全部已配置邮箱。

## 知识库产物

`kb` 命令导出到 `<dir>/<账号>/`：

```
<账号>/
├── index.json                        # 索引
└── <uid>_<日期>_<主题>.md            # 每封一个 Markdown（front-matter + 正文 + 附件列表）
```

## 凭据与收发

邮件收发与授权码由独立的命令行程序负责（用户自建）。本脚本支持环境变量
`YOUJIAN_PASS_<账号名>` 提供凭据，避免在代码/日志里写明文密码。

## 测试

```bash
python tests/test_mailbox.py        # 离线单测（40 项）
python tests/test_integration.py    # 端到端集成测试（36 项，本地 mock IMAP+SMTP）
```

## 参见

- [docx-to-knowledge](../docx-to-knowledge) — 文档转可检索知识库（同类的"建库+检索"思路）
- [verify-deliver](../verify-deliver) — 交付前校验协议

## 文件结构

```
skills/you-jian/
├── README.md              # 本文件
├── SKILL.md               # 技能定义
├── rules/
│   └── digest.md          # 摘要分类规则
├── scripts/
│   └── mailbox.py         # 多邮箱客户端（收/读/搜/建库/发）
└── tests/
    ├── test_mailbox.py    # 离线单测
    ├── mock_imap.py       # 极简 IMAP+SMTP 服务器
    └── test_integration.py# 端到端集成测试
```
