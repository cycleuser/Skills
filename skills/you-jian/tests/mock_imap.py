#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
mock_imap.py — 极简 IMAP 服务器（SSL），仅用于 mailbox.py 的集成测试。
只实现 mailbox.py 实际会发送的命令子集：LOGIN / LIST / SELECT / UID SEARCH /
UID FETCH / UID STORE / UID MOVE / UID COPY / EXPUNGE / CLOSE / LOGOUT / NOOP / CAPABILITY。
"""
import importlib.util
import socket
import ssl
import threading
from pathlib import Path

from email.header import Header
from email.message import EmailMessage
from email.utils import formataddr

# 复用 mailbox.py 的 UTF-7 编码
_SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "mailbox.py"
_spec = importlib.util.spec_from_file_location("ymail", _SCRIPT)
_mb = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mb)
imap_utf7_encode = _mb.imap_utf7_encode


def build_email(subject, from_name, from_addr, body, to="me@example.com", attach=None):
    msg = EmailMessage()
    msg["From"] = formataddr((from_name, from_addr))
    msg["To"] = to
    msg["Subject"] = Header(subject, "utf-8").encode()
    msg["Date"] = "Mon, 25 Sep 2026 10:00:00 +0800"
    msg.set_content(body)
    if attach is not None:
        msg.add_attachment(attach["data"], maintype="application",
                           subtype="octet-stream", filename=attach["name"])
    return msg.as_bytes()


class MailboxState:
    """内存中的邮箱状态。"""

    def __init__(self):
        self.next_uid = 1
        # folder -> list of {"uid": int, "flags": set, "raw": bytes}
        self.folders = {"INBOX": [], "Trash": [], "已归档": []}
        self._add("INBOX", build_email(
            "项目结题截止通知", "张三", "zhangsan@example.com",
            "各位老师，项目结题材料请于本周五前提交。", attach={"name": "报告.pdf", "data": b"%PDF-1.4 fake"}))
        self._add("INBOX", build_email(
            "发票请查收", "李四", "lisi@example.com", "这是本月的发票，请查收并报销。"))
        self._add("INBOX", build_email(
            "培训通知", "教务处", "noreply@school.edu.cn", "本周三下午有教学培训，请准时参加。"))

    def _add(self, folder, raw):
        self.folders.setdefault(folder, []).append(
            {"uid": self.next_uid, "flags": set(), "raw": raw})
        self.next_uid += 1


class MockIMAP:
    def __init__(self, state):
        self.state = state
        self.selected = None
        self.tag = 0

    def handle_line(self, line):
        parts = line.split()
        if not parts:
            return []
        tag, cmd = parts[0], parts[1].upper()
        args = parts[2:]
        return self.dispatch(tag, cmd, args)

    def dispatch(self, tag, cmd, args):
        if cmd == "CAPABILITY":
            return [b"* CAPABILITY IMAP4rev1 UIDPLUS MOVE", f"{tag} OK done".encode()]
        if cmd == "NOOP":
            return [f"{tag} OK".encode()]
        if cmd == "LOGIN":
            return [f"{tag} OK LOGIN ok".encode()]
        if cmd == "LOGOUT":
            return [b"* BYE bye", f"{tag} OK".encode()]
        if cmd == "LIST":
            out = []
            for name in self.state.folders:
                enc = imap_utf7_encode(name)
                out.append(f'* LIST (\\HasNoChildren) "/" "{enc}"'.encode())
            out.append(f"{tag} OK LIST done".encode())
            return out
        if cmd in ("SELECT", "EXAMINE"):
            folder = self._unquote(args[0])
            folder = _mb.imap_utf7_decode(folder)
            self.selected = folder
            n = len(self.state.folders.get(folder, []))
            return [f"* {n} EXISTS".encode(),
                    b"* OK [UIDVALIDITY 1]",
                    f"{tag} OK [READ-WRITE] SELECT done".encode()]
        if cmd == "CLOSE":
            self.selected = None
            return [f"{tag} OK CLOSE done".encode()]
        if cmd == "UID":
            return self.dispatch_uid(tag, args)
        if cmd == "EXPUNGE":
            return [f"{tag} OK EXPUNGE done".encode()]
        if cmd == "STORE":
            return [f"{tag} OK STORE done".encode()]
        return [f"{tag} BAD unknown {cmd}".encode()]

    def dispatch_uid(self, tag, args):
        # args = [SUBCOMMAND, ...]
        sub = args[0].upper()
        if sub == "SEARCH":
            folder = self.selected or "INBOX"
            emails = self.state.folders.get(folder, [])
            # 简单处理 UNSEEN：未读 = 无 \Seen flag
            if any(a.upper() == "UNSEEN" for a in args):
                uids = [e["uid"] for e in emails if "\\Seen" not in e["flags"]]
            else:
                uids = [e["uid"] for e in emails]
            uids = [str(u) for u in uids]
            return [f"* SEARCH {' '.join(uids)}".encode(), f"{tag} OK SEARCH done".encode()]
        if sub == "FETCH":
            uid = int(args[1])
            folder = self.selected or "INBOX"
            emails = self.state.folders.get(folder, [])
            for e in emails:
                if e["uid"] == uid:
                    raw = e["raw"]
                    return self._fetch_response(tag, uid, raw)
            return [f"{tag} OK FETCH done".encode()]
        if sub == "STORE":
            uid = int(args[1])
            folder = self.selected or "INBOX"
            mode = args[2]  # +FLAGS / -FLAGS
            for e in self.state.folders.get(folder, []):
                if e["uid"] == uid:
                    flags = args[3].strip("()").split()
                    if mode == "+FLAGS":
                        e["flags"].update(flags)
                    else:
                        e["flags"].difference_update(flags)
                    f = " ".join(sorted(e["flags"])) or ""
                    return [f"* {uid} FETCH (FLAGS ({f}) UID {uid})".encode(),
                            f"{tag} OK STORE done".encode()]
            return [f"{tag} OK STORE done".encode()]
        if sub in ("MOVE", "COPY"):
            uid = int(args[1])
            target = _mb.imap_utf7_decode(self._unquote(args[2]))
            src_folder = self.selected or "INBOX"
            emails = self.state.folders.get(src_folder, [])
            for i, e in enumerate(emails):
                if e["uid"] == uid:
                    self.state.folders.setdefault(target, []).append(e)
                    if sub == "MOVE":
                        emails.pop(i)
                    return [f"{tag} OK {sub} done".encode()]
            return [f"{tag} OK {sub} done".encode()]
        return [f"{tag} BAD unknown uid {sub}".encode()]

    def _fetch_response(self, tag, uid, raw):
        # 返回完整 RFC822 作为字面量（对 header-fields 与 RFC822 请求都返回全量）
        n = len(raw)
        head = f"* {uid} FETCH (UID {uid} BODY[] {{{n}}}".encode()
        return [head + b"\r\n" + raw + b")\r\n", f"{tag} OK FETCH done".encode()]

    @staticmethod
    def _unquote(s):
        return s.strip('"')


def run_server(port, certfile, keyfile, ready_event):
    state = MailboxState()
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ctx.load_cert_chain(certfile, keyfile)
    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    listener.bind(("127.0.0.1", port))
    listener.listen(5)
    ready_event.set()

    def serve(conn):
        try:
            sconn = ctx.wrap_socket(conn, server_side=True)
            f = sconn.makefile("rb")
            mock = MockIMAP(state)
            sconn.sendall(b"* OK mock imap ready\r\n")
            buf = b""
            while True:
                buf += f.readline()
                if not buf:
                    break
                if not buf.endswith(b"\r\n"):
                    continue
                line = buf.decode("utf-8", errors="replace").strip()
                buf = b""
                if not line:
                    continue
                for resp in mock.handle_line(line):
                    if isinstance(resp, str):
                        resp = resp.encode()
                    sconn.sendall(resp + (b"\r\n" if not resp.endswith(b"\r\n") else b""))
                if line.upper().startswith(("X LOGOUT",)):
                    break
        except (ConnectionError, OSError, ssl.SSLError):
            pass
        finally:
            try:
                conn.close()
            except OSError:
                pass

    while True:
        conn, _ = listener.accept()
        threading.Thread(target=serve, args=(conn,), daemon=True).start()


if __name__ == "__main__":
    import sys
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 19993
    cert, key = sys.argv[2], sys.argv[3]
    run_server(port, cert, key, threading.Event())
    # 阻塞主线程
    threading.Event().wait()


# ---------------------------------------------------------------------------
# 极简 SMTP 服务器（SSL），仅用于 send 命令的集成测试
# ---------------------------------------------------------------------------
class MockSMTP:
    def __init__(self, received):
        self.received = received  # list[dict]
        self.cur = None

    def handle_line(self, line):
        u = line.upper()
        if u.startswith("EHLO") or u.startswith("HELO"):
            return ["250-mock", "250 AUTH PLAIN"]
        if u.startswith("AUTH"):
            # AUTH PLAIN <base64> 一次性带凭据，直接放行
            return ["235 2.7.0 ok"]
        if u.startswith("MAIL FROM"):
            self.cur = {"from": line.split(":", 1)[1].strip()}
            return ["250 ok"]
        if u.startswith("RCPT TO"):
            self.cur["to"] = line.split(":", 1)[1].strip()
            return ["250 ok"]
        if u == "DATA":
            self.cur["data"] = []
            return ["354 go ahead"]
        if u == "QUIT":
            return ["221 bye"]
        # DATA 阶段内容行
        if self.cur is not None and isinstance(self.cur.get("data"), list):
            if line == ".":
                self.cur["data"] = "\n".join(self.cur["data"])
                self.received.append(self.cur)
                self.cur = None
                return ["250 ok"]
            self.cur["data"].append(line)
            return []
        return ["250 ok"]


def run_smtp_server(port, certfile, keyfile, ready_event, received):
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ctx.load_cert_chain(certfile, keyfile)
    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    listener.bind(("127.0.0.1", port))
    listener.listen(5)
    ready_event.set()

    def serve(conn):
        try:
            sconn = ctx.wrap_socket(conn, server_side=True)
            f = sconn.makefile("rb")
            mock = MockSMTP(received)
            sconn.sendall(b"220 mock smtp ready\r\n")
            while True:
                line = f.readline()
                if not line:
                    break
                line = line.decode("utf-8", errors="replace").rstrip("\r\n")
                if not line:
                    continue
                for resp in mock.handle_line(line):
                    sconn.sendall(resp.encode() + b"\r\n")
                if line.upper() == "QUIT":
                    break
        except (ConnectionError, OSError, ssl.SSLError):
            pass
        finally:
            try:
                conn.close()
            except OSError:
                pass

    while True:
        conn, _ = listener.accept()
        threading.Thread(target=serve, args=(conn,), daemon=True).start()
