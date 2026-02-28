import argparse
import json
import os
import time
import urllib.request


API_URL = "https://api.tavily.com/search"


def post_json(url: str, payload: dict, timeout: int = 45) -> dict:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        body = resp.read().decode("utf-8")
    return json.loads(body)


def build_queries(seed_query: str) -> list[str]:
    return [
        seed_query,
        f"{seed_query} systematic review",
        f"{seed_query} randomized controlled trial",
        f"{seed_query} mechanism pathway",
        f"{seed_query} biomarker cohort study",
        f"{seed_query} guideline consensus",
        f"{seed_query} filetype:pdf",
        f"{seed_query} site:pubmed.ncbi.nlm.nih.gov",
        f"{seed_query} site:nature.com filetype:pdf",
        f"{seed_query} site:thelancet.com filetype:pdf",
        f"{seed_query} site:nejm.org filetype:pdf",
        f"{seed_query} site:bmj.com filetype:pdf",
    ]


def normalize_item(item: dict) -> dict:
    url = (item.get("url") or "").strip()
    title = (item.get("title") or "").strip()
    content = (item.get("content") or "").strip()
    return {
        "title": title,
        "url": url,
        "content": content,
        "score": item.get("score"),
        "published_date": item.get("published_date"),
        "is_pdf": url.lower().endswith(".pdf") or "pdf" in url.lower(),
    }


def run_search(api_key: str, query: str, max_results: int) -> dict:
    payload = {
        "api_key": api_key,
        "query": query,
        "search_depth": "advanced",
        "include_answer": True,
        "max_results": max_results,
    }
    return post_json(API_URL, payload)


def main() -> None:
    parser = argparse.ArgumentParser(description="Aggregate Tavily search results to 50+ unique sources")
    parser.add_argument("--query", required=True, help="Optimized English query")
    parser.add_argument("--min-results", type=int, default=50)
    parser.add_argument("--batch-size", type=int, default=10)
    parser.add_argument("--out", default="tavily_results.json")
    parser.add_argument("--sleep", type=float, default=0.8)
    args = parser.parse_args()

    api_key = os.environ.get("TAVILY_API_KEY", "").strip()
    if not api_key:
        raise SystemExit("Missing TAVILY_API_KEY environment variable")

    queries = build_queries(args.query)
    unique: dict[str, dict] = {}
    answers: list[str] = []
    errors: list[dict] = []

    for q in queries:
        try:
            data = run_search(api_key=api_key, query=q, max_results=args.batch_size)
            if data.get("answer"):
                answers.append(str(data.get("answer")))

            for raw in data.get("results", []) or []:
                item = normalize_item(raw)
                if not item["url"]:
                    continue
                unique[item["url"]] = item

            if len(unique) >= args.min_results:
                break
            time.sleep(args.sleep)
        except Exception as exc:
            errors.append({"query": q, "error": str(exc)})

    results = list(unique.values())
    report = {
        "seed_query": args.query,
        "min_results": args.min_results,
        "total_unique": len(results),
        "answers": answers,
        "results": results,
        "errors": errors,
    }

    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(f"Saved {len(results)} unique sources to {args.out}")


if __name__ == "__main__":
    main()
