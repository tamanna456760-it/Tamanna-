 <p align="center">
  <img src="assets/66EA0828-3C61-4162-8695-42D3032168C6.png"alt="TI Tamanna AI Logo" width="220">
</p>
<h1 align="center">Tamanna AI</h1>
<p align="center">
  A modular AI assistant and automation platform with a FastAPI server, memory and knowledge components, project tools, and security modules.
</p>
<p align="center"><strong>Owner: HM INSAN ALI</strong></p>
<p align="center">
  <a href="https://github.com/tamanna456760-it/Tamanna-">Repository</a> ·
  <a href="https://github.com/tamanna456760-it/Tamanna-/actions">GitHub Actions</a> ·
  <a href="https://github.com/tamanna456760-it/Tamanna-/issues">Issues</a>
</p>

⸻

Table of Contents

* Overview
* Features and Modules
* Repository Structure
* Requirements
* Local Installation
* Environment Configuration
* Docker Deployment
* API and Health Check
* Security
* Testing
* Production Deployment
* Contributing
* License

Overview

Tamanna AI is an evolving software project that brings together assistant APIs, project utilities, memory and knowledge components, automation, and defensive security tools.

The primary FastAPI application is implemented in Main.py. The lowercase main.py file is a compatibility launcher that imports the existing application.

Project status: Active development. The repository contains many modules and workflows, but the presence of a file does not guarantee that its functionality is integrated, production-ready, or successfully tested.

Features and Modules

The repository currently includes code for:

* AI Assistant API: Chat, status, skills, and project-operation endpoints.
* Skills and Code Tools: Skill discovery, matching, code inspection, and builder-related operations.
* Memory: Local memory and history modules.
* Knowledge Layer: A foundation for organizing and searching project resources.
* Security: Firewall, Web Application Firewall (WAF), Intrusion Detection System (IDS), endpoint checks, audit, and integrity utilities.
* Deployment: Docker configuration, Nginx/TLS examples, and deployment validation scripts.
* Automation: GitHub Actions workflows for builds, testing, security checks, and maintenance.
* Application Security: An admin API-key verification helper is present; its coverage across sensitive endpoints must be verified.

Some integrations, including a dedicated Gemini client and a documentation indexer, may still need implementation or integration.

Repository Structure

Path	Purpose
Main.py	Main FastAPI application
main.py	Python launch wrapper
tamanna_ai/	AI modules, skills, memory, and knowledge components
app_security/	Application security helpers
firewall/	Firewall policies, access controls, monitoring, and tests
waf/	Web application firewall components
ids/	Intrusion detection components and tests
endpoint_security/	Endpoint integrity, posture, audit, and validation
core/	Boot identity and integrity-related modules
deploy/	Deployment checks, Nginx configuration, and release validation
data/	Runtime data, depending on enabled modules
assets/	Static assets and project logo
.github/workflows/	GitHub Actions workflows
Dockerfile	Container image instructions
docker-compose.yml	Root Docker Compose configuration
requirements-server.txt	Server dependency list
requirements.txt	Broader project dependencies
requirements-optional.txt	Optional feature dependencies

Requirements

For the Python server:

* Python 3.12 is used by the current root Dockerfile.
* Git and Python pip.
* A Python virtual environment for local development.
* Docker Engine and the Docker Compose plugin, if using containers.

Some optional features may require additional operating-system libraries or external services.

Local Installation

Clone the repository:

git clone https://github.com/tamanna456760-it/Tamanna-.git
cd Tamanna-

Create and activate a virtual environment:

python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip

Install server dependencies:

pip install -r requirements-server.txt

Create a local environment file:

cp .env.example .env

Edit .env locally and enter only the configuration required by your setup.

Start the application:

python main.py

The launcher defaults to 127.0.0.1:8000.

When the server is running, open:

* API documentation: http://127.0.0.1:8000/docs
* ReDoc: http://127.0.0.1:8000/redoc
* Health check: http://127.0.0.1:8000/health

These addresses are for local development and work only while the server is running.

Environment Configuration

