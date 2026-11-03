File: ids/run_tests.py

"""
Tamanna AI IDS Test Runner.
Project: Tamanna AI
Owner: HM INSAN ALI
Discovers and runs tests in ids/tests/.
Uses Python's standard unittest framework.
"""
from __future__ import annotations
import sys
import unittest
from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parent
TESTS_DIR = PROJECT_ROOT / "tests"
def run_tests() -> bool:
    """Discover and run all IDS tests."""
    if not TESTS_DIR.is_dir():
        print(f"ERROR: Test directory not found: {TESTS_DIR}")
        return False
    print("=" * 60)
    print("Tamanna AI - Intrusion Detection System Tests")
    print("Owner: HM INSAN ALI")
    print("=" * 60)
    loader = unittest.TestLoader()
    suite = loader.discover(
        start_dir=str(TESTS_DIR),
        pattern="test_*.py",
        top_level_dir=str(PROJECT_ROOT.parent),
    )
    test_count = suite.countTestCases()
    print(f"Discovered test cases: {test_count}")
    if test_count == 0:
        print("ERROR: No test cases were discovered.")
        return False
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    print("\n" + "=" * 60)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("=" * 60)
    return result.wasSuccessful()
if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)