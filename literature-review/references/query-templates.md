# Search Query Templates

Templates for constructing effective literature search queries.

## PubMed Query Syntax

### Field Qualifiers
| Qualifier | Description | Example |
|-----------|-------------|---------|
| [Title/Abstract] | Search in title and abstract | `"term"[Title/Abstract]` |
| [Title] | Search in title only | `"term"[Title]` |
| [MeSH] | MeSH heading | `"term"[MeSH]` |
| [Author] | Author name | `"Smith J"[Author]` |
| [Journal] | Journal name | `"Gastroenterology"[Journal]` |

### Boolean Operators
| Operator | Description | Example |
|----------|-------------|---------|
| OR | Include either term | `"term1" OR "term2"` |
| AND | Include both terms | `"term1" AND "term2"` |
| NOT | Exclude term | `"term1" NOT "term2"` |

### Query Template
```
("primary term"[Title/Abstract] OR "variant1"[Title/Abstract] OR "variant2"[Title/Abstract])
NOT
("exclude1"[Title] OR "exclude2"[Title] OR "exclude3"[Title])
```

## Scopus Query Syntax

### Field Qualifiers
| Qualifier | Description | Example |
|-----------|-------------|---------|
| TITLE-ABS-KEY | Title, abstract, keywords | `TITLE-ABS-KEY("term")` |
| TITLE | Title only | `TITLE("term")` |
| AUTH | Author | `AUTH("Smith")` |
| SRCTITLE | Journal name | `SRCTITLE("Gastroenterology")` |

### Query Template
```
TITLE-ABS-KEY("primary term" OR "variant1" OR "variant2")
AND NOT
TITLE("exclude1" OR "exclude2" OR "exclude3")
```

## Common Search Patterns

### Pattern 1: Disease + Treatment
```
("disease name"[Title/Abstract])
AND
("treatment"[Title/Abstract] OR "therapy"[Title/Abstract] OR "drug"[Title/Abstract])
```

### Pattern 2: Population + Outcome
```
("population"[Title/Abstract] OR "subgroup"[Title/Abstract])
AND
("outcome"[Title/Abstract])
```

### Pattern 3: Methodology + Application
```
("methodology"[Title/Abstract] OR "technique"[Title/Abstract])
AND
("application field"[Title/Abstract])
```

### Pattern 4: Biomarker + Disease
```
("biomarker"[Title/Abstract])
AND
("disease"[Title/Abstract])
AND
("diagnosis"[Title/Abstract] OR "prognosis"[Title/Abstract])
```

## Exclusion Strategies

### Common Exclusions by Field

**Clinical Research:**
- `case report` - Low evidence
- `case presentation` - Low evidence
- `letter` - Not full article
- `editorial` - Opinion piece

**Basic Science:**
- `review` (if seeking primary research)
- `systematic review` - Secondary literature

**Disease-Specific Exclusions:**

| Disease | Common Confusions to Exclude |
|---------|------------------------------|
| IBD | `irritable bowel syndrome`, `IBS` |
| Alzheimer's | `vascular dementia` (if not wanted) |
| Diabetes T2 | `type 1 diabetes` (if not wanted) |
| Heart Failure | `kidney failure` |

## Query Optimization Tips

### Problem: Too Many Results

1. Add more specific terms with AND
2. Use phrase searching: `"exact phrase"`
3. Apply publication date filters
4. Limit to MeSH terms
5. Add exclusions

### Problem: Too Few Results

1. Add synonyms with OR
2. Check spelling variants
3. Use truncation: `term*` (Scopus)
4. Remove some exclusions
5. Broaden field qualifiers

### Problem: Low Relevance

1. Analyze false positives
2. Add specific exclusions
3. Use TITLE instead of TITLE-ABS-KEY
4. Combine with publication type filters

## PubMed URL Encoding

Special characters need encoding:

| Character | Encoded |
|-----------|---------|
| Space | `+` or `%20` |
| Quote | `%22` |
| Parentheses | `%28` `%29` |
| Brackets | `%5B` `%5D` |

Example URL:
```
https://pubmed.ncbi.nlm.nih.gov/?term=%22inflammatory+bowel+disease%22%5BTitle%2FAbstract%5D&sort=date
```

## Example Queries

### IBD (Inflammatory Bowel Disease)

**PubMed:**
```
("inflammatory bowel disease"[Title/Abstract] OR "Crohn disease"[Title/Abstract] OR "Crohn's disease"[Title/Abstract] OR "ulcerative colitis"[Title/Abstract])
NOT
("irritable bowel syndrome"[Title] OR "IBS"[Title] OR "case report"[Title] OR "case presentation"[Title])
```

**Scopus:**
```
TITLE-ABS-KEY("inflammatory bowel disease" OR "Crohn's disease" OR "Crohn disease" OR "ulcerative colitis")
AND NOT
TITLE("irritable bowel syndrome" OR "IBS" OR "case report" OR "case presentation")
```

### Machine Learning in Healthcare

**PubMed:**
```
("machine learning"[Title/Abstract] OR "deep learning"[Title/Abstract] OR "artificial intelligence"[Title/Abstract])
AND
("diagnosis"[Title/Abstract] OR "prediction"[Title/Abstract])
NOT
("review"[Title])
```

### Biomarkers in Cancer

**PubMed:**
```
("biomarker"[Title/Abstract] OR "biomarkers"[Title/Abstract])
AND
("cancer"[Title/Abstract] OR "tumor"[Title/Abstract])
AND
("prognosis"[Title/Abstract] OR "diagnosis"[Title/Abstract] OR "prediction"[Title/Abstract])
NOT
("case report"[Title])
```