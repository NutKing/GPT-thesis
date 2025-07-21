import json
import requests
import difflib
import os
import base64
import time
import logging
import unicodedata
import re

# Configuration
TOKEN_FILE = r"C:\Users\USER\Downloads\THESIS2\THESIS2\Thesis_2\token.txt"
MAPPINGS_FILE = r"C:\Users\USER\Downloads\THESIS2\snippet_to_github_filtered.json"
ORIGINAL_SNIPPETS_DIR = r"C:\Users\USER\Downloads\THESIS2\conversations_new"
OUTPUT_FILE = r"C:\Users\USER\Downloads\THESIS2\snippet_reuse_results.json"
LOG_FILE = r"C:\Users\USER\Downloads\THESIS2\step2_log.txt"

# Load token
try:
    with open(TOKEN_FILE, 'r') as f:
        GITHUB_API_TOKEN = f.read().strip()
except FileNotFoundError:
    GITHUB_API_TOKEN = os.getenv("GITHUB_API_TOKEN", "")
if not GITHUB_API_TOKEN:
    raise ValueError("GitHub API token not found. Set it in token.txt or GITHUB_API_TOKEN environment variable.")

# Set up logging
logging.basicConfig(filename=LOG_FILE, level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")

# Headers for GitHub API requests
HEADERS = {
    "Authorization": f"token {GITHUB_API_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

def validate_token():
    """Validate the GitHub API token."""
    try:
        response = requests.get("https://api.github.com/user", headers=HEADERS, timeout=10)
        if response.status_code == 200:
            logging.info(f"Token validated successfully for user: {response.json().get('login')}")
            print(f"Token validated successfully for user: {response.json().get('login')}")
            return True
        else:
            logging.error(f"Token validation failed: {response.status_code} - {response.text}")
            print(f"Token validation failed: {response.status_code} - {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        logging.error(f"Error validating token: {str(e)}")
        print(f"Error validating token: {str(e)}")
        return False

def check_rate_limit():
    """Check GitHub API rate limit status."""
    try:
        response = requests.get("https://api.github.com/rate_limit", headers=HEADERS, timeout=10)
        if response.status_code == 200:
            rate_info = response.json().get("resources", {}).get("core", {})
            logging.info(f"Rate limit: {rate_info.get('remaining')} remaining, resets at {time.ctime(rate_info.get('reset'))}")
            print(f"Rate limit: {rate_info.get('remaining')} remaining, resets at {time.ctime(rate_info.get('reset'))}")
        else:
            logging.warning(f"Failed to check rate limit: {response.status_code} - {response.text}")
    except requests.exceptions.RequestException as e:
        logging.error(f"Error checking rate limit: {str(e)}")

def fetch_github_code(url):
    """Fetch the code from a GitHub URL using the API."""
    try:
        match = re.match(r"https://github.com/([^/]+)/([^/]+)/blob/([^/]+)/(.+)", url)
        if not match:
            logging.error(f"Invalid GitHub URL format: {url}")
            return None, "invalid_url"
        owner, repo, commit_hash, path = match.groups()
        api_url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}?ref={commit_hash}"
        logging.debug(f"Requesting API URL: {api_url}")
        
        response = requests.get(api_url, headers=HEADERS, timeout=10)
        if response.status_code == 200:
            content = response.json().get("content", "")
            if content:
                decoded = base64.b64decode(content).decode('utf-8', errors='ignore')
                logging.debug(f"Fetched {len(decoded)} characters from {url}")
                return decoded, "success"
            logging.warning(f"No content in {url}")
            return "", "empty_content"
        elif response.status_code == 404:
            logging.error(f"File not found at {url}: {response.status_code} - {response.text}")
            return None, "file_not_found"
        elif response.status_code == 401:
            logging.error(f"Unauthorized access to {url}: {response.status_code} - {response.text}")
            return None, "unauthorized"
        elif response.status_code == 403:
            logging.error(f"Forbidden access to {url}: {response.status_code} - {response.text}")
            return None, "forbidden"
        else:
            logging.error(f"Failed to fetch {url}: {response.status_code} - {response.text}")
            return None, f"error_{response.status_code}"
    except requests.exceptions.RequestException as e:
        logging.error(f"Request exception for {url}: {str(e)}")
        return None, "request_exception"
    except Exception as e:
        logging.error(f"Unexpected exception fetching {url}: {str(e)}")
        return None, "exception"

def get_relative_path(snippet_path):
    """Extract the relative path for the original snippet."""
    path = snippet_path.replace('/', os.sep).replace('\\', os.sep)
    if path.startswith(".." + os.sep + "conversations_new" + os.sep):
        relative_path = path[len(".." + os.sep + "conversations_new" + os.sep):]
    else:
        relative_path = path
    return relative_path

def read_original_snippet(snippet_path):
    """Read the original snippet from the local file system."""
    try:
        relative_path = get_relative_path(snippet_path)
        full_path = os.path.join(ORIGINAL_SNIPPETS_DIR, relative_path)
        logging.debug(f"Attempting to read snippet: {full_path}, Exists: {os.path.exists(full_path)}")
        if os.path.exists(full_path):
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
                logging.debug(f"Read {len(content)} characters from {full_path}")
                return content
        else:
            logging.warning(f"Original snippet not found: {full_path}")
            return None
    except Exception as e:
        logging.error(f"Error reading snippet {snippet_path}: {str(e)}")
        return None

def compare_code(original, fetched):
    """Compare the original snippet with the fetched code."""
    try:
        if not original or not fetched:
            logging.warning(f"Empty content for comparison: original={bool(original)}, fetched={bool(fetched)}")
            return "comparison_failed"
        original = original.strip()
        fetched = fetched.strip()
        if original == fetched:
            return "exact"
        similarity = difflib.SequenceMatcher(None, original, fetched).ratio()
        logging.debug(f"Similarity score: {similarity}")
        return "modified" if similarity > 0.8 else "different"
    except Exception as e:
        logging.error(f"Error comparing code: {str(e)}")
        return "comparison_failed"

def main():
    if not validate_token():
        print("Token validation failed. Please check GITHUB_API_TOKEN and try again.")
        return

    check_rate_limit()

    try:
        with open(MAPPINGS_FILE, 'r', encoding='utf-8') as f:
            mappings = json.load(f)
        logging.info(f"Loaded {len(mappings)} mappings from {MAPPINGS_FILE}")
        print(f"Loaded {len(mappings)} mappings from {MAPPINGS_FILE}")
    except Exception as e:
        logging.error(f"Error loading mappings: {str(e)}")
        print(f"Error loading mappings: {str(e)}")
        return
    
    results = {}
    stats = {
        "success": 0, 
        "file_not_found": 0, 
        "unauthorized": 0, 
        "empty_content": 0, 
        "invalid_url": 0, 
        "missing_snippet": 0, 
        "no_url": 0, 
        "exception": 0,
        "request_exception": 0,
        "forbidden": 0
    }
    for i, (snippet_path, mapping) in enumerate(mappings.items()):
        url = mapping.get("url")
        if not url:
            logging.warning(f"No URL for snippet: {snippet_path}")
            results[snippet_path] = {"status": "no_url", "url": ""}
            stats["no_url"] += 1
            continue
        
        logging.info(f"Fetching {url} for snippet {snippet_path}")
        fetched_code, fetch_status = fetch_github_code(url)
        if fetch_status in stats:
            stats[fetch_status] += 1
        else:
            stats["exception"] += 1
        if fetched_code is None:
            results[snippet_path] = {"status": f"fetch_failed_{fetch_status}", "url": url}
            continue
        
        original_code = read_original_snippet(snippet_path)
        if original_code is None:
            results[snippet_path] = {"status": "original_missing", "url": url, "fetched_code": fetched_code}
            stats["missing_snippet"] += 1
            continue
        
        comparison = compare_code(original_code, fetched_code)
        results[snippet_path] = {
            "status": comparison,
            "url": url,
            "similarity": difflib.SequenceMatcher(None, original_code, fetched_code).ratio() if comparison != "comparison_failed" else 0.0
        }
        
        if i % 50 == 0:
            logging.info(f"Processed {i} snippets")
            print(f"Processed {i} snippets")
            time.sleep(2)
    
    logging.info(f"Fetch statistics: {stats}")
    print(f"Fetch statistics: {stats}")

    try:
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2)
        logging.info(f"Results saved to {OUTPUT_FILE}")
        print(f"Results saved to {OUTPUT_FILE}")
    except Exception as e:
        logging.error(f"Error saving results: {str(e)}")
        print(f"Error saving results: {str(e)}")

if __name__ == "__main__":
    main()