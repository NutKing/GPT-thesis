import json
from collections import Counter
with open(r"C:\Users\USER\Downloads\THESIS2\linter_analysis_results.json", 'r') as f:
    results = json.load(f)
issue_types = Counter()
for r in results.values():
    for issue in r["linter_results"]["fetched_issues"]:
        issue_types[issue["code"]] += 1
print("Most common linter issues:", issue_types.most_common(5))