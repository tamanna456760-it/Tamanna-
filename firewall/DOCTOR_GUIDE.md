Tamanna AI Firewall — Doctor Guide

Owner: HM INSAN ALI

Purpose

The diagnostic CLI checks the Tamanna AI Firewall project and prints a JSON report. It is intended for read-only diagnostics.

Run diagnostics

From the repository root:

python3 -m firewall.doctor_cli

Strict mode

Return a non-zero exit code when diagnostics report issues:

python3 -m firewall.doctor_cli --strict

Check a specific project directory

python3 -m firewall.doctor_cli --base-dir "/path/to/project"

Replace /path/to/project with the actual project directory.

Exit codes

Code	Meaning
0	Diagnostics completed; strict mode did not detect a failure
1	Strict mode found reported issues
2	A handled diagnostic error occurred

Safety

* The CLI is intended to inspect project files and configuration.
* It does not intentionally change operating-system firewall rules.
* A successful diagnostic report does not prove that the system is secure.
* Review the report and investigate warnings before deploying changes.

Testing

Run the CLI tests from the repository root:

python3 -m unittest firewall.tests.test_doctor_cli -v

Run the full firewall test suite:

python3 -m firewall.run_tests