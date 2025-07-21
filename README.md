# ChatGPT Code Quality Analysis Pipeline

This project extracts, filters, and analyzes ChatGPT-generated Python and JavaScript snippets.  
It validates syntax, categorizes snippets, runs linters and security tools, and analyzes how 
developers reuse and modify the snippets over time in GitHub repositories.

The pipeline addresses three research questions (RQ1, RQ2, RQ3):

- **RQ1:** Quality of ChatGPT-generated code (syntax & linting issues)  
- **RQ2:** Quality of reused code fetched from GitHub  
- **RQ3:** How reused code evolves through commits (fixed vs introduced issues)  

---

## 0. Setup Notes

1. **GitHub API Token**  
   - Required for RQ2 (fetching reused snippets) and RQ3 (commit analysis).  
   - Create a Personal Access Token on GitHub with at least `repo` read access.  
   - Save it as `token.txt` in the project root.  

2. **Node.js Linters**  
   - Install required linters:  
     ```bash
     npm install -g esprima eslint jshint standard eslint-plugin-security eslint-plugin-no-unsanitized
     ```
   - Manual commands if needed:  
     ```bash
     eslint --config eslint:recommended [folder]
     jshint [folder]
     standard [folder]
     ```

3. **Path Configuration**  
   - Many scripts have hardcoded paths. Adjust them to your environment or replace with relative paths.

4. **ESLint Configuration**  
   - `step5_compare_linters.py` auto-generates a `.eslintrc.json` if missing.

5. **Snapshot**
  - Retrieve "Snapshot_20230831" from DevGPT github
  - https://github.com/NAIST-SE/DevGPT/tree/main/snapshot_20230831

---

## 1. Requirements

- Python 3.8+  
- Node.js  

**Python libraries:**  
`pip install tqdm pandas matplotlib`  

**Node.js packages:**  
`esprima`, `eslint`, `eslint-plugin-security`, `eslint-plugin-no-unsanitized`, `jshint`, `standard`  

**Global linters:**  
`Bandit`, `Pylint`, `Flake8`  

---

## 2. RQ1 - Dataset Extraction & Quality Analysis

- **Extract.py**  
  Extracts Python/JavaScript snippets from DevGPT snapshots into `conversations_new/`.

- **CheckConversationsMap.py**  
  Counts snippets and how many conversations contain Python vs JavaScript.

- **CheckLanguageSnap.py**  
  Reports snippet and conversation counts per language in the original dataset.

- **SyntaxPython.py / SyntaxPythonWrite.py**  
  Validates Python syntax and categorizes snippets as:  
  `Successful`, `Executable`, `Only Import`, `No Definition`, `Failed`  
  - Outputs CSV+TXT (`SyntaxPython.py`) or JSON+successful list (`SyntaxPythonWrite.py`).

- **SyntaxJS.js / SyntaxJSWrite.js**  
  Same syntax validation for JavaScript snippets using `esprima`.  
  - Outputs CSV+TXT or JSON+list of "Complete" JS snippets.

- **PylintBatch.py**  
  Runs Pylint on successful Python snippets and filters irrelevant warnings.

- **PylintCategorize.py**  
  Groups Pylint rule IDs into Code Style, Code Smell, Potential Bug, Code Vulnerability.

- **PylintExec.py**  
  Summarizes Pylint results by category, most frequent rules, affected conversations.

- **Flake8Categorize.py**  
  Runs Flake8 on Python snippets, categorizes findings by prefix (E/W/N/C/F/S).

- **BanditCategorize.py**  
  Runs Bandit security analysis and extracts unique security rules.

- **BanditAnalyze.py**  
  Summarizes Bandit issues by severity and top 5 vulnerabilities.

**JavaScript linting:**  

We use three linters for JavaScript snippets:  

- **ESLint** with the `eslint:recommended` ruleset + security plugins  
- **JSHint** with default configuration  
- **StandardJS** with default strict style  

To run them manually:  

```bash
# 1. ESLint (recommended rules + security plugins)
npx eslint --config eslint:recommended \
  --plugin security --plugin no-unsanitized \
  path/to/snippets/**/*.js

# 2. JSHint (default configuration)
npx jshint path/to/snippets/**/*.js

# 3. StandardJS (opinionated style guide)
npx standard path/to/snippets/**/*.js
```

Findings grouped into Code Style, Code Smell, Potential Bug, Vulnerability.

**Example RQ1 output snippet (pylint_analysis_summary.csv):**  
```csv
Category,Total Issues,Conversations Affected,Top Rules
Code Style,235,120,C0114 (45),C0301 (32),C0115 (29)
```

---

## 3. RQ2 - Reused Code Analysis from GitHub

- **step1_identify_snippets.py**  
  Maps local snippet folders to GitHub URLs from snapshot JSON titles (with normalization and fuzzy matching).  
  Outputs `snippet_to_github.json` and unmapped title lists.

- **filter_mappings.py**  
  Filters `snippet_to_github.json` to only include Python/JavaScript URLs.

