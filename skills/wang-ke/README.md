# 网课助手

网课鼠标保持技能。自动控制鼠标微移或模拟点击，防止网课平台因鼠标离开/静止而暂停视频。

## 命令

- `/网课` — 启动默认模式（每30秒微移鼠标1像素）
- `/网课 start [间隔秒]` — 自定义间隔启动
- `/网课 stop` — 停止
- `/网课 status` — 查看运行状态
- `/网课 click` — 点击模式（定时点击播放区域）
- `/网课 tampermonkey` — 生成油猴脚本

## 快速使用

```bash
# 默认：每30秒微移一次
python3 scripts/mouse_keeper.py

# 每15秒一次（更激进）
python3 scripts/mouse_keeper.py --interval 15

# 点击模式（应对弹窗检测）
python3 scripts/mouse_keeper.py --mode click

# 运行1小时后自动停
python3 scripts/mouse_keeper.py --duration 3600
```

## 停止方式

- Ctrl+C
- 将鼠标快速移到屏幕四角
- `/网课 stop`

## 依赖

```bash
pip install pyautogui
# macOS: 系统设置 → 隐私与安全 → 辅助功能 → 允许终端
```