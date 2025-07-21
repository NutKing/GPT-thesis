import json
from collections import Counter
with open(r"C:\Users\USER\Downloads\THESIS2\linter_analysis_results.json", 'r', encoding='utf-8') as f:
    results = json.load(f)
error_issues = Counter()
convention_issues = Counter()
for k, r in results.items():
    for issue in r["linter_results"]["fetched_issues"]:
        counter = error_issues if issue["code"].startswith('E') else convention_issues if issue["code"].startswith('C') else Counter()
        counter[issue["code"]] += 1
print(f"Total errors: {sum(error_issues.values())}")
print("Top errors:", error_issues.most_common(5))
print(f"Total conventions: {sum(convention_issues.values())}")
print("Top conventions:", convention_issues.most_common(5))