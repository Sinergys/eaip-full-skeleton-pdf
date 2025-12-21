"""
Simple test runner to check if tests work.
"""
import sys
import subprocess
from pathlib import Path

def run_tests():
    """Run pytest tests and report results."""
    test_dir = Path(__file__).parent
    
    print("=" * 70)
    print("RUNNING VALIDATE SERVICE TESTS")
    print("=" * 70)
    print()
    
    # Check if pytest is installed
    try:
        result = subprocess.run(
            ["pytest", "--version"],
            capture_output=True,
            text=True
        )
        print(f"✓ Pytest found: {result.stdout.strip()}")
    except FileNotFoundError:
        print("✗ Pytest not installed!")
        print("  Run: pip install -r requirements-test.txt")
        return False
    
    print()
    print("-" * 70)
    print("Running tests (without integration tests)...")
    print("-" * 70)
    print()
    
    # Run tests
    result = subprocess.run(
        ["pytest", "tests/", "-v", "-m", "not integration", "--tb=short"],
        cwd=test_dir.parent,
        capture_output=False,
        text=True
    )
    
    print()
    print("=" * 70)
    if result.returncode == 0:
        print("✓ ALL TESTS PASSED!")
    else:
        print("✗ SOME TESTS FAILED")
        print(f"  Exit code: {result.returncode}")
    print("=" * 70)
    
    return result.returncode == 0

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
