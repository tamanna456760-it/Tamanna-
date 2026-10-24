
<p align="center">
  <img
    src="https://raw.githubusercontent.com/tamanna456760-it/Tamanna-/main/assets/tamanna-logo.svg"
    alt="TI Tamanna AI Logo"
    width="280"
  />
</p>


<p align="center">
  <img src="assets/tamanna-logo.svg" alt="TI Tamanna AI Logo" width="260">
</p>
<h1 align="center">TAMANNA AI</h1>
<p align="center">
  <strong>Personal AI System · Automation · Project Intelligence · Security</strong>
</p>
<p align="center">
  <em>Owner: HM INSAN ALI</em>
</p>
<p align="center">
  <a href="https://github.com/tamanna456760-it/Tamanna-">GitHub Repository</a> ·
  <a href="https://github.com/tamanna456760-it/Tamanna-/issues">Issues & Support</a>
</p>

⸻

About Tamanna AI

Tamanna AI is a modular AI and automation project designed to bring conversational interfaces, project analysis, developer tools, system monitoring, and security components together in one extensible platform.

The project is being developed toward a user-controlled AI environment where the owner can manage project files, configure integrations, inspect system activity, and decide which operations are permitted.

Tamanna AI is designed to grow incrementally. Features described as planned or under development must not be assumed to be production-ready until their implementation and tests have been verified.

বাংলা পরিচিতি

Tamanna AI হলো HM INSAN ALI-এর নিজস্ব AI system project। এর লক্ষ্য হলো AI chat, code analysis, project management, automation, memory, server management এবং security tools-কে একটি modular platform-এ একত্র করা।

প্রকল্পটির মূল নীতি:

* নিজের system ও project-এর ওপর ব্যবহারকারীর নিয়ন্ত্রণ।
* অনুমতি ছাড়া গুরুত্বপূর্ণ file বা system পরিবর্তন না করা।
* Sensitive command-এর আগে authorization ও confirmation যাচাই করা।
* Security checks, logs এবং test results-এর মাধ্যমে কাজ যাচাই করা।
* নতুন module যোগ করার সময় পুরোনো working functionality অক্ষত রাখা।

Project Goals

* Develop an extensible AI assistant and API server.
* Provide a foundation for project scanning and code analysis.
* Support controlled file operations and developer automation.
* Organize security tools into separate, testable modules.
* Maintain auditable logs and predictable error handling.
* Integrate external AI providers only when explicitly configured.
* Support user-controlled deployment and future self-hosted operation.

Features and Implementation Status

Component	Purpose	Status
FastAPI server	HTTP API and application entry point	Implemented; deployment testing required
Chat API	Receive messages and return responses	Implemented; end-to-end verification required
Knowledge and memory	Basic knowledge and memory operations	Basic implementation; persistence needs verification
Project scanning	Inspect project files and Python syntax	Partial; coverage needs testing
Code Builder	Plan and manage code changes	Partial; real file-write behavior needs verification
Skill Manager	Organize assistant skills	Partial; actual skill execution needs verification
Linux tools	Provide a foundation for system utilities	Partial; secure execution required
File action bridge	Route file-operation requests	Partial; actual operations need verification
Firewall components	Organize firewall-related utilities	Requires platform-level validation
WAF components	Web request protection utilities	Live request integration must be verified
IDS components	Intrusion detection utilities	Detection and alerting tests required
Endpoint Security	Security posture and audit checks	Partial; monitoring and enforcement must be distinguished
GitHub Actions	Automated checks and workflow execution	Available workflows require run-by-run verification
External AI provider	Connect a real LLM	Requires provider configuration and integration testing
Production deployment	Run a hardened public service	Not declared production-ready

Repository

Main repository:

https://github.com/tamanna456760-it/Tamanna-

Default branch: main

Main project areas

Tamanna-/
├── .github/
│   └── workflows/
├── assets/
│   └── tamanna-logo.svg
├── core/
├── data/
│   ├── action_router/
│   ├── autonomous/
│   ├── control_center/
│   └── linux/
├── endpoint_security/
├── firewall/
├── ids/
├── modules/
│   └── tamanna/
├── runner/
├── tamanna_ai/
│   ├── brain/
│   ├── core/
│   ├── tools/
│   ├── code_builder.py
│   └── skills.py
├── waf/
├── Main.py
├── main.py
├── requirements.txt
├── .gitignore
└── README.md

