import json
with open(r"C:\Users\USER\Downloads\THESIS2\snippet_reuse_results.json", 'r', encoding='utf-8') as f:
    results = json.load(f)
js_snippets = [(k, v["fetched_code"]) for k, v in results.items() if k.endswith('.js') and v["status"] == "original_missing"]
print(f"JavaScript snippets: {len(js_snippets)}")
for i, (path, code) in enumerate(js_snippets[:3]):
    print(f"\nSnippet {i+1}: {path}")
    print("Code (first 500 chars):", code[:500] if code else "Empty")