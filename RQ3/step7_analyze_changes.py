import json
import pandas as pd
import matplotlib.pyplot as plt
from collections import Counter

# Configuration
LINTER_COMPARISON_FILE = r"C:\Users\USER\Downloads\THESIS2\linter_comparison.json"
COMMIT_ANALYSIS_FILE = r"C:\Users\USER\Downloads\THESIS2\commit_analysis_results.json"
OUTPUT_ANALYSIS_FILE = r"C:\Users\USER\Downloads\THESIS2\rq3_analysis.json"
OUTPUT_GRAPH_FILE = r"C:\Users\USER\Downloads\THESIS2\rq3_changes_graph.png"
OUTPUT_TABLE_FILE = r"C:\Users\USER\Downloads\THESIS2\rq3_language_table.csv"

def analyze_changes():
    # Load linter comparison and commit analysis
    with open(LINTER_COMPARISON_FILE, 'r', encoding='utf-8') as f:
        linter_comparison = json.load(f)
    with open(COMMIT_ANALYSIS_FILE, 'r', encoding='utf-8') as f:
        commit_analysis = json.load(f)
    
    # Initialize counters
    py_fixed = Counter()
    py_introduced = Counter()
    py_unchanged = Counter()
    js_fixed = Counter()
    js_introduced = Counter()
    js_unchanged = Counter()
    
    # Analyze each snippet
    for snippet_path, comparison in linter_comparison.items():
        if snippet_path not in commit_analysis:
            continue
        
        # Determine language
        is_python = snippet_path.endswith('.py')
        target_fixed = py_fixed if is_python else js_fixed
        target_introduced = py_introduced if is_python else js_introduced
        target_unchanged = py_unchanged if is_python else js_unchanged
        
        # Count changes
        target_fixed["total"] += comparison["fixed"]
        target_introduced["total"] += comparison["introduced"]
        target_unchanged["total"] += comparison["unchanged"]
    
    # Calculate totals and averages
    py_snippets = sum(1 for k in linter_comparison if k.endswith('.py'))
    js_snippets = sum(1 for k in linter_comparison if k.endswith('.js'))
    
    py_avg_fixed = py_fixed["total"] / py_snippets if py_snippets > 0 else 0
    py_avg_introduced = py_introduced["total"] / py_snippets if py_snippets > 0 else 0
    py_avg_unchanged = py_unchanged["total"] / py_snippets if py_snippets > 0 else 0
    
    js_avg_fixed = js_fixed["total"] / js_snippets if js_snippets > 0 else 0
    js_avg_introduced = js_introduced["total"] / js_snippets if js_snippets > 0 else 0
    js_avg_unchanged = js_unchanged["total"] / js_snippets if js_snippets > 0 else 0
    
    # Prepare results
    results = {
        "python": {
            "snippets": py_snippets,
            "total_fixed": py_fixed["total"],
            "total_introduced": py_introduced["total"],
            "total_unchanged": py_unchanged["total"],
            "avg_fixed": py_avg_fixed,
            "avg_introduced": py_avg_introduced,
            "avg_unchanged": py_avg_unchanged
        },
        "javascript": {
            "snippets": js_snippets,
            "total_fixed": js_fixed["total"],
            "total_introduced": js_introduced["total"],
            "total_unchanged": js_unchanged["total"],
            "avg_fixed": js_avg_fixed,
            "avg_introduced": js_avg_introduced,
            "avg_unchanged": js_avg_unchanged
        }
    }
    
    # Save analysis
    with open(OUTPUT_ANALYSIS_FILE, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)
    
    # Create table
    table_data = [
        ["Language", "Snippets", "Total Fixed", "Total Introduced", "Total Unchanged", "Avg Fixed", "Avg Introduced", "Avg Unchanged"],
        ["Python", py_snippets, py_fixed["total"], py_introduced["total"], py_unchanged["total"], py_avg_fixed, py_avg_introduced, py_avg_unchanged],
        ["JavaScript", js_snippets, js_fixed["total"], js_introduced["total"], js_unchanged["total"], js_avg_fixed, js_avg_introduced, js_avg_unchanged]
    ]
    df = pd.DataFrame(table_data[1:], columns=table_data[0])
    df.to_csv(OUTPUT_TABLE_FILE, index=False)
    
    # Generate bar chart
    categories = ['Fixed', 'Introduced', 'Unchanged']
    py_values = [py_fixed["total"], py_introduced["total"], py_unchanged["total"]]
    js_values = [js_fixed["total"], js_introduced["total"], js_unchanged["total"]]
    
    x = range(len(categories))
    width = 0.35
    fig, ax = plt.subplots()
    ax.bar(x, py_values, width, label='Python')
    ax.bar([i + width for i in x], js_values, width, label='JavaScript')
    ax.set_xlabel('Issue Change Type')
    ax.set_ylabel('Total Issues')
    ax.set_title('Linter Issue Changes by Language')
    ax.set_xticks([i + width / 2 for i in x])
    ax.set_xticklabels(categories)
    ax.legend()
    plt.savefig(OUTPUT_GRAPH_FILE)
    plt.close()
    
    # Print summary
    print("RQ3 Detailed Analysis:")
    print(f"Python snippets: {py_snippets}")
    print(f"  Total fixed: {py_fixed['total']}, Avg: {py_avg_fixed:.2f}")
    print(f"  Total introduced: {py_introduced['total']}, Avg: {py_avg_introduced:.2f}")
    print(f"  Total unchanged: {py_unchanged['total']}, Avg: {py_avg_unchanged:.2f}")
    print(f"JavaScript snippets: {js_snippets}")
    print(f"  Total fixed: {js_fixed['total']}, Avg: {js_avg_fixed:.2f}")
    print(f"  Total introduced: {js_introduced['total']}, Avg: {js_avg_introduced:.2f}")
    print(f"  Total unchanged: {js_unchanged['total']}, Avg: {js_avg_unchanged:.2f}")
    print(f"Graph saved to {OUTPUT_GRAPH_FILE}")
    print(f"Table saved to {OUTPUT_TABLE_FILE}")

if __name__ == "__main__":
    analyze_changes()