TI Tamanna AI

<p align="center">
  <img src="assets/tamanna-logo.svg" alt="TI Tamanna AI Logo" width="240">
</p>
<h3 align="center">Your AI. Your System. Your Control.</h3>
<p align="center">
  An extensible AI assistant and automation platform focused on intelligent tools, developer productivity, system security, and user-controlled infrastructure.
</p>
<p align="center">
  <a href="https://github.com/tamanna456760-it/Tamanna-">Repository</a> ·
  <a href="https://github.com/tamanna456760-it/Tamanna-/issues">Report a Bug</a> ·
  <a href="https://github.com/tamanna456760-it/Tamanna-/actions">GitHub Actions</a>
</p>

⸻

🇧🇩 বাংলা পরিচিতি

Tamanna AI একটি সম্প্রসারণযোগ্য AI assistant ও automation platform। এর লক্ষ্য হলো AI-ভিত্তিক কথোপকথন, developer tools, project analysis, automation এবং security ব্যবস্থাকে একটি সমন্বিত সিস্টেমে আনা।

প্রকল্পটির মালিকানা পরিচিতি: HM INSAN ALI

প্রধান লক্ষ্য

* AI chat ও API integration-এর জন্য একটি সম্প্রসারণযোগ্য ভিত্তি তৈরি করা।
* Python ও অন্যান্য সমর্থিত ভাষার কোড পরীক্ষা এবং debugging workflow তৈরি করা।
* Memory ও tool-routing সুবিধা পর্যায়ক্রমে উন্নত করা।
* GitHub Actions দিয়ে build, syntax validation এবং automated testing করা।
* Firewall, WAF, IDS এবং endpoint-security components-এর পরীক্ষা ও সমন্বয় করা।
* ব্যবহারকারীর অনুমতি ও নিয়ন্ত্রণ বজায় রেখে automation পরিচালনা করা।

গুরুত্বপূর্ণ: কোনো feature-এর কোড repository-তে থাকা মানেই সেটি সম্পূর্ণ কার্যকর বা production-ready নয়। প্রতিটি feature-এর অবস্থা test ও deployment-এর মাধ্যমে যাচাই করতে হবে।

⸻

🇬🇧 English Overview

Tamanna AI is an extensible AI assistant and automation project designed to bring together conversational interfaces, developer tools, project analysis, workflow automation, and security-oriented components.

The project aims to support modular development, controlled integrations, automated testing, and user-managed infrastructure.

Project Objectives

* Provide an extensible AI assistant foundation.
* Support code inspection, debugging, and developer workflows.
* Integrate memory and tool routing as supported modules.
* Validate application code using automated CI workflows.
* Test security components and configuration.
* Preserve user control over repository access, credentials, and automation.

Features and Development Areas

Component	Purpose
AI Assistant	Conversational AI and provider integrations
API Server	HTTP endpoints and application integration
Memory System	Conversation and project context, where implemented
Tool Router	Dispatch supported requests to available tools
Code Analysis	Syntax checks, linting, and debugging workflows
GitHub Automation	CI checks, build validation, and test workflows
Security Modules	Firewall, WAF, IDS, and endpoint-security components
Deployment	Configuration for running the application in supported environments
Audit and Logs	Diagnostic information and security-event review

Feature availability depends on the current implementation, installed dependencies, configuration, and test results.

Repository Structure

The repository may contain the following components as they are developed:

Tamanna-/
├── .github/
│   └── workflows/
├── assets/
│   └── tamanna-logo.svg
├── core/
├── data/
├── endpoint_security/
├── firewall/
├── ids/
├── tamanna_ai/
├── waf/
├── Main.py
├── main.py
├── README.md
└── .gitignore

This is a high-level project map, not a guarantee that every directory or file exists in every revision.

Requirements

* Python 3.12 recommended for the GitHub Actions workflow currently configured for the main runner.
* Git.
* Python packages specified by the project’s actual dependency files.
* Additional tools required by individual modules.
* API credentials only for external services that the user chooses to configure.

Installation

Clone the repository:

git clone https://github.com/tamanna456760-it/Tamanna-.git
cd Tamanna-

Create and activate a virtual environment:

python3 -m venv .venv
source .venv/bin/activate

