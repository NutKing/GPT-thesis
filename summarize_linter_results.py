import json
with open(r"C:\Users\USER\Downloads\THESIS2\linter_analysis_results.json", 'r', encoding='utf-8') as f:
    results = json.load(f)
total_snippets = len(results)
total_issues = sum(r["linter_results"]["comparison"]["introduced"] for r in results.values())
print(f"Processed snippets: {total_snippets}")
print(f"Total linter issues in fetched code: {total_issues}")