#!/usr/bin/env python3
"""
Citation Finder - 智能文献引用检索工具
根据用户输入的学术文本，自动识别需要引用的陈述，并检索相关真实文献
"""

import argparse
import requests
import json
import re
import sys
from typing import List, Dict, Tuple
from dataclasses import dataclass

# API Configuration
API_KEY = "sk-user-ca162725e19a98df2a4a5b249ef7b62b4c167bf96a67b8e4"
BASE_URL = "https://ai4scholar.net"

@dataclass
class CitationNeed:
    """表示一个需要引用的陈述"""
    original_text: str
    topic: str
    suggested_queries: List[str]
    context: str = ""

@dataclass
class FoundPaper:
    """表示找到的文献"""
    title: str
    authors: str
    year: str
    journal: str
    doi: str
    pmid: str
    citations: int
    paper_id: str
    relevance_score: float = 0.0

def get_headers():
    return {
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json'
    }

def analyze_text_for_citations(text: str) -> List[CitationNeed]:
    """
    分析文本，识别需要引用的陈述
    基于学术写作特征：定义、统计数据、历史事实、科学发现等
    """
    citation_needs = []

    # 按句子分割
    sentences = re.split(r'(?<=[.!?])\s+', text)

    for i, sentence in enumerate(sentences):
        sentence = sentence.strip()
        if len(sentence) < 20:  # 跳过太短的句子
            continue

        # 获取上下文（前后各一句）
        context_start = max(0, i-1)
        context_end = min(len(sentences), i+2)
        context = ' '.join(sentences[context_start:context_end])

        # 规则1: 定义性陈述 (is/are defined as, refers to, is characterized by)
        if re.search(r'\b(is|are)\s+(defined\s+as|characterized\s+by|classified\s+as|referred\s+to\s+as)\b', sentence, re.IGNORECASE):
            queries = generate_definition_queries(sentence)
            citation_needs.append(CitationNeed(
                original_text=sentence,
                topic="Definition/Classification",
                suggested_queries=queries,
                context=context
            ))

        # 规则2: 包含具体数字/年份的陈述
        elif re.search(r'\b(first\s+described|since\s+\d{4}|in\s+\d{4}|approximately|about\s+\d+%?|over\s+\d+)\b', sentence, re.IGNORECASE):
            queries = generate_historical_queries(sentence)
            citation_needs.append(CitationNeed(
                original_text=sentence,
                topic="Historical fact/Statistics",
                suggested_queries=queries,
                context=context
            ))

        # 规则3: 疾病发病率/流行病学数据
        elif re.search(r'\b(rare|common|prevalence|incidence|frequency|rate\s+of)\b', sentence, re.IGNORECASE):
            queries = generate_epidemiology_queries(sentence)
            citation_needs.append(CitationNeed(
                original_text=sentence,
                topic="Epidemiology",
                suggested_queries=queries,
                context=context
            ))

        # 规则4: 分子/遗传学发现
        elif re.search(r'\b(gene|mutation|fusion|pathway|rearrangement|genomic|alteration|expression)\b', sentence, re.IGNORECASE):
            queries = generate_molecular_queries(sentence)
            citation_needs.append(CitationNeed(
                original_text=sentence,
                topic="Molecular/Genetic finding",
                suggested_queries=queries,
                context=context
            ))

        # 规则5: 分类标准 (WHO, classification, criteria)
        elif re.search(r'\b(WHO|classification|criteria|standard|guideline)\b', sentence, re.IGNORECASE):
            queries = generate_classification_queries(sentence)
            citation_needs.append(CitationNeed(
                original_text=sentence,
                topic="Classification/Criteria",
                suggested_queries=queries,
                context=context
            ))

        # 规则6: 技术方法描述
        elif re.search(r'\b(sequencing|RNA-seq|scRNA-seq|single-cell|microarray|mass\s+spectrometry|imaging)\b', sentence, re.IGNORECASE):
            queries = generate_method_queries(sentence)
            citation_needs.append(CitationNeed(
                original_text=sentence,
                topic="Method/Technology",
                suggested_queries=queries,
                context=context
            ))

        # 规则7: 临床行为/预后
        elif re.search(r'\b(indolent|aggressive|malignant|benign|prognosis|survival|recurrence|metastasis)\b', sentence, re.IGNORECASE):
            queries = generate_clinical_queries(sentence)
            citation_needs.append(CitationNeed(
                original_text=sentence,
                topic="Clinical behavior",
                suggested_queries=queries,
                context=context
            ))

        # 规则8: 肿瘤微环境相关
        elif re.search(r'\b(tumor\s+microenvironment|TME|stromal|immune\s+microenvironment|tumor\s+immunity)\b', sentence, re.IGNORECASE):
            queries = generate_tme_queries(sentence)
            citation_needs.append(CitationNeed(
                original_text=sentence,
                topic="Tumor microenvironment",
                suggested_queries=queries,
                context=context
            ))

    return citation_needs

