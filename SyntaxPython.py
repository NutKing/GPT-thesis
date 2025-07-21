import os
import ast
import csv

TARGET_DIR = "../conversations_new"

def has_function_or_class(source):
    try:
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                return True
        return False
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
        for node in ast.walk(tree):
            if isinstance(node, (ast.For, ast.While, ast.If, ast.With, ast.Assign, ast.Expr)):
                return True
        return False
    except SyntaxError:
        return False

def check_python_snippets(directory):
    success, failure, executable, no_def_or_class, only_import = [], [], [], [], []

    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        source = f.read()

                    if not source.strip():
                        failure.append(file_path)
                        continue

                    try:
                        compile(source, file_path, 'exec')
                        if has_function_or_class(source):
                            success.append(file_path)
                        elif has_executable_code(source):
                            executable.append(file_path)
                        elif starts_with_import(source):
                            only_import.append(file_path)
                        else:
                            no_def_or_class.append(file_path)
                    except (SyntaxError, ValueError):
                        failure.append(file_path)

                except Exception as e:
                    print(f"⚠️ Error reading {file_path}: {e}")
                    failure.append(file_path)

    return success, failure, executable, no_def_or_class, only_import

def write_to_csv(filename, data):
    headers = ['Code Snippet', 'Category']
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        writer.writeheader()
        for category, snippets in data.items():
            for snippet in snippets:
                writer.writerow({'Code Snippet': snippet, 'Category': category})

# Running the snippet check
success_snippets, failed_snippets, executable_snippets, no_def_class_snippets, only_import_snippets = check_python_snippets(TARGET_DIR)

# Preparing data for CSV
data_for_csv = {
    'Successful': success_snippets,
    'Failed': failed_snippets,
    'Executable': executable_snippets,
    'No Function/Class Definition': no_def_class_snippets,
    'Only Import': only_import_snippets
}

# Writing to CSV
csv_filename = 'snippet_analysis_results.csv'
write_to_csv(csv_filename, data_for_csv)

# Writing summary to text file
txt_filename = 'snippet_summary.txt'
with open(txt_filename, 'w') as file:
    file.write(f"Number of Successful Snippets: {len(success_snippets)}\n")
    file.write(f"Number of Failed Snippets: {len(failed_snippets)}\n")
    file.write(f"Number of Executable Snippets: {len(executable_snippets)}\n")
    file.write(f"Number of Snippets Without Function/Class Definition: {len(no_def_class_snippets)}\n")
    file.write(f"Number of Snippets With Only Import Statements: {len(only_import_snippets)}\n")

print("\n✅ Analysis complete. Results written to CSV and summary written to text file.")
