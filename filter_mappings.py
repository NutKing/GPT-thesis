import json
with open(r"C:\Users\USER\Downloads\THESIS2\snippet_to_github.json", 'r', encoding='utf-8') as f:
    mappings = json.load(f)
filtered = {k: v for k, v in mappings.items() if v["url"].lower().endswith((".py", ".js"))}
with open(r"C:\Users\USER\Downloads\THESIS2\snippet_to_github_filtered.json", 'w', encoding='utf-8') as f:
    json.dump(filtered, f, indent=2)
print(f"Filtered to {len(filtered)} mappings")