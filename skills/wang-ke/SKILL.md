---
name: wang-ke
version: "1.1.0"
description: |
  Auto mouse activity keeper for online course platforms. Prevents video pause caused by
  mouse-leave detection on platforms like 学习通/雨课堂/智慧树/中国大学MOOC.

  Triggers when: Need to keep online course videos playing without manual mouse movement,
  platform pauses video when mouse leaves the player area, or need unattended course playback.

  Commands:
  - /网课 - Start default mouse keeper (move mouse every 30s)
  - /网课 start [interval] - Start with custom interval (seconds)
  - /网课 stop - Stop mouse keeper
  - /网课 status - Check if running
  - /网课 browser - Directly control browser via Selenium (no plugin needed)
  - /网课 click - Click mode (periodically click play button area)
  /wangke - English command

  Capabilities: Cross-platform mouse micro-movement (pyautogui/pynput), direct browser control
  via Selenium (simulates mouse events on video element, auto-resumes paused video),
  configurable interval, CLI background execution, anti-detection stealth mode,
  emergency stop (Ctrl+C or move mouse to corner), supports Windows/macOS/Linux
author: cycleuser
license: MIT
status: Beta
---

## Safety Rules

参见 [_shared/core/safety-rules.md](../_shared/core/safety-rules.md) — 所有安全规则从共享层加载。

关键补充：
- **仅用于保持自有账号的网课播放活跃**，不得用于绕过考试监考或刷课作弊
- 脚本运行时鼠标会自动移动，**不要同时操作电脑**，紧急停止：Ctrl+C 或将鼠标快速移到屏幕角落
- **不绕过人脸识别、不自动答题、不伪造学习记录**，仅保持播放不暂停

# 网课助手 (WangKe / Online Course Mouse Keeper)

网课平台（学习通、雨课堂、智慧树、中国大学MOOC等）普遍有"鼠标离开视频区域就暂停"的机制。
这个技能通过定时微移鼠标或模拟点击，让平台以为用户一直在页面上，从而保持视频持续播放。

## Quick Commands

| Command | 说明 / Description |
|---------|-------------|
| `/网课` | 启动默认模式（每30秒微移鼠标一次） |
| `/网课 start [间隔秒]` | 自定义间隔启动 |
| `/网课 stop` | 停止 |
| `/网课 status` | 查看运行状态 |
| `/网课 browser` | 直接控制浏览器（Selenium，无需插件） |
| `/网课 click` | 点击模式（定时点击播放区域） |
| `/wangke` | English command |

## 三种方案

### 方案一：直接控制浏览器（推荐）

用 Selenium 直接控制浏览器，在网页层面模拟鼠标移动和点击。不需要装任何浏览器插件，比 pyautogui 精准（直接操作 video 元素），不需要手动安装油猴脚本。

```bash
python3 scripts/browser_keeper.py --url "https://mooc1.chaoxing.com/..."
python3 scripts/browser_keeper.py --url "https://..." --interval 10
```

特点：
- 直接在 video 元素上模拟 `mousemove`，平台以为鼠标一直在播放区域
- 自动检测视频是否暂停，暂停了自动调 `video.play()` 恢复
- 自带反检测：隐藏 `navigator.webdriver`、移除自动化标记
- 可指定 URL 自动打开，也可手动在浏览器里导航

### 方案二：Python 系统鼠标控制

用 `pyautogui` 控制系统鼠标，每隔 N 秒微移一次。适用于任何平台，不限于浏览器。

```bash
python3 scripts/mouse_keeper.py --interval 30
```

特点：
- 鼠标每次只移动 1-2 像素然后移回原位，不影响你看屏幕
- 可配置间隔时间（默认 30 秒）
- Ctrl+C 或鼠标移到屏幕角落紧急停止
- 适用范围最广，但对"标签页失焦暂停"无效（需配合浏览器方案）

### 方案三：油猴脚本

在浏览器层面模拟鼠标移动事件，不需要额外装 Python。需要先安装 Tampermonkey 浏览器插件。

用 `/网课 tampermonkey` 生成脚本，安装到 Tampermonkey 后自动生效。

特点：
- 在网页 `document` 上定时触发 `mousemove` 事件
- 可配置间隔时间，只匹配网课域名
- 不影响系统鼠标

## 工作流程

