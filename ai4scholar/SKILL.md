---
name: ai4scholar
description: 学术文献检索与PDF下载工具。使用场景：搜索学术论文、下载PDF原文、查询论文引用和参考文献、批量下载论文。
---

# AI4Scholar 学术文献工具

本工具提供学术论文检索、PDF下载、引用分析等功能，覆盖 arXiv、PubMed、Semantic Scholar、bioRxiv、medRxiv 等学术平台。

## API 配置

- **API Key**: `sk-user-ca162725e19a98df2a4a5b249ef7b62b4c167bf96a67b8e4`
- **MCP 服务地址**: `https://mcp.ai4scholar.net/sse`
- **认证方式**: `Authorization: Bearer <api-key>`

## 支持的工具

### arXiv（3个工具）

| 工具 | 说明 |
|------|------|
| search_arxiv | 在 arXiv 上按关键词搜索论文 |
| download_arxiv | 通过 arXiv ID 下载 PDF |
| read_arxiv_paper | 下载 PDF 并提取全文内容 |

**参数**:
- search_arxiv(query, max_results=10)
- download_arxiv(paper_id, save_path="./downloads")
- read_arxiv_paper(paper_id, save_path="./downloads")

### PubMed（4个工具）

| 工具 | 说明 |
|------|------|
| search_pubmed | 搜索生物医学论文 |
| get_pubmed_paper_detail | 获取论文详细元数据 |
| get_pubmed_citations | 获取引用了该论文的所有论文 |
| get_pubmed_related | 获取相关论文 |

**注意**: PubMed 不支持直接下载 PDF。

### Semantic Scholar（10个工具）

| 工具 | 说明 |
|------|------|
| search_semantic | 搜索论文，支持年份过滤 |
| download_semantic | 下载论文 PDF |
| read_semantic_paper | 下载 PDF 并提取全文 |
| get_semantic_citations | 获取引用列表 |
| get_semantic_references | 获取参考文献列表 |
| search_semantic_authors | 搜索学者 |
| get_semantic_author_papers | 获取学者论文列表 |
| get_semantic_recommendations | 基于示例论文推荐 |
| get_semantic_recommendations_for_paper | 基于单篇论文推荐相似论文 |
| search_semantic_snippets | 在论文全文中搜索文本片段 |

### bioRxiv（3个工具）

| 工具 | 说明 |
|------|------|
| search_biorxiv | 搜索生物学预印本 |
| download_biorxiv | 下载 PDF |
| read_biorxiv_paper | 下载并提取全文 |

### medRxiv（3个工具）

| 工具 | 说明 |
|------|------|
| search_medrxiv | 搜索医学预印本 |
| download_medrxiv | 下载 PDF |
| read_medrxiv_paper | 下载并提取全文 |

## 常用场景

### 搜索论文
```
"帮我搜索关于大语言模型的最新论文"
"在 Semantic Scholar 上搜索 2023-2025 年关于 transformer 的论文"
```

### 下载 PDF
```
"下载 arXiv 论文 2106.12345"
"下载 Semantic Scholar 论文 DOI:10.18653/v1/N18-3011"
```

### 阅读全文
```
"阅读 arXiv 论文 2301.00234 的全文"
```

### 引用查询
```
"哪些论文引用了 ARXIV:2106.15928？"
"列出这篇论文的参考文献：DOI:10.18653/v1/N18-3011"
```

### 学者信息
```
"在 Semantic Scholar 上搜索学者 Yann LeCun"
"列出 Semantic Scholar 作者 1741101 的所有论文"
```

### 相关推荐
```
"推荐与 ARXIV:2106.15928 类似的论文"
```

## 批量下载 PDF

使用 Python 脚本批量下载论文：

```bash
python S17_pdf-download.py --api-key YOUR_KEY --doi "10.1038/s41586-021-03819-2" -o ./output
python S17_pdf-download.py --api-key YOUR_KEY --title "Attention is All You Need" -o ./output
python S17_pdf-download.py --api-key YOUR_KEY --csv papers.csv -o ./batch_output
```

详细使用说明见 references/download.md

## 项目文件位置

- MCP配置: `D:\Life\shared\inbox\Ai4scholar\MCP.md`
- PDF下载脚本: `D:\Life\shared\inbox\Ai4scholar\S17_pdf-download\S17_pdf-download.py`
- API Key: `D:\Life\shared\inbox\Ai4scholar\APIKEY.MD`
