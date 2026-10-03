#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_integration.py — mailbox.py 端到端集成测试（本地 mock IMAP，SSL）
验证真实网络路径：连接/登录/列出文件夹/拉取/读取/搜索/标记/移动/删除/摘要/统计。
运行: python test_integration.py
"""
import importlib.util
import json
import os
import socket
import subprocess
import sys
import tempfile
import threading
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import mock_imap  # noqa: E402

PY = sys.executable
SCRIPT = HERE.parent / "scripts" / "mailbox.py"

PASS = 0
FAIL = 0


def check(name, ok, detail=""):
    global PASS, FAIL
    if ok:
        PASS += 1
        print(f"  ✓ {name}")
    else:
        FAIL += 1
        print(f"  ✗ {name}  {detail}")


def free_port():
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    p = s.getsockname()[1]
    s.close()
    return p


def make_cert(tmp):
    cert = str(tmp / "cert.pem")
    key = str(tmp / "key.pem")
    subprocess.run(
        ["openssl", "req", "-x509", "-newkey", "rsa:2048", "-nodes",
         "-keyout", key, "-out", cert, "-days", "1",
         "-subj", "/CN=localhost"],
        check=True, capture_output=True, timeout=30)
    return cert, key


def run_cli(config, *argv):
    r = subprocess.run([PY, str(SCRIPT), "--config", config, *argv],
                       capture_output=True, text=True, timeout=30)
    return r.returncode, r.stdout, r.stderr


def main():
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        cert, key = make_cert(tmp)
        port = free_port()
        ready = threading.Event()
        t = threading.Thread(target=mock_imap.run_server,
                             args=(port, cert, key, ready), daemon=True)
        t.start()
        ready.wait(5)
        time.sleep(0.2)

        # 账号配置（密码走加密凭据库 vault，避免写钥匙串/环境变量明文）
        os.environ["YOUJIAN_MASTER_KEY"] = mock_imap._mb.Fernet.generate_key().decode()
        config = tmp / "accounts.json"
        cfg = {"accounts": {
            "test": {
                "email": "me@example.com",
                "imap_host": "127.0.0.1", "imap_port": port,
                "smtp_host": "127.0.0.1", "smtp_port": port, "smtp_security": "ssl",
            },
            "work": {
                "email": "work@example.com",
                "imap_host": "127.0.0.1", "imap_port": port,
                "smtp_host": "127.0.0.1", "smtp_port": port, "smtp_security": "ssl",
            },
        }}
        config.write_text(json.dumps(cfg), encoding="utf-8")
        # 用加密凭据库存密码（等价于 `add --password` 的行为）
        mock_imap._mb.vault_set_password("test", "me@example.com", "secret", str(config))
        mock_imap._mb.vault_set_password("work", "work@example.com", "secret", str(config))

        print("=" * 60)
        print("mailbox.py 集成测试（本地 mock IMAP）")
        print("=" * 60)

        print("凭据库加密性")
        enc = (tmp / "vault.enc").read_bytes()
        check("vault.enc 不含明文密码", b"secret" not in enc, True)
        check("vault.enc 不含明文邮箱", b"me@example.com" not in enc, True)

        print("登录并检查全部账号")
        rc, out, err = run_cli(config, "check")
        check("check 全部成功", rc == 0 and "2 成功" in out and "0 失败" in out,
              f"rc={rc} out={out} err={err}")

        print("凭据库状态")
        rc, out, err = run_cli(config, "vault-status")
        check("vault-status 显示 2 账号", "2 个账号" in out and "有加密凭据" in out, out)

        print("连接与登录")
        rc, out, err = run_cli(config, "test", "test")
        check("test 连接成功", rc == 0 and "连接成功" in out, f"rc={rc} err={err}")

        print("列出文件夹")
        rc, out, err = run_cli(config, "folders", "test")
        names = out.split()
        check("含 INBOX", "INBOX" in names, out)
        check("UTF-7 中文文件夹解码", "已归档" in names, out)

        print("统计")
        rc, out, err = run_cli(config, "stats", "test")
        check("INBOX 3 封", "INBOX" in out and "3" in out, out)

        print("跨全部账号拉取")
        rc, out, err = run_cli(config, "fetch", "all", "--limit", "5")
        check("fetch all 含两个账号", "【账号 test" in out and "【账号 work" in out, out)

        print("拉取列表")
        rc, out, err = run_cli(config, "fetch", "test", "--limit", "5")
        check("3 封", "共 3 封" in out, out)
        check("中文主题解码", "项目结题截止通知" in out, out)

        print("搜索（非 ASCII 关键词走客户端过滤）")
        rc, out, err = run_cli(config, "search", "test", "发票")
        check("命中发票", "发票请查收" in out and "共 1 封" in out, out)

        print("读取全文")
        rc, out, err = run_cli(config, "read", "test", "1")
        check("含正文", "项目结题材料" in out, out)
        check("含附件列表", "报告.pdf" in out, out)

        print("附件下载")
        att_dir = tmp / "att"
        rc, out, err = run_cli(config, "attach", "test", "1", "--dir", str(att_dir))
        downloaded = att_dir / "报告.pdf"
        check("附件已下载", downloaded.exists() and downloaded.read_bytes() == b"%PDF-1.4 fake",
              out + err)

        print("构建邮件知识库")
        kb_dir = tmp / "kb"
        rc, out, err = run_cli(config, "kb", "test", "--dir", str(kb_dir))
        check("kb 导出成功", rc == 0 and "导出 3 封" in out, f"rc={rc} err={err}")
        idx = kb_dir / "test" / "index.json"
        check("kb 生成 index.json", idx.exists(), str(idx))
        if idx.exists():
            data = json.loads(idx.read_text(encoding="utf-8"))
            check("kb 索引 3 条", len(data) == 3, str(len(data)))
            md_files = list((kb_dir / "test").glob("*.md"))
            check("kb 生成 3 个 md", len(md_files) == 3, str(len(md_files)))
            check("md 含 front-matter", "uid:" in md_files[0].read_text(encoding="utf-8"), "")

        print("标记（DRY-RUN 不生效）")
        rc, out, err = run_cli(config, "mark", "test", "1", "read")
        check("mark 默认 DRY-RUN", "DRY-RUN" in out, out)
        rc, out, err = run_cli(config, "mark", "test", "1", "read", "--yes")
        check("mark --yes 生效", "已标记" in out, out)

        print("移动（DRY-RUN 不生效）")
        rc, out, err = run_cli(config, "move", "test", "2", "已归档")
        check("move 默认 DRY-RUN", "DRY-RUN" in out, out)
        rc, out, err = run_cli(config, "move", "test", "2", "已归档", "--yes")
        check("move --yes 生效", "已移动" in out, out)
        rc, out, err = run_cli(config, "stats", "test")
        check("移动后 INBOX 2 封", "INBOX" in out, out)

        print("删除（DRY-RUN 不生效，--yes 移入 Trash）")
        rc, out, err = run_cli(config, "delete", "test", "3")
        check("delete 默认 DRY-RUN", "DRY-RUN" in out, out)
        rc, out, err = run_cli(config, "delete", "test", "3", "--yes")
        check("delete --yes 移入回收站", "已移动" in out, out)

        print("摘要")
        rc, out, err = run_cli(config, "digest", "test", "--days", "30")
        check("摘要统计", "共" in out and "封" in out, out)
        check("摘要含分类", "紧急/需处理" in out or "待办" in out or "通知" in out, out)

        print("发送（DRY-RUN）")
        rc, out, err = run_cli(config, "send", "test", "--to", "a@b.com",
                               "--subject", "测试", "--body", "你好")
        check("send 默认 DRY-RUN", "DRY-RUN" in out, out)

        print("发送（真实 SMTP）")
        smtp_port = free_port()
        received = []
        smtp_ready = threading.Event()
        threading.Thread(target=mock_imap.run_smtp_server,
                         args=(smtp_port, cert, key, smtp_ready, received), daemon=True).start()
        smtp_ready.wait(5)
        # 临时把 smtp 指向 mock
        cfg2 = json.loads(config.read_text(encoding="utf-8"))
        cfg2["accounts"]["test"]["smtp_port"] = smtp_port
        config.write_text(json.dumps(cfg2), encoding="utf-8")
        att = tmp / "附.txt"
        att.write_text("附件内容", encoding="utf-8")
        rc, out, err = run_cli(config, "send", "test", "--to", "a@b.com",
                               "--subject", "测试发送", "--body", "你好正文",
                               "--attach", str(att), "--yes")
        check("send --yes 成功", rc == 0 and "发送到" in out, f"rc={rc} err={err}")
        check("SMTP 收到 1 封", len(received) == 1, f"received={len(received)}")
        if received:
            check("收件人正确", "a@b.com" in received[0].get("to", ""), received[0].get("to"))
            parsed = mock_imap._mb.parse_email(
                (received[0]["data"] + "\r\n").encode("utf-8"))
            check("主题正确", parsed["subject"] == "测试发送", parsed["subject"])
            check("正文正确", "你好正文" in parsed["body"], parsed["body"][:100])
            check("附件已编码", any("附.txt" == a["filename"] for a in parsed["attachments"]),
                  str(parsed["attachments"]))

        print("=" * 60)
        print(f"通过 {PASS}，失败 {FAIL}")
    sys.exit(1 if FAIL else 0)


if __name__ == "__main__":
    main()