The tracked .env.example is a template, not a place to store real secrets.

Variable	Purpose
HOST	Server bind address; the launcher defaults to 127.0.0.1
PORT	HTTP port; defaults to 8000
RELOAD	Development auto-reload toggle
GEMINI_API_KEY	Placeholder for a Gemini credential if the integration is configured
TAMANNA_MEMORY_FILE	Optional memory-file path
DEBUG	Debug-mode setting; keep disabled in production

Never commit API keys, passwords, private keys, or production credentials. Use local environment variables or your hosting provider’s secret-management facility. If a secret is committed accidentally, revoke or rotate it; removing it from the latest file does not remove it from Git history.

Docker Deployment

The root Compose configuration references .env. Create it first:

cp .env.example .env

Validate the Compose configuration, then build and start:

docker compose config
docker compose build
docker compose up -d
docker compose ps
docker compose logs -f tamanna-ai

Check the health endpoint:

curl --fail http://127.0.0.1:8000/health

Stop the service:

docker compose down

The Compose file defines a named volume for application data. Verify the actual write paths used by each module before assuming all memory, chat history, or runtime state is persisted there.

Docker commands require Docker Engine to be installed and available.

API and Health Check

The main application declares routes for chat, skills, code-builder utilities, Linux tools, self-healing, and other project operations.

* GET /health — basic health endpoint.
* GET /docs — interactive API documentation.
* GET /redoc — alternative API documentation.

Treat endpoints that execute commands, edit files, apply code, or trigger autonomous actions as privileged. Verify authentication, authorization, input validation, audit logging, rate limits, and execution boundaries before exposing them publicly.

Security

The repository contains defensive security modules. Their presence alone does not prove that a deployed service is secure.

Before a public deployment:

1. Restrict CORS to trusted frontend origins.
2. Require authentication and authorization for administrative, shell, file-write, code-apply, and automation endpoints.
3. Keep credentials out of Git and client-side code.
4. Run dependency and secret scans and review the results.
5. Configure HTTPS with valid certificates.
6. Verify the reverse-proxy upstream and network boundaries.
7. Run tests and smoke checks against the exact release being deployed.
8. Back up persistent data and test restoration.
9. Review GitHub Actions permissions and apply least privilege.
10. Require explicit approval for workflows that make consequential changes or deploy production code.

Do not treat a successful workflow badge or a configuration file as proof of production security. Validate the live deployment independently.

Testing

Security-related test suites exist in several modules. From the repository root, run:

python -m compileall -q Main.py main.py tamanna_ai app_security

If the relevant test dependencies are installed, run:

python -m pytest firewall/tests ids/tests endpoint_security/tests

Inspect any failures and fix the underlying issue instead of hiding failures with || true.

For each release candidate, record the tested commit, Python/dependency versions, test results, security scan results, and Docker/deployment smoke-test results where applicable.

Check the current GitHub Actions results before relying on a build.

Production Deployment

Deployment examples and validation scripts are available under deploy/.

Before using them, verify:

* DNS for tamanna.com and www.tamanna.com points to the intended server.
* TLS certificate paths match the installed certificate.
* Nginx forwards requests to the correct reachable application address.
* In a shared Docker Compose network, the upstream may need to use the service name instead of host loopback.
* Only required network ports are exposed.
* Production environment variables and persistent volumes are configured.
* HTTPS, health checks, logs, restarts, and recovery procedures have been tested.

Configuration examples do not provision a server or deploy the application by themselves.

Contributing

1. Create a focused branch for your change.
2. Keep changes small and avoid committing virtual environments, generated files, logs, or credentials.
3. Add or update tests for behaviour changes.
4. Run the relevant checks and review the diff.
5. Describe changes, test results, and security impact in the pull request.

Avoid removing existing functionality as part of an unrelated change. Report suspected security vulnerabilities privately to the maintainer rather than publishing sensitive exploit details.

License

See the repository’s LICENSE file for the applicable terms.

⸻

<p align="center">
  <sub>Tamanna AI · Owner: HM INSAN ALI</sub>
</p>