#!/usr/bin/env python3
"""
Test script to verify data files are accessible and paths work correctly.
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "eaip_full_skeleton"))

from services.ingest.utils.energy_aggregator import get_data_file_path, DATA_DIR


def main():
    print("=" * 60)
    print("Testing Data File Paths")
    print("=" * 60)
    print(f"\nProject DATA_DIR: {DATA_DIR}")
    print(f"Exists: {DATA_DIR.exists()}")
    
    test_files = [
        "pererashod.xlsx",
        "otoplenie.xlsx",
        "edenic na  kvt.xlsx",
        "gaz.xlsx",
        "voda.xlsx",
        "ograjdayuschie_konstrukcii.xlsx",
    ]
    
    print(f"\n{'File':<40} {'Status':<10} {'Size (KB)':<10}")
    print("-" * 60)
    
    for filename in test_files:
        try:
            file_path = get_data_file_path(filename)
            size_kb = file_path.stat().st_size / 1024
            print(f"{filename:<40} {'✅ Found':<10} {size_kb:>7.2f}")
        except FileNotFoundError:
            print(f"{filename:<40} {'❌ Missing':<10} {'-':<10}")
    
    print("\n" + "=" * 60)
    print("Test Complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()

