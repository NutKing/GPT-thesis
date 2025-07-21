import requests
import json
import re
import base64

# Configuration
TOKEN_FILE = r"C:\Users\USER\Downloads\THESIS2\THESIS2\Thesis_2\token.txt"
RESULTS_FILE = r"C:\Users\USER\Downloads\THESIS2\snippet_reuse_results.json"
OUTPUT_FILE = r"C:\Users\USER\Downloads\THESIS2\commit_analysis_results.json"
#r"C:\Users\USER\Downloads\THESIS2\THESIS2\Thesis_\token.txt"


# Load GitHub API token
with open(TOKEN_FILE, 'r') as f:
    GITHUB_API_TOKEN = f.read().strip()

HEADERS = {
    "Authorization": f"token {GITHUB_API_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

def get_commits(owner, repo, path):
    """Retrieve commit history for a file."""
    url = f"https://api.github.com/repos/{owner}/{repo}/commits?path={path}"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to get commits for {owner}/{repo}/{path}: {response.status_code}")
        return []

def get_file_at_commit(owner, repo, path, sha):
    """Get file content at a specific commit."""
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}?ref={sha}"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        content = response.json().get("content", "")
        if content:
            return base64.b64decode(content).decode('utf-8', errors='ignore')
    return None

def analyze_commits():
    """Analyze commit history for each snippet."""
    with open(RESULTS_FILE, 'r', encoding='utf-8') as f:
        results = json.load(f)
    
    commit_analysis = {}
    for snippet_path, data in results.items():
        url = data.get("url")
        if not url:
            continue
        match = re.match(r"https://github.com/([^/]+)/([^/]+)/blob/([^/]+)/(.+)", url)
        if not match:
            continue
        owner, repo, _, path = match.groups()
        
        # Get commit history
        commits = get_commits(owner, repo, path)
        if not commits or len(commits) < 2:
            continue  # Skip if no history or single commit
        
        # Get initial and final code
        initial_sha = commits[-1]["sha"]  # Oldest commit
        final_sha = commits[0]["sha"]     # Latest commit
        initial_code = get_file_at_commit(owner, repo, path, initial_sha)
        final_code = get_file_at_commit(owner, repo, path, final_sha)
        
        if initial_code and final_code:
            commit_analysis[snippet_path] = {
                "url": url,
                "initial_code": initial_code,
                "final_code": final_code,
                "commits": len(commits)
            }
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(commit_analysis, f, indent=2)
    print(f"Commit analysis saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    analyze_commits()