---
name: literature-review
description: 学术文献调研与综述撰写。用于：(1) 根据研究主题搜索学术论文 (2) 获取文献详细信息和摘要 (3) 分析筛选文献 (4) 撰写结构化综述。当用户说"调研文献"、"写综述"、"搜索论文"、"文献分析"时使用此skill。
---

# 文献调研与综述撰写

## 概述

本skill帮助完成从文献搜索到综述撰写的完整流程。

## API配置

优先使用 ai4scholar.net API（需配置API Key）：

**API Key**: `sk-user-ca162725e19a98df2a4a5b249ef7b62b4c167bf96a67b8e4`
**Base URL**: `https://ai4scholar.net`

备用方案：使用公开API（PubMed、Semantic Scholar、arXiv）

---

## 工作流程

### 第一步：理解需求

向用户确认以下信息：
1. **研究主题/关键词** - 要调研什么主题？
2. **文献类型** - 综述(Review)、研究论文(Research)、还是都要？
3. **时间范围** - 最近5年？10年？还是不限？
4. **参考文献数量** - 需要多少篇文献？（建议20-50篇）
5. **语言偏好** - 中文还是英文？
6. **特定作者/期刊** - 是否需要包含特定作者或期刊？

### 第二步：文献搜索

**方案一：ai4scholar API（推荐）**

```python
import requests

API_KEY = "sk-user-ca162725e19a98df2a4a5b249ef7b62b4c167bf96a67b8e4"
BASE_URL = "https://ai4scholar.net"

# 搜索论文
def search_papers(query, limit=20):
    url = f"{BASE_URL}/graph/v1/paper/search"
    params = {
        'query': query,
        'limit': limit,
        'fields': 'paperId,title,authors,year,abstract,citationCount,venue,openAccessPdf,externalIds'
    }
    headers = {'Authorization': f'Bearer {API_KEY}'}
    response = requests.get(url, params=params, headers=headers)
    return response.json()

# 获取论文详情
def get_paper_detail(paper_id):
    url = f"{BASE_URL}/graph/v1/paper/{paper_id}"
    params = {
        'fields': 'paperId,title,authors,year,abstract,citationCount,venue,openAccessPdf,externalIds,publicationTypes,journal,citations,references'
    }
    headers = {'Authorization': f'Bearer {API_KEY}'}
    response = requests.get(url, params=params, headers=headers)
    return response.json()
```

**方案二：PubMed API（免费）**

```powershell
$query = [uri]::EscapeDataString("关键词")
Invoke-WebRequest -Uri "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=$query&retmode=json&retmax=50&sort=date" -UseBasicParsing
```

**方案三：Semantic Scholar API（免费）**

```powershell
$query = [System.Web.HttpUtility]::UrlEncode("关键词")
Invoke-WebRequest -Uri "https://api.semanticscholar.org/graph/v1/paper/search?query=$query&limit=50&fields=title,authors,year,abstract,citationCount" -UseBasicParsing
```

### 第三步：获取文献详情

使用 ai4scholar:

```python
# 通过 DOI 获取
def get_paper_by_doi(doi):
    url = f"{BASE_URL}/graph/v1/paper/DOI:{doi}"
    params = {'fields': 'title,authors,year,abstract,citationCount,venue,openAccessPdf,externalIds'}
    headers = {'Authorization': f'Bearer {API_KEY}'}
    return requests.get(url, params=params, headers=headers).json()

# 获取引用
def get_citations(paper_id, limit=20):
    url = f"{BASE_URL}/graph/v1/paper/{paper_id}/citations"
    params = {'limit': limit, 'fields': 'paperId,title,authors,year'}
    headers = {'Authorization': f'Bearer {API_KEY}'}
    return requests.get(url, params=params, headers=headers).json()
```

### 第四步：文献分析与筛选

根据以下标准筛选文献：
1. **相关性** - 与研究主题的相关程度
2. **影响力** - 引用次数（建议优先选择高引用）
3. **时效性** - 近期发表的重要发现
4. **质量** - 发表期刊/会议的权威性
5. **多样性** - 不同研究团队/角度

创建文献列表表格：

| # | 标题 | 作者 | 年份 | 期刊 | 引用数 | 摘要概要 |
|---|------|------|------|------|--------|----------|
| 1 | ... | ... | ... | ... | ... | ... |

### 第五步：撰写综述

综述结构建议：

```markdown
# [研究主题] 综述

## 1. 引言
- 研究背景
- 研究意义
- 综述目的

## 2. 研究方法
- 文献检索策略（数据库、时间范围、关键词）
- 筛选标准
- 纳入文献概述

## 3. 研究进展/主要发现
### 3.1 [子主题1]
### 3.2 [子主题2]
### 3.3 [子主题3]

## 4. 争议与挑战
- 当前争议点
- 未解决的问题

## 5. 未来展望
- 研究方向建议
- 技术发展趋势

## 6. 结论
- 主要结论
- 实践意义

## 参考文献
```

### 第六步：输出格式

根据用户需求输出：
- **Markdown文件** - 直接输出到workspace
- **飞书文档** - 使用feishu_doc创建

## ai4scholar MCP工具（如通过MCP调用）

| 工具 | 功能 |
|------|------|
| search_pubmed | 搜索PubMed论文 |
| get_pubmed_paper_detail | 获取论文详情 |
| get_pubmed_citations | 获取引用 |
| get_pubmed_related | 获取相关论文 |
| search_semantic | 搜索论文 |
| download_semantic | 下载PDF |

## 注意事项

1. **版权问题**：不要直接复制整篇论文内容，摘要引用需注明来源
2. **信息核实**：重要发现需交叉验证多篇文献
3. **保持客观**：综述需平衡呈现不同观点
4. **最新进展**：关注近1-2年的最新研究

## 输出文件

生成的综述保存到 workspace 目录：
- `literature_review_[主题].md` - 综述正文
- `papers/` - 文献信息汇总
