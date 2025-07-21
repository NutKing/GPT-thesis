import subprocess
import json
import csv
import os
from collections import defaultdict, Counter
from tqdm import tqdm

SUCCESSFUL_SNIPPETS = 'successful_python_snippets.txt'
FLAKE8_OUTPUT = 'flake8_output.json'
OUTPUT_CSV = 'flake8_analysis_summary.csv'

# === Define Prefix-Based Categorization ===
def categorize_flake8_code(code):
    if code.startswith(('E', 'W', 'N')):
        return 'Code Style'
    elif code.startswith('F'):
        return 'Potential Bug'
    elif code.startswith('C'):
        return 'Code Smell'
    elif code.startswith('B'):
        return 'Potential Bug'
    elif code.startswith('S'):
        return 'Code Vulnerability'
    else:
        return 'Uncategorized'

# === Extract Conversation from Parent Folder ===
def extract_conversation(filepath):
    normalized = filepath.replace('\\', '/')
    parts = normalized.split('/')
    if len(parts) >= 2:
        return parts[-2]  # Parent folder as conversation name
    return "unknown_conversation"

# === Step 1: Load and Normalize Paths ===
with open(SUCCESSFUL_SNIPPETS, 'r') as f:
    files = [line.strip() for line in f if line.strip()]

clean_files = [os.path.abspath(f).replace('\\', '/') for f in files]

print(f"🚀 Running Flake8 on {len(clean_files)} files...\n")

# === Step 2: Run Flake8 ===
subprocess.run(['flake8', '--format=json'] + clean_files, stdout=open(FLAKE8_OUTPUT, 'w'))

print(f"✅ Flake8 scan completed. Output saved to {FLAKE8_OUTPUT}")

# === Step 3: Load Flake8 Output ===
with open(FLAKE8_OUTPUT, 'r') as f:
    flake8_results = json.load(f)

# === Step 4: Initialize Counters ===
category_issue_count = defaultdict(int)
category_conversations = defaultdict(set)
category_files = defaultdict(set)
rule_frequency = defaultdict(Counter)

# === Step 5: Process Each File's Issues ===
for file_path, issues in tqdm(flake8_results.items(), desc="Processing Flake8 Results"):
    conversation = extract_conversation(file_path)

    for issue in issues:
        code = issue.get('code')
        category = categorize_flake8_code(code)
        category_issue_count[category] += 1
        category_conversations[category].add(conversation)
        category_files[category].add(file_path)
        rule_frequency[category][code] += 1

# === Step 6: Output Summary ===
print("\n📊 Flake8 Analysis Summary\n" + "-"*50)

summary_rows = []
for category in ['Code Style', 'Code Smell', 'Potential Bug', 'Code Vulnerability', 'Uncategorized']:
    total_issues = category_issue_count[category]
    conversations_affected = len(category_conversations[category])
    files_affected = len(category_files[category])
    top_rules = rule_frequency[category].most_common(3)

    print(f"\n{category}:")
    print(f" - Total Issues: {total_issues}")
    print(f" - Conversations Affected: {conversations_affected}")
    print(f" - Files Affected: {files_affected}")
    for rule, count in top_rules:
        print(f"   - {rule}: {count} times")

    summary_rows.append({
        'Category': category,
        'Total Issues': total_issues,
        'Conversations Affected': conversations_affected,
        'Files Affected': files_affected,
        'Top Rules': ', '.join([f"{r} ({c})" for r, c in top_rules])
    })

# === Step 7: Export to CSV ===
with open(OUTPUT_CSV, 'w', newline='', encoding='utf-8') as csvfile:
    fieldnames = ['Category', 'Total Issues', 'Conversations Affected', 'Files Affected', 'Top Rules']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()
    for row in summary_rows:
        writer.writerow(row)

print(f"\n✅ Summary exported to {OUTPUT_CSV}")
