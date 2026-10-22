"""Test runner for Tamanna AI Web Application Firewall.
Owner: HM INSAN ALI
Runs the WAF unit tests without changing firewall settings.
"""
from __future__ import annotations
import sys
import unittest
from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
TEST_DIRECTORY = Path(__file__).resolve().parent / "tests"
def main() -> int:
    """Discover and execute WAF unit tests."""
    if not TEST_DIRECTORY.is_dir():
        print(f"ERROR: Test directory not found: {TEST_DIRECTORY}")
        return 2
    # Ensure imports work when this script is launched directly.
    sys.path.insert(0, str(PROJECT_ROOT))
    suite = unittest.defaultTestLoader.discover(
        start_dir=str(TEST_DIRECTORY),
        pattern="test_*.py",
        top_level_dir=str(PROJECT_ROOT),
    )
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    print("\n===== Tamanna AI WAF Test Summary =====")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")
    return 0 if result.wasSuccessful() else 1
if __name__ == "__main__":
    raise SystemExit(main())