This is a high-level map of important project areas, not a guarantee that every optional file or subdirectory exists in every revision.

Requirements

The basic server environment uses:

* Python 3.12 recommended for CI compatibility.
* Git.
* pip.
* FastAPI.
* Uvicorn.
* Additional dependencies required by the modules you enable.

Some optional project components may require operating-system packages, database services, AI-provider credentials, audio libraries, or additional configuration.

Important: Install only dependencies needed for your selected environment. The repository’s full requirements.txt may contain optional or platform-specific packages; verify compatibility before installing everything.

Installation

1. Clone the repository

git clone https://github.com/tamanna456760-it/Tamanna-.git
cd Tamanna-

If the repository is already cloned, open its existing project directory instead of cloning it again.

2. Create a virtual environment

Linux, macOS, or compatible shell:

python3 -m venv .venv
source .venv/bin/activate

Upgrade pip:

python -m pip install --upgrade pip

3. Install the basic server dependencies

python -m pip install fastapi uvicorn

Before installing the full dependency list, inspect requirements.txt and resolve any unsupported or unnecessary packages for your operating system.

If the complete dependency file has been validated for your environment, install it with:

python -m pip install -r requirements.txt

4. Check Python syntax

python -m py_compile main.py Main.py

A successful command returns without a syntax error. This does not prove that all dependencies, routes, integrations, or runtime operations work.

5. Start the application

First inspect main.py to confirm how it launches the application. If it is the intended launcher:

python main.py

If the launcher does not start the server itself, and Main.py exposes the FastAPI object as app, use:

python -m uvicorn Main:app --host 127.0.0.1 --port 8000

Do not start both commands simultaneously on the same port.

6. Verify the local API

If the server starts successfully, open:

* API documentation: http://127.0.0.1:8000/docs
* OpenAPI schema: http://127.0.0.1:8000/openapi.json

These endpoints are available only if the server is running and its configuration permits them.

API Overview

The application contains chat and system-control functionality. The following endpoints must be confirmed against the running server’s OpenAPI schema before use.

Endpoint	Purpose
/docs	Interactive API documentation, when enabled
/openapi.json	API schema, when enabled
/api/chat	Chat request handling
/api/command	Command preview and controlled execution flow
/api/linux/shell	Linux command functionality; sensitive and potentially dangerous
/api/memory/add	Memory operation, if enabled in the running configuration

Chat API example

The following is a generic example. Confirm the exact request schema in /docs before sending it.

curl -X POST http://127.0.0.1:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"Hello Tamanna"}'

A valid response should be inspected for its status code, response structure, and error fields. A successful HTTP response alone does not prove that an external AI model was invoked.

Command execution policy

System commands can change files, permissions, network configuration, or application state. A request field such as confirm: true is not a substitute for identity verification or authorization.

Before enabling command execution:

* Require authenticated access.
* Apply role-based permissions.
* Allow only explicitly approved commands and arguments.
* Avoid shell-string execution.
* Enforce timeouts and resource limits.
* Record permitted operations in an audit log.
* Keep administrative endpoints private until tested.

Do not expose a command-execution API directly to the public internet without these protections.

AI Provider Configuration

Tamanna AI can be extended to use an external or self-hosted AI model, but an AI provider should be considered connected only after its credentials, client implementation, error handling, and real response path have been tested.

Recommended configuration practices:

1. Choose the intended AI provider.
2. Read its official API documentation.
3. Store credentials in environment variables or an approved secret manager.
4. Keep credentials out of source files, logs, and README examples.
5. Configure request timeouts, usage limits, and error handling.
6. Test a real request using non-sensitive input.
7. Document which components require the provider.

Example environment-variable names:

AI_PROVIDER=
AI_API_KEY=
AI_MODEL=

These names are illustrative. The application must explicitly implement and read the corresponding variables before they have any effect.

Never commit a real API key.

Memory and Data Management

