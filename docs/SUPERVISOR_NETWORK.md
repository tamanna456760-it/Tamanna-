# Tamanna AI Supervisor Network

## Team layout

Every detected repository section receives one section lead plus five specialists for architecture, implementation, testing, security, and operations.

The cross-cutting teams include the dedicated Server Operations Team and the **100-agent Cyber Defense & Incident Response Team**.

## 100-agent Cyber Defense Team

The Cyber Defense Team has one lead and exactly 100 specialist agents, organized into ten squads of ten:

1. Network defense and segmentation
2. Identity, authentication, and access governance
3. Application security and secure coding
4. Cloud, container, and infrastructure defense
5. Endpoint, host, and malware defense
6. Data protection, privacy, and database security
7. Threat intelligence and detection engineering
8. Incident response and forensics
9. Business continuity and recovery
10. Security assurance, safe testing, and remediation verification

Its mission is maximum defensive capability: detect intrusions, assess indicators, protect accounts and systems, contain incidents, preserve evidence, close vulnerabilities, and restore trusted services.

**No retaliatory hacking:** this team must not break into an attacker's device or network, steal credentials, deploy malware, disrupt third-party services, or perform unauthorized counterattacks. It may block traffic and accounts on systems the organization controls, isolate affected assets, preserve forensic evidence, and coordinate lawful reporting.

The 100-agent team is read-only and analysis-only. It cannot directly change production controls or perform remediation writes. Findings requiring code changes are handed to the separately approved implementation workflow.

## On-demand execution

Authenticated administrators can submit a task to `POST /api/supervisors/run` with `team_id` and `prompt`. The Defense Team launches one lead plus 100 specialist Codex CLI workers on demand. At most five workers run concurrently to limit resource pressure. All 101 workers use read-only sandbox mode.

Other teams continue to use their own lead and five specialists. Write tasks for those teams require explicit request confirmation and server-side enablement; they run in a new isolated Git branch/worktree with only the Implementation specialist allowed to write. No worker can push, merge, deploy, or change privileged server controls.

## File assignment

The registry is generated from `git ls-files`. Each tracked file receives one section supervisor, five section reviewers, and relevant cross-team routing.

## Security and permissions

- Read-only is the default.
- Defensive actions are limited to systems and accounts the organization owns or is authorized to administer.
- No counterattacks, unauthorized access, credential theft, malware deployment, destructive actions, or denial-of-service activity.
- Evidence must be preserved; conclusions must distinguish verified facts from hypotheses.
- No worker may claim tests passed unless it ran them and observed success.
- Production changes, firewall/DNS/TLS changes, account disabling, service restarts, database migrations, and deployment require separate human approval.
- Supervisors cannot grant themselves permissions, disable controls, or erase audit records.

## API

Authenticated administrators can call:
- `GET /api/supervisors/status` for team coverage and runtime configuration.
- `GET /api/supervisors/file?path=relative/path` for file ownership and reviewers.
- `POST /api/supervisors/run` to execute a selected team. Use `team_id: "defense"` for the 100-agent defensive team.

Execution requires an enabled and authenticated Codex CLI runtime. A configured team roster does not mean workers are running before a task is submitted.
