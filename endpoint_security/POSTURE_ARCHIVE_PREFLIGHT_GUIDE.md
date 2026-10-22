Tamanna AI — Posture Archive Preflight Guide

Owner: HM INSAN ALI

1. Purpose

The preflight checker performs read-only structural checks on a Tamanna AI posture archive index before archive verification.

It checks:

* Project and owner identity
* Index JSON structure
* Report entries and duplicate filenames
* Safe filenames without path traversal
* SHA-256 hash formatting
* Recognized archive entry statuses

Important: Preflight checks validate the index structure. They do not prove that reports are authentic, trustworthy, or free from tampering.

2. Run a syntax check

From the repository root:

python3 -m py_compile \
  endpoint_security/posture_archive_preflight.py

3. Run the preflight checker

Replace PATH_TO_INDEX.json with the actual index path:

python3 -m endpoint_security.posture_archive_preflight \
  --index PATH_TO_INDEX.json

The command prints a JSON result to the terminal. It does not write a report file.

4. Run the tests

python3 -m unittest \
  endpoint_security.tests.test_posture_archive_preflight -v

5. Interpret the result

PASS

The index passed the structural checks implemented by the preflight module.

This does not prove that the report files match the hashes or that the index itself is trusted.

REVIEW_REQUIRED

One or more checks need attention. Review the findings list in the JSON output.

Examples include:

* PROJECT_MISMATCH
* OWNER_MISMATCH
* REPORTS_MUST_BE_LIST
* REPORT_0_INVALID_SHA256
* REPORT_0_UNSAFE_FILENAME

Do not treat a review-required archive as verified.

6. Recommended verification sequence

1. Run the preflight checker.
2. Review every finding.
3. Run the archive verifier against the index and report directory.
4. Preserve the original reports and index during investigation.
5. Review GitHub Actions test results before relying on the workflow.

7. Safety limitations

* The checker is a structural validation utility, not an endpoint detection and response system.
* A SHA-256 match only shows that file bytes match the hash recorded in the index.
* If an attacker can change both a report and its index, hash comparison alone may not detect the attack.
* Use trusted, access-controlled storage and signed or independently authenticated manifests when stronger integrity assurance is required.
* Do not put passwords, API tokens, or private keys into reports or logs.

8. Project identity

* Project: Tamanna AI
* Owner: HM INSAN ALI
* Operation: Read-only preflight validation