def extract_key_terms(sentence: str) -> List[str]:
    """提取句子中的关键术语"""
    # 移除常见停用词
    stop_words = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been',
                  'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
                  'would', 'could', 'should', 'may', 'might', 'must', 'shall',
                  'can', 'need', 'dare', 'ought', 'used', 'to', 'of', 'in',
                  'for', 'on', 'with', 'at', 'by', 'from', 'as', 'into',
                  'through', 'during', 'before', 'after', 'above', 'below',
                  'between', 'under', 'and', 'but', 'or', 'yet', 'so', 'if',
                  'because', 'although', 'though', 'while', 'where', 'when',
                  'that', 'which', 'who', 'whom', 'whose', 'what', 'this',
                  'these', 'those', 'i', 'me', 'my', 'myself', 'we', 'our',
                  'you', 'your', 'he', 'him', 'his', 'she', 'her', 'it',
                  'its', 'they', 'them', 'their', 'most', 'some', 'many',
                  'much', 'more', 'most', 'such', 'only', 'own', 'same',
                  'few', 'little', 'less', 'least', 'other', 'another',
                  'several', 'both', 'either', 'neither', 'one', 'two',
                  'first', 'second', 'new', 'old', 'good', 'bad', 'best',
                  'better', 'high', 'low', 'higher', 'lower', 'large',
                  'small', 'larger', 'smaller', 'significant', 'important',
                  'however', 'therefore', 'thus', 'furthermore', 'moreover',
                  'additionally', 'consequently', 'nevertheless', 'nonetheless',
                  'specific', 'particular', 'certain', 'various', 'different',
                  'similar', 'due', 'based', 'using', 'used', 'shown', 'found',
                  'observed', 'reported', 'demonstrated', 'indicated',
                  'suggested', 'proposed', 'considered', 'remains'}

    words = re.findall(r'\b[a-zA-Z]+\b', sentence.lower())
    key_terms = [w for w in words if w not in stop_words and len(w) > 2]
    return list(dict.fromkeys(key_terms))  # 去重保持顺序

def generate_definition_queries(sentence: str) -> List[str]:
    """生成定义类检索词"""
    terms = extract_key_terms(sentence)
    entity = ' '.join(terms[:4])  # 取前4个关键词
    return [
        f"{entity} definition pathology",
        f"{entity} histology origin",
        f"{entity} review"
    ]

def generate_historical_queries(sentence: str) -> List[str]:
    """生成历史事实类检索词"""
    terms = extract_key_terms(sentence)
    # 提取年份
    years = re.findall(r'\b(19|20)\d{2}\b', sentence)
    year_str = years[0] if years else ""
    entity = ' '.join(terms[:3])
    queries = [f"{entity} first described case report"]
    if year_str:
        queries.append(f"{entity} history {year_str}")
    return queries

def generate_epidemiology_queries(sentence: str) -> List[str]:
    """生成流行病学类检索词"""
    terms = extract_key_terms(sentence)
    entity = ' '.join(terms[:4])
    return [
        f"{entity} epidemiology prevalence incidence",
        f"{entity} clinical features frequency"
    ]

