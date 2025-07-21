import json
import os
import traceback
import re
import difflib

# File paths
json_path = r"C:\Users\USER\Downloads\THESIS2\THESIS2\Thesis_2\Snapshot_20230831\20230831_072722_file_sharings.json"
python_snippets_path = r"C:\Users\USER\Downloads\THESIS2\THESIS2\LintersResult\ListOfTestedSnippets\successful_python_snippets.txt"
js_snippets_path = r"C:\Users\USER\Downloads\THESIS2\THESIS2\LintersResult\ListOfTestedSnippets\complete_js_snippets.txt"

# Load snippet lists with UTF-8 encoding
try:
    with open(python_snippets_path, 'r', encoding='utf-8') as f:
        python_snippets = [line.strip() for line in f if line.strip()]
    print(f"Loaded {len(python_snippets)} Python snippets. First few: {python_snippets[:3]}")
except FileNotFoundError:
    print(f"Error: {python_snippets_path} not found.")
    python_snippets = []

try:
    with open(js_snippets_path, 'r', encoding='utf-8') as f:
        js_snippets = [line.strip() for line in f if line.strip()]
    print(f"Loaded {len(js_snippets)} JavaScript snippets. First few: {js_snippets[:3]}")
except FileNotFoundError:
    print(f"Error: {js_snippets_path} not found.")
    js_snippets = []

# Translation dictionary for non-English and English title variations
title_translations = {
    # Non-English titles (raw)
    '이벤트_리스너_제거_방법': 'event listener removal',
    '속성의_삭제_JavaScript': 'attribute removal',
    '금지_ワードの_投稿_終了': 'banned word posting',
    'Swift类型擦除技术': 'swift type erasure technology',
    '掲示板アプリプログラム': 'bulletin board app program',
    '掲示板アプリ概要': 'bulletin board app overview',
    'マークダウンドキュメントの_ページ_分割': 'markdown document page splitting',
    'モバイルハンバーガーメニュー': 'mobile hamburger menu',
    'Actualizar_archivo_Librecalc_Python': 'update librecalc file',
    'Encuentra_puntos_dentro_área_': 'find points within area',
    'Geokoordinate_Technischer_Spezialist': 'geocoordinate technical specialist',
    # English title variations
    'Accessing_Function_Docstring__Python_': 'access function docstring',
    'Add_CSS_rule_to_selector': 'add css rule',
    'ActivityStreams_Abbreviated_Highlight': 'activitystreams highlight'
}

# Function to normalize titles
def normalize_title(title):
    normalized = re.sub(r'_+', ' ', title.rstrip('_')).lower()
    if normalized.endswith(' python'):
        normalized = normalized[:-7]
    elif normalized.endswith(' javascript'):
        normalized = normalized[:-10]
    # Apply translation if raw title exists in title_translations
    raw_title = title
    if raw_title in title_translations:
        return title_translations[raw_title]
    return normalized.strip()

# Load the JSON file with UTF-8 encoding
print("Loading the large JSON file... This might take a moment.")
try:
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
except FileNotFoundError:
    print(f"Error: {json_path} not found.")
    data = {"Sources": []}
except json.JSONDecodeError as e:
    print(f"Error decoding JSON: {e}")
    data = {"Sources": []}

# Map titles to GitHub URLs
title_to_github = {}
sources = data.get("Sources", [])
if not isinstance(sources, list):
    print(f"Error: 'Sources' is not a list, found {type(sources)}")
else:
    print(f"Found {len(sources)} entries in 'Sources'.")
    for i, source in enumerate(sources):
        try:
            if not isinstance(source, dict):
                print(f"Skipping invalid source at index {i} (not a dict): {str(source)[:50]}...")
                continue
            if "ChatgptSharing" in source:
                for j, sharing in enumerate(source.get("ChatgptSharing", [])):
                    try:
                        title = sharing.get("Title", "")
                        normalized_title = normalize_title(title)
                        url = source.get("URL", "")
                        if title and url:
                            title_to_github[normalized_title] = {"url": url}
                        elif not title:
                            print(f"Warning: Empty or missing 'Title' in sharing at Source[{i}].ChatgptSharing[{j}]: {sharing}")
                        elif not url:
                            print(f"Warning: Empty or missing 'URL' in Source[{i}]: {source.get('URL', 'N/A')}")
                    except Exception as e:
                        print(f"Error processing Source[{i}].ChatgptSharing[{j}]: {e}")
                        traceback.print_exc()
            else:
                print(f"No 'ChatgptSharing' in Source[{i}]")
        except Exception as e:
            print(f"Error processing Source[{i}]: {e}")
            traceback.print_exc()

