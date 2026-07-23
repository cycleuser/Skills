#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
browser_keeper.py — 网课浏览器直接控制脚本
用 Selenium 直接控制浏览器，在网页层面模拟鼠标移动，防止视频暂停。
不需要油猴插件，不需要 pyautogui。

用法:
  python3 browser_keeper.py --url "https://mooc1.chaoxing.com/..."
  python3 browser_keeper.py --url "https://..." --interval 10
  python3 browser_keeper.py --url "https://..." --headless  # 无头模式（不推荐，部分平台检测）

依赖:
  pip install selenium
  # 还需要浏览器驱动：
  # Chrome: pip install webdriver-manager  (自动管理 chromedriver)
  # 或手动下载 chromedriver 放到 PATH

停止:
  Ctrl+C
"""
import argparse
import signal
import sys
import time

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.action_chains import ActionChains
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
except ImportError:
    print("缺少 selenium，正在安装...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "selenium"])
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.action_chains import ActionChains

try:
    from webdriver_manager.chrome import ChromeDriverManager
    HAS_WDM = True
except ImportError:
    HAS_WDM = False

running = True


def signal_handler(sig, frame):
    global running
    running = False
    print("\n收到停止信号，正在退出...")


signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)


def create_driver(headless=False):
    """创建 Chrome 浏览器实例"""
    options = webdriver.ChromeOptions()
    if headless:
        options.add_argument("--headless=new")
    # 伪装成正常用户，避免被检测
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    options.add_argument("--window-size=1280,800")
    options.add_argument("--mute-audio")  # 可选：静音播放

    if HAS_WDM:
        driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
    else:
        driver = webdriver.Chrome(options=options)

    # 进一步隐藏 selenium 痕迹
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    })
    return driver


def keep_alive(driver, interval, duration):
    """定时模拟鼠标移动，保持视频播放"""
    start = time.time()
    count = 0

    print(f"浏览器保活启动 | 间隔={interval}s | 时长={duration or '无限'}s")
    print("停止方式: Ctrl+C")
    print("-" * 50)

    while running:
        try:
            # 查找 video 元素
            videos = driver.find_elements(By.TAG_NAME, "video")
            if videos:
                video = videos[0]
                # 在 video 元素上模拟鼠标移动
                actions = ActionChains(driver)
                actions.move_to_element(video)
                actions.move_by_offset(5, 5)
                actions.move_by_offset(-5, -5)
                actions.perform()

                # 检查是否暂停，暂停了就点播放
                is_paused = driver.execute_script(
                    "var v = document.querySelector('video'); return v ? v.paused : true;"
                )
                if is_paused:
                    print(f"  视频暂停了，尝试点击播放...")
                    try:
                        driver.execute_script(
                            "var v = document.querySelector('video'); if(v) v.play();"
                        )
                    except:
                        actions2 = ActionChains(driver)
                        actions2.click(video).perform()
            else:
                # 没有 video 元素，在 body 上模拟鼠标移动
                body = driver.find_element(By.TAG_NAME, "body")
                actions = ActionChains(driver)
                actions.move_to_element(body)
                actions.move_by_offset(10, 10)
                actions.move_by_offset(-10, -10)
                actions.perform()

                # 尝试触发 focus 事件
                driver.execute_script(
                    "window.dispatchEvent(new Event('focus'));"
                    "document.dispatchEvent(new Event('focusin'));"
                )

            count += 1
            if count % 5 == 1:
                elapsed = int(time.time() - start)
                title = driver.title[:30] if driver.title else "?"
                print(f"[{elapsed}s] 第 {count} 次 | 页面: {title}")

            time.sleep(interval)

            if duration and (time.time() - start) >= duration:
                print(f"达到设定时长 {duration}s，停止。共保活 {count} 次。")
                break

        except Exception as e:
            print(f"[警告] {e}")
            # 可能是页面跳转或刷新，等一下再试
            time.sleep(5)


def main():
    parser = argparse.ArgumentParser(description="网课浏览器直接控制脚本")
    parser.add_argument("--url", type=str, help="网课页面地址（如不指定，需手动在浏览器中打开）")
    parser.add_argument("--interval", type=int, default=20, help="保活间隔（秒），默认20")
    parser.add_argument("--duration", type=int, default=0, help="运行时长（秒），0=无限")
    parser.add_argument("--headless", action="store_true", help="无头模式（不推荐）")
    args = parser.parse_args()

    print("=" * 50)
    print("  网课浏览器保活脚本 / Browser Keeper")
    print("=" * 50)

    print("正在启动浏览器...")
    driver = create_driver(headless=args.headless)

    if args.url:
        print(f"打开页面: {args.url}")
        driver.get(args.url)
        print("页面已打开。请在浏览器中登录并进入视频播放页面。")
        print("登录完成后脚本会自动开始保活。等待 10 秒...")
        time.sleep(10)
    else:
        print("未指定 URL，请在打开的浏览器中手动导航到网课页面。")
        print("导航完成后等待 5 秒自动开始保活...")
        time.sleep(5)

    keep_alive(driver, args.interval, args.duration)

    print("关闭浏览器...")
    driver.quit()
    print("已退出。")


if __name__ == "__main__":
    main()