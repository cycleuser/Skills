# 边界情况与排错 / Edge Cases & Troubleshooting

## 常见文件异常

| 现象 | 原因 | 处理 |
|------|------|------|
| `not an OLE2 container` | 文件其实不是 .doc（可能是 .docx/.rtf/加密），或已损坏 | 确认扩展名与内容一致；用 `inspect` 看首字节魔数 |
| `no WordDocument stream` | OLE2 但非 Word 文档（如 .xls/.ppt 也是 OLE2） | 检查流列表 |
| 转换后文本为空/乱码 | fcMin/fcMac 或分片表解析异常；加密文档 | 用 `inspect` 看 fcMin/fcMac/ccpText 是否合理；fEncrypted 时拒绝转换 |
| 0Table/1Table 二选一错误 | WPS 把 fWhichTblStm 位写反 | 引擎自动按内容探测，无需人工干预 |
| 中文变 `???` | 解码用了错误的码页 | 未压缩分片固定 UTF-16LE；压缩分片用 cp1252 |

## 段落/字符格式

- **FC→CP 换算**：CHPX/PAPX 的 FKP 里存的是 WordDocument 字节偏移（FC），
  不是字符位置；跨分片时 `fc_to_cp` 必须经分片表换算。分片间隙里的 FC
  会被钳制到上一分片末尾，避免产生 cp=0 的重叠段。
- **PAPX 第一个结构**：FKP 页首个 PapxInFkp 带一个 `0x00` 标记字节
  （PLCFPAPX 形态），后续结构没有。解析时先读 size，为 0 则加一字节再读。
- **WPS 字体名**：非扩展 STTBF 头 + UTF-16 名字，靠字节嗅探自动判别。
- **样式链**：样式基于 istdBase 可多级继承；resolve 时要做环检测
  （visited 集合），防止循环引用死循环。

## 表格

- **行内单元格**：行文本按 `0x07` 拆分，**最后一个 `0x07` 是行结束标记
  （fTtp 段），不是真实单元格**，要丢弃。
- **行宽来源**：列宽在行结束段（fTtp=1）的 PAPX 的 `sprmTDefTable` 里，
  operand 为 `cb(2B)+列数(1B)+列界(XAS数组)`，列宽 = 相邻列界之差。
- **gridSpan**：行单元格数 < 网格列数时，末单元格吞并多余列；行单元格数
  > 网格列数时（垂直合并续格），后续格用 vMerge 语义，占位即可。
- **嵌套表格**：暂不支持，`fInnerTableCell` 相关标记会被当作普通表格段落。

## 常见问题排查

- **转换成功但打开 docx 报损坏** → 用 `unzip -t` 检查包完整性；检查每个
  XML part 用 `xmllint --noout` 是否合法。引擎已保证 tblGrid 列数与
  gridSpan 总和一致。
- **某段格式不对** → `inspect` 看该段的 istd/jc/indent；用解包工具看
  `document.xml` 里该段的 pPr/rPr。
- **字体名读出乱码** → 检查字体表（ffn）扩展标志与名字编码；引擎已自动
  判别 UTF-16/ANSI。
- **页眉页脚丢失** → 见 fidelity-map Tier 3，当前版本不还原页眉页脚。
- **超大文件慢** → 文本一次性读入内存；对几十 MB 的 .doc 可先用
  `inspect` 确认结构再转换。

## 命令行

- `-o` 输出路径不存在时会自动建目录。
- `batch` 只处理 `.doc`（不碰 `.docx`），失败单文件记录到 stderr 不中断。
- `check --against` 对比时给出字符比值，作为快速回归指标。
