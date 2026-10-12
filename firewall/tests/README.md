Tamanna AI Firewall — Test Guide

Owner: HM INSAN ALI

Overview

This directory contains automated tests for the Tamanna AI Firewall modules.

The tests cover:

* Access control and default-deny policy
* API request validation
* Firewall configuration validation
* Firewall manager initialization
* Audit log integrity checks
* Rate limiting
* Threat detection
* Security monitoring and reporting
* Defense readiness score
* Port-checking behavior
* Module imports and regression checks

Run All Tests

From the repository root, run:

python3 firewall/run_tests.py

Alternatively, use Python’s built-in test runner:

python3 -m unittest discover -s firewall/tests -t . -v

Run a Specific Test File

For example:

python3 -m unittest firewall.tests.test_access_control -v

Replace test_access_control with the test module you want to run.

Understand the Results

* OK: All tests in that run passed.
* FAIL: A test assertion did not match the observed behavior.
* ERROR: A test encountered an unexpected exception.
* skipped: A test was intentionally skipped.

Investigate failures and errors before treating a module as verified. Test expectations must match the actual implementation.

Safety Notes

* Tests do not prove that a system is completely secure.
* The firewall configuration should remain in audit_only mode until enforcement has been reviewed and explicitly approved.
* Tests should not modify operating-system firewall rules or block real users.
* Use test fixtures and temporary files for audit logs and reports.
* Never commit passwords, API tokens, private keys, or other secrets.

Recommended Validation

Before deployment:

1. Run the complete test suite.
2. Review all failures, errors, and skipped tests.
3. Confirm that access-control rules match the intended policy.
4. Verify that audit logs and reports are written to the expected locations.
5. Review the firewall configuration and deployment permissions.
6. Perform security testing in a controlled environment.

Status: Test documentation prepared. Actual test results have not yet been verified.

Project: Tamanna AI