import json
import csv
import os
from collections import defaultdict, Counter

# === File Paths ===
PYLINT_OUTPUT = '../Data/LintersResult/pylint_output.json'
CATEGORIZATION_FILE = 'CategorizationLinters/pylint_rule_categorization.json'
SUCCESSFUL_SNIPPETS_FILE = '../Data/snippet_lists/successful_python_snippets.txt'
OUTPUT_CSV = 'pylint_analysis_summary.csv'

# === Load Data ===
with open(PYLINT_OUTPUT, 'r') as f:
    pylint_results = json.load(f)

with open(CATEGORIZATION_FILE, 'r') as f:
    category_map = json.load(f)

with open(SUCCESSFUL_SNIPPETS_FILE, 'r') as f:
    successful_snippets = f.read().splitlines()

# === Initialize Counters ===
category_issue_count = defaultdict(int)
category_conversations = defaultdict(set)
rule_frequency = defaultdict(Counter)

def extract_conversation_name(filepath):
    parts = filepath.split('/')
    for part in parts:
        if part.startswith('conversation'):
            return part
    return "unknown_conversation"

# === Process Each Issue ===
for issue in pylint_results:
    file_path = issue.get('path')
    code = issue.get('message-id')

    # Skip if file is not in successful snippets
    full_file_path = os.path.normpath(file_path)
    matched_snippet = next((s for s in successful_snippets if s.endswith(full_file_path)), None)
    if not matched_snippet:
        continue

    category = category_map.get(code, {}).get('category', 'Uncategorized')
    category_issue_count[category] += 1

    conversation = extract_conversation_name(matched_snippet)
    category_conversations[category].add(conversation)

    rule_frequency[category][code] += 1

# === Output Summary ===
print("\n📊 Pylint Analysis Summary\n" + "-"*40)

summary_rows = []
for category in ['Code Style', 'Code Smell', 'Potential Bug', 'Code Vulnerability', 'Uncategorized']:
    total_issues = category_issue_count[category]
    conversations_affected = len(category_conversations[category])
    top_rules = rule_frequency[category].most_common(3)

    print(f"\n{category}:")
    print(f" - Total Issues: {total_issues}")
    print(f" - Conversations Affected: {conversations_affected}")
    for rule, count in top_rules:
        print(f"   - {rule}: {count} times")

    summary_rows.append({
        'Category': category,
        'Total Issues': total_issues,
        'Conversations Affected': conversations_affected,
        'Top Rules': ', '.join([f"{r} ({c})" for r, c in top_rules])
    })

# === Export to CSV ===
with open(OUTPUT_CSV, 'w', newline='', encoding='utf-8') as csvfile:
    fieldnames = ['Category', 'Total Issues', 'Conversations Affected', 'Top Rules']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()
    for row in summary_rows:
        writer.writerow(row)

print(f"\n✅ Summary exported to {OUTPUT_CSV}")
