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

## AAAI/IJCAI Specific Format

### In-Text Citation

```
Single author: (Author, 2024)
Two authors: (Author and Author, 2024)
Three+: (Author et al., 2024)

Multiple citations: (Author1, 2023; Author2, 2024)
```

### Reference List

```
[Author1, First name Last name, and Author2, First name Last name. 2024. 
 Title of the paper. In Proceedings of the AAAI Conference on Artificial 
 Intelligence, pages 1-10.
```

## Citation Elements

### Required Fields

| Type | Required Fields |
|------|-----------------|
| Conference | Authors, Title, Conference, Year, Pages |
| Journal | Authors, Title, Journal, Volume, Issue, Pages, Year |
| arXiv | Authors, Title, arXiv ID, Year |
| Book | Authors, Title, Edition, Publisher, Year |

### Optional Fields

| Type | Optional Fields |
|------|-----------------|
| Conference | DOI, URL |
| Journal | DOI, URL, Month |
| arXiv | URL |
| Book | ISBN, City, Pages |

## Formatting Rules

### Author Names

```
Single: J. Smith
Two: J. Smith and R. Jones
Three: J. Smith, R. Jones, and T. Lee
Four+: J. Smith et al. (in-text, list all in reference)
```

### Title Capitalization

```
IEEE: Sentence case for article titles, Title Case for journal names
ACM: Title Case for all titles
APA: Sentence case for article titles
```

### Abbreviations

Common conference abbreviations:

| Full Name | Abbreviation |
|-----------|--------------|
| AAAI Conference on Artificial Intelligence | AAAI |
| International Joint Conference on Artificial Intelligence | IJCAI |
| International Conference on Machine Learning | ICML |
| Neural Information Processing Systems | NeurIPS |
| Conference on Computer Vision and Pattern Recognition | CVPR |
| Annual Meeting of the Association for Computational Linguistics | ACL |

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

## Common Mistakes to Avoid

1. Inconsistent author name formatting
2. Missing page numbers for conference papers
3. Wrong volume/issue numbers
4. Outdated conference names
5. Missing DOI when available

## Cross-Reference Format

When citing multiple related works:

```
Recent advances in [domain] have proposed various approaches 
[1], [2], [3]. Among them, Method A [4] achieves the best 
performance, while Method B [5] offers better efficiency.
```

## Self-Citation Guidelines

- Limit self-citations to relevant work only
- Do not exceed recommended percentage (typically < 10%)
- Include recent relevant self-citations
- Avoid excessive citations to the same paper