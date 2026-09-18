---
name: video-digest
version: "1.0.0"
description: |
  将任意视频网站链接转换为高效率图文学习材料。

  Triggers when: 用户提供视频链接并要求下载、截图、逐字稿、幻灯片、总结或浓缩。

  Commands:
  - /视频浓缩 <视频链接> — 完整流程：下载/截图→逐字稿→幻灯片→文章
  - /视频截图 <视频链接> — 仅截图并生成幻灯片
  - /视频转文字 <视频链接> — 仅提取逐字稿与总结文章
  - /视频字幕 <视频链接> — 仅生成带时间戳的字幕文件

  Capabilities: 视频下载(合法源)、关键帧提取、语音转文字、基于截图的幻灯片生成、逐字稿+整句字幕+总结文章、多平台支持
author: cycleuser
license: MIT
status: Beta
---

## Safety Rules

参见 [_shared/core/safety-rules.md](../_shared/core/safety-rules.md) — 所有安全规则从共享层加载。

# Video Digest 技能：视频浓缩学习

## 核心定位

看视频费眼睛、耗时间、信息密度低。这个技能把视频转换成文字+图片+幻灯片，用更高效的通道消化内容。

---

## 整体流程（给模型用的模板）

```
步骤1: 获取视频
  若可合法下载 → yt-dlp/you-get 下载到本地
  若不可下载   → 截图关键帧 + 录屏 + 提取音频流

步骤2: 抽取
  截图: 检测场景切换 → 抽取关键帧（每帧唯一，去重）
  音频: 从视频文件或流中提取音频轨道（ffmpeg）

步骤3: 转写
  音频 → 文本（whisper / faster-whisper / 云ASR服务）
  每个句子带时间戳

步骤4: 生成
  逐字稿: 时间戳 + 完整句子 → 整句字幕（SRT/VTT格式）
  幻灯片: 关键帧 + 对应的语音摘要 → PPTX/PDF/图片序列
  总结文章: 全文浓缩，保留逻辑脉络与关键数据
```

---

## Quick Commands

| Command | Description |
|---------|-------------|
| `/视频浓缩 <url>` | 完整流程：下载/截图→逐字稿→幻灯片→文章 |
| `/视频截图 <url>` | 仅截图，生成按时间排序的关键帧并排成幻灯片 |
| `/视频转文字 <url>` | 仅提取逐字稿与总结文章 |
| `/视频字幕 <url>` | 仅生成带时间戳的 SRT/VTT 字幕文件 |

---

## 步骤1：获取视频内容

### 1.1 判断来源

| 平台 | 工具 | 说明 |
|------|------|------|
| YouTube | yt-dlp | 最稳定，带字幕下载 |
| B站 / Bilibili | you-get / yt-dlp | 注意需要 cookie 登录 |
| 公开课平台（Coursera、MOOC等） | yt-dlp 或浏览器截图 | 有 DRM 保护的用截图法 |
| 其他通用网站 | yt-dlp --list-extractors 查支持列表 | 不支持的走截图+音频流 |

### 1.2 合法下载（优先）

```bash
# YouTube 下载最佳质量
yt-dlp -f "bestvideo[height<=1080]+bestaudio/best[height<=1080]" -o "%(title)s.%(ext)s" <url>

# B站 下载
you-get <url>

# 通用尝试
yt-dlp <url>
```

### 1.3 不可下载的场景（截图+音频流方案）

当视频有 DRM 保护或平台无反下载工具时：

```
方案A: headless browser 截图
  1. playwright/puppeteer 打开视频页面
  2. 全屏播放
  3. 定时截图（每5秒/每场景切换时）
  4. 同时录制系统音频（pulseaudio loopback / WASAPI）

方案B: 录屏
  1. ffmpeg 录屏 + 系统音频
  2. 然后按步骤2处理
```

工具选择原则：**先试 yt-dlp，不行再用浏览器方案，尊重视频网站的 robots.txt 和技术限制。**

---

## 步骤2：抽取关键帧

### 2.1 用 ffmpeg 检测场景切换

```bash
# 输出场景切换的时间戳（scene change detection）
ffmpeg -i video.mp4 -vf "select='gt(scene,0.3)',showinfo" -vsync vfr keyframes_%03d.png 2>&1 | grep "pts_time" > scene_times.txt
```

### 2.2 去重与筛选

相似帧只保留一张（感知哈希 SSIM > 0.95 的合并）。每张关键帧与对应时间戳配对。

```
关键帧命名规则: frame_001_00m12s.png  → 第1帧，12秒处
```

---

## 步骤3：语音转文字

### 3.1 提取音频

```bash
ffmpeg -i video.mp4 -vn -acodec pcm_s16le -ar 16000 audio.wav
```

### 3.2 转写（优先本地模型）

| 方案 | 适用场景 |
|------|----------|
| whisper (openai-whisper) | 本地运行，支持中英等多语言，模型越大越准 |
| faster-whisper | whisper 的 CTranslate2 加速版，速度翻倍内存减半 |
| 云 ASR（阿里/腾讯/讯飞） | 超长视频，本地跑不动时用 |

```bash
# faster-whisper 示例
faster-whisper video.mp4 --model large-v3 --language zh --output_format srt --output_dir ./output
```

输出：带时间戳的 JSON，每条包含 `{start, end, text}`

---

