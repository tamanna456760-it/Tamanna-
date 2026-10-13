Tamanna AI — Web Application Firewall (WAF)

Owner: HM INSAN ALI
Version: 1.0.0
Default mode: monitor_only

1. Overview

Tamanna AI WAF is an initial Python-based request-inspection component designed to identify common suspicious HTTP request patterns.

It includes:

* Request metadata inspection
* Basic SQL injection pattern detection
* Basic cross-site scripting (XSS) pattern detection
* Basic path traversal pattern detection
* JSON Lines security event logging
* Configuration and health checks
* JSON health reporting

2. Safety Defaults

The current implementation is monitor-only.

* Request blocking is disabled.
* Operating-system firewall modification is disabled.
* Detection results are informational.
* The WAF is not yet integrated as HTTP middleware.
* A successful health check does not prove that all attacks can be detected.

Do not describe this initial implementation as production-ready protection.

3. Configuration

Main configuration file:

waf/waf_config.json

Important settings include:

* enabled: enables or disables the WAF manager.
* mode: must remain monitor_only.
* request_limits: sets request size and metadata limits.
* detection: enables or disables supported detection rules.
* rules: controls which request fields are inspected.
* logging: controls event logging and redaction.
* enforcement: keeps blocking and system firewall modification disabled.

Validate configuration changes before deploying them.

4. Event Logging

Default event log:

data/waf_events.jsonl

Health report:

reports/waf_report.json

Protect these files with appropriate filesystem permissions. Avoid recording raw passwords, authentication headers, session cookies, or complete sensitive request bodies.

The current logger redacts certain dictionary keys. It does not guarantee removal of secrets embedded in arbitrary strings.

5. Detection Limitations

The current rule engine uses regular expressions and heuristic matching.

It may produce:

* False positives: normal requests flagged as suspicious.
* False negatives: malicious requests that do not match the implemented patterns.
* Inconsistent results for encoded or obfuscated payloads.

These rules do not replace framework security controls, parameterized SQL queries, output encoding, input validation, or a maintained WAF engine.

6. Recommended Validation

Before production use:

1. Run all unit tests.
2. Fix failing tests and interface mismatches.
3. Add tests for URL decoding and repeated query parameters.
4. Validate request-body size before reading the entire body into memory.
5. Test event-log permissions, rotation, and disk-space handling.
6. Integrate with the web framework through a carefully tested middleware layer.
7. Verify that sensitive information is not exposed in logs.
8. Review detection rules against representative benign and malicious test cases.
9. Keep a backup and rollback plan.

7. Test Command

From the repository root:

python3 -m unittest discover -s waf/tests -p "test_*.py" -v

This command is a suggested test procedure; test success has not yet been verified.

8. Security Policy

Do not enable automatic request blocking or system firewall changes through this initial implementation. Any future enforcement feature must have separate tests, explicit authorization, audit logging, and a documented rollback procedure.

⸻

Tamanna AI — HM INSAN ALI
Monitor first. Validate carefully. Enforce only after testing.