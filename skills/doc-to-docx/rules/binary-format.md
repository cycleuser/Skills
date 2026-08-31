# .doc 二进制格式速查 / Binary Format Reference

本文件记录引擎用到的 Word 二进制格式关键结构（MS-DOC 规范的简化版），
并标注了实际验证过的偏移（对 WPS 生成的 Word 97 兼容文件同样有效）。

## 容器：OLE2 / Compound File

`.doc` 是一个 OLE2/CFB 容器（魔数 `D0 CF 11 E0 A1 B1 1A E1`）。关键流：

- **WordDocument**：FIB + 正文文本 + FKP 页 + SEPX。
- **0Table / 1Table**：分片表（CLX）、PlcfBteChpx、PlcfBtePapx、PlcfSed、
  STSH、STTBF ffn 等。**WPS 常把 fWhichTblStm 标志写错，必须靠内容探测**
  选流（见 `_pick_table_stream`）。

## FIB（File Information Block）— WordDocument 流偏移 0

```
0   wIdent  0xA5EC
2   nFib    0x00C1=Word97  0x00D9=Word2000  0x0101=Word2002+
12  flags   bit9 = fWhichTblStm（不可靠）
24  fcMin   正文文本在 WordDocument 流的起始字节偏移
28  fcMac   正文文本结束字节偏移
32  csw     固定 14
34  fibRgW  14 个字
62  cslw    固定 22
64  fibRgLw 22 个长字：cbMac、ccpText、ccpFtn、ccpHdd ...
152 cbRgFcLcb  常为 164（WPS）/ 93（规范值，按字段实际读）
154 fibRgFcLcb (fc,lcb) 对数组，每对 8 字节
```

`fcMin`/`fcMac` 是正文的字节区间；文本按 UTF-16LE 存放，故字符数
`ccpText = (fcMac - fcMin)/2`（压缩分片除外）。

### fibRgFcLcb 关键索引

| 索引 | 结构 | 说明 |
|-----|------|------|
| 0/1 | STSH | 样式表（fStshfOrig / fStshf） |
| 6 | PlcfSed | 分节描述（SEPX 位置） |
| 12 | PlcfBteChpx | 字符属性异常表 |
| 13 | PlcfBtePapx | 段落属性异常表 |
| 15 | STTBF ffn | 字体名表 |
| 33 | CLX | 文本分片表 |

## 分片表（CLX / PlcPcd / PCD）

```
CLX = 若干 Pcdt（clxt=0x02, lcb, PlcPcd） + grpprl
PlcPcd = (n+1) 个 CP（4B）+ n 个 PCD（8B）
PCD   = flags(2B) + fc(4B, FcCompressed) + prm(2B)
FcCompressed: fc 占 bit0-29；bit30=fCompressed；bit31 保留
```

- 未压缩分片：文本 UTF-16LE，字节区间 `[fc, fc+2*(cp1-cp0))`。
- 压缩分片：文本 cp1252/ANSI，字节区间 `[fc, fc+(cp1-cp0))`。
- **FC 与 CP 换算**：CP 是字符位置（全文档统一），FC 是 WordDocument 流
  字节偏移。跨分片换算必须经分片表（`fc_to_cp`）。

## FKP 页（CHPX / PAPX 的载体）

CHPX/PAPX 的 PLCF 里每条记录是一个 **PnFkp = 页号 ×512**，指向
WordDocument 流中的一个 512 字节 FKP 页。

### ChpxFkp（字符格式）
```
0            rgfc: crun+1 个 FC（4B/个），run 的字节区间
(crun+1)*4   rgb: crun 个字节，Chpx 结构偏移 = rgb[i]*2
511          crun（最后一个字节！）
Chpx = cb(1B) + grpprl(cb B)
```

### PapxFkp（段落格式）
```
0            rgfc: cpara+1 个 FC（4B/个），run 的字节区间
(cpara+1)*4  rgb 字节按 stride=13 存放，PapxInFkp 偏移 = rgb[i]*2
511          cpara（最后一个字节）
PapxInFkp    [第一个结构前多 1 个 0x00 标记字节][size_byte][istd(2B)][grpprl]
             size_byte*2 = 3 + len(grpprl)（grpprl 补齐为奇数长）
```
> **stride=13 是实测/antiword 一致的布局**，不要想当然按 BxPap 连续 2B 读。

## sprm（Single Property Modifier）

Prl = sprm(2B) + operand。sprm 编码：

```
bit0-9   ispmd + fSpec（属性编号）
bit10-12 sgc（0=段落 1=分节 2=字符 3=表格 4=文档）
bit13-15 spra（operand 尺寸）
```

