import json
import pandas as pd

# Configuration
LINTER_COMPARISON_FILE = r"C:\Users\USER\Downloads\THESIS2\linter_comparison.json"
OUTPUT_SUMMARY_FILE = r"C:\Users\USER\Downloads\THESIS2\rq3_summary.json"
OUTPUT_TABLE_FILE = r"C:\Users\USER\Downloads\THESIS2\rq3_summary_table.csv"

def summarize_results():
    with open(LINTER_COMPARISON_FILE, 'r', encoding='utf-8') as f:
        comparison = json.load(f)
    
    # Initialize totals
    total_fixed = 0
    total_introduced = 0
    total_unchanged = 0
    snippet_data = []
    
    # Process each snippet
    for snippet_path, data in comparison.items():
        fixed = data["fixed"]
        introduced = data["introduced"]
        unchanged = data["unchanged"]
        total_fixed += fixed
        total_introduced += introduced
        total_unchanged += unchanged
        snippet_data.append({
            "snippet": snippet_path,
            "fixed": fixed,
            "introduced": introduced,
            "unchanged": unchanged,
            "net_change": fixed - introduced
        })
    
    # Calculate averages
    num_snippets = len(comparison)
    avg_fixed = total_fixed / num_snippets if num_snippets > 0 else 0
    avg_introduced = total_introduced / num_snippets if num_snippets > 0 else 0
    avg_unchanged = total_unchanged / num_snippets if num_snippets > 0 else 0
    
    # Find top snippets
    top_fixed = max(snippet_data, key=lambda x: x["fixed"], default={"snippet": "N/A", "fixed": 0})
    top_introduced = max(snippet_data, key=lambda x: x["introduced"], default={"snippet": "N/A", "introduced": 0})
    top_net_improvement = max(snippet_data, key=lambda x: x["net_change"], default={"snippet": "N/A", "net_change": 0})
    
    # Summary
    summary = {
        "total_snippets": num_snippets,
        "total_fixed": total_fixed,
        "total_introduced": total_introduced,
        "total_unchanged": total_unchanged,
        "avg_fixed_per_snippet": avg_fixed,
        "avg_introduced_per_snippet": avg_introduced,
        "avg_unchanged_per_snippet": avg_unchanged,
        "top_fixed_snippet": top_fixed,
        "top_introduced_snippet": top_introduced,
        "top_net_improvement_snippet": top_net_improvement
    }
    
    # Save summary
    with open(OUTPUT_SUMMARY_FILE, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2)
    
    # Create summary table
    df = pd.DataFrame(snippet_data)
    df.to_csv(OUTPUT_TABLE_FILE, index=False)
    
    # Print summary
    print("RQ3 Summary:")
    print(f"Total snippets: {num_snippets}")
    print(f"Total fixed issues: {total_fixed}")
    print(f"Total introduced issues: {total_introduced}")
    print(f"Total unchanged issues: {total_unchanged}")
    print(f"Average fixed per snippet: {avg_fixed:.2f}")
    print(f"Average introduced per snippet: {avg_introduced:.2f}")
    print(f"Average unchanged per snippet: {avg_unchanged:.2f}")
    print(f"Snippet with most fixed issues: {top_fixed['snippet']} ({top_fixed['fixed']})")
    print(f"Snippet with most introduced issues: {top_introduced['snippet']} ({top_introduced['introduced']})")
    print(f"Snippet with best net improvement: {top_net_improvement['snippet']} (net change: {top_net_improvement['net_change']})")

if __name__ == "__main__":
    summarize_results()