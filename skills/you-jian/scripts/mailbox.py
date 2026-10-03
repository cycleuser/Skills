#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
mailbox.py — 多邮箱 IMAP/SMTP 客户端（纯 Python 标准库，零第三方依赖）

支持任意邮箱服务商（Gmail / Outlook / QQ / 163 / 126 / 新浪 / iCloud / 139 / Zoho …），
只要对方开放 IMAP 收信 + SMTP 发信。密码优先从 macOS 钥匙串或环境变量读取，
不要求把授权码明文写进配置文件。

用法（详见 --help）:
  python mailbox.py providers
  python mailbox.py add <账号名> <邮箱地址> [--provider 预设]
  python mailbox.py list / remove <账号名> / folders <账号名> / stats <账号名>
  python mailbox.py fetch <账号名> [--folder INBOX] [--limit N] [--unread] [--from x] [--since 日期]
  python mailbox.py read <账号名> <uid>
  python mailbox.py search <账号名> <关键词> [--folder INBOX] [--limit N]
  python mailbox.py attach <账号名> <uid> [--dir 目录]
  python mailbox.py mark <账号名> <uid> <read|unread|flag|unflag>
  python mailbox.py move <账号名> <uid> <目标文件夹> [--yes]
  python mailbox.py delete <账号名> <uid> [--yes]
  python mailbox.py send <账号名> --to x [--cc x] [--subject x] [--body x | --body-file f] [--attach f...]
  python mailbox.py digest <账号名> [--days N] [--limit N]
  python mailbox.py test <账号名>

安全约定:
  - 所有读操作（fetch/read/search/digest/stats/folders/attach/check）默认只读，不改变服务器状态。
  - move / delete / mark 会改变服务器状态，默认 DRY-RUN 打印将要执行的动作，必须加 --yes 才真正执行。
  - 授权码加密存储：Fernet（AES-128-CBC + HMAC-SHA256 认证加密）写入凭据库 vault.enc，
    主密钥来自环境变量 YOUJIAN_MASTER_KEY 或 macOS 钥匙串(you-jian-master) 或 master.key 文件。
    授权码永不落明文、永不进日志。
  - 账号名可传 `all` 以对所有已配置邮箱统一操作（fetch/search/digest/stats/check）。