print(f"Extracted {len(title_to_github)} unique titles from JSON. First few: {list(title_to_github.keys())[:5]}")

# Fuzzy matching function
def find_closest_title(normalized_title, json_titles, threshold=0.8):
    matches = difflib.get_close_matches(normalized_title, json_titles, n=1, cutoff=threshold)
    return matches[0] if matches else None

# Match snippets to GitHub URLs
snippet_to_github = {}
unmapped_titles = []
all_snippets = python_snippets + js_snippets
json_titles = list(title_to_github.keys())
print(f"Total snippets to match: {len(all_snippets)}")
for snippet in all_snippets:
    try:
        parts = snippet.replace('/', os.sep).split(os.sep)
        print(f"Processing snippet: {snippet}, Parts: {parts}")
        if len(parts) >= 2:
            folder_file = parts[-2]
            if folder_file.startswith('../conversations_new' + os.sep):
                title = folder_file[len('../conversations_new' + os.sep):]
            else:
                title = folder_file
            normalized_title = normalize_title(title)
            print(f"Extracted title: {title}, Normalized: {normalized_title}")
            if normalized_title in title_to_github:
                snippet_to_github[snippet] = title_to_github[normalized_title]
            else:
                # Try fuzzy matching
                closest_title = find_closest_title(normalized_title, json_titles)
                if closest_title:
                    print(f"Fuzzy match: {normalized_title} -> {closest_title}")
                    snippet_to_github[snippet] = title_to_github[closest_title]
                else:
                    print(f"No match for normalized title: {normalized_title}")
                    unmapped_titles.append((title, normalized_title))
        else:
            print(f"Invalid snippet path (too few parts): {snippet}, Raw: {repr(snippet)}")
            unmapped_titles.append((snippet, "Invalid path"))
    except Exception as e:
        print(f"Error processing snippet {snippet}: {e}")
        traceback.print_exc()

# Save unmapped titles for analysis
unmapped_path = r"C:\Users\USER\Downloads\THESIS2\unmapped_titles.json"
try:
    with open(unmapped_path, 'w', encoding='utf-8') as f:
        json.dump(unmapped_titles, f, indent=2)
    print(f"Saved {len(unmapped_titles)} unmapped titles to 'unmapped_titles.json'.")
except Exception as e:
    print(f"Error saving unmapped titles: {e}")

# Save unmatched JSON titles
unmatched_json_titles = list(title_to_github.keys())
for snippet in snippet_to_github:
    parts = snippet.replace('/', os.sep).split(os.sep)
    if len(parts) >= 2:
        folder_file = parts[-2]
        if folder_file.startswith('../conversations_new' + os.sep):
            title = folder_file[len('../conversations_new' + os.sep):]
        else:
            title = folder_file
        normalized_title = normalize_title(title)
        if normalized_title in unmatched_json_titles:
            unmatched_json_titles.remove(normalized_title)
unmatched_json_path = r"C:\Users\USER\Downloads\THESIS2\unmatched_json_titles.json"
try:
    with open(unmatched_json_path, 'w', encoding='utf-8') as f:
        json.dump(unmatched_json_titles, f, indent=2)
    print(f"Saved {len(unmatched_json_titles)} unmatched JSON titles to 'unmatched_json_titles.json'.")
except Exception as e:
    print(f"Error saving unmatched JSON titles: {e}")

# Save the results
output_path = r"C:\Users\USER\Downloads\THESIS2\snippet_to_github.json"
try:
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(snippet_to_github, f, indent=2)
    print(f"Found {len(snippet_to_github)} snippets with GitHub mappings. Saved to 'snippet_to_github.json'.")
except Exception as e:
    print(f"Error saving output: {e}")