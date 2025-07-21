import json
import matplotlib.pyplot as plt
from collections import Counter
import numpy as np

# Load results
with open(r"C:\Users\USER\Downloads\THESIS2\linter_analysis_results.json", 'r', encoding='utf-8') as f:
    results = json.load(f)

# Initialize counters
error_issues = Counter()
convention_issues = Counter()
warning_issues = Counter()
per_snippet_issues = []

# Categorize issues
for k, r in results.items():
    issues = r["linter_results"]["fetched_issues"]
    snippet_issues = 0
    for issue in issues:
        code = issue["code"]
        snippet_issues += 1
        if code.startswith('E'):
            error_issues[code] += 1
        elif code.startswith('C'):
            convention_issues[code] += 1
        elif code.startswith('W'):
            warning_issues[code] += 1
    per_snippet_issues.append(snippet_issues)

# Print statistics
print(f"Total snippets: {len(results)}")
print(f"Python snippets: {sum(1 for k in results if k.endswith('.py'))}")
print(f"JavaScript snippets: {sum(1 for k in results if k.endswith('.js'))}")
print(f"\nTotal issues: {sum(per_snippet_issues)}")
print(f"Errors: {sum(error_issues.values())} ({sum(error_issues.values())/2849*100:.1f}%)")
print(f"Conventions: {sum(convention_issues.values())} ({sum(convention_issues.values())/2849*100:.1f}%)")
print(f"Warnings: {sum(warning_issues.values())} ({sum(warning_issues.values())/2849*100:.1f}%)")
print("\nTop 5 errors:", error_issues.most_common(5))
print("Top 5 conventions:", convention_issues.most_common(5))
print("Top 5 warnings:", warning_issues.most_common(5))
print(f"\nAverage issues per snippet: {np.mean(per_snippet_issues):.1f}")
print(f"Median issues per snippet: {np.median(per_snippet_issues):.1f}")
print(f"Max issues in a snippet: {max(per_snippet_issues)}")

# Optional: Plot top issues
top_issues = (error_issues + convention_issues + warning_issues).most_common(5)
codes, counts = zip(*top_issues)
plt.figure(figsize=(10, 6))
plt.bar(codes, counts, color='skyblue')
plt.title('Top 5 Linter Issues in Reused ChatGPT-Generated Code')
plt.xlabel('Issue Code')
plt.ylabel('Frequency')
plt.savefig(r"C:\Users\USER\Downloads\THESIS2\top_issues.png")
plt.close()
print("Plot saved to C:\\Users\\USER\\Downloads\\THESIS2\\top_issues.png")