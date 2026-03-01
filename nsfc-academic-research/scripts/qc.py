import json

path = r"d:\Life\shared\inbox\周医生科研馆智能体\tavily_results.json"
with open(path, encoding="utf-8") as f:
    d = json.load(f)

pdf_sources = [r for r in d["results"] if r.get("is_pdf")]
print("total_unique  :", d["total_unique"])
print("pdf_sources   :", len(pdf_sources))
print("errors        :", len(d.get("errors", [])))
print()
print("--- First 5 sources ---")
for i, r in enumerate(d["results"][:5], 1):
    title = r.get("title", "")[:72]
    url = r.get("url", "")[:80]
    pdf = " [PDF]" if r.get("is_pdf") else ""
    print(f"[{i}]{pdf} {title}")
    print(f"     {url}")
print()
print("--- PDF sources ---")
for i, r in enumerate(pdf_sources[:5], 1):
    print(f"  {r.get('url','')[:80]}")
