#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gzh_archive.py — WeChat Official Account (公众号) full-archive scraper (GongZhongHao skill).

Drives a real browser (Selenium + Chrome) to enumerate a 公众号's historical
articles, fetches each, converts HTML to clean Markdown with local images, and
saves to ~/WeChatArchives/<account>/ with resumable progress and dedup.

Subcommands:
    gzh_archive.py check
    gzh_archive.py enumerate <name-or-biz>
    gzh_archive.py fetch <biz> [--resume] [--retry-failed]
    gzh_archive.py refresh <biz>
    gzh_archive.py search <keyword>
    gzh_archive.py list

Requires: selenium, markdownify, readability-lxml, requests, beautifulsoup4, pyyaml
  pip install selenium webdriver-manager markdownify readability-lxml requests beautifulsoup4 pyyaml

Env:
    GZH_ARCHIVES_ROOT (default ~/WeChatArchives)
    GZH_USER_DATA_DIR (default ~/.opencode-gzh-profile)
    GZH_MIN_DELAY (default 3)  GZH_MAX_DELAY (default 7)
"""
import argparse
import hashlib
import json
import os
import random
import re
import shutil
import sys
import time
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse, parse_qsl, urlencode, quote

ARCHIVES_ROOT = Path(os.environ.get("GZH_ARCHIVES_ROOT", str(Path.home() / "WeChatArchives")))
USER_DATA_DIR = Path(os.environ.get("GZH_USER_DATA_DIR", str(Path.home() / ".opencode-gzh-profile")))
MIN_DELAY = float(os.environ.get("GZH_MIN_DELAY", "5"))
MAX_DELAY = float(os.environ.get("GZH_MAX_DELAY", "10"))
MANIFEST_NAME = "manifest.jsonl"
PROGRESS_NAME = "progress.json"


# ---------- deps bootstrap (like wang-ke pattern) ----------
def ensure_deps():
    deps = ["selenium", "markdownify", "readability", "requests", "bs4", "yaml"]
    missing = []
    for d in deps:
        try:
            __import__(d)
        except ImportError:
            missing.append(d)
    if missing:
        print(f"缺少依赖 {missing}，尝试安装...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", *missing])


# ---------- paths ----------
def account_dir(biz_or_name: str) -> Path:
    return ARCHIVES_ROOT / biz_or_name


def progress_path(biz_or_name: str) -> Path:
    return account_dir(biz_or_name) / PROGRESS_NAME


def manifest_path(biz_or_name: str) -> Path:
    return account_dir(biz_or_name) / MANIFEST_NAME


def articles_dir(biz_or_name: str) -> Path:
    return account_dir(biz_or_name) / "articles"


def images_dir(biz_or_name: str) -> Path:
    return account_dir(biz_or_name) / "images"


# ---------- io ----------
def iso_now() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def atomic_save(path: Path, data: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(path)


def append_manifest(biz: str, record: dict):
    mp = manifest_path(biz)
    mp.parent.mkdir(parents=True, exist_ok=True)
    with open(mp, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def load_progress(biz: str) -> dict:
    p = progress_path(biz)
    if p.exists():
        return json.loads(p.read_text(encoding="utf-8"))
    return {
        "biz": biz, "account_name": "", "crawled_urls": [], "crawled_hashes": [],
        "pending_urls": [], "last_url": "", "last_crawl": "",
        "last_article_date": "", "stats": {"total": 0, "success": 0, "failed": 0, "deleted": 0},
        "failed_urls": [],
    }


def save_progress(biz: str, prog: dict):
    prog["last_crawl"] = prog.get("last_crawl") or iso_now()
    atomic_save(progress_path(biz), prog)


# ---------- url normalize ----------
def normalize_url(url: str) -> str:
    p = urlparse(url)
    q = dict(parse_qsl(p.query))
    keep = {k: v for k, v in q.items() if k in ("__biz", "mid", "idx", "sn")}
    return f"{p.scheme}://{p.netloc}{p.path}?{urlencode(keep)}"


# ---------- slugify ----------
def slugify(title: str) -> str:
    s = re.sub(r"[^\w\u4e00-\u9fff\s-]", "", title).strip()
    s = re.sub(r"[\s-]+", "-", s)
    return s[:30] or "untitled"


# ---------- browser ----------
def create_driver(headless: bool = False):
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    try:
        from webdriver_manager.chrome import ChromeDriverManager
        has_wdm = True
    except ImportError:
        has_wdm = False
    options = Options()
    if headless:
        options.add_argument("--headless=new")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    options.add_argument("--window-size=1280,900")
    options.add_argument(f"--user-data-dir={USER_DATA_DIR}")
    options.set_capability("goog:loggingPrefs", {"performance": "ALL"})
    if has_wdm:
        driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
    else:
        driver = webdriver.Chrome(options=options)
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": "Object.defineProperty(navigator,'webdriver',{get:()=>undefined})"
    })
    return driver


# ---------- enumeration: album API (primary, no login needed) ----------
def fetch_album_articles(biz: str, album_id: str, cookies: dict | None = None) -> list[dict]:
    """Fetch all articles in a WeChat album via appmsgalbum JSON API.

    API: mp.weixin.qq.com/mp/appmsgalbum?action=getalbum&album_id=<id>&f=json
    Returns list of {url, title, publish_time}. No login needed for getalbum.
    """
    import requests
    arts = []
    for begin in range(0, 1000, 100):
        url = f"https://mp.weixin.qq.com/mp/appmsgalbum?__biz={biz}&action=getalbum&album_id={album_id}&count=100&begin={begin}&f=json"
        try:
            r = requests.get(url, headers={"User-Agent": "Mozilla/5.0", "Referer": "https://mp.weixin.qq.com/"},
                             cookies=cookies or {}, timeout=15)
            d = r.json()
            if d.get("base_resp", {}).get("ret", 0) != 0 and d.get("ret", 0) != 0:
                print(f"  album API ret={d.get('ret')} {d.get('errmsg','')}")
                break
            lst = d.get("getalbum_resp", {}).get("article_list", [])
            if not lst:
                break
            for a in lst:
                u = (a.get("url") or "").replace("&amp;", "&")
                arts.append({"url": u, "title": a.get("title", ""), "publish_time": ""})
            print(f"  album begin={begin}: {len(lst)} 篇")
            if len(lst) < 100:
                break
            time.sleep(random.uniform(1, 2))
        except Exception as e:
            print(f"  album API error: {e}")
            break
    # dedup by url
    seen = set()
    out = []
    for a in arts:
        nu = normalize_url(a["url"])
        if nu in seen:
            continue
        seen.add(nu)
        out.append(a)
    return out


def extract_album_ids_from_article(driver) -> set[str]:
    """From a WeChat article page, extract all album_id values (合辑)."""
    src = driver.page_source
    ids = set(re.findall(r"album_id\s*[:=]\s*[\"']?(\d+)", src))
    return ids


def extract_prev_next_urls(driver) -> tuple[list[str], list[str]]:
    """From a WeChat article page, extract prev/next article URLs (含 __biz/mid/idx/sn).

    微信文章页 JS 里 URL 形如 __biz=...\\x26amp;mid=...\\x26amp;idx=1\\x26amp;sn=...
    开头可能没有 http://，需构造完整 URL。
    """
    src = driver.page_source
    urls = set()
    # match __biz=...mid=...idx=...sn=... patterns (with \x26amp; or & separators)
    for m in re.finditer(r'__biz=([A-Za-z0-9+/=]+)\\x26amp;mid=(\d+)\\x26amp;idx=(\d+)\\x26amp;sn=([a-f0-9]+)', src):
        biz, mid, idx, sn = m.groups()
        urls.add(f"https://mp.weixin.qq.com/s?__biz={biz}&mid={mid}&idx={idx}&sn={sn}&scene=124")
    # also match &amp; variant
    for m in re.finditer(r'__biz=([A-Za-z0-9+/=]+)&amp;mid=(\d+)&amp;idx=(\d+)&amp;sn=([a-f0-9]+)', src):
        biz, mid, idx, sn = m.groups()
        urls.add(f"https://mp.weixin.qq.com/s?__biz={biz}&mid={mid}&idx={idx}&sn={sn}&scene=124")
    # also match plain & variant
    for m in re.finditer(r'__biz=([A-Za-z0-9+/=]+)&mid=(\d+)&idx=(\d+)&sn=([a-f0-9]+)', src):
        biz, mid, idx, sn = m.groups()
        urls.add(f"https://mp.weixin.qq.com/s?__biz={biz}&mid={mid}&idx={idx}&sn={sn}&scene=124")
    return list(urls)


# ---------- enumeration: snowball via prev/next (covers articles not in albums) ----------
def snowball_articles(driver, start_url: str, max_visits: int = 500) -> list[dict]:
    """Snowball from a start article: extract prev/next article URLs from each
    page, recursively visit unvisited ones, collect all articles.

    微信文章页底部 '上一篇/下一篇' 导航含完整 __biz/mid/idx/sn URL，递归遍历可覆盖全部文章。
    """
    visited = set()
    queue = [start_url]
    articles = []
    print(f"滚雪球枚举: 起始 {start_url[:80]}")
    count = 0
    while queue and count < max_visits:
        url = queue.pop(0)
        nu = normalize_url(url)
        if nu in visited:
            continue
        visited.add(nu)
        count += 1
        driver.get(url)
        time.sleep(random.uniform(MIN_DELAY, MAX_DELAY))
        title = driver.title[:60] if driver.title else ""
        if "Verify" in (driver.title or "") or "环境异常" in driver.page_source[:1500]:
            print(f"  [{count}] 拦截，跳过: {url[:60]}")
            continue
        if "该内容已被发布者删除" in driver.page_source[:5000] or "此内容因违规" in driver.page_source[:5000]:
            print(f"  [{count}] 已删: {title}")
            continue
        articles.append({"url": url, "title": title, "publish_time": ""})
        prev_next = extract_prev_next_urls(driver)
        new = 0
        for u in prev_next:
            nu2 = normalize_url(u)
            if nu2 not in visited:
                queue.append(u)
                new += 1
        print(f"  [{count}] {title} (新邻接 {new})")
    print(f"滚雪球完成: 访问 {count} 篇，收集 {len(articles)} 篇")
    return articles


def snowball_fetch(driver, biz: str, prog: dict, start_urls: list[str], max_visits: int = 500) -> int:
    """Snowball + fetch in one pass: visit each article once, extract content AND
    prev/next URLs together, save Markdown immediately. Avoids double-visiting.

    返回成功抓取数。比先枚举再抓取更高效（不重复访问同一文章）。
    """
    ad = articles_dir(biz)
    idir = images_dir(biz)
    crawled = {normalize_url(u) for u in prog["crawled_urls"]}
    hashes = set(prog["crawled_hashes"])
    visited = set()
    queue = list(start_urls)
    count = 0
    success = 0
    print(f"滚雪球抓取: 起始 {len(start_urls)} 篇")
    while queue and count < max_visits:
        url = queue.pop(0)
        nu = normalize_url(url)
        if nu in visited or nu in crawled:
            continue
        visited.add(nu)
        count += 1
        print(f"[{count}] {url[:70]}")
        driver.get(url)
        time.sleep(random.uniform(MIN_DELAY, MAX_DELAY))
        src = driver.page_source
        # detect blocks
        title_full = driver.title or ""
        if "Verify" in title_full or "环境异常" in src[:1500] or "访问过于频繁" in src[:1500]:
            print(f"  ⛔ 风控/验证码，停止。进度已保存，用 resume 继续。")
            prog["failed_urls"].append({"url": url, "reason": "blocked", "time": iso_now()})
            save_progress(biz, prog)
            break
        if "该内容已被发布者删除" in src[:5000] or "此内容因违规" in src[:5000]:
            print(f"  ✗ 已删")
            append_manifest(biz, {"url": url, "title": "", "status": "deleted", "time": iso_now()})
            prog["stats"]["deleted"] += 1
            prog["crawled_urls"].append(url)
            save_progress(biz, prog)
            continue
        # extract prev/next BEFORE content extraction (page may change)
        prev_next = extract_prev_next_urls(driver)
        # extract content
        meta = extract_article_fields(src, url)
        meta["account"] = prog.get("account_name", biz)
        clean = preprocess_html(meta["content"])
        md = to_markdown(clean, idir, url)
        sha = hashlib.sha256(md.encode()).hexdigest()
        if sha in hashes:
            print(f"  = 同文重复，跳过")
            prog["crawled_urls"].append(url)
            save_progress(biz, prog)
            continue
        hashes.add(sha)
        date_str = parse_date(meta["publish_time"])
        base = f"{date_str}-{slugify(meta['title'])}"
        p = unique_path(ad, base)
        p.write_text(build_front_matter(meta, sha) + md, encoding="utf-8")
        append_manifest(biz, {"url": url, "title": meta["title"], "publish_time": meta["publish_time"],
                              "local_path": str(p.relative_to(account_dir(biz))), "sha256": sha,
                              "status": "ok", "crawled_at": iso_now()})
        prog["crawled_urls"].append(url)
        prog["crawled_hashes"].append(sha)
        prog["last_url"] = url
        prog["last_article_date"] = meta["publish_time"]
        prog["stats"]["total"] += 1
        prog["stats"]["success"] += 1
        save_progress(biz, prog)
        print(f"  ✓ {p.name} ({len(md)} 字符, 邻接 {len(prev_next)})")
        # enqueue unvisited neighbors
        new = 0
        for u in prev_next:
            nu2 = normalize_url(u)
            if nu2 not in visited and nu2 not in crawled:
                queue.append(u)
                new += 1
        if new:
            print(f"    → 加入 {new} 篇邻接")
    print(f"滚雪球抓取完成: 访问 {count} 篇，成功 {success}（实际写入 {prog['stats']['success']}）")
    return success


# ---------- enumeration (legacy, kept as fallback) ----------
def extract_biz_from_article(driver, sogou_link: str) -> tuple[str, str] | None:
    """Open a sogou article link (follows redirect to mp.weixin.qq.com),
    extract __biz from the article page HTML. Returns (biz, article_url)."""
    d = driver
    handles = d.window_handles
    d.execute_script("window.open(arguments[0])", sogou_link)
    time.sleep(5)
    d.switch_to.window(d.window_handles[-1])
    try:
        cur = d.current_url
        src = d.page_source
        m = re.search(r"__biz=([A-Za-z0-9+/=]+)", src) or re.search(r"__biz\s*[:=]\s*['\"]*(M[A-Za-z0-9+/=]+)", src)
        biz = m.group(1) if m else ""
        return (biz, cur)
    finally:
        d.close()
        d.switch_to.window(handles[0])


def search_account_by_articles(driver, name: str, max_pages: int = 10) -> dict | None:
    """Search 搜一搜 文章 (type=2) for articles by account `name`, filter items
    whose account name starts with `name`, extract biz from first article page.

    搜狗账号搜索(type=1) 常返回"暂无认证账号"，文章搜索(type=2)更可靠：
    按 div.s-p 文本过滤归属账号，从文章页 HTML 提取 __biz。
    """
    from selenium.webdriver.common.by import By
    biz = ""
    article_urls = []
    print(f"按文章搜索定位公众号: {name}")
    for page in range(1, max_pages + 1):
        url = f"https://weixin.sogou.com/weixin?type=2&query={quote(name)}&ie=utf8&page={page}"
        print(f"  搜一搜文章页 {page}: {url}")
        driver.get(url)
        # poll for results or captcha (non-blocking)
        deadline = time.time() + 60
        items = []
        while time.time() < deadline:
            try:
                src = driver.page_source[:3000]
                if "antispider" in src or "请输入验证码" in src or "用户你好" in src:
                    print("  检测到验证码页，请在浏览器中手动完成（脚本继续轮询）...")
                    time.sleep(8)
                    continue
                items = driver.find_elements(By.CSS_SELECTOR, "ul.news-list li")
                if items:
                    break
            except Exception:
                pass
            time.sleep(3)
        if not items:
            print(f"  第 {page} 页无结果，停止翻页")
            break
        matched = 0
        for it in items:
            try:
                sp = it.find_elements(By.CSS_SELECTOR, "div.s-p")
                acct_text = sp[0].text if sp else ""
                # filter by account name (div.s-p 文本形如 "CycleUser2026-3-29")
                if not acct_text.startswith(name):
                    continue
                matched += 1
                a = it.find_element(By.CSS_SELECTOR, "a[href*='/link?url=']")
                href = a.get_attribute("href") or ""
                if href.startswith("/"):
                    href = "https://weixin.sogou.com" + href
                title_el = it.find_elements(By.CSS_SELECTOR, "h4, .tit, a")
                title = title_el[0].text if title_el else ""
                article_urls.append({"url": href, "title": title, "acct": acct_text})
            except Exception:
                continue
        print(f"  第 {page} 页: {len(items)} 条结果，归属 {name} 的 {matched} 条")
        if len(items) < 10:
            break
        time.sleep(random.uniform(2, 4))
    if not article_urls:
        print(f"  未在搜狗文章搜索中找到归属 {name} 的文章")
        return None
    # extract biz from first article page
    print(f"  从首篇文章页提取 biz...")
    biz, art_url = extract_biz_from_article(driver, article_urls[0]["url"]) or ("", "")
    if not biz:
        print("  未能从文章页提取 biz（可能被微信 Verify 拦截）")
    return {"name": name, "biz": biz, "article_urls": article_urls}


def enumerate_articles(driver, biz: str, max_scrolls: int = 500) -> list[dict]:
    """Scroll the history page, collect article urls+titles+times.

    Note: mp.weixin.qq.com/mp/profile_ext 常被 Verify 拦截（需在微信客户端内打开）。
    若被拦，调用方应回退到搜狗文章搜索结果。这里仍尝试，被拦时返回 []。
    """
    from selenium.webdriver.common.by import By
    url = f"https://mp.weixin.qq.com/mp/profile_ext?action=home&__biz={biz}&scene=124#wechat_redirect"
    print(f"尝试历史消息页: {url}")
    driver.get(url)
    time.sleep(5)
    # detect Verify wall
    if "Verify" in (driver.title or "") or "环境异常" in driver.page_source[:2000]:
        print("  历史消息页被微信 Verify 拦截（需微信客户端内打开），跳过此路径")
        return []
    articles = []
    last_height = 0
    for i in range(max_scrolls):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(random.uniform(2, 4))
        cards = driver.find_elements(By.CSS_SELECTOR, ".weui_msg_card, .wx_news_card, .card")
        for c in cards:
            try:
                a = c.find_elements(By.TAG_NAME, "a")
                href = a[0].get_attribute("href") if a else c.get_attribute("data-url")
                title_el = c.find_elements(By.CSS_SELECTOR, ".weui_msg_card_title, .title, h2")
                time_el = c.find_elements(By.CSS_SELECTOR, ".weui_msg_card_extra, .time, .post-date")
                if href:
                    articles.append({
                        "url": href,
                        "title": title_el[0].text if title_el else "",
                        "publish_time": time_el[0].text if time_el else "",
                    })
            except Exception:
                continue
        new_h = driver.execute_script("return document.body.scrollHeight")
        if new_h == last_height:
            print(f"  到底，滚动 {i+1} 次后停止")
            break
        last_height = new_h
    seen = set()
    out = []
    for a in articles:
        nu = normalize_url(a["url"])
        if nu in seen:
            continue
        seen.add(nu)
        a["url"] = a["url"].replace("&amp;", "&")
        out.append(a)
    print(f"  历史页枚举得 {len(out)} 篇文章")
    return out


# ---------- fetch + convert ----------
def fetch_article_html(driver, url: str) -> str | None:
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    try:
        driver.get(url)
    except Exception as e:
        # timeout or connection error — treat as transient, return None to skip
        if "timeout" in str(e).lower() or "ERR_INTERNET" in str(e) or "net::" in str(e):
            print(f"  ✗ 页面加载超时/断网，跳过")
            return None
        raise
    try:
        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#js_content, #page-content")))
    except Exception:
        body = driver.page_source
        if "环境异常" in body or "访问过于频繁" in body or "请完成验证" in body:
            return "BLOCKED"
        if "该内容已被发布者删除" in body or "此内容因违规" in body:
            return "DELETED"
        return None
    return driver.page_source


def extract_article_fields(html: str, url: str) -> dict:
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, "html.parser")
    title_el = soup.select_one("#activity-name, .rich_media_title")
    author_el = soup.select_one("#js_name, .rich_media_meta_text")
    time_el = soup.select_one("#publish_time, .rich_media_meta_text em")
    content_el = soup.select_one("#js_content, #page-content")
    title = title_el.get_text(strip=True) if title_el else ""
    author = author_el.get_text(strip=True) if author_el else ""
    publish = time_el.get_text(strip=True) if time_el else ""
    content = str(content_el) if content_el else ""
    return {"title": title, "author": author, "publish_time": publish, "content": content, "url": url}


NOISE_SELECTORS = [
    ".qr_code_pc", "[data-src*='qrcode']", ".weui-msg__tips", ".rich_media_tool",
    "#js_pc_qr_code_img", ".reward_area", "#js_reward_area", ".recommend_area",
    "script", "style", "iframe", "#js_tags, .tags",
]


def preprocess_html(html: str) -> str:
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, "html.parser")
    for sel in NOISE_SELECTORS:
        for el in soup.select(sel):
            el.decompose()
    return str(soup)


def download_image(url: str, img_dir: Path, referer: str = "https://mp.weixin.qq.com") -> Path | None:
    import requests
    try:
        r = requests.get(url, headers={"Referer": referer, "User-Agent": "Mozilla/5.0"}, timeout=15)
        if r.status_code != 200 or not r.content:
            return None
        ct = r.headers.get("Content-Type", "")
        ext = ".jpg"
        if "png" in ct: ext = ".png"
        elif "gif" in ct: ext = ".gif"
        elif "webp" in ct: ext = ".webp"
        h = hashlib.sha1(r.content).hexdigest()[:16]
        p = img_dir / f"{h}{ext}"
        if not p.exists():
            p.write_bytes(r.content)
        return p
    except Exception:
        return None


def fix_images(soup, img_dir: Path, referer: str):
    for img in soup.find_all("img"):
        src = img.get("data-src") or img.get("src") or ""
        if not src or src.startswith("data:"):
            continue
        local = download_image(src, img_dir, referer)
        if local:
            img["src"] = f"../images/{local.name}"
        else:
            img["src"] = src
            img.insert_after(soup.new_string(f"<!-- remote: {src} -->"))
        if img.get("data-src"):
            del img["data-src"]
    return soup


def to_markdown(content_html: str, img_dir: Path, referer: str) -> str:
    from bs4 import BeautifulSoup
    from markdownify import markdownify as md
    soup = BeautifulSoup(content_html, "html.parser")
    soup = fix_images(soup, img_dir, referer)
    html = str(soup)
    out = md(html, heading_style="ATX", strip=["script", "style", "iframe"], bullets="-")
    out = re.sub(r"\n{3,}", "\n\n", out)
    out = re.sub(r"</?(?:div|span|section|article)[^>]*>", "", out)
    out = re.sub(r"!\[\]\(", "![image](", out)
    out = "\n".join(l.rstrip() for l in out.splitlines()).strip() + "\n"
    return out


def build_front_matter(meta: dict, sha: str) -> str:
    import yaml
    fm = {
        "title": meta.get("title", ""),
        "author": meta.get("author", ""),
        "account": meta.get("account", ""),
        "publish_time": meta.get("publish_time", ""),
        "source_url": meta.get("url", ""),
        "crawled_at": iso_now(),
        "sha256": sha,
    }
    return "---\n" + yaml.safe_dump(fm, allow_unicode=True, sort_keys=False).strip() + "\n---\n\n"


def parse_date(d: str) -> str:
    """Return YYYYMMDD for file naming; fallback to today."""
    for fmt in ("%Y-%m-%d %H:%M", "%Y-%m-%d", "%Y年%m月%d日"):
        try:
            return datetime.strptime(d.strip(), fmt).strftime("%Y%m%d")
        except (ValueError, TypeError):
            continue
    return datetime.now().strftime("%Y%m%d")


def unique_path(d: Path, base: str) -> Path:
    p = d / f"{base}.md"
    if not p.exists():
        return p
    i = 2
    while (d / f"{base}-v{i}.md").exists():
        i += 1
    return d / f"{base}-v{i}.md"


# ---------- commands ----------
def cmd_check(args):
    ensure_deps()
    print("检查依赖与浏览器...")
    try:
        import selenium, markdownify, readability, requests, bs4, yaml
        print("  ✅ python 依赖齐全")
    except ImportError as e:
        print(f"  ❌ 缺少: {e}")
    print(f"  存档根: {ARCHIVES_ROOT}")
    print(f"  user-data-dir: {USER_DATA_DIR} ({'已存在' if USER_DATA_DIR.exists() else '首次运行需登录'})")
    print("环境检查完成。首次运行浏览器会弹出，需手动扫码登录微信。")


def cmd_run(args):
    """Full flow: enumerate + fetch.

    Strategy (by reliability):
    1. 文章 URL 直接给定 (含 mp.weixin.qq.com) → 滚雪球 (prev/next 递归) + 合辑 API
    2. biz-id 直接给定 → 合辑 API (需先从任一文章页取 album_id) + 滚雪球
    3. 名称 → 搜狗文章搜索定位 biz → 滚雪球
    微信历史消息页 profile_ext 常被 Verify 拦截，不再依赖。
    """
    ensure_deps()
    target = args.target
    driver = create_driver()
    biz = ""
    start_url = ""
    # case 1: target is a WeChat article URL
    if "mp.weixin.qq.com" in target:
        start_url = target
        driver.get(target)
        time.sleep(5)
        m = re.search(r"__biz=([A-Za-z0-9+/=]+)", driver.page_source)
        biz = m.group(1) if m else ""
        acct_name = ""
        if not biz:
            print("无法从文章页提取 biz"); return 1
    # case 2: target is biz-id
    elif re.match(r"M[A-Za-z0-9+/=]+$", target) or "__biz=" in target:
        biz = re.search(r"__biz=([^&]+)", target)
        biz = biz.group(1) if biz else target
        start_url = ""
    # case 3: search by name
    else:
        acct = search_account_by_articles(driver, target, max_pages=10)
        if not acct:
            print(f"未找到公众号: {target}")
            return 1
        biz = acct.get("biz") or ""
        start_url = acct["article_urls"][0]["url"] if acct.get("article_urls") else ""
        acct_name = acct.get("name", target)
    d = account_dir(biz or target)
    d.mkdir(parents=True, exist_ok=True)
    articles_dir(biz or target).mkdir(exist_ok=True)
    images_dir(biz or target).mkdir(exist_ok=True)
    key = biz or target
    prog = load_progress(key)
    prog["account_name"] = prog.get("account_name") or (acct.get("name", target) if "acct" in dir() else target)
    print(f"账号: {prog['account_name']} biz={biz or '(未取得)'}")
    # enumerate: snowball+fetch (primary, one-pass) + album API
    start_urls = []
    album_ids = set()
    if start_url:
        driver.get(start_url); time.sleep(5)
        album_ids = extract_album_ids_from_article(driver)
        print(f"发现合辑: {album_ids or '(无合辑)'}")
        start_urls.append(start_url)
    # snowball+fetch from start article (covers articles via prev/next chain)
    if start_urls:
        snowball_fetch(driver, key, prog, start_urls, max_visits=500)
    # fetch album articles via API, then grab those not yet crawled
    album_arts = []
    for aid in album_ids:
        print(f"抓取合辑 {aid} 文章列表...")
        al = fetch_album_articles(biz, aid)
        album_arts.extend(al)
    # fetch album articles not yet in crawled set
    prog = load_progress(key)
    remaining = [a for a in album_arts if normalize_url(a["url"]) not in {normalize_url(u) for u in prog["crawled_urls"]}]
    if remaining:
        print(f"合辑新增待抓: {len(remaining)} 篇")
        fetch_loop(driver, key, prog, remaining, resume=True, retry_failed=False)
    prog = load_progress(key)
    if prog["stats"]["success"] == 0 and biz:
        arts = enumerate_articles(driver, biz)
        if arts:
            fetch_loop(driver, key, prog, arts, args.resume, retry_failed=False)
    prog = load_progress(key)
    s = prog["stats"]
    print(f"\n完成：成功 {s['success']}，删除 {s['deleted']}，失败 {s['failed']}，存档 {account_dir(key)}")
    generate_index(key, prog)
    return 0


def fetch_loop(driver, biz, prog, arts, resume, retry_failed):
    ad = articles_dir(biz)
    idir = images_dir(biz)
    crawled = {normalize_url(u) for u in prog["crawled_urls"]}
    hashes = set(prog["crawled_hashes"])
    if resume:
        print(f"断点续抓: 已抓 {len(crawled)} 篇")
    block_count = 0
    for a in arts:
        url = a["url"]
        nu = normalize_url(url)
        if nu in crawled:
            continue
        print(f"抓取: {a.get('title','')[:40]} → {url[:60]}...")
        html = fetch_article_html(driver, url)
        if html == "BLOCKED":
            block_count += 1
            print(f"  ⛔ 风控/验证码，停止。已完成进度已保存，用 resume 继续。")
            prog["failed_urls"].append({"url": url, "reason": "blocked", "time": iso_now()})
            save_progress(biz, prog)
            break
        if html == "DELETED":
            print("  ✗ 已删除")
            append_manifest(biz, {"url": url, "title": a.get("title", ""), "status": "deleted", "time": iso_now()})
            prog["stats"]["deleted"] += 1
            prog["crawled_urls"].append(url)
            save_progress(biz, prog)
            continue
        if not html:
            print("  ✗ 抓取失败（空内容）")
            prog["failed_urls"].append({"url": url, "reason": "empty", "time": iso_now()})
            prog["stats"]["failed"] += 1
            save_progress(biz, prog)
            continue
        meta = extract_article_fields(html, url)
        meta["account"] = prog["account_name"]
        clean = preprocess_html(meta["content"])
        md = to_markdown(clean, idir, url)
        sha = hashlib.sha256(md.encode()).hexdigest()
        if sha in hashes:
            print("  = 同文重复，跳过")
            append_manifest(biz, {"url": url, "title": meta["title"], "sha256": sha, "status": "duplicate", "time": iso_now()})
            prog["crawled_urls"].append(url)
            save_progress(biz, prog)
            continue
        hashes.add(sha)
        date_str = parse_date(meta["publish_time"])
        base = f"{date_str}-{slugify(meta['title'])}"
        p = unique_path(ad, base)
        p.write_text(build_front_matter(meta, sha) + md, encoding="utf-8")
        append_manifest(biz, {"url": url, "title": meta["title"], "publish_time": meta["publish_time"],
                              "local_path": str(p.relative_to(account_dir(biz))), "sha256": sha,
                              "status": "ok", "crawled_at": iso_now()})
        prog["crawled_urls"].append(url)
        prog["crawled_hashes"].append(sha)
        prog["last_url"] = url
        prog["last_article_date"] = meta["publish_time"]
        prog["stats"]["total"] += 1
        prog["stats"]["success"] += 1
        save_progress(biz, prog)
        print(f"  ✓ {p.name} ({len(md)} 字符)")
        time.sleep(random.uniform(MIN_DELAY, MAX_DELAY))
    prog["last_crawl"] = iso_now()
    save_progress(biz, prog)
    s = prog["stats"]
    print(f"\n完成：成功 {s['success']}，删除 {s['deleted']}，失败 {s['failed']}，存档 {account_dir(biz)}")
    generate_index(biz, prog)
    return 0


def generate_index(biz: str, prog: dict):
    mp = manifest_path(biz)
    if not mp.exists():
        return
    rows = []
    for line in mp.read_text(encoding="utf-8").splitlines():
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    ok = [r for r in rows if r.get("status") == "ok"]
    ok.sort(key=lambda r: r.get("publish_time", ""), reverse=True)
    idx = account_dir(biz) / "index.md"
    lines = [f"# {prog['account_name']} 文章索引", "", f"共 {len(ok)} 篇，抓取于 {prog.get('last_crawl','')}。", "",
             "| 日期 | 标题 | 本地 |", "|------|------|------|"]
    for r in ok:
        pt = r.get("publish_time", "")
        lines.append(f"| {pt} | {r.get('title','')} | {r.get('local_path','')} |")
    idx.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"索引: {idx}")


def cmd_refresh(args):
    ensure_deps()
    biz = args.target
    prog = load_progress(biz)
    if not prog.get("last_crawl"):
        print("无历史记录，请先完整抓取一次")
        return 1
    driver = create_driver()
    arts = enumerate_articles(driver, biz)
    last = prog["last_crawl"]
    new = [a for a in arts if a.get("publish_time", "") > last]
    print(f"上次 {last}，新增 {len(new)} 篇")
    return fetch_loop(driver, biz, prog, new, resume=True, retry_failed=False)


def cmd_search(args):
    import subprocess
    keyword = args.keyword
    hits = 0
    for acct_dir in ARCHIVES_ROOT.iterdir():
        if not acct_dir.is_dir():
            continue
        ad = articles_dir(acct_dir.name)
        if not ad.exists():
            continue
        try:
            r = subprocess.run(["rg", "-n", "--no-heading", keyword, str(ad)],
                               capture_output=True, text=True, timeout=30)
            if r.stdout:
                for line in r.stdout.strip().splitlines()[:50]:
                    print(line)
                    hits += 1
        except FileNotFoundError:
            print("需安装 ripgrep (rg) 用于检索")
            return 1
    print(f"\n命中 {hits} 处")
    return 0


def cmd_list(args):
    if not ARCHIVES_ROOT.exists():
        print("(无存档)")
        return 0
    for d in sorted(ARCHIVES_ROOT.iterdir()):
        if not d.is_dir():
            continue
        prog = load_progress(d.name)
        ad = articles_dir(d.name)
        n = len(list(ad.glob("*.md"))) if ad.exists() else 0
        print(f"{d.name}\t{n} 篇\tlast_crawl={prog.get('last_crawl','')}")


def main():
    ap = argparse.ArgumentParser(prog="gzh_archive.py", description="公众号文章存档")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("check").set_defaults(func=cmd_check)
    p = sub.add_parser("run"); p.add_argument("target"); p.add_argument("--resume", action="store_true"); p.set_defaults(func=cmd_run)
    p = sub.add_parser("fetch"); p.add_argument("target"); p.add_argument("--resume", action="store_true"); p.add_argument("--retry-failed", action="store_true"); p.set_defaults(func=cmd_run)
    p = sub.add_parser("refresh"); p.add_argument("target"); p.set_defaults(func=cmd_refresh)
    p = sub.add_parser("search"); p.add_argument("keyword"); p.set_defaults(func=cmd_search)
    p = sub.add_parser("list").set_defaults(func=cmd_list)
    args = ap.parse_args()
    sys.exit(args.func(args) or 0)


if __name__ == "__main__":
    main()