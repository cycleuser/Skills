# 证据图收集与嵌入 (Evidence Images)

## 收集

- 按正文/表格列出的清单逐项匹配证据文件（证书 jpg/png、证明 PDF、名单 PDF）。
- `embed_evidence.py prep <目录> <输出>`：
  - jpg/jpeg → PIL 转真 PNG（**不要只改扩展名**，python-docx 靠魔数识别，假 .png 会报 UnrecognizedImageError）。
  - png → 直拷。
  - pdf → pymupdf 取第 1 屏转 PNG（dpi=110）。
- 清单中缺图的项：正文标注"（待补）"，不编造。

## 嵌入（python-docx）

```
run.add_picture(png, width=Cm(w))
```
- 横版图宽 14-15cm；竖版（证书）宽 12cm；居中。
- 图下加注：宋体 10.5pt 灰色，如"支撑材料：××证书（证书编号××）"。
- 一个文档几十张图 → 输出 docx 可达 50MB 级，属正常。

## 防呆

- 嵌入前 `Image.open(png).verify()`。
- 每图加注要写清"来源/编号/内容"，便于评审核对。
