import json
import os
from collections import defaultdict

DATA_DIR = "../Snapshot_20230831"

def analyze_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    snippet_counts = defaultdict(int)
    conversations_with_lang = defaultdict(set)

    sources = data.get("Sources", [])
    for source_index, source in enumerate(sources):
        for sharing_index, sharing in enumerate(source.get("ChatgptSharing", [])):
            conversation_id = f"{os.path.basename(filepath)}|S{source_index}|C{sharing_index}"

            languages_found = set()

            for conv in sharing.get("Conversations", []):
                for snippet in conv.get("ListOfCode", []):
                    lang = (snippet.get("Type") or "").strip()
                    if lang == "":
                        continue
                    snippet_counts[lang] += 1
                    languages_found.add(lang)

            for lang in languages_found:
                conversations_with_lang[lang].add(conversation_id)

    return snippet_counts, conversations_with_lang

def analyze_all_files(directory):
    total_snippets = defaultdict(int)
    total_conversations = defaultdict(set)

    for filename in os.listdir(directory):
        if filename.endswith('.json'):
            path = os.path.join(directory, filename)
            snippets, conversations = analyze_file(path)

            for lang, count in snippets.items():
                total_snippets[lang] += count

            for lang, convo_set in conversations.items():
                total_conversations[lang].update(convo_set)

    return total_snippets, total_conversations

# Run analysis
snippet_totals, conversation_totals = analyze_all_files(DATA_DIR)

# Combine and sort by number of snippets
language_summary = []
for lang in snippet_totals:
    language_summary.append({
        "Language": lang,
        "Snippets": snippet_totals[lang],
        "Conversations": len(conversation_totals[lang])
    })

# Sort from big to small (by snippet count)
language_summary = sorted(language_summary, key=lambda x: x["Snippets"], reverse=True)

# Output
print("\n===== Code Snippets and Conversations per Language =====")
for entry in language_summary:
    print(f"{entry['Language']}: {entry['Snippets']} snippets in {entry['Conversations']} conversations")
