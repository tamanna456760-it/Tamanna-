# Tamanna AI Autonomous Operations Policy

## Goal

Tamanna AI may continuously inspect, diagnose, propose fixes, and improve its own application and website. Autonomy must be bounded by explicit capabilities, a restricted execution environment, and recoverable changes. "Full permission" must never mean unrestricted access to the host, credentials, user data, external accounts, or production deployment.

## Permission tiers

| Tier | Allowed actions | Default |
| --- | --- | --- |
| Observe | Read repository files, application health, logs with secrets redacted, test results, dependency advisories, and public release notes | Enabled for authenticated administrators |
| Diagnose | Run allowlisted read-only checks, tests, static analysis, and dependency/configuration validation in an isolated workspace | Enabled after runtime setup |
| Propose | Prepare patches, explain impact, show diffs, and create a branch or draft pull request | Enabled after GitHub access is configured |
| Sandbox write | Edit files only inside the dedicated repository workspace; run tests; create commits on a non-protected branch | Disabled until explicitly enabled by an administrator |
| Production change | Merge to protected main, deploy/restart services, change DNS/firewall/TLS, alter databases, or modify infrastructure | Require a separate human approval for each operation |
| Sensitive / destructive | Read or export secrets, change credentials, disable security controls, delete data/backups, run arbitrary shell commands, or grant itself more privileges | Never allowed autonomously |

## Required safeguards

1. Run the agent as a dedicated non-root OS account in a container or isolated worker. Mount only the repository workspace; do not mount the host root, Docker socket, SSH keys, cloud credentials, or unrelated user data.
2. Keep production secrets in a secret manager or private environment. Do not expose secret values to prompts, logs, task output, or repository files.
3. Use an allowlist of diagnostics and commands. Never accept a shell command, filesystem path, URL target, or deployment target directly from an untrusted chat prompt.
4. Default to read-only. Sandbox writes require an administrator-controlled server setting and per-task confirmation. The agent cannot enable its own write/deploy permissions.
5. Require a clean baseline, tests, reviewable diff, backup/rollback plan, and explicit approval before merge or production deployment.
6. Keep immutable audit records of who requested an action, the task, files changed, commands/checks run, results, approvals, and rollback reference. Redact secrets and personal data.
7. Apply rate limits, timeouts, output limits, resource quotas, and a kill switch controlled outside the agent.
8. Never allow the agent to alter its own permission policy, remove audit records, disable monitoring, or change the protected-branch rules.
9. For website and server incidents, diagnose first. Automatically apply only reversible, pre-approved fixes in the sandbox; production restart, migration, firewall, DNS, certificate, and data changes require approval.
10. Feature discovery may review official release notes and security advisories, then produce a compatibility proposal. It must not copy code blindly, add dependencies, or deploy new features without tests and review.

## Continuous operation model

Use an external process supervisor and health monitoring (for example, systemd or a container orchestrator) to keep the backend alive and restart it after a crash. Tamanna AI itself must not be the only process responsible for keeping its own supervisor alive. A GitHub Codespace or github.dev editor is a development workspace, not a guaranteed always-on production host.

Use separate health checks for:
- API readiness and liveness
- model-provider availability
- database connectivity and backup freshness
- website HTTP/TLS response
- CI status and dependency/security alerts

Alert an administrator when a check fails. An automated repair may run only when it matches a documented, reversible runbook. Otherwise create a diagnosis and proposed patch.

## Safe rollout

1. Observe-only mode; verify authentication, redaction, logging, and health checks.
2. Read-only diagnostics and tests.
3. Branch-only code changes in an isolated workspace.
4. Human-reviewed pull requests and CI.
5. Separately approved production deployment and rollback verification.

The Codex bridge is only one execution adapter. It does not by itself provide a durable worker, a production supervisor, automatic deployment, or a guarantee that the backend remains online.
