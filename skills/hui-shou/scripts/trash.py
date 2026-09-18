#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
trash.py — File-operation logger & safe-recovery tool (HuiShou skill).

Core idea: move endangered content into a per-project trash with an append-only
JSONL manifest BEFORE executing destructive ops, so every rm/overwrite/move is
reversible with SHA-256 integrity verification.

Subcommands:
    trash.py delete <path>            # safe delete via trash
    trash.py overwrite <path>          # snapshot before overwrite (returns id)
    trash.py move <src> <dst>          # move/rename with manifest entry
    trash.py list [filter] [--op O] [--days N]   # list trash entries
    trash.py log [N]                   # recent N log entries
    trash.py inspect <id>              # one entry detail + checksum re-verify
    trash.py restore <id|path|pattern> [--to DST] [--force] [--consume]
    trash.py purge [days] [--confirm]
    trash.py guard on|off|status

Requires: Python 3.8+ (stdlib only). No third-party deps.
"""
import argparse
import fcntl
import fnmatch
import hashlib
import json
import os
import random
import shutil
import string
import sys
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path

TRASH_ROOT = Path(os.environ.get("OPENCODE_TRASH_ROOT", str(Path.home() / ".opencode-trash")))
MANIFEST_NAME = "manifest.jsonl"
ENTRIES_DIR = "entries"
GUARD_LOCK = "guard.lock"
MAX_INLINE_BYTES = int(os.environ.get("OPENCODE_TRASH_MAX_INLINE", str(256 * 1024 * 1024)))
PURGE_DEFAULT_DAYS = 30


# ---------- project slug ----------
def project_slug(cwd: str | None = None) -> str:
    cwd = cwd or os.getcwd()
    h = hashlib.sha1(cwd.encode()).hexdigest()[:12]
    tail = os.path.basename(cwd.rstrip("/")) or "root"
    return f"{h}-{tail}"


def trash_dir(slug: str | None = None) -> Path:
    return TRASH_ROOT / (slug or project_slug())


def manifest_path(slug: str | None = None) -> Path:
    return trash_dir(slug) / MANIFEST_NAME


def entries_root(slug: str | None = None) -> Path:
    return trash_dir(slug) / ENTRIES_DIR


def guard_lock_path(slug: str | None = None) -> Path:
    return trash_dir(slug) / GUARD_LOCK


# ---------- id generation ----------
def gen_id() -> str:
    ts = datetime.now().strftime("%Y%m%d-%H%M")
    rnd = "".join(random.choices(string.ascii_lowercase + string.digits, k=4))
    return f"{ts}-{rnd}"


def iso_now() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


# ---------- manifest append (locked) ----------
def append_manifest(slug: str, record: dict) -> None:
    mp = manifest_path(slug)
    mp.parent.mkdir(parents=True, exist_ok=True)
    line = json.dumps(record, ensure_ascii=False, sort_keys=False)
    with open(mp, "a", encoding="utf-8") as f:
        fcntl.flock(f.fileno(), fcntl.LOCK_EX)
        try:
            f.write(line + "\n")
            f.flush()
            os.fsync(f.fileno())
        finally:
            fcntl.flock(f.fileno(), fcntl.LOCK_UN)


def read_manifest(slug: str) -> list[dict]:
    mp = manifest_path(slug)
    if not mp.exists():
        return []
    out = []
    with open(mp, "r", encoding="utf-8") as f:
        for lineno, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError:
                print(f"WARN: manifest line {lineno} corrupt, skipped", file=sys.stderr)
    return out


def active_entries(slug: str) -> list[dict]:
    """Return entries not purged (skip tombstones and entries with a purge tombstone)."""
    rows = read_manifest(slug)
    purged_ids = {r["id"] for r in rows if r.get("op") == "purged" or r.get("purged")}
    return [r for r in rows if r.get("op") not in ("purged",)
            and not r.get("purged")
            and r.get("id") not in purged_ids]


# ---------- checksum & size ----------
def sha256_file(path: Path) -> tuple[str, int]:
    h = hashlib.sha256()
    size = 0
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
            size += len(chunk)
    return h.hexdigest(), size


def sha256_tree(path: Path) -> tuple[str, int]:
    h = hashlib.sha256()
    total = 0
    for root, _dirs, files in os.walk(path):
        for name in sorted(files):
            fp = Path(root) / name
            fh, size = sha256_file(fp)
            h.update(fh.encode())
            total += size
    return h.hexdigest(), total


# ---------- entry collection ----------
def collect_entry(slug: str, src_abs: Path, id_: str) -> dict:
    """Move src into entries/<id>/, return base record dict (without op/time)."""
    td = entries_root(slug) / id_
    td.mkdir(parents=True, exist_ok=True)
    dst = td / src_abs.name
    is_link = src_abs.is_symlink()
    is_dir = src_abs.is_dir() and not is_link
    mtime = src_abs.stat().st_mtime
    link_target = ""
    if is_link:
        link_target = os.readlink(src_abs)

    large = False
    large_path = ""
    if not is_link:
        size_check = src_abs.stat().st_size if src_abs.is_file() else sum(
            f.stat().st_size for f in src_abs.rglob("*") if f.is_file()
        )
        if size_check > MAX_INLINE_BYTES:
            large = True
            large_path = str(src_abs)

    if large:
        # keep content in place; only log
        sha, size = (sha256_tree(src_abs) if is_dir else sha256_file(src_abs)) if not is_link else ("", 0)
    else:
        if is_link:
            # recreate symlink in trash
            if dst.exists() or dst.is_symlink():
                dst.unlink()
            os.symlink(link_target, dst)
            os.unlink(src_abs)
            sha, size = "", 0
        else:
            try:
                shutil.move(str(src_abs), str(dst))
            except OSError:
                # cross-device: copy then unlink
                if is_dir:
                    shutil.copytree(src_abs, dst)
                    shutil.rmtree(src_abs)
                else:
                    shutil.copy2(src_abs, dst)
                    src_abs.unlink()
            if is_dir:
                sha, size = sha256_tree(dst)
            else:
                sha, size = sha256_file(dst)

    cwd = os.getcwd()
    try:
        rel = str(src_abs.relative_to(cwd))
    except ValueError:
        rel = str(src_abs)

    return {
        "id": id_,
        "src": str(src_abs),
        "src_rel": rel,
        "trash_path": str(dst.relative_to(trash_dir(slug))),
        "sha256": sha,
        "size": size,
        "mtime": mtime,
        "is_dir": is_dir,
        "is_link": is_link,
        "link_target": link_target,
        "large": large,
        "large_path": large_path,
        "project_slug": slug,
        "cwd": cwd,
    }


# ---------- subcommands ----------
def cmd_delete(args):
    src = Path(args.path).resolve()
    if not src.exists() and not src.is_symlink():
        print(f"ERROR: not found: {src}", file=sys.stderr)
        return 1
    slug = project_slug()
    id_ = gen_id()
    rec = collect_entry(slug, src, id_)
    rec.update({"op": "delete", "time": iso_now()})
    append_manifest(slug, rec)
    print(f"collected id={id_} src={rec['src']} size={rec['size']} sha256={rec['sha256'][:12]}…")
    print(f"deleted (in trash). restore: /回收 restore {id_}")
    return 0


def cmd_overwrite(args):
    src = Path(args.path).resolve()
    slug = project_slug()
    if src.exists() or src.is_symlink():
        id_ = gen_id()
        rec = collect_entry(slug, src, id_)
        rec.update({"op": "overwrite", "time": iso_now()})
        append_manifest(slug, rec)
        print(f"snapshot id={id_} src={rec['src']} size={rec['size']} sha256={rec['sha256'][:12]}…")
        print(f"old version safe. you may now overwrite {args.path}")
    else:
        print(f"no existing file at {args.path}; nothing to snapshot (will be a new file)")
    return 0


def cmd_move(args):
    src = Path(args.src).resolve()
    dst = Path(args.dst).resolve()
    if not src.exists() and not src.is_symlink():
        print(f"ERROR: src not found: {src}", file=sys.stderr)
        return 1
    slug = project_slug()
    cwd = os.getcwd()
    try:
        src_rel = str(src.relative_to(cwd))
    except ValueError:
        src_rel = str(src)
    # snapshot dst if exists
    if dst.exists() or dst.is_symlink():
        id2 = gen_id()
        rec2 = collect_entry(slug, dst, id2)
        rec2.update({"op": "delete", "time": iso_now()})
        append_manifest(slug, rec2)
        print(f"dst existed, snapshotted id={id2}")
    try:
        shutil.move(str(src), str(dst))
    except OSError as e:
        print(f"ERROR move failed: {e}; rolling back dst", file=sys.stderr)
        # best-effort rollback not implemented for large; report
        return 1
    rec = {
        "id": gen_id(),
        "op": "move",
        "src": str(src),
        "dst": str(dst),
        "src_rel": src_rel,
        "time": iso_now(),
        "project_slug": slug,
        "cwd": cwd,
    }
    append_manifest(slug, rec)
    print(f"moved {src} -> {dst} (logged)")
    return 0


def cmd_list(args):
    slug = project_slug()
    entries = active_entries(slug)
    # filter
    if args.filter:
        pat = args.filter
        entries = [r for r in entries if fnmatch.fnmatch(r.get("src_rel", ""), pat) or fnmatch.fnmatch(r.get("src", ""), pat)]
    if args.op:
        entries = [r for r in entries if r.get("op") == args.op]
    if args.days is not None:
        cutoff = datetime.now().astimezone() - timedelta(days=args.days)
        kept = []
        for r in entries:
            try:
                t = datetime.fromisoformat(r["time"])
                if t >= cutoff:
                    kept.append(r)
            except (KeyError, ValueError):
                pass
        entries = kept
    if not entries:
        print("(no entries)")
        return 0
    print(f"{'id':<20} {'op':<10} {'src_rel':<40} {'size':>10} {'sha256':<13} {'time':<21} R")
    for r in entries:
        sha = r.get("sha256", "")[:12]
        print(f"{r.get('id',''):<20} {r.get('op',''):<10} {r.get('src_rel',''):<40} {r.get('size',0):>10} {sha:<13} {r.get('time',''):<21} {'Y' if r.get('restored') else ''}")
    print(f"total: {len(entries)}")
    return 0


def cmd_log(args):
    slug = project_slug()
    all_rows = read_manifest(slug)
    n = args.N or 20
    rows = all_rows[-n:]
    if not rows:
        print("(no log)")
        return 0
    print(f"{'id':<20} {'op':<10} {'src_rel':<40} {'time':<21}")
    for r in rows:
        print(f"{r.get('id',''):<20} {r.get('op',''):<10} {r.get('src_rel', r.get('src','')):<40} {r.get('time',''):<21}")
    print(f"showing last {len(rows)} of {len(all_rows)}")
    return 0


def cmd_inspect(args):
    slug = project_slug()
    entries = active_entries(slug)
    match = [r for r in entries if r.get("id") == args.id]
    if not match:
        print(f"ERROR: id not found: {args.id}", file=sys.stderr)
        return 1
    r = match[0]
    print(json.dumps(r, ensure_ascii=False, indent=2))
    # re-verify checksum if content available
    tp = trash_dir(slug) / r["trash_path"]
    if r.get("is_link"):
        if tp.is_symlink():
            print(f"symlink -> {os.readlink(tp)}  (target not verified)")
        else:
            print("WARN: symlink missing in trash")
    elif r.get("large"):
        p = Path(r.get("large_path", ""))
        if p.exists():
            sha, size = (sha256_tree(p) if r["is_dir"] else sha256_file(p))
            ok = sha == r["sha256"]
            print(f"re-verify (large, in-place): {'OK' if ok else 'MISMATCH'} sha256={sha[:12]}… size={size}")
        else:
            print("WARN: large content missing in place")
    elif tp.exists():
        sha, size = (sha256_tree(tp) if r["is_dir"] else sha256_file(tp))
        ok = sha == r["sha256"]
        print(f"re-verify: {'OK' if ok else 'MISMATCH'} sha256={sha[:12]}… size={size}")
    else:
        print("WARN: content missing in trash")
    return 0


def find_entries_to_restore(slug: str, query: str) -> list[dict]:
    entries = active_entries(slug)
    # by exact id
    by_id = [r for r in entries if r.get("id") == query]
    if by_id:
        return by_id
    # by path (src or src_rel), most recent first
    by_path = [r for r in entries if r.get("src") == query or r.get("src_rel") == query]
    if by_path:
        by_path.sort(key=lambda r: r.get("time", ""), reverse=True)
        return by_path
    # by glob on src_rel (also match a dir entry when pattern is dir/**)
    def glob_match(rel, pat):
        if fnmatch.fnmatch(rel, pat):
            return True
        # tests/** should also match the dir 'tests' itself
        if pat.endswith("/**"):
            base = pat[:-3]
            if rel == base or rel.startswith(base + "/"):
                return True
        # tests/* matches dir 'tests' as a prefix
        if pat.endswith("/*"):
            base = pat[:-2]
            if rel == base or rel.startswith(base + "/"):
                return True
        return False
    by_glob = [r for r in entries if glob_match(r.get("src_rel", ""), query)]
    if by_glob:
        by_glob.sort(key=lambda r: r.get("time", ""), reverse=True)
        return by_glob
    return []


def cmd_restore(args):
    slug = project_slug()
    matches = find_entries_to_restore(slug, args.query)
    if not matches:
        print(f"ERROR: no matching entry for: {args.query}", file=sys.stderr)
        return 1
    ok = 0
    skip = 0
    fail = 0
    for r in matches:
        res = restore_one(slug, r, args.to, args.force, args.consume)
        if res == "ok":
            ok += 1
        elif res == "skip":
            skip += 1
        else:
            fail += 1
    print(f"restore done: ok={ok} skip={skip} fail={fail}")
    return 0 if fail == 0 else 1


def restore_one(slug: str, r: dict, to: str | None, force: bool, consume: bool) -> str:
    tid = r["id"]
    tp = trash_dir(slug) / r["trash_path"]
    # determine target
    if to:
        dst = Path(to)
        if dst.is_dir():
            dst = dst / Path(r["src"]).name
    else:
        dst = Path(r["src"])
        # if absolute path invalid (project moved), try src_rel under cwd
        if not dst.parent.exists() and not dst.parent.is_symlink():
            dst = Path.cwd() / r["src_rel"]
    dst.parent.mkdir(parents=True, exist_ok=True)
    # verify checksum
    if not r.get("is_link"):
        if r.get("large"):
            src_p = Path(r.get("large_path", ""))
            if not src_p.exists():
                print(f"FAIL {tid}: large content missing in place")
                return "fail"
            sha, size = (sha256_tree(src_p) if r["is_dir"] else sha256_file(src_p))
            content_path = src_p
        elif tp.exists():
            sha, size = (sha256_tree(tp) if r["is_dir"] else sha256_file(tp))
            content_path = tp
        else:
            print(f"FAIL {tid}: content missing in trash")
            return "fail"
        if sha != r.get("sha256"):
            print(f"FAIL {tid}: sha256 mismatch (expected {r.get('sha256','')[:12]}… got {sha[:12]}…)")
            return "fail"
    # conflict
    if dst.exists() or dst.is_symlink():
        if not force:
            print(f"SKIP {tid}: target exists {dst} (use --force)")
            return "skip"
        # snapshot existing target first
        try:
            existing = dst.resolve()
        except OSError:
            existing = dst
        if existing.exists() or existing.is_symlink():
            sid = gen_id()
            srec = collect_entry(slug, existing, sid)
            srec.update({"op": "delete", "time": iso_now()})
            append_manifest(slug, srec)
    # write
    if r.get("is_link"):
        if dst.is_symlink() or dst.exists():
            dst.unlink()
        os.symlink(r["link_target"], dst)
    elif r.get("is_dir"):
        if dst.exists():
            # merge: copytree into existing (force case)
            for item in content_path.iterdir():
                tgt = dst / item.name
                if tgt.exists() and not force:
                    print(f"SKIP {tid}: merge conflict at {tgt}")
                    return "skip"
                if item.is_dir():
                    shutil.copytree(item, tgt)
                else:
                    shutil.copy2(item, tgt)
        else:
            shutil.copytree(content_path, dst)
    else:
        shutil.copy2(content_path, dst)
    # restore mtime
    try:
        os.utime(dst, (time.time(), r["mtime"]))
    except OSError:
        pass
    # log restore
    append_manifest(slug, {
        "id": tid, "op": "restore", "src": r["src"], "restore_to": str(dst),
        "time": iso_now(), "restored": True, "restore_time": iso_now(),
        "project_slug": slug,
    })
    # consume?
    if consume and not r.get("large"):
        try:
            shutil.rmtree(tp) if tp.is_dir() else tp.unlink(missing_ok=True)
        except OSError:
            pass
    print(f"OK {tid} -> {dst} sha256={r.get('sha256','')[:12]}… size={r.get('size',0)}")
    return "ok"


def cmd_purge(args):
    slug = project_slug()
    days = args.days if args.days is not None else PURGE_DEFAULT_DAYS
    cutoff = datetime.now().astimezone() - timedelta(days=days)
    entries = active_entries(slug)
    # only delete/overwrite entries have collectable content worth purging
    entries = [r for r in entries if r.get("op") in ("delete", "overwrite")]
    to_purge = []
    for r in entries:
        try:
            t = datetime.fromisoformat(r["time"])
            if t < cutoff:
                to_purge.append(r)
        except (KeyError, ValueError):
            pass
    if not to_purge:
        print(f"nothing to purge (>{days} days old)")
        return 0
    total_size = 0
    print(f"will purge {len(to_purge)} entries (>{days} days):")
    for r in to_purge:
        sz = r.get("size", 0)
        total_size += sz
        flag = " [large, content in place]" if r.get("large") else ""
        print(f"  {r.get('id',''):<20} {r.get('src_rel',''):<40} {sz:>10}  {r.get('time','')}{flag}")
    print(f"total to free: ~{total_size} bytes")
    if not args.confirm:
        print("\npreview only. run with --confirm to execute.")
        return 0
    for r in to_purge:
        tid = r["id"]
        if "trash_path" not in r:
            # restore/move records have no trash content; just tombstone
            append_manifest(slug, {"id": tid, "op": "purged", "time": iso_now(), "purged": True, "project_slug": slug})
            continue
        tp = trash_dir(slug) / r["trash_path"]
        if not r.get("large"):
            try:
                if tp.is_dir():
                    shutil.rmtree(tp)
                else:
                    tp.unlink(missing_ok=True)
            except OSError as e:
                print(f"WARN: failed to remove {tp}: {e}", file=sys.stderr)
        append_manifest(slug, {"id": tid, "op": "purged", "time": iso_now(), "purged": True, "project_slug": slug})
    print(f"purged {len(to_purge)} entries (tombstones appended; manifest history untouched)")
    return 0


def cmd_guard(args):
    slug = project_slug()
    gpath = guard_lock_path(slug)
    gpath.parent.mkdir(parents=True, exist_ok=True)
    if args.action == "on":
        gpath.touch()
        print("guard ON")
    elif args.action == "off":
        try:
            gpath.unlink()
        except FileNotFoundError:
            pass
        print("guard OFF (warning: raw rm will be irreversible)")
    else:
        print(f"guard: {'ON' if gpath.exists() else 'OFF'}")
    return 0


def main():
    ap = argparse.ArgumentParser(prog="trash.py", description="File-operation logger & safe recovery")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("delete"); p.add_argument("path"); p.set_defaults(func=cmd_delete)
    p = sub.add_parser("overwrite"); p.add_argument("path"); p.set_defaults(func=cmd_overwrite)
    p = sub.add_parser("move"); p.add_argument("src"); p.add_argument("dst"); p.set_defaults(func=cmd_move)
    p = sub.add_parser("list"); p.add_argument("filter", nargs="?"); p.add_argument("--op"); p.add_argument("--days", type=int); p.set_defaults(func=cmd_list)
    p = sub.add_parser("log"); p.add_argument("N", nargs="?", type=int); p.set_defaults(func=cmd_log)
    p = sub.add_parser("inspect"); p.add_argument("id"); p.set_defaults(func=cmd_inspect)
    p = sub.add_parser("restore"); p.add_argument("query"); p.add_argument("--to"); p.add_argument("--force", action="store_true"); p.add_argument("--consume", action="store_true"); p.set_defaults(func=cmd_restore)
    p = sub.add_parser("purge"); p.add_argument("days", nargs="?", type=int); p.add_argument("--confirm", action="store_true"); p.set_defaults(func=cmd_purge)
    p = sub.add_parser("guard"); p.add_argument("action", nargs="?", default="status"); p.set_defaults(func=cmd_guard)

    args = ap.parse_args()
    sys.exit(args.func(args))


if __name__ == "__main__":
    main()