operand 尺寸（`sprm_len`，与 antiword iGet8InfoLength 一致）：

| spra | operand 长度 |
|------|-------------|
| 0,1 | 1 字节 |
| 2,4,5 | 2 字节 |
| 3 | 4 字节 |
| 7 | 3 字节 |
| 6 | 首字节 = 剩余长度 |

### 常用字符 sprm → OOXML

| sprm | 值 | OOXML |
|------|-----|-------|
| sprmCFBold | 0x0835 | `w:b` |
| sprmCFItalic | 0x0836 | `w:i` |
| sprmCKul | 0x2A3E | `w:u w:val=...` |
| sprmCv | 0x6870 | `w:color`（0x00BBGGRR） |
| sprmCHps | 0x4A43 | `w:sz`（半磅） |
| sprmCIss / sprmCHpsPos | 0x2A48 / 0x4845 | `w:vertAlign` |
| sprmCRgFtc0/1/2 | 0x4A4F/50/51 | `w:rFonts w:ascii/eastAsia/hAnsi` |
| sprmCHighlight | 0x2A0C | `w:highlight` |

### 常用段落 sprm → OOXML

| sprm | 值 | OOXML |
|------|-----|-------|
| sprmPJc / PJc80 | 0x2461 / 0x2403 | `w:jc` |
| sprmPDxaLeft/Right | 0x845E / 0x845D | `w:ind left/right` |
| sprmPDxaLeft1 | 0x8460 | `w:ind firstLine/hanging` |
| sprmPDyaBefore/After | 0xA413 / 0xA414 | `w:spacing before/after` |
| sprmPDyaLine | 0x6412 | `w:spacing line/lineRule` |
| sprmPFKeep / KeepFollow | 0x2405 / 0x2406 | `w:keepLines / keepNext` |
| sprmPFPageBreakBefore | 0x2407 | `w:pageBreakBefore` |
| sprmPFInTable / PFTtp | 0x2416 / 0x2417 | 表格标记 |
| sprmTDefTable | 0xD608 | 行列宽（TDefTableOperand） |
| sprmTTableBorders | 0xD613 | 表格边框 |

### 常用分节 sprm → OOXML sectPr

| sprm | 值 | 说明 |
|------|-----|------|
| sprmSXaPage / SYaPage | 0xB01F / 0xB020 | 页宽/页高（缇 twips） |
| sprmSDxaLeft/Right | 0xB021 / 0xB022 | 左右边距 |
| sprmSDyaTop/Bottom | 0x9023 / 0x9024 | 上下边距 |
| sprmSBOrientation | 0x301D | 横/竖版 |
| sprmSPgnStart | 0x7044 | 起始页码 |
| sprmSCcolumns | 0x500B | 分栏数 |

## STSH（样式表）

```
0-1   word[0]  = rglpstd 偏移 - 2
2     cstd     样式数
4     cbSTDBase = 18
2+word[0]      rglpstd：cstd 个 STD
STD: len(2B) + 主体
  主体[2:4]  type(低4位) | istdBase(高12位)
  主体[4:6]  cupx(低4位) | istdNext(高12位)
  主体[18]   stName（Xst：cch(2B)+字符+cch 计数不含终止符，其后另加 2B 空）
  之后       UpxPapx（段落样式）：cbUpx(2B)+istd(2B)+grpprl(cbUpx-2)
              UpxChpx：cbUpx(2B)+grpprl(cbUpx)
  每个 Upx 后补齐偶数长度
```

样式解析用两遍：先按索引收集原始 grpprl，再按 istdBase 链式 resolve 出
完整默认格式（`_read_styles`）。

## STTBF ffn（字体表）

```
0-1   fExtend：0xFFFF=扩展（Unicode 名）；否则该字直接是 cData
2     cData   字体数
4     cbExtra 常为 0
每个 FFN：cbFfnM1(1B, 整结构长-1) prq/ff(1) wWeight(2) chs(1) ibszChi(1)
         panose(10) fs(24) szFfn(变长，空终止)
```

**WPS 在“非扩展”头下仍写 UTF-16LE 字体名**，引擎对每个名字做字节嗅探
（按 UTF-16LE 解码打分）自动判别，保证宋体/黑体等中文名正确读出。

## 单位

- 1 缇（twip）= 1/20 pt = 1/1440 英寸。docx 页尺寸用 EMU（1 缇 ≈ 635 EMU）。
- 字号 sprmCHps 以半磅计：21 → 10.5pt（五号），24 → 12pt（小四）。

## 参考实现

格式细节与 antiword（`prop8.c`、`stylesheet.c`、`options.c`）逐字节对齐；
sprm 表取自 MS-DOC 规范 2.6 节。