"""
import argparse
import base64
import getpass
import imaplib
import json
import os
import re
import smtplib
import subprocess
import sys
import unicodedata
from datetime import datetime, timedelta, timezone
from email import policy
from email.header import decode_header
from email.message import EmailMessage
from email.utils import getaddresses, parsedate_to_datetime, formataddr
from pathlib import Path

try:
    from cryptography.fernet import Fernet, InvalidToken
    HAVE_CRYPTO = True
except ImportError:  # pragma: no cover - 无 cryptography 时降级到钥匙串/环境变量
    Fernet = None
    InvalidToken = Exception
    HAVE_CRYPTO = False

VERSION = "1.1.0"

# ---------------------------------------------------------------------------
# 内置服务商预设（IMAP 收信 / SMTP 发信）。授权码/应用专用密码获取方式见 README。
# ---------------------------------------------------------------------------
PROVIDERS = {
    "gmail": {
        "imap_host": "imap.gmail.com", "imap_port": 993,
        "smtp_host": "smtp.gmail.com", "smtp_port": 465, "smtp_security": "ssl",
        "note": "需在 Google 账号开启两步验证后生成「应用专用密码」",
    },
    "outlook": {
        "imap_host": "outlook.office365.com", "imap_port": 993,
        "smtp_host": "smtp.office365.com", "smtp_port": 587, "smtp_security": "starttls",
        "note": "Microsoft 365 / outlook.com，需应用密码或 OAuth",
    },
    "qq": {
        "imap_host": "imap.qq.com", "imap_port": 993,
        "smtp_host": "smtp.qq.com", "smtp_port": 465, "smtp_security": "ssl",
        "note": "QQ 邮箱设置→账户→开启 IMAP/SMTP，使用「授权码」而非登录密码",
    },
    "163": {
        "imap_host": "imap.163.com", "imap_port": 993,
        "smtp_host": "smtp.163.com", "smtp_port": 465, "smtp_security": "ssl",
        "note": "网易邮箱开启 IMAP/SMTP 后使用「客户端授权密码」",
    },
    "126": {
        "imap_host": "imap.126.com", "imap_port": 993,
        "smtp_host": "smtp.126.com", "smtp_port": 465, "smtp_security": "ssl",
        "note": "同 163，使用客户端授权密码",
    },
    "sina": {
        "imap_host": "imap.sina.com", "imap_port": 993,
        "smtp_host": "smtp.sina.com", "smtp_port": 465, "smtp_security": "ssl",
        "note": "新浪邮箱需开启客户端授权",
    },
    "icloud": {
        "imap_host": "imap.mail.me.com", "imap_port": 993,
        "smtp_host": "smtp.mail.me.com", "smtp_port": 587, "smtp_security": "starttls",
        "note": "iCloud 需在 Apple ID 生成「App 专用密码」",
    },
    "139": {
        "imap_host": "imap.139.com", "imap_port": 993,
        "smtp_host": "smtp.139.com", "smtp_port": 465, "smtp_security": "ssl",
        "note": "移动 139 邮箱，使用授权码",
    },
    "zoho": {
        "imap_host": "imap.zoho.com", "imap_port": 993,
        "smtp_host": "smtp.zoho.com", "smtp_port": 587, "smtp_security": "starttls",
        "note": "Zoho 需生成应用专用密码",
    },
}


# ---------------------------------------------------------------------------
# 配置读写
# ---------------------------------------------------------------------------
def default_config_path():
    env = os.environ.get("YOUJIAN_CONFIG")
    if env:
        return Path(env).expanduser()
    return Path.home() / ".config" / "you-jian" / "accounts.json"


def load_config(path=None):
    p = Path(path) if path else default_config_path()
    if not p.exists():
        return {"accounts": {}}
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        die(f"配置文件 {p} 解析失败：{e}")
    data.setdefault("accounts", {})
    return data


def save_config(cfg, path=None):
    p = Path(path) if path else default_config_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(cfg, ensure_ascii=False, indent=2), encoding="utf-8")
    try:
        os.chmod(p, 0o600)  # 权限收紧：仅本人可读写
    except OSError:
        pass
    return p


def env_var_for(account):
    safe = re.sub(r"[^A-Za-z0-9]", "_", account).upper()
    return f"YOUJIAN_PASS_{safe}"


def config_dir(path=None):
    p = Path(path) if path else default_config_path()
    return p.parent


def vault_path(path=None):
    return config_dir(path) / "vault.enc"


def master_key_path(path=None):
    return config_dir(path) / "master.key"


def _keychain_get(service, account):
    if sys.platform != "darwin":
        return None
    try:
        out = subprocess.run(
            ["security", "find-generic-password", "-s", service, "-a", account, "-w"],
            capture_output=True, text=True, timeout=10,
        )
        if out.returncode == 0 and out.stdout.strip():
            return out.stdout.strip()
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    return None


def _keychain_set(service, account, value):
    if sys.platform != "darwin":
        return False
    try:
        subprocess.run(
            ["security", "add-generic-password", "-s", service, "-a", account,
             "-w", value, "-U"],
            check=True, capture_output=True, timeout=15,
        )
        return True
    except (FileNotFoundError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return False


def get_master_key(path=None):
    """主密钥解析顺序：环境变量 YOUJIAN_MASTER_KEY → macOS 钥匙串(you-jian-master) → master.key 文件。"""
    env = os.environ.get("YOUJIAN_MASTER_KEY")
    if env and env.strip():
        return env.strip()
    k = _keychain_get("you-jian-master", "master")
    if k:
        return k
    p = master_key_path(path)
    if p.exists():
        k = p.read_text(encoding="utf-8").strip()
        if k:
            return k
    return None


def init_master_key(path=None, force=False):
    """生成 Fernet 主密钥并存入钥匙串（或 master.key 文件，0600）。"""
    if not HAVE_CRYPTO:
        die("需要 cryptography 库来加密凭据。请安装：pip install cryptography")
    existing = get_master_key(path)
    if existing and not force:
        return existing
    key = Fernet.generate_key().decode()  # urlsafe base64，44 字符
    if _keychain_set("you-jian-master", "master", key):
        print("✓ 主密钥已生成并存入 macOS 钥匙串（service=you-jian-master, account=master）。")
    else:
        p = master_key_path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(key, encoding="utf-8")
        try:
            os.chmod(p, 0o600)
        except OSError:
            pass
        print(f"✓ 主密钥已生成并写入 {p}（权限 600）。请妥善保管此文件。")
    return key


def _fernet(path=None):
    key = get_master_key(path)
    if not key:
        return None
    try:
        return Fernet(key.encode() if isinstance(key, str) else key)
    except Exception:
        return None


def load_vault(path=None):
    """解密凭据库 vault.enc，返回 {账号名: {email, password}}。"""
    p = vault_path(path)
    if not p.exists():
        return {}
    f = _fernet(path)
    if f is None:
        die(f"无法解密凭据库 {p}：缺少主密钥。请运行 vault-init，"
            f"或设置环境变量 YOUJIAN_MASTER_KEY。")
    try:
        data = f.decrypt(p.read_bytes())
        return json.loads(data.decode("utf-8"))
    except InvalidToken:
        die(f"凭据库 {p} 解密失败：主密钥错误或文件被篡改。")
    except (ValueError, json.JSONDecodeError) as e:
        die(f"凭据库 {p} 内容损坏：{e}")


def save_vault(vault, path=None):
    """加密写回凭据库（若尚无主密钥则先生成）。"""
    if get_master_key(path) is None:
        init_master_key(path)
    f = _fernet(path)
    p = vault_path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(f.encrypt(json.dumps(vault, ensure_ascii=False).encode("utf-8")))
    try:
        os.chmod(p, 0o600)
    except OSError:
        pass
    return p


def vault_get_password(account, email, path=None):
    entry = load_vault(path).get(account)
    if isinstance(entry, dict) and entry.get("email") == email:
        return entry.get("password")
    return None


def vault_set_password(account, email, password, path=None):
    v = load_vault(path)
    v[account] = {"email": email, "password": password}
    return save_vault(v, path)


def get_password(acct, account, path=None):
    """凭据解析顺序：环境变量 YOUJIAN_PASS_<账号名> → 加密凭据库 vault.enc → macOS 钥匙串(旧版兜底)。"""
    env = os.environ.get(env_var_for(account))
    if env:
        return env
    pw = vault_get_password(account, acct["email"], path)
    if pw:
        return pw
    return _keychain_get("you-jian", acct["email"])


# ---------------------------------------------------------------------------
# 编码 / MIME 工具
# ---------------------------------------------------------------------------
def die(msg, code=1):
    print(f"[错误] {msg}", file=sys.stderr)
    sys.exit(code)


def warn(msg):
    print(f"[警告] {msg}", file=sys.stderr)


def imap_utf7_encode(s):
    """普通字符串 → IMAP modified UTF-7（用于带中文的文件夹名）。"""
    res, buf = [], []

    def flush():
        if buf:
            b = "".join(buf).encode("utf-16-be")
            res.append("&" + base64.b64encode(b, b"+-").decode("ascii").rstrip("=") + "-")
            buf.clear()

    for ch in s:
        o = ord(ch)
        if 0x20 <= o <= 0x7E:
            flush()
            res.append("&-" if ch == "&" else ch)
        else:
            buf.append(ch)
    flush()
    return "".join(res)


def imap_utf7_decode(s):
    if "&" not in s:
        return s
    out, i = [], 0
    while i < len(s):
        if s[i] == "&":
            j = s.find("-", i)
            if j == -1:
                out.append(s[i])
                i += 1
                continue
            if j == i + 1:  # "&-" 表示字面 "&"
                out.append("&")
                i = j + 1
                continue
            b = (s[i + 1:j] + "=" * (-len(s[i + 1:j]) % 4)).encode("ascii")
            try:
                out.append(base64.b64decode(b, b"+-").decode("utf-16-be"))
            except Exception:
                out.append(s[i:j + 1])
            i = j + 1
        else:
            out.append(s[i])
            i += 1
    return "".join(out)


def decode_header_value(raw):
    if not raw:
        return ""
    parts = []
    for text, charset in decode_header(raw):
        if isinstance(text, bytes):
            parts.append(text.decode(charset or "utf-8", errors="replace"))
        else:
            parts.append(text)
    return "".join(parts)


def decode_part(part):
    payload = part.get_payload(decode=True)
    if payload is None:
        return ""
    charset = part.get_content_charset() or "utf-8"
    for cs in (charset, "utf-8", "gb18030", "gbk", "big5", "latin-1"):
        try:
            return payload.decode(cs)
        except (LookupError, UnicodeDecodeError):
            continue
    return payload.decode("utf-8", errors="replace")


def strip_html(html):
    text = re.sub(r"(?is)<(script|style).*?>.*?</\1>", " ", html)
    text = re.sub(r"(?s)<[^>]+>", " ", text)
    text = re.sub(r"&nbsp;?", " ", text)
    text = re.sub(r"&amp;", "&", text)
    text = re.sub(r"&lt;", "<", text).replace("&gt;", ">")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n\s*\n+", "\n", text)
    return text.strip()


def parse_email(raw_bytes):
    """把 RFC822 原始字节解析成结构化字典。"""
    msg = EmailMessage()
    try:
        msg = msg.__class__()
    except TypeError:
        pass
    from email.parser import BytesParser
    msg = BytesParser(policy=policy.default).parsebytes(raw_bytes)

    def addresses(hdr):
        out = []
        for header in msg.get_all(hdr, []):
            # policy.default 下结构化 header 自带 .addresses（已正确解码显示名）
            addrs = getattr(header, "addresses", None)
            if addrs is not None:
                for a in addrs:
                    if getattr(a, "addr_spec", None):
                        out.append({"name": str(getattr(a, "display_name", "") or ""),
                                    "email": a.addr_spec})
            else:
                # 兜底：手动解码后再解析
                decoded = decode_header_value(str(header))
                for n, e in getaddresses([decoded]):
                    if e:
                        out.append({"name": n, "email": e})
        return out

    plain_parts, html_parts = [], []
    atts = []
    for part in msg.walk():
        cd = str(part.get("Content-Disposition") or "").lower()
        fn = part.get_filename()
        if fn:
            fn = decode_header_value(fn)
            atts.append({"filename": fn, "part": part, "size": len(part.get_payload(decode=True) or b"")})
            continue
        ct = part.get_content_type()
        if "attachment" in cd and not fn:
            atts.append({"filename": "(未命名附件)", "part": part, "size": len(part.get_payload(decode=True) or b"")})
            continue
        if ct == "text/plain":
            plain_parts.append(decode_part(part))
        elif ct == "text/html":
            html_parts.append(decode_part(part))

    plain = "\n".join(p for p in plain_parts if p).strip()
    html = "\n".join(p for p in html_parts if p).strip()
    body = plain if plain else (strip_html(html) if html else "")

    date = None
    if msg.get("Date"):
        try:
            date = parsedate_to_datetime(msg.get("Date"))
        except Exception:
            date = None

    return {
        "subject": decode_header_value(msg.get("Subject")) or "(无主题)",
        "from": addresses("From"),
        "to": addresses("To"),
        "cc": addresses("Cc"),
        "date": date,
        "message_id": msg.get("Message-ID", ""),
        "body": body,
        "html": html,
        "attachments": [{"filename": a["filename"], "size": a["size"]} for a in atts],
        "_att_parts": atts,
    }


def sanitize_filename(name):
    name = name.replace("\\", "/").split("/")[-1]  # 去路径
    name = "".join(ch for ch in name if ch.isprintable())
    name = name.strip().strip(".")
    return name or "attachment.bin"


# ---------------------------------------------------------------------------
# IMAP 连接
# ---------------------------------------------------------------------------
def connect_imap(acct, password, readonly=False):
    host = acct.get("imap_host") or acct["imap_server"]
    port = acct.get("imap_port", 993)
    M = imaplib.IMAP4_SSL(host, int(port))
    M.login(acct["email"], password)
    return M


def select_folder(M, folder, readonly=False):
    enc = imap_utf7_encode(folder)
    typ, data = M.select(enc, readonly=readonly)
    if typ != "OK":
        raise RuntimeError(f"无法打开文件夹 {folder}: {data}")
    return int(data[0]) if data and data[0] else 0


def list_folders(M):
    typ, data = M.list()
    if typ != "OK":
        raise RuntimeError(f"列出文件夹失败: {data}")
    out = []
    for line in data:
        if isinstance(line, bytes):
            line = line.decode("utf-8", errors="replace")
        m = re.match(r'\((?P<flags>.*?)\)\s+"(?P<delim>.)"\s+(?P<name>.+)', line)
        if m:
            name = m.group("name").strip('"')
            out.append({"name": imap_utf7_decode(name), "flags": m.group("flags"),
                        "delim": m.group("delim")})
    return out


def search_uids(M, folder, criteria, limit=None):
    select_folder(M, folder, readonly=True)
    typ, data = M.uid("SEARCH", None, *criteria)
    if typ != "OK":
        raise RuntimeError(f"搜索失败: {data}")
    uids = [u.decode() if isinstance(u, bytes) else str(u) for u in data[0].split()]
    if limit and int(limit) > 0:
        uids = uids[-int(limit):]  # 取最新
    return uids


def fetch_summary(M, uid):
    uid = uid.decode() if isinstance(uid, bytes) else str(uid)
    typ, data = M.uid("FETCH", uid, "(BODY.PEEK[HEADER.FIELDS (SUBJECT FROM TO DATE)])")
    if typ != "OK" or not data or data[0] is None:
        return None
    raw = b""
    for item in data:
        if isinstance(item, tuple):
            raw += item[1]
    msg = parse_email(raw + b"\r\n")
    return {"uid": uid, "subject": msg["subject"], "from": msg["from"],
            "to": msg["to"], "date": msg["date"]}


def fetch_full(M, uid):
    uid = uid.decode() if isinstance(uid, bytes) else str(uid)
    typ, data = M.uid("FETCH", uid, "(RFC822)")
    if typ != "OK" or not data:
        raise RuntimeError(f"读取邮件 {uid} 失败")
    raw = b""
    for item in data:
        if isinstance(item, tuple):
            raw += item[1]
    return raw


def resolve_uids_by_client_filter(M, folder, keyword, limit):
    """非 ASCII 关键词无法可靠走服务器端 SEARCH 时，拉取头部在客户端过滤。"""
    select_folder(M, folder, readonly=True)
    typ, data = M.uid("SEARCH", None, "ALL")
    uids = [u.decode() if isinstance(u, bytes) else str(u)
            for u in (data[0].split() if typ == "OK" and data[0] else [])]
    matched = []
    kw = keyword.lower()
    for uid in reversed(uids):  # 从最新往旧找
        s = fetch_summary(M, uid)
        if not s:
            continue
        hay = " ".join([
            s["subject"],
            " ".join(a["email"] + " " + a["name"] for a in s["from"]),
        ]).lower()
        if kw in hay:
            matched.append(uid)
            if limit and len(matched) >= int(limit):
                break
    return list(reversed(matched))


# ---------------------------------------------------------------------------
# 命令实现
# ---------------------------------------------------------------------------
def cmd_providers(args):
    print("内置服务商预设（IMAP/SMTP）:\n")
    for name, p in PROVIDERS.items():
        print(f"  {name:8s} imap://{p['imap_host']}:{p['imap_port']}"
              f"  smtp://{p['smtp_host']}:{p['smtp_port']} ({p['smtp_security']})")
        print(f"           {p['note']}")
    print("\n任意支持 IMAP/SMTP 的邮箱都可用 --imap/--smtp 手动指定服务器。")


def cmd_add(args):
    cfg = load_config(args.config)
    if args.account in cfg["accounts"] and not args.force:
        die(f"账号 {args.account} 已存在，加 --force 覆盖。")
    acct = {"email": args.email, "name": args.name or args.account}

    if args.provider:
        if args.provider not in PROVIDERS:
            die(f"未知服务商 {args.provider}，可用: {', '.join(PROVIDERS)}")
        p = PROVIDERS[args.provider]
        acct.update({"provider": args.provider, "imap_host": p["imap_host"],
                     "imap_port": p["imap_port"], "smtp_host": p["smtp_host"],
                     "smtp_port": p["smtp_port"], "smtp_security": p["smtp_security"]})
    else:
        if not args.imap or not args.smtp:
            die("需提供 --provider 预设，或 --imap 与 --smtp 服务器地址。")
        imap_host, _, imap_port = args.imap.partition(":")
        smtp_host, _, smtp_port = args.smtp.partition(":")
        acct.update({"imap_host": imap_host, "imap_port": int(imap_port or 993),
                     "smtp_host": smtp_host, "smtp_port": int(smtp_port or 465),
                     "smtp_security": args.smtp_security or "ssl"})

    # 密码处理（加密存入凭据库，不落明文）
    password = args.password
    if password is None:
        print(f"为 {args.email} 输入授权码/密码（不回显）：")
        password = getpass.getpass("  ")
    if password:
        if HAVE_CRYPTO:
            if get_master_key(args.config) is None:
                init_master_key(args.config)
            vault_set_password(args.account, acct["email"], password, args.config)
            print("  ✓ 授权码已加密存入凭据库 vault.enc（Fernet 认证加密）。")
        elif _keychain_set("you-jian", acct["email"], password):
            print("  ✓ 已存入 macOS 钥匙串（未装 cryptography 库时的兜底）。")
        else:
            print(f"  ⚠ 未装 cryptography 库且无钥匙串。请设置环境变量 {env_var_for(args.account)}，"
                  f"或 pip install cryptography。")

    cfg["accounts"][args.account] = acct
    p = save_config(cfg, args.config)
    print(f"已保存账号 {args.account} → {p}")
    print(f"下一步可运行: python mailbox.py check {args.account} 验证连接。")


def cmd_list(args):
    cfg = load_config(args.config)
    if not cfg["accounts"]:
        print("尚未配置任何邮箱。用 `add` 添加。")
        return
    print(f"{'账号':<12}{'邮箱':<32}{'IMAP':<28}{'SMTP':<28}")
    print("-" * 100)
    for name, a in cfg["accounts"].items():
        im = f"{a.get('imap_host','')}:{a.get('imap_port','')}"
        sm = f"{a.get('smtp_host','')}:{a.get('smtp_port','')}"
        print(f"{name:<12}{a['email']:<32}{im:<28}{sm:<28}")


def cmd_remove(args):
    cfg = load_config(args.config)
    if args.account not in cfg["accounts"]:
        die(f"账号 {args.account} 不存在。")
    del cfg["accounts"][args.account]
    save_config(cfg, args.config)
    print(f"已移除账号 {args.account}（未删除任何服务器上的邮件）。")


def _require_account(args):
    cfg = load_config(args.config)
    if args.account not in cfg["accounts"]:
        die(f"账号 {args.account} 不存在，先 `add` 或 `list` 查看。")
    acct = cfg["accounts"][args.account]
    pw = get_password(acct, args.account, args.config)
    if not pw:
        die(f"找不到账号 {args.account} 的凭据。请运行 add 重新配置，或设置环境变量 "
            f"{env_var_for(args.account)}。")
    return acct, pw


def iter_accounts(args, require_pw=True):
    """返回 [(账号名, acct, pw)]；args.account == 'all' 时遍历全部已配置账号。"""
    cfg = load_config(args.config)
    names = list(cfg["accounts"].keys()) if args.account == "all" else [args.account]
    out = []
    for name in names:
        if name not in cfg["accounts"]:
            die(f"账号 {name} 不存在，先 `add` 或 `list` 查看。")
        acct = cfg["accounts"][name]
        pw = get_password(acct, name, args.config) if require_pw else None
        if require_pw and not pw:
            warn(f"账号 {name} 无凭据，跳过。")
            continue
        out.append((name, acct, pw))
    if not out and require_pw:
        die("没有可用凭据的账号。")
    return out


def cmd_test(args):
    acct, pw = _require_account(args)
    M = connect_imap(acct, pw)
    folders = list_folders(M)
    n = 0
    try:
        n = select_folder(M, "INBOX")
    except RuntimeError:
        pass
    print(f"✓ 连接成功：{acct['email']}")
    print(f"  文件夹数 {len(folders)}，INBOX 邮件数 {n}")
    if args.folders:
        for f in folders:
            print(f"    - {f['name']}")
    M.logout()


def cmd_vault_init(args):
    init_master_key(args.config, force=args.force)
    p = vault_path(args.config)
    if not p.exists():
        save_vault({}, args.config)
    print(f"✓ 主密钥就绪，凭据库 {p}。")


def cmd_vault_status(args):
    if not HAVE_CRYPTO:
        print("⚠ 未安装 cryptography 库，无法使用加密凭据库。")
        print("  安装：pip install cryptography（或用环境变量 YOUJIAN_PASS_<账号名> 提供密码）。")
        return
    src = "环境变量" if os.environ.get("YOUJIAN_MASTER_KEY") else \
        ("macOS 钥匙串" if _keychain_get("you-jian-master", "master") else
         ("master.key 文件" if master_key_path(args.config).exists() else "未设置"))
    print(f"主密钥来源: {src}")
    p = vault_path(args.config)
    if not p.exists():
        print(f"凭据库: 尚未创建（{p} 不存在）。用 `add` 或 `vault-init` 创建。")
        return
    try:
        v = load_vault(args.config)
    except SystemExit:
        return
    cfg = load_config(args.config)
    print(f"凭据库: {p}（Fernet 加密，{len(v)} 个账号存有凭据）")
    all_names = sorted(set(list(cfg["accounts"].keys()) + list(v.keys())))
    for name in all_names:
        in_vault = name in v
        email = cfg["accounts"].get(name, {}).get("email", v.get(name, {}).get("email", "?"))
        print(f"  - {name:<14}{email:<34}{'有加密凭据' if in_vault else '无凭据'}")


def cmd_check(args):
    accounts = iter_accounts(args)
    print(f"检查 {len(accounts)} 个账号的连接...")
    ok = fail = 0
    for name, acct, pw in accounts:
        try:
            M = connect_imap(acct, pw)
            folders = list_folders(M)
            n = 0
            try:
                n = select_folder(M, "INBOX", readonly=True)
            except RuntimeError:
                pass
            M.logout()
            ok += 1
            print(f"  ✓ {name:<14}{acct['email']:<34}INBOX {n} 封 / {len(folders)} 文件夹")
        except Exception as e:
            fail += 1
            print(f"  ✗ {name:<14}{acct['email']:<34}{e}")
    print(f"结果: {ok} 成功，{fail} 失败")
    sys.exit(1 if fail else 0)


def cmd_folders(args):
    acct, pw = _require_account(args)
    M = connect_imap(acct, pw)
    for f in list_folders(M):
        print(f["name"])
    M.logout()


def cmd_stats(args):
    for name, acct, pw in iter_accounts(args):
        M = connect_imap(acct, pw)
        if args.account == "all":
            print(f"\n【账号 {name} · {acct['email']}】")
        print(f"{'文件夹':<30}{'邮件数':>8}")
        print("-" * 40)
        total = 0
        for f in list_folders(M):
            try:
                n = select_folder(M, f["name"], readonly=True)
            except RuntimeError:
                n = 0
            total += n
            print(f"{f['name']:<30}{n:>8}")
        print("-" * 40)
        print(f"{'合计':<30}{total:>8}")
        M.logout()


def _build_criteria(args):
    crit = []
    if getattr(args, "unread", False):
        crit.append("UNSEEN")
    if getattr(args, "from_", None):
        crit += ["FROM", f'"{args.from_}"']
    if getattr(args, "since", None):
        try:
            d = datetime.strptime(args.since, "%Y-%m-%d").date()
            crit += ["SINCE", d.strftime("%d-%b-%Y")]
        except ValueError:
            die(f"--since 需为 YYYY-MM-DD 格式，得到 {args.since}")
    return crit


def _print_list(items):
    if not items:
        print("（无匹配邮件）")
        return
    print(f"{'UID':>10}  {'日期':<20}{'发件人':<28}主题")
    print("-" * 100)
    for it in items:
        d = it["date"].strftime("%Y-%m-%d %H:%M") if it["date"] else "?"
        frm = it["from"][0]["email"] if it["from"] else "?"
        subj = it["subject"].replace("\n", " ")[:44]
        print(f"{it['uid']:>10}  {d:<20}{frm:<28}{subj}")


def cmd_fetch(args):
    folder = args.folder or "INBOX"
    for name, acct, pw in iter_accounts(args):
        M = connect_imap(acct, pw)
        uids = search_uids(M, folder, _build_criteria(args), args.limit)
        items = [s for s in (fetch_summary(M, uid) for uid in uids) if s]
        if args.account == "all":
            print(f"\n【账号 {name} · {acct['email']}】文件夹 {folder}，共 {len(items)} 封：")
        else:
            print(f"文件夹 {folder}，共 {len(items)} 封：")
        _print_list(items)
        M.logout()


def cmd_search(args):
    folder = args.folder or "INBOX"
    kw = args.keyword
    for name, acct, pw in iter_accounts(args):
        M = connect_imap(acct, pw)
        if kw.isascii():
            uids = search_uids(M, folder, ["TEXT", f'"{kw}"'], args.limit)
        else:
            uids = resolve_uids_by_client_filter(M, folder, kw, args.limit)
        items = [s for s in (fetch_summary(M, uid) for uid in uids) if s]
        if args.account == "all":
            print(f"\n【账号 {name} · {acct['email']}】关键词「{kw}」，文件夹 {folder}，共 {len(items)} 封：")
        else:
            print(f"关键词「{kw}」，文件夹 {folder}，共 {len(items)} 封：")
        _print_list(items)
        M.logout()


def cmd_read(args):
    acct, pw = _require_account(args)
    M = connect_imap(acct, pw)
    select_folder(M, args.folder or "INBOX")
    raw = fetch_full(M, args.uid)
    msg = parse_email(raw)
    print("=" * 100)
    print(f"主题: {msg['subject']}")
    frm = ", ".join(f"{a['name']} <{a['email']}>" for a in msg["from"]) or "?"
    to = ", ".join(a["email"] for a in msg["to"]) or "?"
    print(f"发件: {frm}")
    print(f"收件: {to}")
    if msg["cc"]:
        print(f"抄送: {', '.join(a['email'] for a in msg['cc'])}")
    if msg["date"]:
        print(f"时间: {msg['date'].strftime('%Y-%m-%d %H:%M:%S %z')}")
    if msg["attachments"]:
        print("附件: " + ", ".join(f"{a['filename']}({a['size']}B)" for a in msg["attachments"]))
    print("=" * 100)
    print(msg["body"] if msg["body"] else "(无正文文本，可能为纯 HTML/图片邮件)")
    M.logout()


def cmd_attach(args):
    acct, pw = _require_account(args)
    out_dir = Path(args.dir) if args.dir else Path.cwd() / f"attachments_{args.uid}"
    out_dir.mkdir(parents=True, exist_ok=True)
    M = connect_imap(acct, pw)
    select_folder(M, args.folder or "INBOX")
    raw = fetch_full(M, args.uid)
    msg = parse_email(raw)
    saved = 0
    for att in msg["_att_parts"]:
        fn = sanitize_filename(att["filename"])
        dest = out_dir / fn
        if dest.exists() and not args.force:
            warn(f"{dest} 已存在，跳过（加 --force 覆盖）。")
            continue
        data = att["part"].get_payload(decode=True) or b""
        dest.write_bytes(data)
        print(f"✓ {dest} ({len(data)} 字节)")
        saved += 1
    print(f"共保存 {saved} 个附件到 {out_dir}")
    M.logout()


def cmd_kb(args):
    """把邮箱里的邮件构建成本地可检索知识库（Markdown + index.json）。"""
    out_root = Path(args.dir) if args.dir else Path.cwd() / "MailKB"
    folder = args.folder or "INBOX"
    for name, acct, pw in iter_accounts(args):
        M = connect_imap(acct, pw)
        uids = search_uids(M, folder, _build_criteria(args), args.limit)
        out_dir = out_root / name
        out_dir.mkdir(parents=True, exist_ok=True)
        index = []
        for uid in uids:
            raw = fetch_full(M, uid)
            msg = parse_email(raw)
            frm = ", ".join(f"{a['name']} <{a['email']}>" for a in msg["from"]) or "?"
            d = msg["date"].strftime("%Y-%m-%d") if msg["date"] else "unknown"
            subj = msg["subject"]
            fn = f"{uid}_{d}_{sanitize_filename(subj[:40])}.md"
            atts = [a["filename"] for a in msg["attachments"]]
            md = (
                f"---\nuid: {uid}\nfrom: {frm}\n"
                f"date: {msg['date'].isoformat() if msg['date'] else ''}\n"
                f"subject: {subj}\nattachments: "
                f"{json.dumps(atts, ensure_ascii=False)}\n---\n\n"
                f"# {subj}\n\n{msg['body'] or '(无正文)'}\n"
            )
            (out_dir / fn).write_text(md, encoding="utf-8")
            index.append({"uid": uid, "file": fn, "from": frm,
                          "date": msg["date"].isoformat() if msg["date"] else "",
                          "subject": subj, "attachments": atts})
        (out_dir / "index.json").write_text(
            json.dumps(index, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"✓ 账号 {name}：导出 {len(index)} 封 → {out_dir}")
        M.logout()


def cmd_mark(args):
    acct, pw = _require_account(args)
    M = connect_imap(acct, pw)
    select_folder(M, args.folder or "INBOX")
    states = {"read", "unread", "flag", "unflag"}
    if args.state not in states:
        die(f"标记状态需为 {', '.join(sorted(states))}")
    flag = "\\Seen" if args.state in ("read", "unread") else "\\Flagged"
    mode = "+FLAGS" if args.state in ("read", "flag") else "-FLAGS"
    if not args.yes:
        print(f"[DRY-RUN] 将执行: UID STORE {args.uid} {mode} ({flag})")
        return
    typ, data = M.uid("STORE", args.uid, mode, f"({flag})")
    print(f"✓ 已标记 → {typ}")
    M.logout()


def _move_uid(M, uid, target, yes):
    enc_target = imap_utf7_encode(target)
    if not yes:
        print(f"[DRY-RUN] 将移动 uid={uid} → 文件夹「{target}」")
        return
    # 优先用 MOVE (RFC 6851)，不支持则 COPY + \Deleted + EXPUNGE
    try:
        typ, data = M.uid("MOVE", uid, enc_target)
        if typ == "OK":
            print(f"✓ 已移动 uid={uid} → {target}")
            return
    except imaplib.IMAP4.error:
        pass
    typ, data = M.uid("COPY", uid, enc_target)
    if typ != "OK":
        raise RuntimeError(f"移动失败: {data}")
    M.uid("STORE", uid, "+FLAGS", "(\\Deleted)")
    M.expunge()
    print(f"✓ 已移动 uid={uid} → {target}（COPY+EXPUNGE 方式）")


def cmd_move(args):
    acct, pw = _require_account(args)
    M = connect_imap(acct, pw)
    select_folder(M, args.folder or "INBOX")
    _move_uid(M, args.uid, args.target, args.yes)
    M.logout()


def _find_trash(folders):
    for f in folders:
        n = f["name"].lower()
        if n in ("trash", "deleted items", "deleted messages", "已删除", "垃圾箱", "废纸篓"):
            return f["name"]
    return None


def cmd_delete(args):
    acct, pw = _require_account(args)
    M = connect_imap(acct, pw)
    select_folder(M, args.folder or "INBOX")
    trash = _find_trash(list_folders(M))
    if not args.yes:
        where = f"（移入 {trash}）" if trash else "（标记 \\Deleted 并 EXPUNGE，不可恢复）"
        print(f"[DRY-RUN] 将删除 uid={args.uid} {where}")
        print("  确认请加 --yes。")
        return
    if trash:
        _move_uid(M, args.uid, trash, True)
    else:
        M.uid("STORE", args.uid, "+FLAGS", "(\\Deleted)")
        M.expunge()
        print(f"✓ 已永久删除 uid={args.uid}（无回收站文件夹，已 EXPUNGE）")
    M.logout()


def _build_message(args):
    msg = EmailMessage()
    msg["From"] = formataddr((args.sender_name or "", args.from_)) if args.sender_name else args.from_
    msg["To"] = args.to
    if args.cc:
        msg["Cc"] = args.cc
    if args.bcc:
        msg["Bcc"] = args.bcc
    msg["Subject"] = args.subject or "(无主题)"
    body = args.body
    if args.body_file:
        body = Path(args.body_file).read_text(encoding="utf-8")
    if body is None:
        body = ""
    msg.set_content(body)
    for f in (args.attach or []):
        p = Path(f)
        if not p.exists():
            die(f"附件不存在: {f}")
        ctype = "application/octet-stream"
        sub = p.suffix.lower()
        if sub in (".txt", ".md"):
            ctype = "text/plain"
        elif sub in (".pdf",):
            ctype = "application/pdf"
        elif sub in (".png",):
            ctype = "image/png"
        elif sub in (".jpg", ".jpeg"):
            ctype = "image/jpeg"
        elif sub in (".docx",):
            ctype = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        elif sub in (".xlsx",):
            ctype = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        msg.add_attachment(p.read_bytes(), maintype=ctype.split("/")[0],
                           subtype=ctype.split("/")[1], filename=p.name)
    return msg


def cmd_send(args):
    cfg = load_config(args.config)
    acct = cfg["accounts"].get(args.account)
    if not acct:
        die(f"账号 {args.account} 不存在。")
    pw = get_password(acct, args.account, args.config)
    if not pw:
        die(f"找不到账号 {args.account} 的凭据。")
    if not args.from_:
        args.from_ = acct["email"]
    msg = _build_message(args)

    if not args.yes:
        print("[DRY-RUN] 将发送邮件：")
        print(f"  From: {msg['From']}")
        print(f"  To:   {msg['To']}")
        if msg["Cc"]:
            print(f"  Cc:   {msg['Cc']}")
        print(f"  主题: {msg['Subject']}")
        body_preview = (msg.get_body().get_content() if msg.get_body() else "")[:120]
        print(f"  正文预览: {body_preview}")
        print("  确认请加 --yes。")
        return

    smtp_host = acct.get("smtp_host") or acct["smtp_server"]
    smtp_port = int(acct.get("smtp_port", 465))
    security = acct.get("smtp_security", "ssl")
    if security == "starttls":
        S = smtplib.SMTP(smtp_host, smtp_port, timeout=30)
        S.starttls()
    else:
        S = smtplib.SMTP_SSL(smtp_host, smtp_port, timeout=30)
    S.login(acct["email"], pw)
    S.send_message(msg)
    S.quit()
    print(f"✓ 已通过 {acct['email']} 发送到 {msg['To']}")


def _guess_importance(subject, frm, body):
    text = f"{subject}\n{body[:2000]}".lower()
    senders = " ".join(a["email"] + " " + a["name"] for a in frm).lower()
    k_urgent = ["截止", "deadline", "urgent", "紧急", "尽快", "asap", "请回复", "请确认",
                "逾期", "最后", "final", "评审", "答辩", "查重", "缴费", "逾期不候"]
    k_todo = ["发票", "报销", "合同", "审批", "签到", "投票", "问卷", "盖章", "签字",
              "提交", "补交", "材料", "成绩", "名单", "成绩单", "考核"]
    k_notice = ["通知", "公告", "公示", "会议", "培训", "讲座", "讲座通知", "任前公示"]
    k_code = ["验证码", "verification code", "security code", "验证", "激活"]
    k_ads = ["优惠", "广告", "推广", "unsubscribe", "退订", "促销", "秒杀", "双十一"]
    k_no_reply = ["no-reply", "noreply", "noreply@", "do-not-reply", "自动", "系统邮件"]
    if any(k in text for k in k_urgent):
        return "紧急/需处理"
    if any(k in text for k in k_todo):
        return "待办"
    if any(k in text for k in k_code):
        return "验证码/自动"
    if any(k in text for k in k_ads) or any(k in senders for k in k_ads):
        return "营销/可忽略"
    if any(k in senders for k in k_no_reply) or any(k in text for k in k_notice):
        return "通知"
    return "普通"


def cmd_digest(args):
    folder = args.folder or "INBOX"
    days = int(args.days) if args.days else 7
    since = (datetime.now() - timedelta(days=days)).strftime("%d-%b-%Y")
    for name, acct, pw in iter_accounts(args):
        M = connect_imap(acct, pw)
        uids = search_uids(M, folder, ["SINCE", since], args.limit)
        rows = []
        for uid in uids:
            raw = fetch_full(M, uid)
            msg = parse_email(raw)
            frm = msg["from"][0]["email"] if msg["from"] else "?"
            cat = _guess_importance(msg["subject"], msg["from"], msg["body"])
            rows.append({"uid": uid, "subject": msg["subject"][:60], "from": frm,
                         "date": msg["date"], "cat": cat,
                         "att": len(msg["attachments"])})
        M.logout()

        if not rows:
            print(f"【账号 {name}】近 {days} 天无新邮件。")
            continue

        from collections import Counter
        cats = Counter(r["cat"] for r in rows)
        senders = Counter(r["from"] for r in rows)
        print(f"\n【账号 {name} · {acct['email']}】近 {days} 天共 {len(rows)} 封邮件：")
        print(f"{'UID':>10}  {'日期':<11}{'分类':<10}{'附':>3}  发件人 / 主题")
        print("-" * 100)
        for r in rows:
            d = r["date"].strftime("%m-%d %H:%M") if r["date"] else "?"
            print(f"{r['uid']:>10}  {d:<11}{r['cat']:<10}{r['att']:>3}  {r['from']:<28}{r['subject']}")
        print("\n分类统计: " + "、".join(f"{k} {v} 封" for k, v in cats.most_common()))
        top = senders.most_common(5)
        if top:
            print("高频发件人: " + "、".join(f"{e} {n} 封" for e, n in top))
        urgent = [r for r in rows if r["cat"] in ("紧急/需处理", "待办")]
        if urgent:
            print("\n建议优先处理:")
            for r in urgent:
                print(f"  {name}:{r['uid']}  [{r['cat']}] {r['subject']}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def build_parser():
    ap = argparse.ArgumentParser(
        prog="mailbox.py",
        description="多邮箱 IMAP/SMTP 客户端（纯标准库）。读操作只读，写操作需 --yes。",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--config", help="配置文件路径（默认 ~/.config/you-jian/accounts.json）")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("providers", help="列出内置服务商预设")
    p.set_defaults(func=cmd_providers)

    p = sub.add_parser("add", help="添加邮箱账号（授权码加密存入凭据库）")
    p.add_argument("account")
    p.add_argument("email")
    p.add_argument("--provider", choices=list(PROVIDERS), help="服务商预设")
    p.add_argument("--imap", help="IMAP 服务器（host:port）")
    p.add_argument("--smtp", help="SMTP 服务器（host:port）")
    p.add_argument("--smtp-security", choices=["ssl", "starttls"], help="SMTP 加密方式")
    p.add_argument("--password", help="授权码（不传则交互输入；存入加密凭据库）")
    p.add_argument("--name", help="显示名称")
    p.add_argument("--force", action="store_true", help="覆盖已存在账号")
    p.set_defaults(func=cmd_add)

    p = sub.add_parser("vault-init", help="初始化主密钥与加密凭据库")
    p.add_argument("--force", action="store_true", help="重新生成主密钥")
    p.set_defaults(func=cmd_vault_init)

    p = sub.add_parser("vault-status", help="查看凭据库状态（不泄露密码）")
    p.set_defaults(func=cmd_vault_status)

    p = sub.add_parser("check", help="登录并检查账号连接（默认全部）")
    p.add_argument("account", nargs="?", default="all", help="账号名或 all（默认 all）")
    p.set_defaults(func=cmd_check)

    p = sub.add_parser("list", help="列出已配置账号")
    p.set_defaults(func=cmd_list)

    p = sub.add_parser("remove", help="移除账号配置（不动服务器邮件）")
    p.add_argument("account")
    p.set_defaults(func=cmd_remove)

    p = sub.add_parser("test", help="测试连接")
    p.add_argument("account")
    p.add_argument("--folders", action="store_true", help="同时列出文件夹")
    p.set_defaults(func=cmd_test)

    p = sub.add_parser("folders", help="列出文件夹")
    p.add_argument("account")
    p.set_defaults(func=cmd_folders)

    p = sub.add_parser("stats", help="各文件夹邮件数统计")
    p.add_argument("account", help="账号名或 all")
    p.set_defaults(func=cmd_stats)

    p = sub.add_parser("fetch", help="拉取邮件列表")
    p.add_argument("account", help="账号名或 all")
    p.add_argument("--folder", help="文件夹（默认 INBOX）")
    p.add_argument("--limit", type=int, help="最多返回 N 封（最新）")
    p.add_argument("--unread", action="store_true", help="只看未读")
    p.add_argument("--from", dest="from_", help="按发件人过滤")
    p.add_argument("--since", help="起始日期 YYYY-MM-DD")
    p.set_defaults(func=cmd_fetch)

    p = sub.add_parser("search", help="按关键词搜索")
    p.add_argument("account", help="账号名或 all")
    p.add_argument("keyword")
    p.add_argument("--folder", help="文件夹（默认 INBOX）")
    p.add_argument("--limit", type=int, help="最多返回 N 封")
    p.set_defaults(func=cmd_search)

    p = sub.add_parser("read", help="读某封邮件全文")
    p.add_argument("account")
    p.add_argument("uid")
    p.add_argument("--folder", help="邮件所在文件夹（默认 INBOX）")
    p.set_defaults(func=cmd_read)

    p = sub.add_parser("attach", help="下载某封邮件的附件")
    p.add_argument("account")
    p.add_argument("uid")
    p.add_argument("--folder", help="邮件所在文件夹（默认 INBOX）")
    p.add_argument("--dir", help="输出目录")
    p.add_argument("--force", action="store_true", help="覆盖已存在文件")
    p.set_defaults(func=cmd_attach)

    p = sub.add_parser("kb", help="把邮件构建成本地可检索知识库（Markdown + index.json）")
    p.add_argument("account", help="账号名或 all")
    p.add_argument("--dir", help="输出根目录（默认 ./MailKB）")
    p.add_argument("--folder", help="文件夹（默认 INBOX）")
    p.add_argument("--limit", type=int, help="最多导出 N 封（最新）")
    p.add_argument("--unread", action="store_true", help="只看未读")
    p.add_argument("--from", dest="from_", help="按发件人过滤")
    p.add_argument("--since", help="起始日期 YYYY-MM-DD")
    p.set_defaults(func=cmd_kb)

    p = sub.add_parser("mark", help="标记 read/unread/flag/unflag")
    p.add_argument("account")
    p.add_argument("uid")
    p.add_argument("state", choices=["read", "unread", "flag", "unflag"])
    p.add_argument("--folder", help="邮件所在文件夹（默认 INBOX）")
    p.add_argument("--yes", action="store_true", help="真正执行")
    p.set_defaults(func=cmd_mark)

    p = sub.add_parser("move", help="移动到指定文件夹")
    p.add_argument("account")
    p.add_argument("uid")
    p.add_argument("target")
    p.add_argument("--folder", help="邮件当前所在文件夹（默认 INBOX）")
    p.add_argument("--yes", action="store_true", help="真正执行")
    p.set_defaults(func=cmd_move)

    p = sub.add_parser("delete", help="删除邮件（默认移入回收站）")
    p.add_argument("account")
    p.add_argument("uid")
    p.add_argument("--folder", help="邮件当前所在文件夹（默认 INBOX）")
    p.add_argument("--yes", action="store_true", help="真正执行")
    p.set_defaults(func=cmd_delete)

    p = sub.add_parser("send", help="发送邮件")
    p.add_argument("account")
    p.add_argument("--from", dest="from_", help="发件地址（默认用账号邮箱）")
    p.add_argument("--sender-name", help="发件人显示名")
    p.add_argument("--to", required=True)
    p.add_argument("--cc")
    p.add_argument("--bcc")
    p.add_argument("--subject")
    p.add_argument("--body")
    p.add_argument("--body-file", help="正文从文件读取（UTF-8）")
    p.add_argument("--attach", nargs="*", help="附件路径（可多个）")
    p.add_argument("--yes", action="store_true", help="真正发送")
    p.set_defaults(func=cmd_send)

    p = sub.add_parser("digest", help="生成最近邮件摘要")
    p.add_argument("account", help="账号名或 all")
    p.add_argument("--days", type=int, default=7, help="最近 N 天（默认 7）")
    p.add_argument("--limit", type=int, help="最多处理 N 封")
    p.add_argument("--folder", help="文件夹（默认 INBOX）")
    p.set_defaults(func=cmd_digest)

    return ap


def main(argv=None):
    args = build_parser().parse_args(argv)
    try:
        args.func(args)
    except imaplib.IMAP4.error as e:
        die(f"IMAP 错误: {e}")
    except smtplib.SMTPException as e:
        die(f"SMTP 错误: {e}")
    except (ConnectionError, TimeoutError, OSError) as e:
        die(f"网络错误: {e}")
    except KeyboardInterrupt:
        die("已中断", 130)


if __name__ == "__main__":
    main()
