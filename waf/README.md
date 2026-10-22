Tamanna AI — Web Application Firewall (WAF)

Owner: HM INSAN ALI
Version: 1.0.0
Current mode: Monitor-only

Overview

Tamanna AI WAF is a Python-based request inspection component designed to identify suspicious web requests and record security findings.

It provides an initial foundation for detecting:

* SQL injection-like patterns
* Cross-site scripting (XSS) patterns
* Path traversal attempts
* Oversized requests
* Suspicious or malformed request metadata

Security defaults

* Monitor-only mode: enabled by default
* Automatic request blocking: disabled
* Operating-system firewall changes: disabled
* Manual approval: required for enforcement changes
* Security event logging: configurable
* Request and header limits: configurable

Important: This is an initial security component, not a complete production WAF. It does not protect live traffic until it is deliberately integrated with the web server or application middleware.

Project files

File or directory	Purpose
waf_config.json	WAF configuration and safety defaults
request_inspector.py	Checks request size and metadata limits
rule_engine.py	Detects suspicious request patterns
event_logger.py	Writes security events to JSONL
waf_manager.py	Coordinates inspection, rules, and logging
health_check.py	Checks configuration and component health
waf_report.py	Generates a health report
run_tests.py	Runs the unit test suite
tests/	WAF unit tests
SECURITY_GUIDE.md	Security guidance and known limitations

Run the health check

From the repository root:

python3 -m waf

Or specify the configuration path:

python3 -m waf waf/waf_config.json

Run the tests

python3 waf/run_tests.py

Tests must pass in your environment before you treat this component as validated.

Generate a health report

python3 -m waf.waf_report

The default report location is reports/waf_report.json.

Known limitations

* Pattern matching can produce false positives and false negatives.
* URL-encoded attacks may not be detected correctly until decoding and normalization are implemented.
* Request inspection is not equivalent to full HTTP protocol validation.
* This component has not been integrated into live FastAPI traffic by these files alone.
* A successful health check does not prove that the WAF can stop every attack.

Recommended next steps

1. Run the unit tests and fix all failures.
2. Add URL decoding and canonicalization before security-rule matching.
3. Improve duplicate query-parameter counting.
4. Add integration tests using a test-only web application.
5. Integrate monitor-only inspection into the application middleware.
6. Validate performance and security behavior before considering any enforcement mode.

⸻

Tamanna AI — Security through inspection, testing, and controlled changes.