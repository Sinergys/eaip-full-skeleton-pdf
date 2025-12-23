"""
Quick test runner - runs only structure tests (no server required).
"""
import subprocess
import sys
from pathlib import Path

def main():
    print("=" * 70)
    print("RUNNING VALIDATE SERVICE STRUCTURE TESTS")
    print("(No server required)")
    print("=" * 70)
    print()
    
    test_dir = Path(__file__).parent.parent
    
    # Run only structure tests
    result = subprocess.run(
        [
            sys.executable, "-m", "pytest",
            "tests/test_structure.py",
            "-v",
            "--tb=short"
        ],
        cwd=test_dir
    )
    
    print()
    print("=" * 70)
    if result.returncode == 0:
        print("✓ ALL STRUCTURE TESTS PASSED!")
        print()
        print("To run API tests (requires running server):")
        print("  1. Start validate service: python main.py")
        print("  2. Run: pytest tests/test_validate_api.py -v")
    else:
        print("✗ SOME TESTS FAILED")
    print("=" * 70)
    
    return result.returncode

if __name__ == "__main__":
    sys.exit(main())
