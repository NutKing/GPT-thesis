import json
import os
import csv
from collections import defaultdict, Counter

# File paths
PYLINT_OUTPUT = 'pylint_output.json'
CATEGORY_FILE = 'pylint_rule_categorization.json'
CSV_OUTPUT = 'pylint_analysis_summary.csv'

# Load data
with open(PYLINT_OUTPUT, 'r', encoding='utf-8') as f:
    pylint_results = json.load(f)

with open(CATEGORY_FILE, 'r', encoding='utf-8') as f:
    category_map = json.load(f)

# Initialize counters
category_counts = defaultdict(int)
file_set = set()
conversation_set = set()
issue_counter = Counter()

# Process each issue
for issue in pylint_results:
    code = issue.get('message-id')
    file_path = issue.get('path')
    
    # Track files and conversations
    file_set.add(file_path)
    conversation = os.path.normpath(file_path).split(os.sep)[-2]
    conversation_set.add(conversation)
    
    # Categorize
    category = category_map.get(code, {}).get('category', 'Uncategorized')
    category_counts[category] += 1
    issue_counter[code] += 1

# Summary
print("📊 Pylint Analysis Summary")
print(f"Total Issues: {sum(category_counts.values())}")
print(f"Total Files Affected: {len(file_set)}")
print(f"Total Conversations Affected: {len(conversation_set)}\n")

for cat, count in category_counts.items():
    print(f"{cat}: {count} issues")

print("\n⭐ Top 5 Most Frequent Issues:")
for code, count in issue_counter.most_common(5):
    print(f"{code}: {count} times")

# Export to CSV
with open(CSV_OUTPUT, 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['Category', 'Total Issues'])
    for cat, count in category_counts.items():
        writer.writerow([cat, count])
    writer.writerow([])
    writer.writerow(['Top 5 Issues', 'Occurrences'])
    for code, count in issue_counter.most_common(5):
        writer.writerow([code, count])

print(f"\n✅ Summary exported to {CSV_OUTPUT}")