def generate_molecular_queries(sentence: str) -> List[str]:
    """生成分子/遗传学类检索词"""
    terms = extract_key_terms(sentence)
    # 提取基因名（通常是大写或大小写混合）
    genes = re.findall(r'\b[A-Z]{2,}\d*\b', sentence)
    gene_str = ' '.join(genes[:2]) if genes else ''
    entity = ' '.join(terms[:3])

    queries = [f"{entity} molecular genetic"]
    if gene_str:
        queries.append(f"{entity} {gene_str} fusion mutation")
    return queries

def generate_classification_queries(sentence: str) -> List[str]:
    """生成分类标准类检索词"""
    terms = extract_key_terms(sentence)
    entity = ' '.join(terms[:3])
    return [
        f"{entity} WHO classification criteria",
        f"{entity} malignant benign diagnosis"
    ]

def generate_method_queries(sentence: str) -> List[str]:
    """生成方法学类检索词"""
    terms = extract_key_terms(sentence)
    # 提取方法名称
    methods = re.findall(r'(scRNA-seq|RNA-seq|single-cell|sequencing|microarray)', sentence, re.IGNORECASE)
    method_str = ' '.join(methods[:2]) if methods else terms[0] if terms else ""
    entity = ' '.join(terms[:2])

    return [
        f"{method_str} cancer tumor review",
        f"{method_str} {entity} application"
    ]

def generate_clinical_queries(sentence: str) -> List[str]:
    """生成临床行为类检索词"""
    terms = extract_key_terms(sentence)
    entity = ' '.join(terms[:4])
    return [
        f"{entity} malignant metastasis prognosis",
        f"{entity} clinical behavior outcome"
    ]

def generate_tme_queries(sentence: str) -> List[str]:
    """生成肿瘤微环境类检索词"""
    terms = extract_key_terms(sentence)
    entity = ' '.join(terms[:3])
    return [
        f"tumor microenvironment {entity} progression",
        f"TME {entity} immunotherapy review"
    ]

def search_papers(query: str, limit: int = 5) -> List[FoundPaper]:
    """使用 AI4Scholar API 搜索论文"""
    url = f"{BASE_URL}/graph/v1/paper/search"
    params = {
        'query': query,
        'limit': limit,
        'fields': 'paperId,title,authors,year,abstract,citationCount,venue,externalIds,journal'
    }

    try:
        response = requests.get(url, headers=get_headers(), params=params, timeout=30)
        if response.status_code != 200:
            print(f"  ⚠️  API error: HTTP {response.status_code}")
            return []

        data = response.json()
        papers = data.get('data', [])

        results = []
        for paper in papers:
            authors = paper.get('authors', [])
            author_names = ', '.join([a.get('name', '') for a in authors[:3]])
            if len(authors) > 3:
                author_names += f" et al."

            external_ids = paper.get('externalIds', {})

            results.append(FoundPaper(
                title=paper.get('title', 'N/A'),
                authors=author_names,
                year=str(paper.get('year', 'N/A')),
                journal=paper.get('venue', paper.get('journal', {}).get('name', 'N/A')),
                doi=external_ids.get('DOI', ''),
                pmid=external_ids.get('PubMed', ''),
                citations=paper.get('citationCount', 0),
                paper_id=paper.get('paperId', '')
            ))

        return results

    except Exception as e:
        print(f"  ⚠️  Search error: {e}")
        return []

