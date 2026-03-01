#!/usr/bin/env python3
"""
PubMed Journal Article Downloader
Usage: python fetch_journal_articles.py <journal_name> <years_back> [output_format]
Example: python fetch_journal_articles.py "Nature" 5 csv
"""

import sys
import os
import time
import csv
import json
import xml.etree.ElementTree as ET
from urllib.parse import urlencode
from urllib.request import urlopen, Request
import ssl
from datetime import datetime

# NCBI API Key
API_KEY = os.environ.get('NCBI_API_KEY', '3b4ce1d9fe79b0bdfd598602ab26959ef909')
BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"

def esearch(db, term, retmax=20000):
    """Search NCBI and return IDs."""
    params = {
        'db': db,
        'term': term,
        'retmax': retmax,
        'usehistory': 'y',
        'api_key': API_KEY,
        'retmode': 'json'
    }
    url = f"{BASE_URL}/esearch.fcgi?{urlencode(params)}"

    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    req = Request(url)
    with urlopen(req, context=ctx) as response:
        data = json.load(response)

    return data.get('esearchresult', {})

def efetch_xml(db, ids):
    """Fetch article details by IDs as XML."""
    if not ids:
        return []

    results = []
    batch_size = 100

    for i in range(0, len(ids), batch_size):
        batch = ids[i:i+batch_size]
        idlist = ','.join(map(str, batch))

        params = {
            'db': db,
            'id': idlist,
            'retmode': 'xml',
            'api_key': API_KEY,
            'rettype': 'abstract'
        }
        url = f"{BASE_URL}/efetch.fcgi?{urlencode(params)}"

        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

        req = Request(url)
        try:
            with urlopen(req, context=ctx) as response:
                xml_data = response.read().decode('utf-8')
                results.append(xml_data)
        except Exception as e:
            print(f"Error fetching batch {i//batch_size + 1}: {e}", file=sys.stderr)

        # Rate limiting
        time.sleep(0.35)

    return results

def parse_articles(xml_results):
    """Parse XML results into structured list."""
    articles = []

    for xml_data in xml_results:
        if not xml_data:
            continue

        try:
            root = ET.fromstring(xml_data)
            for article in root.findall('.//PubmedArticle'):
                pmid = article.find('.//PMID')
                title = article.find('.//ArticleTitle')
                journal = article.find('.//Journal/Title')
                pubdate = article.find('.//Journal/JournalIssue/PubDate/Year')

                # Authors
                authors = article.findall('.//Author')
                author_names = []
                for author in authors:
                    last_name = author.find('LastName')
                    fore_name = author.find('ForeName')
                    if last_name is not None:
                        name = last_name.text
                        if fore_name is not None:
                            name = f"{fore_name.text} {name}"
                        author_names.append(name)

                # Abstract
                abstract_elem = article.find('.//AbstractText')
                abstract = abstract_elem.text if abstract_elem is not None else 'N/A'

                articles.append({
                    'pmid': pmid.text if pmid is not None else 'N/A',
                    'title': title.text if title is not None else 'N/A',
                    'authors': author_names,
                    'journal': journal.text if journal is not None else 'N/A',
                    'pubdate': pubdate.text if pubdate is not None else 'N/A',
                    'abstract': abstract if abstract else 'N/A'
                })
        except ET.ParseError as e:
            print(f"XML parse error: {e}", file=sys.stderr)
            continue

    return articles

def format_authors(authors):
    """Format authors list as string."""
    if not authors:
        return 'N/A'

    names = authors[:10]
    if len(authors) > 10:
        return ', '.join(names) + f', et al. ({len(authors)} total)'
    return ', '.join(names)

def save_csv(articles, output_file):
    """Save articles to CSV."""
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['PMID', 'Title', 'Authors', 'Journal', 'PubDate', 'Abstract'])

        for art in articles:
            writer.writerow([
                art['pmid'],
                art['title'],
                format_authors(art['authors']),
                art['journal'],
                art['pubdate'],
                art['abstract']
            ])

    print(f"Saved {len(articles)} articles to {output_file}")

def save_json(articles, output_file):
    """Save articles to JSON."""
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(articles, f, ensure_ascii=False, indent=2)

    print(f"Saved {len(articles)} articles to {output_file}")

def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)

    journal_name = sys.argv[1]
    years_back = int(sys.argv[2])
    output_format = sys.argv[3] if len(sys.argv) > 3 else 'csv'

    # Build search query
    current_year = datetime.now().year
    start_year = current_year - years_back

    term = f'{journal_name}[Journal] AND {start_year}:{current_year}[DP]'
    print(f"Searching: {term}")

    # Step 1: Search
    print("Searching PubMed...")
    search_result = esearch('pubmed', term)
    idlist = search_result.get('idlist', [])

    if not idlist:
        print("No articles found.")
        sys.exit(0)

    print(f"Found {len(idlist)} articles")

    # Step 2: Fetch details
    print("Fetching article details (this may take a while)...")
    xml_results = efetch_xml('pubmed', idlist)

    # Step 3: Parse
    articles = parse_articles(xml_results)
    print(f"Parsed {len(articles)} articles")

    # Step 4: Save
    safe_name = journal_name.replace(' ', '_').replace('/', '_')
    timestamp = datetime.now().strftime('%Y%m%d')

    if output_format == 'json':
        output_file = f"{safe_name}_{years_back}years_{timestamp}.json"
        save_json(articles, output_file)
    else:
        output_file = f"{safe_name}_{years_back}years_{timestamp}.csv"
        save_csv(articles, output_file)

if __name__ == '__main__':
    main()
