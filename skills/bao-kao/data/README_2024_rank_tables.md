# 2024 年高考一分一段表数据采集结果

## 数据来源
- 来源网站：教育在线 (gaokao.eol.cn)
- 采集时间：2024 年
- 数据格式：Markdown 表格

## 已成功采集的省份 (11 个)

| 省份 | 科目 | 文件路径 | 状态 |
|------|------|----------|------|
| 安徽 | 物理类 | an_hui/rank_tables/2024_rank_物理.md | ✅ 完整 |
| 北京 | 综合 | bei_jing/rank_tables/2024_rank_综合.md | ✅ 完整 |
| 重庆 | 物理类 | chong_qing/rank_tables/2024_rank_物理.md | ✅ 完整 |
| 福建 | 物理类 | fu_jian/rank_tables/2024_rank_物理.md | ✅ 完整 |
| 甘肃 | 物理类 | gan_su/rank_tables/2024_rank_物理.md | ✅ 完整 |
| 河北 | 物理类 | he_bei/rank_tables/2024_rank_物理.md | ✅ 完整 |
| 江西 | 物理类 | jiang_xi/rank_tables/2024_rank_物理.md | ✅ 完整 |
| 内蒙古 | 理科 | nei_meng_gu/rank_tables/2024_rank_理科.md | ✅ 完整 |
| 宁夏 | 理科 | ning_xia/rank_tables/2024_rank_理科.md | ✅ 完整 |
| 上海 | 综合 | shang_hai/rank_tables/2024_rank_综合.md | ✅ 完整 |
| 浙江 | 综合 | zhe_jiang/rank_tables/2024_rank_综合.md | ✅ 完整 |

## 无法采集的省份 (20 个)

### 数据以图片形式展示（无法提取）
| 省份 | 原因 |
|------|------|
| 天津 | 数据以图片形式展示，webfetch 无法提取 |

### 只返回分数线（无一分一段表数据）
| 省份 | 原因 |
|------|------|
| 山东 | 页面只返回分数线信息，无详细分段表 |
| 江苏 | 页面只返回分数线信息，无详细分段表 |
| 山西 | 页面只返回分数线信息，无详细分段表 |
| 黑龙江 | 页面只返回分数线信息，无详细分段表 |
| 吉林 | 页面只返回分数线信息，无详细分段表 |

### 页面 404 错误
| 省份 | URL |
|------|-----|
| 河南 | https://gaokao.eol.cn/he_nan/dongtai/202406/t20240624_2618937.shtml |
| 湖北 | https://gaokao.eol.cn/hu_bei/dongtai/202406/t20240625_2619229.shtml |
| 湖南 | https://gaokao.eol.cn/hu_nan/dongtai/202406/t20240624_2618996.shtml |
| 广东 | https://gaokao.eol.cn/guang_dong/dongtai/202406/t20240624_2618923.shtml |
| 广西 | https://gaokao.eol.cn/guang_xi/dongtai/202406/t20240624_2618919.shtml |
| 海南 | https://gaokao.eol.cn/hai_nan/dongtai/202406/t20240624_2618930.shtml |
| 四川 | https://gaokao.eol.cn/si_chuan/dongtai/202406/t20240624_2619007.shtml |
| 贵州 | https://gaokao.eol.cn/gui_zhou/dongtai/202406/t20240624_2619000.shtml |
| 云南 | https://gaokao.eol.cn/yun_nan/dongtai/202406/t20240624_2619033.shtml |
| 陕西 | https://gaokao.eol.cn/shan_xi_sheng/dongtai/202406/t20240624_2619054.shtml |
| 辽宁 | https://gaokao.eol.cn/liao_ning/dongtai/202406/t20240624_2618961.shtml |
| 西藏 | https://gaokao.eol.cn/xizang/dongtai/202406/t20240625_2619270.shtml |
| 青海 | https://gaokao.eol.cn/qing_hai/dongtai/202406/t20240625_2619267.shtml |
| 新疆 | https://gaokao.eol.cn/xin_jiang/dongtai/202406/t20240625_2619304.shtml |

## 采集成功率
- 成功：11 个省份 (35.5%)
- 失败：20 个省份 (64.5%)

## 失败原因分析
1. **数据以图片形式展示**：部分省份的一分一段表以图片形式嵌入网页，无法通过文本提取
2. **页面只返回分数线**：部分 URL 只包含分数线信息，没有详细的分段统计表
3. **页面 404**：部分 URL 已失效或不存在

## 建议
如需获取完整数据，建议：
1. 直接访问各省教育考试院官方网站
2. 使用 OCR 技术提取图片中的表格数据
3. 查找其他数据源（如中国教育在线汇总页面）
