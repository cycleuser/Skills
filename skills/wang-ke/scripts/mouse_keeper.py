#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
mouse_keeper.py — 网课鼠标保持脚本
定时微移鼠标或模拟点击，防止网课平台因鼠标静止/离开而暂停视频。

用法:
  python3 mouse_keeper.py                          # 默认：每30秒微移1像素
  python3 mouse_keeper.py --interval 15            # 每15秒一次
  python3 mouse_keeper.py --mode click             # 点击模式
  python3 mouse_keeper.py --duration 3600          # 运行1小时后自动停止
  python3 mouse_keeper.py --corner-stop false      # 关闭角落退出

停止:
  Ctrl+C 或 将鼠标快速移到屏幕四角

依赖:
  pip install pyautogui
  # macOS 还需要: 系统设置 → 隐私与安全 → 辅助功能 → 允许终端
"""
import argparse
import signal
import sys
import time

try:
    import pyautogui
except ImportError:
    print("缺少 pyautogui，正在安装...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pyautogui"])
    import pyautogui

pyautogui.FAILSAFE = True  # 鼠标移到角落自动触发异常（安全退出）
pyautogui.PAUSE = 0  # 不在每次调用后暂停

running = True


def signal_handler(sig, frame):
    global running
    running = False
    print("\n收到停止信号，正在退出...")
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)


def move_mode(interval, pixel, duration):
    """微移模式：每次移动1像素然后移回"""
    start = time.time()
    count = 0
    print(f"微移模式启动 | 间隔={interval}s | 像素={pixel} | 时长={duration or '无限'}s")
    print(f"停止方式: Ctrl+C 或 将鼠标快速移到屏幕角落")
    print("-" * 50)

    while running:
        try:
            x, y = pyautogui.position()
            # 微移到右下方1像素再移回
            pyautogui.moveRel(pixel, pixel, duration=0.1)
            pyautogui.moveRel(-pixel, -pixel, duration=0.1)
            count += 1
            if count % 10 == 1:
                elapsed = int(time.time() - start)
                print(f"[{elapsed}s] 活动第 {count} 次 @ ({x}, {y})")
            time.sleep(interval)
            if duration and (time.time() - start) >= duration:
                print(f"达到设定时长 {duration}s，自动停止。共活动 {count} 次。")
                break
        except pyautogui.FailSafeException:
            print("\n鼠标移到屏幕角落，安全退出。")
            break


def click_mode(interval, duration):
    """点击模式：在当前鼠标位置定时点击"""
    start = time.time()
    count = 0
    print(f"点击模式启动 | 间隔={interval}s | 时长={duration or '无限'}s")
    print(f"停止方式: Ctrl+C 或 将鼠标快速移到屏幕角落")
    print(f"注意: 请先将鼠标放在视频播放区域上！")
    print("-" * 50)
    time.sleep(2)  # 给用户2秒把鼠标移到播放区域

    while running:
        try:
            pyautogui.click()
            count += 1
            if count % 10 == 1:
                elapsed = int(time.time() - start)
                x, y = pyautogui.position()
                print(f"[{elapsed}s] 点击第 {count} 次 @ ({x}, {y})")
            time.sleep(interval)
            if duration and (time.time() - start) >= duration:
                print(f"达到设定时长 {duration}s，自动停止。共点击 {count} 次。")
                break
        except pyautogui.FailSafeException:
            print("\n鼠标移到屏幕角落，安全退出。")
            break


def main():
    parser = argparse.ArgumentParser(description="网课鼠标保持脚本")
    parser.add_argument("--interval", type=int, default=30, help="活动间隔（秒），默认30")
    parser.add_argument("--mode", choices=["move", "click"], default="move", help="模式：move微移或click点击")
    parser.add_argument("--pixel", type=int, default=1, help="微移像素数，默认1")
    parser.add_argument("--duration", type=int, default=0, help="运行时长（秒），0=无限")
    parser.add_argument("--corner-stop", default="true", help="鼠标移到角落是否停止")
    args = parser.parse_args()

    if args.corner_stop.lower() == "false":
        pyautogui.FAILSAFE = False

    print("=" * 50)
    print("  网课鼠标保持脚本 / Mouse Keeper")
    print("=" * 50)

    if args.mode == "click":
        click_mode(args.interval, args.duration)
    else:
        move_mode(args.interval, args.pixel, args.duration)


if __name__ == "__main__":
    main()