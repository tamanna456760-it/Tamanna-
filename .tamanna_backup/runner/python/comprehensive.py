#!/usr/bin/env python3
import argparse
import sys


def run_wireshark_test_suite():
    """Run complete Wireshark test suite"""
    print("📡 Wireshark Comprehensive Test Suite")
    print("=" * 60)

    test_suites = [
        TestWiresharkCore,
        TestWiresharkAdvanced,
        TestWiresharkAutomation,
        TestWiresharkPerformance,
        TestWiresharkSecurity,
    ]

    total_tests = 0
    passed_tests = 0
    skipped_tests = 0

    loader = unittest.TestLoader()

    for test_suite in test_suites:
        print(f"\n🔧 Running {test_suite.__name__}...")
        suite = loader.loadTestsFromTestCase(test_suite)
        runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
        result = runner.run(suite)

        total_tests += result.testsRun
        passed_tests += result.testsRun - len(result.failures) - len(result.errors)
        skipped_tests += len(result.skipped)

    print("\n" + "=" * 60)
    print("📊 WIRESHARK TEST SUMMARY")
    print("=" * 60)
    print(f"Total Tests Run: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {len(result.failures) + len(result.errors)}")
    print(f"Skipped: {skipped_tests}")

    if len(result.failures) + len(result.errors) == 0:
        print("🎉 All critical tests passed! Wireshark is functioning correctly.")
        return True
    else:
        print("⚠ Some tests failed or were skipped. Review output for details.")
        return False


def benchmark_wireshark_performance():
    """Benchmark Wireshark performance"""
    print("\n⚡ Wireshark Performance Benchmark")
    print("=" * 40)

    import time

    benchmark_tests = [
        (
            ["tshark", "-r", "large_capture.pcap", "-Y", "tcp", "-c", "1000"],
            "Filter 1000 TCP packets",
        ),
        (["tshark", "-r", "large_capture.pcap", "-z", "io,stat,0"], "I/O Statistics"),
        (
            ["tshark", "-r", "large_capture.pcap", "-T", "json", "-c", "100"],
            "Export 100 packets to JSON",
        ),
    ]

    for cmd, description in benchmark_tests:
        try:
            start_time = time.time()
            result = subprocess.run(cmd, capture_output=True, timeout=60)
            execution_time = time.time() - start_time

            if result.returncode == 0:
                print(f"✓ {description}: {execution_time:.2f}s")
            else:
                print(f"⚠ {description}: Failed")
        except subprocess.TimeoutExpired:
            print(f"⏰ {description}: Timed out")
        except FileNotFoundError:
            print(f"📁 {description}: Test file not available")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Wireshark Test Suite")
    parser.add_argument(
        "--performance", action="store_true", help="Run performance benchmarks"
    )
    parser.add_argument(
        "--security", action="store_true", help="Run security tests only"
    )

    args = parser.parse_args()

    if args.security:
        print("🔒 Running Security Tests Only")
        suite = unittest.TestLoader().loadTestsFromTestCase(TestWiresharkSecurity)
        runner = unittest.TextTestRunner(verbosity=2)
        runner.run(suite)
    else:
        # Run comprehensive tests
        success = run_wireshark_test_suite()

        # Run performance benchmarks if requested
        if args.performance:
            benchmark_wireshark_performance()

        sys.exit(0 if success else 1)
