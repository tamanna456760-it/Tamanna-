# Tamanna AI Supervisor Network

## Team layout

Every detected repository section receives one section lead plus five specialists:
- Architecture: design consistency and cross-module compatibility.
- Implementation: code creation and upgrades, limited to an approved sandbox or feature branch.
- Testing: regression, syntax, build, and test evidence.
- Security: privacy, access control, vulnerability, and threat review.
- Operations: runtime reliability and recovery review.

Two dedicated cross-cutting teams also cover the repository:

### Defense and Security Team
One team lead and five specialists: threat detection, hardening, vulnerability management, incident response, and recovery integrity. Security-sensitive files are routed to this team in addition to their section team.

### Server Operations Team
One team lead and five specialists: health monitoring, deployment planning, infrastructure review, backup/restore validation, and reliability. Server, deployment, firewall, Cloudflare, and infrastructure files are routed to this team in addition to their section team.

## File assignment and code changes

The registry is generated from `git ls-files` at runtime. Each tracked file receives one section supervisor, five section reviewers, and optional defense/server cross-team routing. New tracked files are assigned automatically.

The implementation specialist role can propose code creation and upgrades, but this registry does not itself grant write access. Any actual code changes must run through an authenticated, isolated worker and an approved sandbox or feature branch. GitHub pushes require scoped credentials and approval. Production deployment and privileged server changes require separate human approval.

## Runtime status

This module defines team roles and routing records only. It does not spawn model processes or claim that supervisors are running. The status reports `workers_started: false` until a real model runtime, dispatcher, isolated worker, and audit trail are configured.

## Permission boundaries

- Read-only inspection is the default.
- Sandbox writes require administrator-controlled enablement and per-task confirmation.
- Tests and security review are required before a proposed patch is accepted.
- Merge, production deployment, service restarts, database migrations, DNS/firewall/TLS changes, and destructive operations require separate human approval.
- Supervisors cannot grant themselves permissions, change protected-branch rules, disable security controls, or erase audit records.

## API

Authenticated administrators can call:
- `GET /api/supervisors/status` for section coverage, dedicated teams, permissions, and runtime state.
- `GET /api/supervisors/file?path=relative/path` for the owner and reviewers assigned to one tracked file.

These endpoints do not expose file contents or secrets and do not execute supervisor tasks.
