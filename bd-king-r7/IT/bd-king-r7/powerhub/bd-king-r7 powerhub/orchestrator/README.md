```markdown
# bd-king-r7 powerhub — Scalable Auto-Sync System

What this package provides

- Agent (Python) to run on each server that hosts bd-king-r7 code:
  - Safe automated sync, auto-fix, build/test, update marker files, commit & optional push.
  - Posts JSON reports to a central orchestrator.
  - Locking to avoid overlapping runs and logs to /var/log.
- Orchestrator (Flask) to receive reports and provide a small dashboard.
- Docker Compose for running the orchestrator centrally.
- systemd unit for the agent.

Why this is more powerful

- Central reporting and history of automated runs for many servers.
- Token-based authentication for agents.
- Per-server configuration allows different fix/build hooks.
- Better safety defaults: dedicated automation branch, push disabled by default.
- Can be extended: add alerts (Slack/email), advanced dashboards, role-based access, certificate-based mTLS, or GitOps triggers.

Quick install (orchestrator)

1. On the central server:
   - Copy the orchestrator folder to /opt/bd-king-r7-orchestrator
   - Set a strong ORCHESTRATOR_TOKEN in an env file or export it
   - Run: docker-compose up -d --build
   - Visit http://<server-ip>:8000 to view recent reports.

Agent install (per server)

1. Copy agent.py to /opt/bd-king-r7-powerhub/agent.py
2. Create /etc/bdking/agent.yml (see agent.example.yml) and edit values:
   - repo_path, branch, fix_cmds, build_cmds, server_url, auth_token
3. Ensure Python3 and 'requests' and 'pyyaml' are installed:
   pip3 install requests pyyaml
4. Create systemd unit /etc/systemd/system/bd-king-agent.service (edit User)
5. Enable and start:
   sudo systemctl daemon-reload
   sudo systemctl enable --now bd-king-agent.service
6. Check logs:
   tail -f /var/log/bd-king-r7-powerhub.log
7. Test run:
   sudo -u youruser /usr/bin/env python3 /opt/bd-king-r7-powerhub/agent.py
   (or stop service then run manually for one loop)

Security notes

- Use a unique ORCHESTRATOR_TOKEN and keep it secret.
- Use HTTPS for orchestrator (put a reverse proxy like nginx/Caddy/Traefik in front).
- Consider mTLS or per-agent tokens for better security in production.
- Make sure the user running agent has only necessary permissions.

Operational notes

- Default interval: 60 seconds. Increase to 5m/15m for production to reduce churn.
- Keep PUSH_CHANGES=false until you validate behavior.
- To avoid commit history growth, consider using "git commit --amend --no-edit" and force-push on a dedicated branch (ask if you want this variant).
- Add alerts if build_ok=false for timely human intervention.

Next steps I can do for you (choose any)

- Pre-fill FIX_CMDS and BUILD_CMDS for bd-king-r7 if you give me the repo URL and build commands.
- Provide an amended-commit variant to limit commit history.
- Add email/Slack webhook alerts for failed builds.
- Add TLS & reverse-proxy configuration (nginx/Caddy).
- Create GitHub Actions workflow alternative (serverless) if you prefer using GitHub instead of self-hosted orchestrator.
```
