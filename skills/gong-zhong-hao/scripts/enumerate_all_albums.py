#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""enumerate_all_albums.py — 滚动加载每个合辑页，提取全部文章链接，存 CSV+JSON。"""
import csv, json, re, time, os
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# 账号 biz 与合辑 id 请按需填写，或用环境变量提供，避免在仓库里硬编码具体账号
BIZ = os.environ.get("GZH_BIZ", "YOUR_BIZ_ID")
ARCHIVE_DIR = Path.home() / "WeChatArchives" / BIZ
ALBUMS = {
    # "合辑id": "合辑名称",
    "ALBUM_ID_1": "合辑1",
    "ALBUM_ID_2": "合辑2",
}
OUT_JSON = ARCHIVE_DIR / "all_articles.json"
OUT_CSV = ARCHIVE_DIR / "all_articles.csv"
MAX_SCROLL = 120
SCROLL_WAIT = 3.5


def make_driver():
    opts = Options()
    opts.add_argument("--disable-blink-features=AutomationControlled")
    opts.add_experimental_option("excludeSwitches", ["enable-automation"])
    opts.add_argument("--user-data-dir=/tmp/opencode/gzh-fresh-profile")
    opts.add_argument("--window-size=1280,900")
    d = webdriver.Chrome(options=opts)
    d.set_page_load_timeout(30)
    return d


def scroll_album(driver, biz, album_id, album_name):
    """Open album page, scroll to trigger lazy load, extract all article links+titles."""
    url = f"https://mp.weixin.qq.com/mp/appmsgalbum?__biz={biz}&action=getalbum&album_id={album_id}"
    print(f"\n=== #{album_name} ({album_id}) ===")
    driver.get(url)
    time.sleep(6)
    seen = {}  # url -> title
    prev = 0
    stale = 0
    for i in range(MAX_SCROLL):
        h = driver.execute_script("return document.body.scrollHeight")
        # scroll to bottom
        driver.execute_script(f"window.scrollTo(0, {h})")
        time.sleep(SCROLL_WAIT)
        # wiggle: scroll up a bit then down again to trigger IntersectionObserver
        driver.execute_script(f"window.scrollTo(0, {h-300})")
        time.sleep(0.5)
        driver.execute_script(f"window.scrollTo(0, {h})")
        time.sleep(1)
        src = driver.page_source
        links = re.findall(r'data-link="(https?://mp\.weixin\.qq\.com/s\?[^"]+)"', src)
        titles = re.findall(r'data-title="([^"]+)"', src)
        for l, t in zip(links, titles):
            l = l.replace("&amp;", "&")
            seen[l] = t
        if len(seen) != prev:
            print(f"  scroll {i}: {len(seen)} 篇")
            prev = len(seen)
            stale = 0
        else:
            stale += 1
        # stop if no new articles for 15 consecutive scrolls
        if stale > 15:
            print(f"  scroll {i}: 无新增，停止 (stale={stale})")
            break
    print(f"  最终: {len(seen)} 篇")
    return [{"url": u, "title": t, "album": album_name, "album_id": album_id} for u, t in seen.items()]


def main():
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    driver = make_driver()
    all_articles = []
    for aid, nm in ALBUMS.items():
        arts = scroll_album(driver, BIZ, aid, nm)
        all_articles.extend(arts)
    driver.quit()
    # dedup by url
    seen_urls = set()
    dedup = []
    for a in all_articles:
        if a["url"] in seen_urls:
            continue
        seen_urls.add(a["url"])
        dedup.append(a)
    # extract mid for sorting
    for a in dedup:
        m = re.search(r"mid=(\d+)", a["url"])
        a["mid"] = int(m.group(1)) if m else 0
    dedup.sort(key=lambda x: x["mid"])
    # save JSON
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(dedup, f, ensure_ascii=False, indent=2)
    # save CSV
    with open(OUT_CSV, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["mid", "title", "album", "album_id", "url"])
        w.writeheader()
        w.writerows(dedup)
    print(f"\n=== 汇总 ===")
    print(f"总计 {len(dedup)} 篇文章（去重后）")
    print(f"JSON: {OUT_JSON}")
    print(f"CSV:  {OUT_CSV}")
    # show per-album count
    from collections import Counter
    cnt = Counter(a["album"] for a in dedup)
    for nm, c in cnt.items():
        print(f"  #{nm}: {c} 篇")


if __name__ == "__main__":
    main()