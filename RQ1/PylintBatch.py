import subprocess
import os
import json
from tqdm import tqdm  # Progress bar

# === CONFIGURATION ===
OUTPUT_FILE = 'pylint_output.json'
THIRD_PARTY_LIBS = ['scrapy', 'selenium', 'pims', 'pandas', 'numpy', 'cv2', 'matplotlib', 'torch']

# Load successful snippets
with open('successful_python_snippets.txt', 'r') as f:
    files = [line.strip() for line in f if line.strip()]

# Normalize paths
clean_files = [os.path.abspath(f).replace('\\', '/') for f in files]

all_issues = []

print(f"🔧 Running Pylint on {len(clean_files)} files...\n")

for file_path in tqdm(clean_files, desc="Pylint Progress"):
    result = subprocess.run(
        ['pylint', file_path, '--output-format=json', '--score=n'],
        capture_output=True, text=True
    )
    try:
        issues = json.loads(result.stdout)
    except json.JSONDecodeError:
        issues = []

    # === FILTERING LOGIC ===
    filtered_issues = []
    for issue in issues:
        code = issue.get('message-id')
        if code in ['C0114', 'C0115', 'C0116']:
            continue  # Skip missing docstrings

        if code == 'E0401':
            msg = issue.get('message', '').lower()
            if any(lib.lower() in msg for lib in THIRD_PARTY_LIBS):
                continue  # Skip known third-party import errors

        filtered_issues.append(issue)

    all_issues.extend(filtered_issues)

# Save combined filtered output
with open(OUTPUT_FILE, 'w') as f_out:
    json.dump(all_issues, f_out, indent=4)

print(f"\n✅ Pylint completed. {len(all_issues)} issues saved to {OUTPUT_FILE}")
