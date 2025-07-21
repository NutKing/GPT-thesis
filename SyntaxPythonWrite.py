import os
import ast
import json

TARGET_DIR = "../conversations_new"
OUTPUT_DIR = "../Data/snippet_lists_py"

os.makedirs(OUTPUT_DIR, exist_ok=True)

def has_function_or_class(source):
    try:
        tree = ast.parse(source)
        return any(isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) for node in ast.walk(tree))
    except SyntaxError:
        return False

def starts_with_import(source):
    try:
        tree = ast.parse(source)
        first_statement = tree.body[0] if tree.body else None
        return isinstance(first_statement, (ast.Import, ast.ImportFrom))
    except SyntaxError:
        return False

def has_executable_code(source):
    try:
        tree = ast.parse(source)
        return any(isinstance(node, (ast.For, ast.While, ast.If, ast.With, ast.Assign, ast.Expr)) for node in ast.walk(tree))
    except SyntaxError:
        return False

def check_python_snippets(directory):
    categories = {
        'Successful': [],
        'Failed': [],
        'Executable': [],
        'No Function/Class Definition': [],
        'Only Import': []
    }

    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                rel_path = os.path.relpath(os.path.join(root, file), directory)
                try:
                    with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
                        source = f.read()

                    if not source.strip():
                        categories['Failed'].append(rel_path)
                        continue

                    try:
                        compile(source, file, 'exec')
                        if has_function_or_class(source):
                            categories['Successful'].append(rel_path)
                        elif has_executable_code(source):
                            categories['Executable'].append(rel_path)
                        elif starts_with_import(source):
                            categories['Only Import'].append(rel_path)
                        else:
                            categories['No Function/Class Definition'].append(rel_path)
                    except (SyntaxError, ValueError):
                        categories['Failed'].append(rel_path)

                except Exception as e:
                    print(f"⚠️ Error reading {rel_path}: {e}")
                    categories['Failed'].append(rel_path)

    return categories

# Run the analysis
categorized_snippets = check_python_snippets(TARGET_DIR)

# Save full categorized list as JSON
with open(os.path.join(OUTPUT_DIR, 'python_snippet_categories.json'), 'w', encoding='utf-8') as json_file:
    json.dump(categorized_snippets, json_file, indent=4)

# Save only Successful snippets to a separate TXT file
with open(os.path.join(OUTPUT_DIR, 'successful_python_snippets.txt'), 'w', encoding='utf-8') as txt_file:
    for path in categorized_snippets['Successful']:
        txt_file.write(f"{TARGET_DIR}/{path}\n")

print(f"\n✅ Categorization complete. Files saved in '{OUTPUT_DIR}' folder.")
