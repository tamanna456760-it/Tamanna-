"""
Tamanna AI Firewall Test Runner
Owner: HM INSAN ALI
Discovers and runs firewall unit tests.
This runner reports actual test results; it does not guarantee
that the firewall is secure or that every test will pass.
"""
from pathlib import Path
import sys
import unittest
PROJECT_ROOT = Path(__file__).resolve().parents[1]
TESTS_DIR = PROJECT_ROOT / "firewall" / "tests"
def main():
    if not TESTS_DIR.is_dir():
        print(f"ERROR: Test directory not found: {TESTS_DIR}")
        return 2
    root_text = str(PROJECT_ROOT)
    if root_text not in sys.path:
        sys.path.insert(0, root_text)
    loader = unittest.TestLoader()
    try:
        suite = loader.discover(
            start_dir=str(TESTS_DIR),
            pattern="test_*.py",
            top_level_dir=str(PROJECT_ROOT),
        )
    except Exception as exc:
        print(f"ERROR: Could not discover tests: {exc}")
        return 2
    print("=" * 60)
    print("Tamanna AI Firewall — Test Suite")
    print(f"Owner: HM INSAN ALI")
    print(f"Test directory: {TESTS_DIR}")
    print("=" * 60)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    print("\n" + "=" * 60)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")
    print("=" * 60)
    return 0 if result.wasSuccessful() else 1
if __name__ == "__main__":
    raise SystemExit(main())