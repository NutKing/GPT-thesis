import json
import os

# Set your paths
DATA_DIR = "../Snapshot_20230831"
OUTPUT_DIR = "../conversations_new"

os.makedirs(OUTPUT_DIR, exist_ok=True)

def sanitize_name(name):
    """Sanitize folder and file names to remove problematic characters."""
    return "".join(c if c.isalnum() or c in ('-', '_') else '_' for c in name)

def extract_code_snippets(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    sources = data.get("Sources", [])
    skipped_snippets = 0
    total_saved = 0
    python_detected = 0
    javascript_detected = 0
    unknown_languages = set()

    for source_index, source in enumerate(sources):
        for sharing_index, sharing in enumerate(source.get("ChatgptSharing", [])):

            # Use Title or fallback name
            raw_name = sharing.get("Title") or f"{os.path.basename(filepath)}_S{source_index}_C{sharing_index}"
            convo_dir_name = sanitize_name(raw_name)
            convo_dir_path = os.path.join(OUTPUT_DIR, convo_dir_name)
            os.makedirs(convo_dir_path, exist_ok=True)

            snippet_counter = 1

            for conv in sharing.get("Conversations", []):
                for snippet in conv.get("ListOfCode", []):
                    lang_raw = snippet.get("Type")
                    lang = (lang_raw or "").strip().lower()
                    content = snippet.get("Content", "")

                    # Language detection
                    if lang.startswith("python"):
                        ext = ".py"
                        python_detected += 1
                    elif lang == "javascript":
                        ext = ".js"
                        javascript_detected += 1
                    else:
                        if lang != "":
                            unknown_languages.add(lang)
                        continue  # Skip non-Python/JS

                    # Skip empty content
                    if content is None or not content.strip():
                        skipped_snippets += 1
                        continue

                    # Unique filename
                    filename = f"snippet_{source_index}_{sharing_index}_{snippet_counter}{ext}"
                    full_path = os.path.join(convo_dir_path, filename)

                    with open(full_path, 'w', encoding='utf-8') as code_file:
                        code_file.write(content)

                    snippet_counter += 1
                    total_saved += 1

    return {
        "saved": total_saved,
        "skipped": skipped_snippets,
        "python_detected": python_detected,
        "javascript_detected": javascript_detected,
        "unknown_languages": unknown_languages
    }

def process_all_files():
    totals = {
        "saved": 0,
        "skipped": 0,
        "python_detected": 0,
        "javascript_detected": 0,
        "unknown_languages": set()
    }

    for filename in os.listdir(DATA_DIR):
        if filename.endswith('.json'):
            result = extract_code_snippets(os.path.join(DATA_DIR, filename))
            totals["saved"] += result["saved"]
            totals["skipped"] += result["skipped"]
            totals["python_detected"] += result["python_detected"]
            totals["javascript_detected"] += result["javascript_detected"]
            totals["unknown_languages"].update(result["unknown_languages"])

    # Final Report
    print(f"\n🔹 Total Python snippets detected: {totals['python_detected']}")
    print(f"🔹 Total JavaScript snippets detected: {totals['javascript_detected']}")
    print(f"✅ Total code files saved: {totals['saved']}")
    print(f"⚠️ Total snippets skipped (empty content): {totals['skipped']}")

    if totals['unknown_languages']:
        print(f"\n⚠️ Unknown languages found: {totals['unknown_languages']}")

process_all_files()
