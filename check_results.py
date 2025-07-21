import json
with open(r"C:\Users\USER\Downloads\THESIS2\snippet_reuse_results.json", 'r', encoding='utf-8') as f:
    results = json.load(f)
status_counts = {}
for _, v in results.items():
    status = v["status"]
    status_counts[status] = status_counts.get(status, 0) + 1
valid_snippets = [(k, v) for k, v in results.items() if v["status"] in ["exact", "modified"]]
print(f"Total snippets: {len(results)}")
print(f"Valid snippets (exact or modified): {len(valid_snippets)}")
print(f"Status counts: {status_counts}")
print("Sample entries (first 10):", list(results.items())[:10])
print("Sample URLs for non-failed statuses:", [(k, v["url"]) for k, v in results.items() if not v["status"].startswith("fetch_failed")][:5])