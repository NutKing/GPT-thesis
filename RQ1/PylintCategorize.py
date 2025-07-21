import subprocess
import re
import json

def get_pylint_messages():
    output = subprocess.check_output(['pylint', '--list-msgs'], text=True)
    return output

def categorize_message(code, description):
    desc_lower = description.lower()
    if code.startswith('C'):
        return 'Code Style'
    elif code.startswith('R'):
        return 'Code Smell'
    elif code.startswith(('E', 'F')):
        return 'Potential Bug'
    elif code.startswith('W'):
        if any(keyword in desc_lower for keyword in ['security', 'unsafe', 'eval', 'exec', 'injection']):
            return 'Code Vulnerability'
        elif any(keyword in desc_lower for keyword in ['deprecated', 'redundant', 'inefficient']):
            return 'Code Smell'
        else:
            return 'Potential Bug'
    else:
        return 'Uncategorized'

# Fetch pylint messages
pylint_output = get_pylint_messages()

# Regex to match lines like:
# :symbol (CODE): *Description*
pattern = re.compile(r"^:([a-z0-9\-]+) \(([A-Z]\d{4})\): \*(.+)\*", re.MULTILINE)

categorized = {}

for match in pattern.findall(pylint_output):
    symbol, code, description = match
    category = categorize_message(code, description)
    categorized[code] = {
        'symbol': symbol,
        'description': description.strip(),
        'category': category
    }

with open('pylint_rule_categorization.json', 'w', encoding='utf-8') as f:
    json.dump(categorized, f, indent=4)

print(f"✅ Parsed {len(categorized)} Pylint rules. Output saved to pylint_rule_categorization.json")
