# Citation Formatting Rules

## IEEE Style (Default for CS Conferences)

### Conference Paper

```
[X] A. Author and B. Author, "Title of the paper," in Proc. International 
    Conference on Machine Learning (ICML), 2024, pp. 1-10.
```

### Journal Article

```
[X] A. Author, B. Author, and C. Author, "Title of the article," 
    IEEE Transactions on Pattern Analysis and Machine Intelligence, 
    vol. 46, no. 3, pp. 1234-1250, Mar. 2024.
```

### arXiv Preprint

```
[X] A. Author and B. Author, "Title of the paper," arXiv preprint 
    arXiv:2401.12345, 2024.
```

### Book

```
[X] A. Author, Title of the Book, 2nd ed. City: Publisher, 2024.
```

### Web Resource

```
[X] A. Author, "Title," Website Name, 2024. [Online]. Available: 
    https://example.com
```

## ACM Style

### Conference Paper

```
[X] Author, A. and Author, B. 2024. Title of the paper. In Proceedings 
    of the International Conference on Machine Learning (ICML '24). 
    ACM, New York, NY, USA, 1-10.
```

### Journal Article

```
[X] Author, A., Author, B., and Author, C. 2024. Title of the article. 
    ACM Transactions on Knowledge Discovery from Data 18, 3 (2024), 
    Article 45, 1-25.
```

## APA Style (7th Edition)

### Journal Article

```
Author, A. A., & Author, B. B. (2024). Title of the article. Journal 
Name, Volume(Issue), page-range. https://doi.org/xxxx
```

### Conference Paper

```
Author, A. A. (2024, June). Title of the paper. In Proceedings of the 
Conference Name (pp. 1-10). Publisher.
```

## AAAI/IJCAI In-Text Citation

```
Single author: (Author, 2024)
Two authors: (Author and Author, 2024)
Three+: (Author et al., 2024)
Multiple: (Author1, 2023; Author2, 2024)
```

## GB/T 7714-2015 (Chinese Standard)

### 期刊论文

```
[X] 作者. 论文标题[J]. 期刊名, 年, 卷(期): 起止页.
[1] 张三, 李四. 基于深度学习的图像分类方法[J]. 计算机学报, 2024, 47(3): 521-535.
```

### 会议论文

```
[X] 作者. 论文标题[C]//会议名. 出版地: 出版者, 年: 起止页.
[2] 王五. 知识图谱构建方法研究[C]//中国人工智能大会. 北京: 科学出版社, 2024: 112-120.
```

### 学位论文

```
[X] 作者. 论文标题[D]. 城市: 学校, 年.
[3] 赵六. 强化学习在机器人控制中的应用[D]. 北京: 清华大学, 2024.
```

### 图书

```
[X] 作者. 书名[M]. 版本. 出版地: 出版者, 年.
[4] 周七. 机器学习导论[M]. 2版. 北京: 高等教育出版社, 2024.
```

### 电子资源

```
[X] 作者. 标题[EB/OL]. (发布日期)[引用日期]. URL.
[5] 百度. 文心一言[EB/OL]. (2024-03-16)[2024-05-08]. https://yiyan.baidu.com.
```

### 中文论文引用英文文献

中文论文中引用英文文献，保持英文原文格式，按GB/T 7714的英文规则：

```
[6] Vaswani A, Shazeer N, Parmar N, et al. Attention is all you need[C]//
    Advances in Neural Information Processing Systems. 2017: 5998-6008.
```

## BibTeX Templates

### Conference

```bibtex
@inproceedings{key2024,
  author    = {Author, First and Author, Second},
  title     = {Title of the Paper},
  booktitle = {Proceedings of the International Conference on Machine Learning},
  year      = {2024},
  pages     = {1--10}
}
```

### Journal

```bibtex
@article{key2024,
  author  = {Author, First and Author, Second},
  title   = {Title of the Article},
  journal = {IEEE Transactions on Pattern Analysis and Machine Intelligence},
  volume  = {46},
  number  = {3},
  pages   = {1234--1250},
  year    = {2024}
}
```

### arXiv

```bibtex
@article{key2024,
  author  = {Author, First and Author, Second},
  title   = {Title of the Paper},
  journal = {arXiv preprint arXiv:2401.12345},
  year    = {2024}
}
```

### BibTeX Workflow

```bash
# Create/update bibliography
# 1. Collect BibTeX entries from:
#    - DBLP: dblp.org → search → "export as BibTeX"  
#    - Semantic Scholar: API returns BibTeX
#    - Google Scholar: "Cite" → "BibTeX"
#    - arXiv: "Export BibTeX" link

# 2. Store in references.bib

# 3. In LaTeX:
#    \bibliographystyle{IEEEtran}  % or acm, plainnat
#    \bibliography{references}
```

## Citation Integration in Text

Bad: Just drop citation numbers as decoration.
Good: Integrate citations into the argument.

```
Bad: "Deep learning has achieved great success [1, 2, 3, 4, 5]."
Good: "Deep learning dominates image classification [1] and machine translation 
      [2], but its application to small-sample scenarios remains limited [3, 4]."
```

### Multiple Citations

```
Bad: [1] [2] [3] [4] [5]  (scattered)
Good: [1]–[5]             (IEEE range)
Good: [1, 3, 5]           (specific papers)
```

## Self-Citation Guidelines

- Cite your own work only when directly building upon it
- Limit self-citations to < 10% of total references
- Cite the specific work, not your CV
- Reviewers notice excessive self-citation and it hurts credibility

## Citation Consistency

- Use one style consistently throughout the paper
- Verify every in-text citation appears in the reference list
- Verify every reference is cited in text (no orphans)
- Conference abbreviations: use standard ones (see list)
- Page numbers: include when available, especially for conference papers

### Standard Abbreviations

| Full Name | Abbreviation |
|-----------|--------------|
| AAAI Conference on Artificial Intelligence | AAAI |
| International Joint Conference on AI | IJCAI |
| International Conference on Machine Learning | ICML |
| Neural Information Processing Systems | NeurIPS |
| Conference on Computer Vision and Pattern Recognition | CVPR |
| Annual Meeting of the Association for Computational Linguistics | ACL |
| International Conference on Learning Representations | ICLR |