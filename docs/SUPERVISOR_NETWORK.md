# Tamanna AI Supervisor Network

## Structure

The repository uses a hierarchical supervisor registry. Each detected repository section has:
- one section supervisor responsible for ownership, coordination, and escalation;
- five specialist reviewers for architecture, implementation, testing, security, and operations;
- one deterministic ownership record for every tracked file, linking that file to its section supervisor and all five specialist reviewers.

The registry is generated from `git ls-files` at runtime, so newly tracked files are assigned automatically without creating thousands of manually maintained agent files. Files not in a Git checkout are discovered by a filesystem fallback.

## Important distinction

These are **supervisor roles and routing records**, not five newly running independent AI models per section. No additional model processes, paid API calls, or background workers are created by importing the registry. A future worker/orchestrator can dispatch tasks to these roles when a real model runtime is configured.

## Permission boundaries

- Read-only inspection is the default.
- Sandbox code changes require an administrator-controlled server setting and per-task confirmation.
- Each proposed patch should pass the specialist test and security reviews.
- Merge, production deployment, service restarts, database migrations, DNS/firewall/TLS changes, and destructive operations require separate human approval.
- Supervisors cannot grant themselves permissions, change protected-branch rules, disable security controls, or erase audit records.

## API

Authenticated administrators can call `GET /api/supervisors/status` for section and file coverage counts, and `GET /api/supervisors/file?path=relative/path` to inspect the owner and five specialist reviewers for one tracked file. These endpoints do not expose file contents or secrets, and do not execute supervisor tasks.