Memory functionality should clearly distinguish between:

* Temporary, in-process memory.
* Persistent storage on disk.
* Database-backed memory.
* External provider or service storage.

Do not assume that memory survives a server restart unless persistence has been implemented and tested.

Recommended safeguards:

* Validate input before saving.
* Limit stored data and request sizes.
* Protect memory endpoints with authentication.
* Avoid storing passwords, API keys, or sensitive personal information.
* Define retention and backup policies.
* Test recovery and data deletion procedures.

Security Architecture

Tamanna AI contains separate security-related project areas, including firewall, WAF, IDS, and endpoint-security components.

These components are intended to form a layered security approach. Their actual protection depends on correct implementation, integration, configuration, and testing.

1. Application security

* Authenticate users before sensitive operations.
* Authorize each administrative action separately.
* Validate request data.
* Limit request rates and payload sizes.
* Avoid exposing stack traces or secrets in API responses.
* Configure trusted CORS origins explicitly.

2. Firewall

Firewall functionality should be tested on the intended operating system with least-privilege rules and a recovery plan. A Python module alone does not establish that operating-system firewall rules are active.

3. Web Application Firewall

A WAF must inspect real incoming traffic through an integrated middleware or reverse-proxy layer. Test both allowed and blocked requests, including false positives.

4. Intrusion Detection System

IDS functionality should have tested event sources, detection rules, alert delivery, and evidence records. Detection-only functionality must not be described as automatic blocking.

5. Endpoint security

Endpoint monitoring and security enforcement are different capabilities. Clearly document whether each check only reports a finding or actually takes an authorized protective action.

6. HTTPS and TLS

Use HTTPS for remote deployments. Manage certificates, renewals, trusted proxy configuration, and secure transport settings. Never assume that HTTPS is active simply because a TLS configuration file exists.

7. Logs and audit records

Logs should include useful event details without exposing credentials, session tokens, or private data. Protect logs against unauthorized modification and define retention limits.

GitHub Actions and CI

The repository contains GitHub Actions workflows for application startup checks and security-related testing.

The CI pipeline should progressively verify:

1. Python syntax.
2. Dependency installation.
3. Module imports.
4. Configuration and JSON validation.
5. Unit tests.
6. Security checks.
7. Application startup.
8. API health checks.
9. Chat and memory integration tests.
10. Authorization and command-safety tests.

A passing syntax check or an HTTP response from /openapi.json does not establish that every feature is working.

Run workflows

1. Open the repository on GitHub.
2. Select Actions.
3. Choose the workflow you want to inspect.
4. Open its latest run.
5. Review each step’s result and logs.

GitHub Actions workflow files must be located under .github/workflows/ to be recognized as standard repository workflows.

Testing

Run the tests that exist in the repository and confirm their actual results before declaring a component functional.

Basic checks

python -m py_compile main.py Main.py

Inspect available test files:

find . -type f -name 'test_*.py' \
  -not -path './.git/*' \
  -not -path './.venv/*'

If pytest is installed and the repository’s tests are configured for it:

python -m pytest -q

If the project uses unittest, run the relevant test modules according to their documented invocation.

Minimum release checklist

* [ ]	Application imports successfully.
* [ ]	Server starts without an unexpected exception.
* [ ]	Health and OpenAPI endpoints respond as expected.
* [ ]	Chat request validation works.
* [ ]	AI integration is verified, if configured.
* [ ]	Memory persistence behavior is documented and tested.
* [ ]	Unauthorized requests cannot execute sensitive operations.
* [ ]	Command execution uses an enforced allowlist.
* [ ]	Security configuration validators behave correctly.
* [ ]	Audit tests pass on valid and invalid configurations.
* [ ]	Logs do not expose credentials.
* [ ]	Backup and restore procedures have been tested.
* [ ]	Deployment uses HTTPS where remote access is enabled.

Configuration and Secrets

Do not store secrets or private credentials in source control.

Common sensitive items include:

* .env and environment-specific configuration.
* API keys and access tokens.
* api/token and api/token.txt.
* Credential JSON files.
* Private keys and TLS certificates.
* Database credentials and session secrets.

