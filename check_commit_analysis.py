import json

with open(r"C:\Users\USER\Downloads\THESIS2\commit_analysis_results.json", 'r', encoding='utf-8') as f:
    results = json.load(f)

py_snippets = [k for k in results if k.endswith('.py')]
js_snippets = [k for k in results if k.endswith('.js')]

print(f"Total snippets: {len(results)}")
print(f"Python snippets: {len(py_snippets)}")
print("Sample Python snippets (first 3):", py_snippets[:3])
print(f"JavaScript snippets: {len(js_snippets)}")
print("Sample JavaScript snippets (first 3):", js_snippets[:3])

# Inspect a JavaScript snippet's code (if any)
if js_snippets:
    js_snippet = js_snippets[0]
    print(f"\nInitial code for {js_snippet} (first 500 chars):")
    print(results[js_snippet]["initial_code"][:500])
    print(f"Final code for {js_snippet} (first 500 chars):")
    print(results[js_snippet]["final_code"][:500])