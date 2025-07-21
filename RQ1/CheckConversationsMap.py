import os

# Path to your "conversations" folder
CONVERSATIONS_DIR = "../conversations_new"

# Initialize counters
python_snippet_count = 0
javascript_snippet_count = 0
conversations_with_python = 0
conversations_with_javascript = 0

# Traverse each conversation directory
for convo_dir in os.listdir(CONVERSATIONS_DIR):
    convo_path = os.path.join(CONVERSATIONS_DIR, convo_dir)
    if not os.path.isdir(convo_path):
        continue

    has_python = False
    has_javascript = False

    for file in os.listdir(convo_path):
        if file.endswith('.py'):
            python_snippet_count += 1
            has_python = True
        elif file.endswith('.js'):
            javascript_snippet_count += 1
            has_javascript = True

    if has_python:
        conversations_with_python += 1
    if has_javascript:
        conversations_with_javascript += 1

# Print results
print(f"🔹 Total Python code snippets (files): {python_snippet_count}")
print(f"🔹 Total JavaScript code snippets (files): {javascript_snippet_count}")
print(f"💬 Conversations with Python snippets: {conversations_with_python}")
print(f"💬 Conversations with JavaScript snippets: {conversations_with_javascript}")
