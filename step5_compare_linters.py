import json
import subprocess
import os
import logging
import tempfile

# Configuration
COMMIT_ANALYSIS_FILE = r"C:\Users\USER\Downloads\THESIS2\commit_analysis_results.json"
LINTER_RESULTS_FILE = r"C:\Users\USER\Downloads\THESIS2\linter_comparison.json"
LOG_FILE = r"C:\Users\USER\Downloads\THESIS2\step5_log.txt"
ESLINT_PATH = r"C:\Users\USER\AppData\Roaming\npm\eslint.cmd"  # Confirmed path

# Set up logging
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def run_linter(code, file_path, linter_type):
    """Run linter on the given code."""
    try:
        # Write code to temporary file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(code)
        logging.info(f"Created temporary file: {file_path}")
        
        # Prepare command based on linter type
        if linter_type == 'pylint':
            cmd = ['pylint', file_path, '--output-format=json']
        elif linter_type == 'eslint':
            # Use .eslintrc.json if it exists, otherwise use default
            config_path = os.path.join(os.path.dirname(__file__), '.eslintrc.json')
            cmd = [ESLINT_PATH, file_path, '--format=json']
            if os.path.exists(config_path):
                cmd.append(f"--config={config_path}")
        else:
            logging.error(f"Unknown linter type: {linter_type}")
            return []
        
        logging.info(f"Executing command: {' '.join(cmd)}")
        
        # Run linter with explicit shell=False for security
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60,
            shell=False
        )
        
        logging.debug(f"{linter_type} stdout: {result.stdout}")
        logging.debug(f"{linter_type} stderr: {result.stderr}")
        logging.debug(f"{linter_type} return code: {result.returncode}")
        
        if result.stdout:
            try:
                if linter_type == 'pylint':
                    issues = json.loads(result.stdout)
                    return issues
                elif linter_type == 'eslint':
                    # ESLint outputs a list of file results
                    output = json.loads(result.stdout)
                    return output[0].get("messages", []) if output else []
            except json.JSONDecodeError as e:
                logging.error(f"Failed to parse {linter_type} output for {file_path}: {e}")
                return []
        else:
            logging.warning(f"No output from {linter_type} for {file_path}")
            return []
    except subprocess.TimeoutExpired:
        logging.error(f"{linter_type} timed out for {file_path}")
        return []
    except FileNotFoundError as e:
        logging.error(f"{linter_type} executable not found: {e}")
        return []
    except Exception as e:
        logging.error(f"Error running {linter_type} on {file_path}: {e}")
        return []

def compare_linter_issues(initial_issues, final_issues):
    """Compare linter issues between versions."""
    def issue_key(issue):
        # Use consistent keys for pylint and eslint
        message = issue.get('message', '') or issue.get('message-id', '')
        return (issue.get('line', 0), message)
    
    initial_set = {issue_key(issue) for issue in initial_issues}
    final_set = {issue_key(issue) for issue in final_issues}
    
    fixed = initial_set - final_set
    introduced = final_set - initial_set
    unchanged = initial_set & final_set
    
    return {
        "fixed": len(fixed),
        "introduced": len(introduced),
        "unchanged": len(unchanged)
    }

def analyze_linter_changes():
    """Analyze linter changes between initial and final code."""
    try:
        with open(COMMIT_ANALYSIS_FILE, 'r', encoding='utf-8') as f:
            commit_analysis = json.load(f)
        logging.info(f"Loaded {COMMIT_ANALYSIS_FILE} with {len(commit_analysis)} snippets")
    except Exception as e:
        logging.error(f"Failed to load {COMMIT_ANALYSIS_FILE}: {e}")
        print(f"Error: Failed to load {COMMIT_ANALYSIS_FILE}")
        return
    
    linter_comparison = {}
    for snippet_path, data in commit_analysis.items():
        initial_code = data.get("initial_code")
        final_code = data.get("final_code")
        if not initial_code or not final_code:
            logging.warning(f"Skipping {snippet_path}: missing initial or final code")
            continue
        
        # Determine linter type
        linter_type = 'pylint' if snippet_path.endswith('.py') else 'eslint' if snippet_path.endswith('.js') else None
        if not linter_type:
            logging.warning(f"Skipping {snippet_path}: unsupported file type")
            continue
        
        logging.info(f"Processing {snippet_path} with {linter_type}")
        
        # Use temporary directory for files
        with tempfile.TemporaryDirectory() as temp_dir:
            initial_file = os.path.join(temp_dir, f"initial_{os.path.basename(snippet_path)}")
            final_file = os.path.join(temp_dir, f"final_{os.path.basename(snippet_path)}")
            
            # Run linters
            initial_issues = run_linter(initial_code, initial_file, linter_type)
            final_issues = run_linter(final_code, final_file, linter_type)
            
            # Compare issues
            comparison = compare_linter_issues(initial_issues, final_issues)
            linter_comparison[snippet_path] = comparison
            logging.info(f"Comparison for {snippet_path}: {comparison}")
    
    try:
        with open(LINTER_RESULTS_FILE, 'w', encoding='utf-8') as f:
            json.dump(linter_comparison, f, indent=2)
        logging.info(f"Saved results to {LINTER_RESULTS_FILE}")
        print(f"Linter comparison saved to {LINTER_RESULTS_FILE}")
    except Exception as e:
        logging.error(f"Failed to save {LINTER_RESULTS_FILE}: {e}")
        print(f"Error: Failed to save {LINTER_RESULTS_FILE}")

if __name__ == "__main__":
    # Ensure ESLint configuration exists
    eslint_config = {
        "env": {
            "browser": True,
            "node": True
        },
        "extends": "eslint:recommended"
    }
    config_path = os.path.join(os.path.dirname(__file__), '.eslintrc.json')
    if not os.path.exists(config_path):
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(eslint_config, f, indent=2)
        logging.info(f"Created ESLint config at {config_path}")
    
    analyze_linter_changes()