## 步骤4：生成产出物

### 4.1 逐字稿（整句字幕 SRT）

```
规则: 
- 每句一行，最大时长不超过8秒
- 句末带标点
- 时间戳精确到毫秒
- 外语视频保留原文并附中文翻译

格式示例（SRT）:
1
00:00:00,000 --> 00:00:05,200
今天我们来讲一下量子力学的基本原理。

2
00:00:05,200 --> 00:00:12,800
在经典物理中，粒子的位置和动量是可以同时确定的。
```

### 4.2 幻灯片

```
生成规则:
1. 每张幻灯片 = 一张关键帧截图 + 对应时间段的语音摘要
2. 摘要字数：30-60字，提取核心观点
3. 保持原视频的逻辑顺序不变
4. 关键公式/图表优先保留
5. 输出格式：PPTX（python-pptx）或 PDF（reportlab/img2pdf）

PPTX 模板:
- 上半部分：关键帧图片（高度占 60%）
- 下半部分：摘要文字 + 时间戳
- 每页右下角标注来源视频链接
```

### 4.3 总结文章

```
要求:
1. 2000-5000字（根据视频长度自适应）
2. Markdown 格式
3. 结构：
   - 标题（视频原标题或概括）
   - 摘要（100字以内，一段话概括全文）
   - 正文（按逻辑分段，每段有明确主题句）
   - 关键结论（3-5条 bullet points）
   - 来源信息（视频链接、时长、发布日期）
4. 保留所有重要的数字、公式、人名、术语
5. 去除口头语、重复、铺垫等低信息密度内容
6. 图片引用：关键截图嵌入文中对应位置
```

---

## 输出文件清单（每个视频一个文件夹）

```
output/<视频标题>/
├── original_url.txt          # 原始链接
├── video.mp4                 # 下载的视频（若可下载）
├── transcript.srt            # 逐字稿字幕（整句，带时间戳）
├── transcript.txt            # 纯文本逐字稿
├── summary.md                # 总结文章（Markdown）
├── slides.pptx               # 幻灯片（图片+摘要）
├── slides/                   # 幻灯片单页图片（若不需要pptx）
│   ├── slide_001.png
│   ├── slide_002.png
│   └── ...
├── keyframes/                # 提取的关键帧
│   ├── frame_001_00m12s.png
│   └── ...
└── audio.wav                 # 提取的音频（中间产物，可删除）
```

---

## 测试用例：赵征老先生物理讲座

### 测试步骤

1. 用 `/视频浓缩` 命令传入赵峥的物理讲座视频链接，例如 `https://www.bilibili.com/video/BV1Gv411y76Y?t=20.5`
2. 预期产出：
   - 完整的逐字稿（赵老先生的讲述逐句记录）
   - 幻灯片（黑板板书/示意图作为关键帧 + 对应的物理概念摘要）
   - 总结文章（物理原理的逻辑推演，保留公式和推导步骤）
3. 验证要点：
   - 物理公式的 OCR 是否正确（黑板上的公式转写为 LaTeX）
   - 逐字稿是否保留了赵老的讲授风格和逻辑链
   - 幻灯片是否抓住了每一次"黑板书写"的时刻

### 特殊处理

- 黑板书写帧优先度高（scene change > 0.4 的帧大概率是写完一段落笔的时刻）
- 公式区域单独截图，尝试 OCR 为 LaTeX（Mathpix / pix2tex）
- 手势指向黑板的帧也保留（讲课的指示性动作）

---

## 平台适配表

| 视频源 | 下载工具 | 字幕源 | 截图方案 | 备注 |
|--------|----------|--------|----------|------|
| YouTube | yt-dlp | yt-dlp自带/内置字幕 | ffmpeg | 最完善 |
| Bilibili | you-get/yt-dlp | 弹幕转字幕/ASR | ffmpeg | 需cookie登录 |
| 中国大学MOOC | 浏览器截图 | 内置字幕/ASR | playwright | DRM可能阻止下载 |
| Coursera | yt-dlp | 内置字幕 | ffmpeg | 需登录cookie |
| TED | yt-dlp | 多语言字幕 | ffmpeg | 字幕质量最好 |
| 微信视频号 | 浏览器截图 | ASR | playwright | 无公开下载工具 |
| 抖音/TikTok | yt-dlp支持 | ASR | ffmpeg | 短视频 |
| 本地视频文件 | 直接读取 | ASR | ffmpeg | 最自由 |

---

## 模型执行检查清单

当模型被要求执行这个技能时，必须在响应中逐步完成以下事项：

- [ ] 确认收到视频 URL，识别平台
- [ ] 选择下载或截图方案
- [ ] 提供使用的具体命令行或代码
- [ ] 输出关键帧数量与时间戳
- [ ] 输出逐字稿文本（至少前100句预览）
- [ ] 输出幻灯片摘要列表（每页标题）
- [ ] 输出总结文章
- [ ] 生成的文件路径清单

---

## 注意事项

- **尊重版权**：仅用于个人学习目的。不对受 DRM 保护的付费视频进行破解。
- **隐私**：不缓存不转存用户提供的视频链接。
- **学术诚信**：幻灯片和总结文章应标注原始视频来源，不可冒充原创。
- **工具依赖**：本地需安装 ffmpeg、whisper/faster-whisper、yt-dlp。首次使用前检查环境。