Upgrade pip:

python -m pip install --upgrade pip

Install dependencies using the dependency file that exists in the checked-out revision:

if [ -f requirements.txt ]; then
  python -m pip install -r requirements.txt
elif [ -f pyproject.toml ]; then
  python -m pip install .
else
  echo "No root dependency manifest found."
  echo "Check the documentation for the selected module."
fi

Do not assume that installing the root dependencies installs every optional security, AI, or automation module.

Running Tamanna AI

Inspect the entry points and their instructions before starting the application:

python3 -m py_compile main.py Main.py

If both files exist and the syntax check succeeds, run the documented entry point for the current revision. For the configured main runner, the command is:

python3 main.py

The server’s actual startup requirements, available endpoints, and required environment variables must be confirmed from the implementation.

For a local FastAPI application, the OpenAPI document is commonly available at:

http://127.0.0.1:8000/openapi.json

This URL applies only if the application starts on that host and port and exposes the OpenAPI endpoint.

Configuration and Secrets

* Keep API keys, access tokens, passwords, and private credentials out of source code.
* Store local secrets in environment variables or an appropriate secrets manager.
* Keep .env files and credential files out of version control.
* Use .env.example for placeholder configuration only; never include real secrets.
* Grant GitHub Actions only the permissions required by each workflow.
* Review third-party integrations before enabling write access.

Never publish an active token in README files, logs, screenshots, or commits. If a secret is exposed, revoke or rotate it and investigate the repository history.

Security

Security-related development areas may include:

* Firewall configuration and request controls.
* Web Application Firewall (WAF) validation.
* Intrusion Detection System (IDS) tests.
* Endpoint-security and configuration audits.
* HTTPS/TLS configuration and certificate checks.
* Dependency and source-code validation.
* Audit logs and security test reports.

These components require appropriate configuration and independent testing. Their presence does not, by itself, establish that the application is secure or protected against every attack.

Do not expose an application publicly until authentication, authorization, TLS, secret management, and network access controls have been reviewed.

Testing and GitHub Actions

Review automated workflow results here:

Tamanna AI — GitHub Actions

Recommended validation includes:

1. Python syntax checks.
2. Dependency installation.
3. Unit tests.
4. API health checks.
5. Security configuration validation.
6. Secret scanning and dependency checks.
7. Deployment configuration validation.

A passing workflow verifies only the checks it actually runs.

Development Principles

* Preserve existing working code when adding features.
* Prefer small, reviewable changes over broad automatic rewrites.
* Test changes before committing them.
* Back up important work before resolving merge conflicts.
* Require explicit authorization for sensitive external actions.
* Keep credentials private and minimize permissions.
* Document known limitations and incomplete features.

Roadmap

* [ ]	Complete and verify the main application setup instructions.
* [ ]	Document the actual API endpoints.
* [ ]	Verify chat and AI provider integrations.
* [ ]	Test memory and tool-routing modules.
* [ ]	Validate all active GitHub Actions workflows.
* [ ]	Review secret exposure and repository permissions.
* [ ]	Test security modules independently.
* [ ]	Document supported deployment options.
* [ ]	Add verified examples and troubleshooting instructions.

Troubleshooting

Dependency installation fails

Check the Python version, the dependency manifest, and the error output. Install optional dependencies only when required by the selected module.

The application does not start

Check the entry point, syntax, imports, required environment variables, and startup logs.

GitHub Actions fails

Open the failed workflow run and inspect the first failing step. Fix the underlying issue before rerunning the workflow.

An API endpoint returns an error

Check the route implementation, server logs, configuration, and authentication requirements.

A credential may have been exposed

Revoke or rotate it immediately, check the commit history, and review access logs where available.

Contributing

Contributions should include a clear description of the change and relevant test results. Security-sensitive changes should be reviewed carefully before deployment.

License

A license has not been specified in this README. Check the repository for an existing license before declaring usage, redistribution, or contribution terms.

Project Ownership

Owner: HM INSAN ALI

Project: TI Tamanna AI

Repository: https://github.com/tamanna456760-it/Tamanna-

⸻

<p align="center">
  <strong>TI Tamanna AI</strong><br>
  Build carefully. Test continuously. Keep control in the user's hands.
</p>