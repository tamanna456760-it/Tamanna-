# Tamanna AI Supervisor Network

## Team layout

Every detected repository section receives one section lead plus five specialists:
- Architecture: design consistency and cross-module compatibility.
- Implementation: code creation and upgrades, restricted to a new isolated Git worktree.
- Testing: regression, syntax, build, and test evidence.
- Security: privacy, access control, vulnerability, and threat review.
- Operations: runtime reliability and recovery review.

Two dedicated cross-cutting teams also cover the repository:

### Defense and Security Team
One team lead and five specialists: threat detection, hardening, vulnerability management, incident response, and recovery integrity. Security-sensitive files are routed to this team in addition to their section team.

### Server Operations Team
One team lead and five specialists: health monitoring, deployment planning, infrastructure review, backup/restore validation, and reliability. Server, deployment, firewall, Cloudflare, and infrastructure files are routed to this team in addition to their section team.

## Live execution

Authenticated administrators can submit a task to `POST /api/supervisors/run` with `team_id` and `prompt`. The runtime launches six separate Codex CLI invocations: one team lead and five specialists. Read-only tasks use six read-only workers in parallel.

A write task requires all three controls:
- Request fields `write_access=true` and `confirm_write=true`.
- Server setting `TAMANNA_CODEX_WRITE_ENABLED=true`.
- Server setting `TAMANNA_CODEX_ENABLED=true`.

Write tasks create a new local Git branch and isolated worktree. Only the Implementation specialist receives workspace-write; the team lead and remaining four specialists review read-only after implementation. The worktree and branch are retained for inspection. Workers do not push to GitHub, merge, deploy, restart services, or alter privileged infrastructure.

## File assignment

The registry is generated from `git ls-files` at runtime. Each tracked file receives one section supervisor, five section reviewers, and optional Defense/Server Operations cross-team routing. New tracked files are assigned automatically.

## Accuracy and permissions

- Read-only inspection is the default.
- Each worker must inspect source and distinguish verified evidence from assumptions.
- No worker may claim tests passed unless it ran them and observed success.
- Writes are isolated in a newly created branch/worktree; no direct writes to the active checkout.
- GitHub pushes require a separately configured scoped credential and approval.
- Merge, production deployment, service restarts, database migrations, DNS/firewall/TLS changes, and destructive operations require separate human approval.
- Supervisors cannot grant themselves permissions, change protected-branch rules, disable security controls, or erase audit records.
- Worker output is bounded and task execution is rate-limited; structured run summaries are emitted to the server logger.

## API

Authenticated administrators can call:
- `GET /api/supervisors/status` for section coverage, dedicated teams, permissions, and runtime state.
- `GET /api/supervisors/file?path=relative/path` for the owner and reviewers assigned to one tracked file.
- `POST /api/supervisors/run` to execute one selected six-worker team.

The read endpoints do not expose file contents or secrets. The run endpoint requires an authenticated administrator and an enabled Codex CLI runtime.
