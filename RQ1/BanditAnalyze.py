import json
import os
import pandas as pd
from collections import defaultdict, Counter

# === Load Data ===
with open('bandit_output_raw.json', 'r') as f:
    bandit_data = json.load(f)

with open('bandit_rule_categorization.json', 'r') as f:
    rule_categories = json.load(f)

results = bandit_data.get('results', [])

# === Initialize Counters ===
severity_counts = defaultdict(int)
files_per_severity = defaultdict(set)
conversations_per_severity = defaultdict(set)
issue_counter = Counter()

# === Process Each Issue ===
for issue in results:
    rule = issue.get('test_id')
    filename = issue.get('filename')
    severity = issue.get('issue_severity', 'Undefined')

    severity_counts[severity] += 1
    files_per_severity[severity].add(filename)

    conversation = os.path.basename(os.path.dirname(filename))
    conversations_per_severity[severity].add(conversation)

    issue_counter[rule] += 1

# === Prepare Severity Summary ===
severity_data = []
for sev in ['HIGH', 'MEDIUM', 'LOW', 'UNDEFINED']:
    total_issues = severity_counts.get(sev, 0)
    if total_issues == 0:
        continue
    severity_data.append({
        'Severity': sev,
        'Total Issues': total_issues,
        'Files Affected': len(files_per_severity[sev]),
        'Conversations Affected': len(conversations_per_severity[sev])
    })

severity_df = pd.DataFrame(severity_data)

# === Top 5 Most Frequent Issues ===
top_issues = issue_counter.most_common(5)
top_issues_data = []
for rule, count in top_issues:
    rule_info = rule_categories.get(rule, {})
    top_issues_data.append({
        'Bandit Rule': rule,
        'Occurrences': count,
        'Severity': rule_info.get('default_severity', 'N/A'),
        'Description': rule_info.get('description', 'No description')
    })

top_issues_df = pd.DataFrame(top_issues_data)

# === Export CSVs ===
severity_df.to_csv('bandit_severity_summary.csv', index=False)
top_issues_df.to_csv('bandit_top5_issues.csv', index=False)

# === Console Output ===
print("\n📊 Bandit Severity Summary:")
print(severity_df)
print("\n🏆 Top 5 Most Frequent Bandit Issues:")
print(top_issues_df)
print("\n✅ Analysis completed. CSV files generated.")