Use environment variables or a dedicated secret manager. Keep .env.example limited to placeholder values.

Important: .gitignore prevents matching untracked files from being added by normal Git workflows, but it does not automatically remove a secret file that is already tracked. If a real credential has been committed, revoke or rotate it first and then remove it from version control appropriately.

Backup and Recovery

Before making major changes:

1. Check the current Git status.
2. Create a backup of important uncommitted work.
3. Review the planned changes.
4. Run relevant tests.
5. Commit only the intended files.
6. Verify the resulting commit and CI run.

For sensitive configuration and user data, maintain a separate protected backup. Do not commit backups containing secrets or personal data.

A rollback procedure should be tested before being relied upon for recovery.

Troubleshooting

ModuleNotFoundError

Activate the correct virtual environment and install the dependencies required by the missing module.

Port 8000 is already in use

Inspect the process listening on the port before stopping anything. Do not terminate an unknown process blindly.

Server starts but chat does not work

Check the application logs, chat route schema, required environment variables, provider credentials, and the configured AI integration.

GitHub Actions fails during installation

Inspect the first failing installation step. Check Python compatibility, platform-specific dependencies, and whether all listed packages are required for that workflow.

Security audit fails

Inspect the individual validator outputs and test results. Confirm that result types and error handling are consistent. Do not suppress a failed check merely to obtain a green workflow.

A module reports success without changing anything

Verify the implementation and inspect the resulting file, system state, or audit evidence. Status messages alone are not proof that an operation completed.

Development Principles

Contributions to Tamanna AI should follow these principles:

* Prefer additive, reviewable changes.
* Preserve existing working behavior unless a change is intentional.
* Keep security-sensitive functionality isolated and permission-controlled.
* Use clear module boundaries.
* Validate all external input.
* Avoid silent exception handling.
* Add tests for bug fixes.
* Document incomplete features honestly.
* Never include real secrets in code, test fixtures, or documentation.

Roadmap

The following are development goals, not claims that the features are already complete.

Phase 1 — Core stability

* [ ]	Complete the README and installation instructions.
* [ ]	Standardize runtime dependencies.
* [ ]	Verify application startup and API routes.
* [ ]	Fix security-audit and validation defects.
* [ ]	Establish reliable automated tests.

Phase 2 — Security hardening

* [ ]	Enforce authentication and authorization.
* [ ]	Secure command execution.
* [ ]	Restrict CORS and administrative endpoints.
* [ ]	Verify WAF and IDS integration.
* [ ]	Improve logging and audit evidence.
* [ ]	Test backup and recovery.

Phase 3 — AI capabilities

* [ ]	Integrate and test a real AI provider.
* [ ]	Improve persistent memory.
* [ ]	Add verified code analysis and generation.
* [ ]	Make file operations transactional and auditable.
* [ ]	Add controlled tool execution.

Phase 4 — User-controlled deployment

* [ ]	Provide reproducible deployment configuration.
* [ ]	Add HTTPS and TLS verification.
* [ ]	Improve monitoring and health checks.
* [ ]	Document private-server deployment.
* [ ]	Add tested update and rollback procedures.

Phase 5 — Advanced automation

* [ ]	Add approval-based automation workflows.
* [ ]	Improve project indexing and search.
* [ ]	Add controlled Git integration.
* [ ]	Verify integrations with external services.
* [ ]	Expand regression and security testing.

Contributing

Contributions should include a clear description of the problem, the intended behavior, the changes made, and the tests performed.

For bug reports, include:

* Relevant module or file.
* Steps to reproduce.
* Expected behavior.
* Actual behavior.
* Sanitized logs or error messages.
* Environment and Python version.

Do not publish secrets, private credentials, or sensitive production logs in issues.

License

A license has not been confirmed in this documentation. Review the repository’s licensing status before redistributing, modifying, or commercially using the project.

Project Ownership

Project: Tamanna AI
Owner attribution: HM INSAN ALI
Repository: tamanna456760-it/Tamanna-

⸻

<p align="center">
  <strong>TAMANNA AI</strong><br>
  <em>Build carefully. Verify every feature. Keep the system under user control.</em>
</p>