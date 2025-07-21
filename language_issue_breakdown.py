import json
from collections import Counter
with open(r"C:\Users\USER\Downloads\THESIS2\linter_analysis_results.json", 'r', encoding='utf-8') as f:
    results = json.load(f)
py_issues = Counter()
js_issues = Counter()
for k, r in results.items():
    issues = r["linter_results"]["fetched_issues"]
    counter = py_issues if k.endswith('.py') else js_issues if k.endswith('.js') else Counter()
    for issue in issues:
        counter[issue["code"]] += 1
print(f"Python snippets: {sum(1 for k in results if k.endswith('.py'))}")
print("Top Python issues:", py_issues.most_common(5))
print(f"JavaScript snippets: {sum(1 for k in results if k.endswith('.js'))}")
print("Top JavaScript issues:", js_issues.most_common(5))