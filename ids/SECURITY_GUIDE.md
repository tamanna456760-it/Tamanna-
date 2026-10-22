Tamanna AI IDS — Security Guide

Project: Tamanna AI
Owner: HM INSAN ALI
Version: 1.0.0

1. Purpose

Tamanna AI Intrusion Detection System (IDS) monitors security-related events and identifies suspicious activity.

The IDS is designed for monitoring and alerting. It must not automatically block IP addresses or modify the operating system firewall.

2. Security Principles

* Monitor-only: Detect and report suspicious activity.
* No automatic blocking: Never block an IP automatically.
* No firewall modification: Do not change operating-system firewall rules.
* Secret protection: Avoid recording passwords, API keys, tokens, and session cookies.
* Bounded storage: Keep in-memory event and alert histories within configured limits.
* Validation: Reject malformed or unsupported input.
* Testing: Run the automated tests before integrating the IDS with other services.

3. Main Components

File	Purpose
event_collector.py	Collects and inspects events
detection_engine.py	Detects suspicious login and request patterns
alert_manager.py	Validates, filters, and stores alerts
ids_manager.py	Coordinates IDS components
health_check.py	Reports component health
ids_report.py	Generates a status report
run_tests.py	Runs the IDS test suite

4. Run the Tests

From the repository root, run:

python -m ids.run_tests

A successful test run is necessary before deployment, but it does not prove that every security risk has been eliminated.

5. Run the Health Check

python -m ids.health_check

Review the component statuses and investigate any reported errors.

6. Generate an IDS Report

python -m ids.ids_report

The current report uses in-memory event and alert information. It is not a persistent historical audit report.

7. Operational Safety

Before production integration:

1. Verify that all tests pass.
2. Review input validation and secret redaction.
3. Confirm that event and alert histories have appropriate limits.
4. Protect access to security reports and logs.
5. Avoid exposing internal security events to public APIs.
6. Test failure handling and malformed requests.
7. Review the configuration before enabling collection.

8. Limitations

* Detection thresholds may produce false positives or miss sophisticated attacks.
* In-memory events may be lost when the process restarts.
* A health check confirms component checks, not overall system security.
* The IDS requires further integration and security testing before production use.

9. Safety Guarantee

The intended operating mode is monitor_only.

Automatic IP blocking and operating-system firewall modification must remain disabled unless a separate, explicitly reviewed and authorized design is implemented.

⸻

Tamanna AI — Security through monitoring, validation, and responsible operation.