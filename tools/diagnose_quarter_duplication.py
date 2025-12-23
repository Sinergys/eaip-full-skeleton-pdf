"""
Diagnostic script to identify quarter month duplication issues.
"""
import json
import sys
from pathlib import Path
from collections import Counter

def analyze_aggregated_data(aggregated_json_path):
    """Analyze aggregated data for month duplication in quarters."""

    with open(aggregated_json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    issues = []

    for resource_type, quarters in data.items():
        if not isinstance(quarters, dict):
            continue

        print(f"\n{'='*80}")
        print(f"Analyzing resource: {resource_type}")
        print(f"{'='*80}")

        for quarter_key, quarter_data in quarters.items():
            if not isinstance(quarter_data, dict):
                continue

            months = quarter_data.get("months", [])
            month_names = [m.get("month") for m in months if isinstance(m, dict)]

            print(f"\n{quarter_key}:")
            print(f"  Total months: {len(month_names)}")
            print(f"  Month names: {month_names}")

            # Check for duplicates
            month_counts = Counter(month_names)
            duplicates = {month: count for month, count in month_counts.items() if count > 1}

            if duplicates:
                print(f"  ⚠️  DUPLICATES FOUND: {duplicates}")
                issues.append({
                    "resource": resource_type,
                    "quarter": quarter_key,
                    "duplicates": duplicates,
                    "all_months": month_names
                })

            # Check if quarter has correct number of months (should be 3)
            if len(set(month_names)) != 3:
                print(f"  ⚠️  Expected 3 unique months, got {len(set(month_names))}")

            # Check for months appearing in wrong quarter
            year = quarter_data.get("year")
            quarter_num = quarter_data.get("quarter")
            if year and quarter_num:
                expected_month_nums = range((quarter_num-1)*3 + 1, quarter_num*3 + 1)
                print(f"  Expected month numbers for Q{quarter_num}: {list(expected_month_nums)}")

    if issues:
        print(f"\n{'='*80}")
        print(f"SUMMARY: Found {len(issues)} quarters with duplication issues")
        print(f"{'='*80}")
        for issue in issues:
            print(f"\n{issue['resource']} - {issue['quarter']}:")
            print(f"  Duplicates: {issue['duplicates']}")
            print(f"  All months: {issue['all_months']}")
    else:
        print(f"\n{'='*80}")
        print("✅ No duplication issues found!")
        print(f"{'='*80}")

    return issues

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python diagnose_quarter_duplication.py <path_to_aggregated_json>")
        print("\nExample:")
        print("  python diagnose_quarter_duplication.py C:\\eaip\\data\\aggregated\\batch123_aggregated.json")
        sys.exit(1)

    json_path = Path(sys.argv[1])
    if not json_path.exists():
        print(f"Error: File not found: {json_path}")
        sys.exit(1)

    analyze_aggregated_data(json_path)
