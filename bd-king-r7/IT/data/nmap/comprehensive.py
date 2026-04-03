#!/usr/bin/env python3
import sys
import time


def run_comprehensive_nmap_tests():
    """Run all Nmap tests with detailed reporting"""
    print("🔍 Nmap Comprehensive Upgrade Test Suite")
    print("=" * 50)

    test_suites = [
        TestNmapCoreFunctionality,
        TestNmapAdvancedScans,
        TestNmapPerformance,
        TestCustomNSEScripts,
        TestNmapUpgrade,
    ]

    total_tests = 0
    passed_tests = 0
    failed_tests = 0

    loader = unittest.TestLoader()

    for test_suite in test_suites:
        print(f"\n📋 Running {test_suite.__name__}...")
        suite = loader.loadTestsFromTestCase(test_suite)
        runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
        result = runner.run(suite)

        total_tests += result.testsRun
        passed_tests += result.testsRun - \
            len(result.failures) - len(result.errors)
        failed_tests += len(result.failures) + len(result.errors)

    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {failed_tests}")
    print(
        f"Success Rate: {(passed_tests/total_tests)*100:.1f}%"
        if total_tests > 0
        else "N/A"
    )

    if failed_tests == 0:
        print("🎉 All tests passed! Nmap upgrade successful.")
        return True
    else:
        print("❌ Some tests failed. Please review the upgrade.")
        return False


def performance_benchmark():
    """Benchmark Nmap performance before and after upgrade"""
    print("\n⚡ Performance Benchmark")
    print("=" * 30)

    test_commands = [
        (["nmap", "-T4", "-F", "127.0.0.1"], "Fast scan"),
        (["nmap", "-sS", "-p-", "127.0.0.1"], "Full port scan"),
        (["nmap", "-A", "127.0.0.1"], "Aggressive scan"),
    ]

    for cmd, description in test_commands:
        try:
            start_time = time.time()
            result = subprocess.run(cmd, capture_output=True, timeout=120)
            execution_time = time.time() - start_time

            if result.returncode == 0:
                print(f"✓ {description}: {execution_time:.2f}s")
            else:
                print(
                    f"⚠ {description}: Failed (return code {result.returncode})")
        except subprocess.TimeoutExpired:
            print(f"⏰ {description}: Timed out")


if __name__ == "__main__":
    # Run comprehensive tests
    success = run_comprehensive_nmap_tests()

    # Run performance benchmarks
    performance_benchmark()

    # Exit with appropriate code
    sys.exit(0 if success else 1)
