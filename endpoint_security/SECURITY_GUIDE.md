Tamanna AI — Endpoint Security Guide

Owner: HM INSAN ALI
Version: 1.0.0
Default mode: monitor_only

1. Purpose

Tamanna AI Endpoint Security provides an initial framework for inspecting running processes, calculating file hashes, comparing file integrity baselines, and recording security events.

It is designed to support controlled security monitoring. It is not a replacement for a mature endpoint detection and response (EDR) platform.

2. Safety defaults

The default configuration disables:

* Process termination
* File deletion
* File quarantine
* Operating-system setting changes

The implementation is monitor-only. Do not enable enforcement options unless a separate, reviewed implementation explicitly supports them.

3. Components

Component	Purpose
endpoint_config.json	Monitoring and safety configuration
process_monitor.py	Collects limited process inventory
file_integrity.py	Calculates SHA-256 hashes and compares baselines
event_logger.py	Writes structured security events
manager.py	Coordinates monitoring components
health_check.py	Checks configuration and initialization
__main__.py	Command-line interface
tests/	Unit tests

4. Installation

From the repository root:

python3 -m pip install -r endpoint_security/requirements.txt

If psutil cannot be installed in your environment, process monitoring may report that it is unavailable.

5. Usage

Check configuration health:

python3 -m endpoint_security health

Inspect the current process inventory:

python3 -m endpoint_security processes

Calculate the hash of a selected file:

python3 -m endpoint_security file-hash README.md

Run unit tests:

python3 -m unittest discover -s endpoint_security/tests -v

6. File integrity baselines

A hash is useful only when compared against a trusted baseline.

* Generate baselines from files known to be legitimate.
* Store baseline records separately with restricted write access.
* Recheck files after approved updates.
* Investigate unexpected changes before taking action.

A hash match does not prove a file is safe; it only shows that its contents match the supplied baseline.

7. Logging and privacy

The logger attempts to redact values under recognized sensitive dictionary keys. It does not reliably identify secrets embedded in arbitrary text.

Protect log files with appropriate file permissions. Add log rotation and retention limits before deploying on a long-running system.

8. Known limitations

* Unknown or non-allowlisted processes are not necessarily malicious.
* Process visibility varies by operating system and permissions.
* Monitoring is not continuous unless an external scheduler or service is configured.
* Health checks do not establish that the host is malware-free.
* File hashes can be misleading if both a file and its baseline are compromised.
* This implementation does not prevent attacks or automatically remediate threats.

9. Validation checklist

* [ ]	Run the unit tests.
* [ ]	Verify the monitor-only configuration.
* [ ]	Test file hashing using temporary sample files.
* [ ]	Confirm log files do not contain secrets.
* [ ]	Confirm process inventory works in the target operating system.
* [ ]	Review file permissions and logging retention.
* [ ]	Document the expected process allowlist before enabling alerts.

⸻

Tamanna AI — Monitor carefully, validate findings, and keep enforcement under explicit control.