def format_citation_report(citation_needs: List[CitationNeed], all_results: Dict[int, List[FoundPaper]], output_format: str = "markdown") -> str:
    """格式化引用报告"""

    lines = []

    if output_format == "markdown":
        lines.append("# 文献引用检索报告\n")
        lines.append(f"**生成时间**: {json.loads(requests.get('http://worldtimeapi.org/api/ip').text)['datetime'][:10] if False else 'Today'}\n")
        lines.append("---\n")

        for i, need in enumerate(citation_needs, 1):
            lines.append(f"\n## {i}. {need.topic}\n")
            lines.append(f"**原文**: {need.original_text}\n")

            papers = all_results.get(i-1, [])
            if papers:
                lines.append(f"\n**推荐引用 ({len(papers)}篇)**:\n")
                for j, paper in enumerate(papers[:3], 1):  # 只显示前3篇
                    lines.append(f"\n### {j}. {paper.title}\n")
                    lines.append(f"- **作者**: {paper.authors}\n")
                    lines.append(f"- **期刊**: {paper.journal}\n")
                    lines.append(f"- **年份**: {paper.year}\n")
                    lines.append(f"- **被引**: {paper.citations}次\n")
                    if paper.doi:
                        lines.append(f"- **DOI**: {paper.doi}\n")
                    if paper.pmid:
                        lines.append(f"- **PMID**: {paper.pmid}\n")
            else:
                lines.append("\n⚠️ 未找到相关文献，建议手动检索以下关键词:\n")
                for q in need.suggested_queries:
                    lines.append(f"- `{q}`\n")

            lines.append("\n---\n")

    return ''.join(lines)

def main():
    parser = argparse.ArgumentParser(
        description='Citation Finder - 智能文献引用检索工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
使用示例:
  # 从文件读取文本并检索引用
  python citation_finder.py --input article.txt --output citations.md

  # 直接输入文本
  python citation_finder.py --text "Glomus tumors are rare perivascular neoplasms..."

  # 输出为JSON格式
  python citation_finder.py --input article.txt --format json
        '''
    )

    parser.add_argument('--input', '-i', help='输入文件路径 (.txt)')
    parser.add_argument('--text', '-t', help='直接输入文本内容')
    parser.add_argument('--output', '-o', default='citation_report.md', help='输出文件路径 (默认: citation_report.md)')
    parser.add_argument('--format', choices=['markdown', 'json'], default='markdown', help='输出格式')
    parser.add_argument('--max-results', type=int, default=5, help='每个查询返回的最大结果数 (默认: 5)')

    args = parser.parse_args()

    # 获取输入文本
    if args.input:
        try:
            with open(args.input, 'r', encoding='utf-8') as f:
                text = f.read()
        except FileNotFoundError:
            print(f"❌ 错误: 文件不存在 {args.input}")
            sys.exit(1)
    elif args.text:
        text = args.text
    else:
        # 从标准输入读取
        print("请输入需要分析的文本 (Ctrl+D 结束):")
        text = sys.stdin.read()

    if not text.strip():
        print("❌ 错误: 输入文本为空")
        sys.exit(1)

    print("=" * 70)
    print("🔍 Citation Finder - 智能文献引用检索")
    print("=" * 70)

    # 分析文本
    print("\n📋 步骤 1: 分析文本，识别需要引用的陈述...")
    citation_needs = analyze_text_for_citations(text)
    print(f"   ✓ 识别到 {len(citation_needs)} 处需要引用\n")

    # 检索文献
    print("📚 步骤 2: 检索相关文献...")
    all_results = {}

    for i, need in enumerate(citation_needs):
        print(f"\n   [{i+1}/{len(citation_needs)}] {need.topic}")
        print(f"   原文: {need.original_text[:80]}...")

        best_papers = []
        for query in need.suggested_queries[:2]:  # 每个主题最多2个查询
            print(f"   🔎 检索: {query}")
            papers = search_papers(query, limit=args.max_results)

            # 去重并合并结果
            for p in papers:
                if p.paper_id not in [bp.paper_id for bp in best_papers]:
                    best_papers.append(p)

        all_results[i] = best_papers[:3]  # 保留前3篇
        print(f"   ✓ 找到 {len(all_results[i])} 篇相关文献")

    # 生成报告
    print("\n📝 步骤 3: 生成引用报告...")
    report = format_citation_report(citation_needs, all_results, args.format)

    # 保存输出
    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"\n✅ 完成！报告已保存至: {args.output}")
    print(f"   共识别 {len(citation_needs)} 处引用需求")
    print(f"   共检索到 {sum(len(p) for p in all_results.values())} 篇文献")

if __name__ == "__main__":
    main()
