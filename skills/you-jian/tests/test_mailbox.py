#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_mailbox.py — mailbox.py 的离线自测（不联网，只测纯函数）
运行: python test_mailbox.py
"""
import importlib.util
import sys
from pathlib import Path

# 按路径加载 mailbox.py（避免与标准库 mailbox 模块冲突）
_SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "mailbox.py"
_spec = importlib.util.spec_from_file_location("ymail", _SCRIPT)
mb = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(mb)

PASS = 0
FAIL = 0


def check(name, got, want):
    global PASS, FAIL
    if got == want:
        PASS += 1
        print(f"  ✓ {name}")
    else:
        FAIL += 1
        print(f"  ✗ {name}\n    期望: {want!r}\n    实际: {got!r}")


def make_email(subject="测试邮件", from_addr="张三 <zhangsan@example.com>",
               body="你好，这是正文。", attach=None, charset="utf-8"):
    """构造一封合成邮件，返回 RFC822 字节。用 EmailMessage + formataddr 保证头格式正确。"""
    from email.header import Header
    from email.message import EmailMessage
    from email.utils import formataddr

    msg = EmailMessage()
    name, _, addr = from_addr.rpartition("<")
    if addr:
        msg["From"] = formataddr((name.strip(), addr.rstrip(">")))
    else:
        msg["From"] = from_addr
    msg["To"] = "lisi@example.com"
    msg["Subject"] = Header(subject, charset).encode()
    if charset != "utf-8":
        msg.set_content(body.encode(charset), maintype="text", subtype="plain")
        msg.replace_header("Content-Type", f"text/plain; charset={charset}")
    else:
        msg.set_content(body)
    if attach is not None:
        msg.add_attachment(attach, maintype="application", subtype="octet-stream",
                           filename="报告.pdf")
    return msg.as_bytes()


def test_imap_utf7():
    print("imap_utf7 编解码")
    pairs = ["INBOX", "已删除", "&123", "收件箱/工作", "a&b"]
    for s in pairs:
        check(f"roundtrip {s!r}", mb.imap_utf7_decode(mb.imap_utf7_encode(s)), s)
    enc = mb.imap_utf7_encode("收件箱")
    check("非 ASCII 编码含 &", "&" in enc, True)
    check("INBOX 保持 ASCII", mb.imap_utf7_encode("INBOX"), "INBOX")


def test_decode_header():
    print("decode_header_value")
    from email.header import Header
    raw = Header("测试主题", "utf-8").encode()
    check("utf-8 主题", mb.decode_header_value(raw), "测试主题")
    check("空头", mb.decode_header_value(""), "")


def test_parse_email():
    print("parse_email")
    m = mb.parse_email(make_email())
    check("主题解码", m["subject"], "测试邮件")
    check("发件人", m["from"][0]["email"], "zhangsan@example.com")
    check("正文", m["body"].strip(), "你好，这是正文。")
    check("附件数量", len(m["attachments"]), 0)

    m2 = mb.parse_email(make_email(attach=b"%PDF-1.4 fake"))
    check("带附件数量", len(m2["attachments"]), 1)
    check("附件名", m2["attachments"][0]["filename"], "报告.pdf")

    m3 = mb.parse_email(make_email(subject="会议通知", body="请于周五参会。", charset="gbk"))
    check("GBK 正文", m3["body"].strip(), "请于周五参会。")


def test_quoted_printable():
    print("quoted-printable 解码")
    import quopri
    from email.mime.text import MIMEText
    m = MIMEText("", "plain", "utf-8")
    m.set_payload(quopri.encodestring("quoted printable 测试".encode("utf-8")))
    m.replace_header("Content-Transfer-Encoding", "quoted-printable")
    parsed = mb.parse_email(m.as_bytes())
    check("QP 正文", parsed["body"].strip(), "quoted printable 测试")


def test_strip_html():
    print("strip_html")
    check("去标签", mb.strip_html("<p>你好<b>世界</b></p>"), "你好 世界")
    check("去 script", mb.strip_html("<script>x()</script>正文"), "正文")


def test_sanitize_filename():
    print("sanitize_filename")
    check("去路径", mb.sanitize_filename("../../etc/passwd"), "passwd")
    check("去控制符", mb.sanitize_filename("a\x00b.txt"), "ab.txt")
    check("空名兜底", mb.sanitize_filename("..."), "attachment.bin")


def test_importance():
    print("_guess_importance")
    frm = [{"email": "noreply@school.edu.cn", "name": ""}]
    check("截止", mb._guess_importance("项目结题截止周五", [], ""), "紧急/需处理")
    check("发票", mb._guess_importance("请提交发票", [], ""), "待办")
    check("验证码", mb._guess_importance("您的验证码是 1234", [], ""), "验证码/自动")
    check("营销", mb._guess_importance("双十一特惠", [], ""), "营销/可忽略")
    check("通知", mb._guess_importance("培训通知", frm, ""), "通知")
    check("普通", mb._guess_importance("你好", [], ""), "普通")


def test_config(tmp):
    print("config 读写")
    cfg = mb.load_config(tmp)
    cfg["accounts"]["work"] = {"email": "a@b.com"}
    p = mb.save_config(cfg, tmp)
    cfg2 = mb.load_config(tmp)
    check("保存后可读回", cfg2["accounts"]["work"]["email"], "a@b.com")
    mode = p.stat().st_mode & 0o777
    check("配置权限 600", mode, 0o600)
    check("环境变量名", mb.env_var_for("my-work"), "YOUJIAN_PASS_MY_WORK")


def test_vault(tmp):
    print("加密凭据库 vault（Fernet）")
    import os
    os.environ["YOUJIAN_MASTER_KEY"] = mb.Fernet.generate_key().decode()
    cfg_path = os.path.join(tmp, "accounts.json")

    # 加密写入 + 解密读回
    mb.save_vault({"work": {"email": "a@b.com", "password": "secret123"}}, cfg_path)
    v = mb.load_vault(cfg_path)
    check("vault 往返", v["work"]["password"], "secret123")

    # 密文不含明文，且不是 JSON
    enc = open(mb.vault_path(cfg_path), "rb").read()
    check("密文不含明文密码", b"secret123" not in enc, True)
    check("密文不含明文邮箱", b"a@b.com" not in enc, True)

    # vault_set / vault_get
    mb.vault_set_password("school", "t@x.edu.cn", "pwd456", cfg_path)
    check("vault_get 正确", mb.vault_get_password("school", "t@x.edu.cn", cfg_path), "pwd456")
    check("vault_get 邮箱不匹配", mb.vault_get_password("school", "other@x.edu.cn", cfg_path), None)

    # 权限 600
    mode = mb.vault_path(cfg_path).stat().st_mode & 0o777
    check("vault 权限 600", mode, 0o600)

    # get_password 优先级：环境变量 > vault
    mb.vault_set_password("w", "a@b.com", "vaultpw", cfg_path)
    acct = {"email": "a@b.com"}
    check("vault 提供密码", mb.get_password(acct, "w", cfg_path), "vaultpw")
    os.environ["YOUJIAN_PASS_W"] = "envpw"
    check("环境变量优先", mb.get_password(acct, "w", cfg_path), "envpw")
    del os.environ["YOUJIAN_PASS_W"]

    # 篡改检测（放到最后，会破坏 vault 文件）
    p = mb.vault_path(cfg_path)
    enc = p.read_bytes()
    p.write_bytes(b"tampered" + enc[8:])
    raised = False
    try:
        mb.load_vault(cfg_path)
    except SystemExit:
        raised = True
    check("篡改应拒绝解密", raised, True)


def main():
    import os
    import tempfile
    print("=" * 60)
    print("mailbox.py 离线自测")
    print("=" * 60)
    test_imap_utf7()
    test_decode_header()
    test_parse_email()
    test_quoted_printable()
    test_strip_html()
    test_sanitize_filename()
    test_importance()
    with tempfile.TemporaryDirectory() as td:
        test_config(os.path.join(td, "accounts.json"))
    with tempfile.TemporaryDirectory() as td:
        test_vault(td)
    print("=" * 60)
    print(f"通过 {PASS}，失败 {FAIL}")
    sys.exit(1 if FAIL else 0)


if __name__ == "__main__":
    main()
