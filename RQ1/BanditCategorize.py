import subprocess
import json
import os
from tqdm import tqdm

TARGET_FILES = 'successful_python_snippets.txt'
BANDIT_RAW_OUTPUT = 'bandit_output_raw.json'
BANDIT_RULES_JSON = 'bandit_rule_categorization.json'

# Load file list and normalize paths
with open(TARGET_FILES, 'r') as f:
    files = [line.strip() for line in f if line.strip()]

clean_files = [os.path.abspath(f).replace('\\', '/') for f in files]

print(f"🔎 Running Bandit on {len(clean_files)} files...")

# Run Bandit with cleaned paths
subprocess.run(['bandit', '-f', 'json', '-o', BANDIT_RAW_OUTPUT] + clean_files)

# Load Bandit output
with open(BANDIT_RAW_OUTPUT, 'r') as f:
    bandit_data = json.load(f)

results = bandit_data.get('results', [])

# Extract unique rules
unique_rules = {}
for item in tqdm(results, desc="Processing Bandit Results"):
    test_id = item.get('test_id')
    if test_id not in unique_rules:
        unique_rules[test_id] = {
            'test_name': item.get('test_name'),
            'description': item.get('issue_text'),
            'default_severity': item.get('issue_severity'),
            'confidence': item.get('issue_confidence'),
            'cwe': item.get('cwe', {}).get('id', 'N/A'),
            'category': 'Code Vulnerability'
        }

# Save categorization JSON
with open(BANDIT_RULES_JSON, 'w') as f_out:
    json.dump(unique_rules, f_out, indent=4)

print(f"\n✅ Bandit rule categorization saved to {BANDIT_RULES_JSON}")