```
Step 1  确认需求
  什么平台？需要多久？是否需要点击播放按钮？

Step 2  选择方案
  直接控制浏览器（推荐）/ Python系统鼠标 / 油猴脚本

Step 3  启动
  浏览器: python3 scripts/browser_keeper.py --url "https://..." --interval 20
  系统鼠标: python3 scripts/mouse_keeper.py --interval 30
  油猴: 安装生成的脚本到 Tampermonkey

Step 4  监控
  脚本运行中，定时模拟鼠标活动
  Ctrl+C 或移鼠标到角落停止

Step 5  停止
  Ctrl+C 或 /网课 stop
```

## 脚本参数

### browser_keeper.py（直接控制浏览器）

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `--url` | 无 | 网课页面地址 |
| `--interval` | 20 | 保活间隔（秒） |
| `--duration` | 0 | 运行时长（秒），0=无限 |
| `--headless` | false | 无头模式（不推荐，部分平台检测） |

### mouse_keeper.py（系统鼠标控制）

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `--interval` | 30 | 鼠标活动间隔（秒） |
| `--mode` | move | 模式：move（微移）或 click（点击） |
| `--pixel` | 1 | 微移像素数 |
| `--duration` | 0 | 运行时长（秒），0=无限 |
| `--corner-stop` | true | 鼠标移到屏幕角落自动停止 |

## 安全设计

1. **紧急停止**：Ctrl+C 随时中断
2. **角落退出**：鼠标快速移到屏幕任意角落（距边 < 5px）自动停止
3. **微移不影响操作**：每次只移 1 像素然后移回，你盯着屏幕看也察觉不到
4. **不模拟键盘**：只动鼠标，不自动按键，不干扰其他操作
5. **可见提示**：启动时打印运行参数和停止方式，每隔 10 次活动打印一次心跳

## 平台适配

不同平台的检测机制略有差异：

| 平台 | 检测方式 | 推荐方案 | 推荐间隔 |
|------|---------|---------|---------|
| 学习通 | 鼠标离开 iframe 暂停 | 浏览器直接控制 | 15-20s |
| 雨课堂 | 失焦暂停 | 浏览器直接控制 | 15-20s |
| 智慧树 | 鼠标静止超时暂停 | Python 微移 | 25-30s |
| 中国大学MOOC | 标签页失焦暂停 | 浏览器直接控制 | 10-15s |
| 超星泛雅 | 鼠标离开暂停 | 浏览器直接控制 | 15-20s |

如果默认参数不生效，缩短间隔到 10-15 秒再试。

## 边界情况

- **多显示器**：鼠标只在主显示器活动，不跨屏；浏览器方案不受影响
- **全屏播放**：微移不影响全屏状态；浏览器方案在全屏下仍可模拟 video 元素事件
- **弹窗检测**：部分平台会弹"是否继续学习"，浏览器方案的 click 模式可点击确认
- **后台运行**：终端最小化不影响，但终端被关闭则脚本停止
- **休眠问题**：电脑休眠会暂停脚本，需在系统设置中关闭自动休眠或使用 `caffeinate`
- **Selenium 被检测**：脚本已隐藏 `navigator.webdriver` 标记，但部分平台检测更严，需配合 `--headless false`（可见模式更不容易被检测）

## Rules

- [rules/platform-config.md](rules/platform-config.md) - 各平台检测机制与适配参数

## 常见问题排查 / Troubleshooting

- **视频还是暂停了** → 间隔太长，缩短到 10-15 秒；或换浏览器直接控制方案
- **鼠标乱跑** → pixel 参数设太大，改为 1
- **macOS 权限报错** → 系统设置 → 隐私与安全 → 辅助功能 → 允许终端
- **脚本启动报错** → `pip install pyautogui`（系统鼠标）或 `pip install selenium webdriver-manager`（浏览器控制）
- **Selenium 找不到 video 元素** → 页面可能用了 iframe，需先 `driver.switch_to.frame()`
- **油猴脚本不生效** → 检查域名匹配规则是否正确
- **浏览器被平台检测到自动化** → 确认用了 `--disable-blink-features=AutomationControlled`，不要用 `--headless`

## 版本历史 / Version History

| 版本 | 日期 | 变更 |
|------|------|------|
| 1.0.0 | 2026-07-17 | 初始版本：Python 微移/点击模式 + 油猴脚本生成 |
| 1.1.0 | 2026-07-17 | 新增浏览器直接控制方案（Selenium），自动检测视频暂停并恢复，反检测隐藏 |

## See Also / 相关技能

- `/sleepless` from **sleepless** — 长时间无人值守执行任务的通用模式