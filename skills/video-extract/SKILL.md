---
name: video-extract
version: "1.0.0"
description: |
  视频萃取：将任意视频链接转化为图文学习材料（逐字稿、关键帧、幻灯片、总结文章、网页）。

  Triggers when: 用户提供视频链接并要求萃取、浓缩、转录、生成学习材料。

  Commands:
  - /视频萃取 <视频链接> — 完整流程：下载→字幕→文本修正→关键帧→网页+幻灯片+总结
  - /VideoExtract <url> — English equivalent

  Capabilities: 多平台视频下载、音频转文字、关键帧提取、幻灯片生成、总结提炼、网页打包
author: cycleuser
license: MIT
status: Beta
---

## Safety Rules

参见 [_shared/core/safety-rules.md](../../_shared/core/safety-rules.md)

# 视频萃取技能 (Video Extract)

## 核心定位

将视频链接中的内容萃取出图文学习材料，提高信息获取效率。

---

## 命令

| Command | Description |
|---------|-------------|
| `/视频萃取 <url>` | 完整五步流程 |
| `/VideoExtract <url>` | English equivalent |

---

## 五步流程

### 第一步：获取视频

```
优先: yt-dlp 下载
  yt-dlp -f "best[height<=1080]" -o "video.mp4" <url>
  如果 B 站需要 cookie: yt-dlp --cookies-from-browser chrome <url>

兜底: 若 DRM 保护或无法下载
  使用 playwright/puppeteer 截图 + 录屏 + 系统音频录制
```

### 第二步：获取文本

```
优先: yt-dlp 提取内嵌字幕
  yt-dlp --write-subs --sub-lang zh --convert-subs srt --skip-download <url>

兜底: 提取音频 + ASR 转写
  ffmpeg -i video.mp4 -vn -acodec pcm_s16le -ar 16000 -ac 1 audio.wav
  faster-whisper video.mp4 --model large-v3 --language zh --output_format json

输出: 带时间戳的文本数组 [{start, end, text}]
```

### 第三步：修正文本

```
审查上一步得到的文本，检查并修正:
- 口误（说错但转写成了正确文字的）
- 笔误/错别字（转写错误）
- 重复的口头禅（呃、那个、就是说 等无意义的重复）
- 保持原意不变，只做纠错和去噪
```

### 第四步：提取关键帧

```bash
ffmpeg -i video.mp4 -vf "select='gt(scene,0.4)',showinfo" -vsync vfr keyframes_%03d.png 2>&1 | grep pts_time > keyframes.json
```

- 阈值 0.4（PPT 类课程用 0.3，实拍用 0.4）
- 每帧记录时间戳（秒）
- 相邻帧若 SSIM > 0.95 则合并去重
- 输出: {frame_id, time_sec, filepath} 列表

### 第五步：生成产物

**网页（index.html）**：
- 顶部：视频标题、来源链接
- 正文区：修改后的逐字稿，关键帧插图嵌入对应位置
- 每段文字附时间戳，点击可跳转
- 自适应手机屏幕

**总结文章（summary.md）**：
- 2000-5000 字
- 结构：标题→摘要→正文分段→关键结论
- 保留所有公式、数据、专有名词
- 去除口头语、重复、铺垫

**幻灯片（slides.pptx）**：
- 每页 = 一张关键帧图片 + 30-60 字摘要
- python-pptx 生成

**Word 文档**：
- 将网页内容转为 .docx（pandoc 或 python-docx）

### 完成后询问

> 中间临时文件（video.mp4、audio.wav、keyframes/*.png）要保留还是删除？

---

## 输出目录结构

```
~/Desktop/VideoExtract_<视频标题>/
├── index.html          # 嵌入图片和文本的网页
├── summary.md          # 干货总结
├── slides.pptx         # 幻灯片
├── transcript.json     # 修正后的逐字稿（JSON）
├── article.docx        # Word 文档
├── keyframes/          # 关键帧图片
│   ├── 000_12.5s.png
│   └── ...
└── temp/               # 临时文件（可删除）
    ├── video.mp4
    └── audio.wav
```

---

## 测试用例

使用以下命令验证技能：

```
/视频萃取 https://www.bilibili.com/video/BV1ra4y157fN
```

预期产出：
- B 站视频下载成功
- 提取音频并转写（若视频本身无字幕）
- 修正转写文本
- 提取关键帧（课程类视频，scene threshold 0.35）
- 生成 index.html、summary.md、slides.pptx
- 所有产物放入 ~/Desktop/VideoExtract_*/ 目录

---

## 依赖

| 工具 | 用途 | 安装 |
|------|------|------|
| yt-dlp | 视频下载 | pip install yt-dlp |
| ffmpeg | 音视频处理 | brew install ffmpeg |
| faster-whisper | 语音转文字 | pip install faster-whisper |
| opencv-python | 帧去重 | pip install opencv-python |
| python-pptx | 幻灯片 | pip install python-pptx |
| python-docx | Word 文档 | pip install python-docx |
