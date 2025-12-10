```markdown
bd-king-r7 powerhub (.NET) — Orchestrator + Agent skeleton
==========================================================

What this provides
- Orchestrator: ASP.NET Core app (SQLite/EF Core) that accepts agent reports at POST /api/report (Authorization: Bearer <token>) and shows a minimal HTML dashboard.
- Agent: .NET Worker Service that runs on each server, performs git sync, runs fixers/build commands, updates 'ficar' and 'power_sync' files, and posts JSON reports to the orchestrator.
- Dockerfile + docker-compose for orchestrator, systemd unit template for agent.
- Example config file for the agent at /etc/bdking/agent.yml.

Quick start — Orchestrator (Docker)
1. Copy orchestrator files to a host directory (e.g., /opt/bd-king-orchestrator).
2. Set ORCHESTRATOR_TOKEN to a strong secret (env or .env).
3. Start:
   docker-compose up -d --build
4. Visit http://<host>:8000

Quick start — Agent on Linux host
1. Build/publish agent:
   cd agent
   dotnet publish -c Release -o /opt/bd-king-r7-powerhub
2. Install agent config:
   sudo mkdir -p /etc/bdking
   sudo cp agent.example.yml /etc/bdking/agent.yml
   Edit /etc/bdking/agent.yml (repo_path, server_url, auth_token, user, etc.)
3. Copy service unit and binary:
   sudo cp /opt/bd-king-r7-powerhub/agent.dll /opt/bd-king-r7-powerhub/
   sudo cp agent/bd-king-agent.service /etc/systemd/system/
   sudo sed -i 's@User=youruser@User=deployuser@' /etc/systemd/system/bd-king-agent.service
4. Enable & start:
   sudo systemctl daemon-reload
   sudo systemctl enable --now bd-king-agent.service
5. Check logs:
   sudo journalctl -u bd-king-agent.service -f

Configuration notes
- Start with push_changes=false until validated.
- IntervalSeconds default is 60 seconds. Increase to 5m/15m in production to reduce churn.
- Use HTTPS and a reverse proxy (nginx/Caddy) for the orchestrator in production.
- Keep Orchestrator token secret; rotate periodically.

Next steps I can do for you
- Fill in the agent fix_cmds/build_cmds for bd-king-r7 if you give me the repo URL and precise build/test commands.
- Add automatic TLS + nginx reverse proxy setup for orchestrator (with certbot).
- Add alerting (Slack/email) for failed builds.
- Add "single-commit" amend+force-push mode to keep an automation branch compact.
- Create a GitHub repo layout with these files and a GitHub Actions workflow to build/publish the orchestrator image.

Security & safety
- Run agents with least privilege; consider a dedicated service account.
- Start with disabled push and a dedicated automation branch to prevent accidental pushes to main.
- Make periodic backups of the orchestrator DB (if using SQLite) or use a managed DB for production.

```