- **step2_locate_snippets.py**  
  Uses GitHub API to fetch code from mapped URLs.  
  Compares fetched vs local snippet content (`exact`, `modified`, `different`).  
  Outputs `snippet_reuse_results.json` with fetch status & similarity.

- **inspect_js_code.py**  
  Inspects JavaScript snippets marked as `original_missing` to preview fetched code.

- **step3_analyze_linters.py**  
  Runs linters on fetched code from `snippet_reuse_results.json`:  
  `pylint` for Python, `eslint` for JavaScript.  
  Saves `linter_analysis_results.json` with fetched issues.

- **summarize_linter_results.py**  
  Counts processed snippets and total issues in fetched code.

- **analyze_issues.py**  
  Shows most common linter issue codes.

- **issue_severity.py**  
  Separates issues into errors (E) and conventions (C).

- **language_issue_breakdown.py**  
  Splits top 5 issues by Python vs JavaScript.

- **rq2_analysis.py**  
  Full stats of fetched code:  
  Total issues, category percentages, top 5 issues, avg/median issues per snippet.  
  Generates `top_issues.png` plot.

- **check_results.py**  
  Counts status categories in `snippet_reuse_results.json` (exact, modified, etc.).  
  Lists valid snippets and sample URLs.

- **check_js_snippets.py**  
  Filters JavaScript snippets in `linter_analysis_results.json`.  
  Prints count and shows first 3 as sample.

**Example RQ2 output snippet (from snippet_reuse_results.json):**  
```json
{
  "conversations_new/example/snippet_1.py": {
    "status": "modified",
    "url": "https://github.com/user/repo/blob/commit/path/to/file.py",
    "similarity": 0.92
  }
}
```

---

## 4. RQ3 - Commit Evolution & Linter Comparison

- **step4_analyze_commits.py**  
  Fetches commit history for each reused snippet from GitHub.  
  Retrieves initial and final code versions per file.  
  Saves `commit_analysis_results.json`.

- **check_commit_analysis.py**  
  Quick check: counts Python vs JS snippets with commit data, previews code.

- **step5_compare_linters.py**  
  Runs linters on initial vs final code:  
  `pylint` for Python, `eslint` for JavaScript.  
  Compares issues to find **fixed**, **introduced**, **unchanged**.  
  Outputs `linter_comparison.json`.

- **step6_summarize_results.py**  
  Summarizes snippet-level changes:  
  Total/avg fixed, introduced, unchanged issues.  
  Snippet with most fixes, most introduced, best net improvement.  
  Outputs `rq3_summary.json` + `rq3_summary_table.csv`.

- **step7_analyze_changes.py**  
  Aggregates by language:  
  Total + average fixes, introduced, unchanged issues for Python vs JS.  
  Generates:  
  - `rq3_analysis.json`  
  - `rq3_language_table.csv`  
  - `rq3_changes_graph.png` (bar chart Python vs JS)

**Example RQ3 output snippet (from linter_comparison.json):**  
```json
{
  "conversations_new/example/snippet_1.py": {
    "fixed": 3,
    "introduced": 1,
    "unchanged": 4
  }
}
```

---

## 5. Outputs

- `conversations_new/` → Extracted code files  
- `successful_python_snippets.txt` → Valid Python snippets  
- `python_snippet_categories.json` → Python syntax categorization  
- `js_snippet_categories.json` → JavaScript syntax categorization  

**RQ1 outputs:**  
- `pylint_output.json`, `pylint_analysis_summary.csv`  
- `flake8_analysis_summary.csv`  
- `bandit_output_raw.json`, `bandit_severity_summary.csv`, `bandit_top5_issues.csv`  

**RQ2 outputs:**  
- `snippet_to_github.json`, `snippet_to_github_filtered.json`  
- `snippet_reuse_results.json`  
- `linter_analysis_results.json`  
- `top_issues.png`  

**RQ3 outputs:**  
- `commit_analysis_results.json`  
- `linter_comparison.json`  
- `rq3_summary.json`, `rq3_summary_table.csv`  
- `rq3_analysis.json`, `rq3_language_table.csv`, `rq3_changes_graph.png`  

---

## 6. Pipeline Order

**RQ1 - Quality of original snippets:**  
```bash
python Extract.py
python SyntaxPythonWrite.py
node SyntaxJSWrite.js
python PylintBatch.py
python PylintCategorize.py
python PylintExec.py
python Flake8Categorize.py
python BanditCategorize.py
python BanditAnalyze.py
```

**RQ2 - Quality of reused GitHub code:**  
```bash
python step1_identify_snippets.py
python filter_mappings.py
python step2_locate_snippets.py
python step3_analyze_linters.py
python summarize_linter_results.py
python rq2_analysis.py
# Optional helpers:
python check_results.py
python check_js_snippets.py
python inspect_js_code.py
python analyze_issues.py
python issue_severity.py
python language_issue_breakdown.py
```

**RQ3 - Evolution over commits:**  
```bash
python step4_analyze_commits.py
python check_commit_analysis.py
python step5_compare_linters.py
python step6_summarize_results.py
python step7_analyze_changes.py
```

---
