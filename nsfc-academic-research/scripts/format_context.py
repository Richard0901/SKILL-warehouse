import argparse
import json


def to_markdown(payload: dict) -> str:
    answers = payload.get("answers", [])
    results = payload.get("results", [])

    lines = []
    lines.append("# Tavily Deep Search Context")
    lines.append("")
    lines.append(f"- Seed Query: {payload.get('seed_query', '')}")
    lines.append(f"- Total Unique Sources: {payload.get('total_unique', 0)}")
    lines.append("")

    if answers:
        lines.append("## Aggregated Short Answers")
        lines.append("")
        for i, ans in enumerate(answers, start=1):
            lines.append(f"{i}. {ans}")
        lines.append("")

    lines.append("## Sources")
    lines.append("")
    for idx, item in enumerate(results, start=1):
        pdf_tag = " [PDF]" if item.get("is_pdf") else ""
        lines.append(f"### [Source {idx}] {item.get('title', '').strip()}{pdf_tag}")
        lines.append(f"- URL: {item.get('url', '').strip()}")
        if item.get("published_date"):
            lines.append(f"- Published: {item.get('published_date')}")
        if item.get("score") is not None:
            lines.append(f"- Relevance Score: {item.get('score')}")
        snippet = (item.get("content") or "").strip()
        if snippet:
            lines.append(f"- Snippet: {snippet}")
        lines.append("")

    return "\n".join(lines).strip() + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert Tavily JSON into markdown citation context")
    parser.add_argument("--in", dest="input_path", required=True)
    parser.add_argument("--out", dest="output_path", default="context.md")
    args = parser.parse_args()

    with open(args.input_path, "r", encoding="utf-8") as f:
        payload = json.load(f)

    text = to_markdown(payload)
    with open(args.output_path, "w", encoding="utf-8") as f:
        f.write(text)

    print(f"Saved markdown context to {args.output_path}")


if __name__ == "__main__":
    main()
