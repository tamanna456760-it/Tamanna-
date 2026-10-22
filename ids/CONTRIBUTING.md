Contributing to Tamanna AI IDS

Project: Tamanna AI
Owner: HM INSAN ALI
Version: 1.0.0

Thank you for contributing to Tamanna AI IDS.

1. Core Principles

All contributions must preserve these principles:

* Keep the default mode set to monitor_only.
* Never enable automatic IP blocking by default.
* Never modify the operating system firewall automatically.
* Redact sensitive information from collected events.
* Keep detection logic separate from alert handling.
* Prefer small, testable changes.

2. Development Setup

From the repository root, install development dependencies:

python3 -m pip install -r ids/requirements-dev.txt

Validate the configuration:

python3 -m ids.ids_cli config

Run the tests:

python3 -m unittest discover -s ids/tests -p "test_*.py" -v

These commands should be run in a suitable Python environment. They have not yet been verified against every project file.

3. Adding Detection Rules

When adding a detection rule:

1. Define the event or behavior being detected.
2. Specify the threshold and time window.
3. Include a clear reason in each alert.
4. Avoid storing passwords, tokens, or unnecessary personal data.
5. Add unit tests for normal, suspicious, and boundary cases.
6. Confirm that alerts do not trigger automatic blocking.

4. Adding or Changing Configuration

* Update ids/ids_config.json when configuration keys change.
* Update ids/config_loader.py to validate new settings.
* Update configuration tests.
* Reject invalid values clearly.
* Preserve monitor_only as the supported operating mode.

5. Testing Requirements

Before submitting a change, run:

python3 -m unittest discover -s ids/tests -p "test_*.py" -v
python3 -m ids.validate_project

Report any failing tests honestly. Do not claim a test passed unless it actually ran successfully.

6. Security Requirements

Contributions must not:

* Execute shell commands from untrusted event data.
* Expose credentials in logs or reports.
* Introduce hidden network activity.
* Change firewall rules without an explicitly designed and reviewed authorization process.
* Disable existing validation or safety checks to make a test pass.

7. Pull Request Checklist

* [ ]	Tests added or updated.
* [ ]	Configuration validation updated where necessary.
* [ ]	Sensitive data handling reviewed.
* [ ]	Monitor-only behavior preserved.
* [ ]	No real secrets committed.
* [ ]	Documentation updated.
* [ ]	Test results included in the pull request.

8. Reporting Security Issues

Do not publish real credentials, personal information, or exploitable details in public issues. Use a private reporting channel controlled by the repository owner when available.

⸻

Tamanna AI IDS is intended to provide visibility into suspicious activity while keeping enforcement disabled by default.