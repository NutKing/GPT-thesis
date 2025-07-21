import json
with open(r"C:\Users\USER\Downloads\THESIS2\linter_analysis_results.json", 'r', encoding='utf-8') as f:
    results = json.load(f)
js_snippets = [(k, v) for k, v in results.items() if k.endswith('.js')]
print(f"JavaScript snippets processed: {len(js_snippets)}")
print("Sample JS snippets (first 3):", js_snippets[:3])