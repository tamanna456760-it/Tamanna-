#!/usr/bin/env python3
"""Run Tamanna AI Endpoint Security unit tests.
Owner: HM INSAN ALI
Runs repository tests only. Does not perform enforcement actions.
"""
from __future__ import annotations
import argparse
import sys
import unittest
from pathlib import Path
DEFAULT_TEST_DIR = Path(__file__).resolve().parent / "tests"
def run_tests(test_dir: Path, pattern: str) -> bool:
    """Discover and run tests. Return True if all tests pass."""
    if not test_dir.is_dir():
        print(f"ERROR: Test directory not found: {test_dir}")
        return False
    loader = unittest.TestLoader()
    suite = loader.discover(
        start_dir=str(test_dir),
        pattern=pattern,
        top_level_dir=str(test_dir.parent),
    )
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    print("\n===== Tamanna AI Endpoint Security Test Summary =====")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")
    if result.testsRun == 0:
        print("WARNING: No tests were discovered.")
        return False
    return result.wasSuccessful()
def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run Tamanna AI Endpoint Security tests."
    )
    parser.add_argument(
        "--test-dir",
        type=Path,
        default=DEFAULT_TEST_DIR,
        help="Directory containing unittest files.",
    )
    parser.add_argument(
        "--pattern",
        default="test_*.py",
        help="Filename pattern for test discovery.",
    )
    args = parser.parse_args()
    try:
        success = run_tests(args.test_dir, args.pattern)
    except (OSError, ImportError, TypeError, ValueError) as exc:
        print(f"ERROR: Test runner failed ({exc.__class__.__name__}).")
        return 2
    return 0 if success else 1
if __name__ == "__main__":
    sys.exit(main())