import json
import os
import subprocess
import tempfile
import logging
import re

# Configuration
RESULTS_FILE = r"C:\Users\USER\Downloads\THESIS2\snippet_reuse_results.json"
OUTPUT_FILE = r"C:\Users\USER\Downloads\THESIS2\linter_analysis_results.json"
LOG_FILE = r"C:\Users\USER\Downloads\THESIS2\step3_log.txt"

# Set up logging
logging.basicConfig(filename=LOG_FILE, level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")

def is_valid_code(code, file_extension):
    if not code or len(code.strip()) < 50:  # Stricter minimum length
        return False
    if file_extension == '.py':
        python_patterns = r'(def |class |import |from |if |else |for |while |try |except )'
        return bool(re.search(python_patterns, code))
    elif file_extension == '.js':
        js_patterns = r'(function |const |let |var |if |else |for |while |try |catch |=>|\bclass\b)'
        lines = code.splitlines()
        code_lines = [line for line in lines if line.strip() and not line.strip().startswith('//')]
        return len(code_lines) > 5 and bool(re.search(js_patterns, code))
    return False

def run_pylint(code, file_path):
    """Run pylint on the provided Python code."""
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(code)
        
        result = subprocess.run(
            ['pylint', file_path, '--output-format=json'],
            capture_output=True, text=True, timeout=30
        )
        if result.stdout:
            issues = json.loads(result.stdout)
            return [{"code": issue["message-id"], "message": issue["message"], "line": issue["line"]} for issue in issues]
        return []
    except subprocess.TimeoutExpired:
        logging.error(f"Pylint timed out for {file_path}")
        return []
    except json.JSONDecodeError:
        logging.error(f"Pylint output not valid JSON for {file_path}")
        return []
    except Exception as e:
        logging.error(f"Pylint error for {file_path}: {str(e)}")
        return []

def run_eslint(code, file_path):
    """Run eslint on the provided JavaScript code."""
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(code)
        
        result = subprocess.run(
            ['eslint', file_path, '--format=json'],
            capture_output=True, text=True, timeout=30
        )
        if result.stdout:
            issues = json.loads(result.stdout)[0].get("messages", [])
            return [{"code": issue["ruleId"], "message": issue["message"], "line": issue["line"]} for issue in issues]
        return []
    except subprocess.TimeoutExpired:
        logging.error(f"ESLint timed out for {file_path}")
        return []
    except json.JSONDecodeError:
        logging.error(f"ESLint output not valid JSON for {file_path}")
        return []
    except Exception as e:
        logging.error(f"ESLint error for {file_path}: {str(e)}")
        return []

def analyze_snippet(snippet_path, data):
    """Analyze the snippet using the appropriate linter."""
    status = data.get("status")
    url = data.get("url", "")
    
    if status != "original_missing":
        logging.info(f"Skipping {snippet_path}: status is {status}, not original_missing")
        return None
    
    fetched_code = data.get("fetched_code")
    if not fetched_code:
        logging.warning(f"No fetched code for {snippet_path}")
        return None
    
    # Determine file type based on snippet_path extension
    file_extension = os.path.splitext(snippet_path.lower())[1]
    if file_extension == '.py':
        linter_type = 'pylint'
    elif file_extension == '.js':
        linter_type = 'eslint'
    else:
        logging.warning(f"Unsupported file extension {file_extension} for {snippet_path}")
        return None
    
    # Validate fetched code
    if not is_valid_code(fetched_code, file_extension):
        logging.warning(f"Fetched content does not resemble {file_extension} code for {snippet_path}")
        return None
    
    # Create temporary files for linter analysis
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_file = os.path.join(temp_dir, os.path.basename(snippet_path))
        
        # Analyze fetched code
        logging.info(f"Running {linter_type} on fetched code for {snippet_path}")
        fetched_issues = []
        if linter_type == 'pylint':
            fetched_issues = run_pylint(fetched_code, temp_file)
        elif linter_type == 'eslint':
            fetched_issues = run_eslint(fetched_code, temp_file)
        
        return {
            "fetched_issues": fetched_issues,
            "comparison": {
                "fixed": 0,  # No original to compare
                "introduced": len(fetched_issues),
                "total_fetched_issues": len(fetched_issues)
            }
        }

def main():
    # Load snippet reuse results
    try:
        with open(RESULTS_FILE, 'r', encoding='utf-8') as f:
            results = json.load(f)
        logging.info(f"Loaded {len(results)} snippets from {RESULTS_FILE}")
        print(f"Loaded {len(results)} snippets from {RESULTS_FILE}")
    except Exception as e:
        logging.error(f"Error loading {RESULTS_FILE}: {str(e)}")
        print(f"Error loading {RESULTS_FILE}: {str(e)}")
        return
    
    linter_results = {}
    for i, (snippet_path, data) in enumerate(results.items()):
        logging.info(f"Processing {snippet_path}")
        analysis = analyze_snippet(snippet_path, data)
        if analysis:
            linter_results[snippet_path] = {
                "url": data.get("url", ""),
                "status": data.get("status"),
                "linter_results": analysis
            }
            print(f"Processed {snippet_path}")
        else:
            print(f"Skipped {snippet_path}")
        
        if i % 50 == 0:
            logging.info(f"Processed {i} snippets")
            print(f"Processed {i} snippets")
    
    # Save linter analysis results
    try:
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(linter_results, f, indent=2)
        logging.info(f"Results saved to {OUTPUT_FILE}")
        print(f"Results saved to {OUTPUT_FILE}")
    except Exception as e:
        logging.error(f"Error saving {OUTPUT_FILE}: {str(e)}")
        print(f"Error saving {OUTPUT_FILE}: {str(e)}")

if __name__ == "__main__":
    main()