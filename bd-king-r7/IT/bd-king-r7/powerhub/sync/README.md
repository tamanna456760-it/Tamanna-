```markdown
# bd-king-r7 powerhub — Auto sync / fix / build system

What this does
- Every minute (systemd timer) it pulls the repository, runs configured fixers (formatters / linters / codegen), runs build/test commands, updates two marker files (`ficar` and `power_sync`), commits and optionally pushes changes to a dedicated branch, and will run a power-sync hook if you configure one.

Why use it carefully
- This system automates commits and pushes; it can create a lot of commits quickly. Use a dedicated automation branch (default `powerhub-auto`) and keep PUSH_CHANGES=false until you verify behavior.
- Make sure the system user has correct Git credentials (SSH key) and permissions.

Installation (example)
1. Copy files to the host as root or via sudo:
   sudo mkdir -p /opt/bd-king-r7-powerhub
   sudo chown youruser:youruser /opt/bd-king-r7-powerhub
   sudo cp sync_and_fix.sh /opt/bd-king-r7-powerhub/
   sudo chmod +x /opt/bd-king-r7-powerhub/sync_and_fix.sh
   sudo cp bd-king-r7-sync.service /etc/systemd/system/
   sudo cp bd-king-r7-sync.timer /etc/systemd/system/
   sudo chown youruser:youruser /opt/bd-king-r7-powerhub/sync_and_fix.sh

2. Edit /opt/bd-king-r7-powerhub/sync_and_fix.sh and set:
   - REPO_PATH (local path to your repo)
   - USER (system user)
   - BRANCH (automation branch)
   - FIX_CMDS (array of fix commands)
   - BUILD_CMDS (array of build/test commands)
   - PUSH_CHANGES (true/false)
   - POWER_SYNC_CMD (optional, if you want a power sync script to run)

3. (Optional) Create a dedicated branch on remote or let script create it.
   git checkout -b powerhub-auto
   git push origin powerhub-auto

4. Reload systemd and enable timer:
   sudo systemctl daemon-reload
   sudo systemctl enable --now bd-king-r7-sync.timer

5. Check status and logs:
   systemctl status bd-king-r7-sync.timer
   journalctl -u bd-king-r7-sync.service -f
   tail -n 200 /var/log/bd-king-r7-powerhub.log

Customization tips
- For Node projects use:
  FIX_CMDS=( "npm ci --no-audit --no-fund || true" "npx eslint --fix . || true" )
  BUILD_CMDS=( "npm ci && npm run build && npm test" )
- For Python:
  FIX_CMDS=( "python -m pip install -r requirements-dev.txt || true" "black . || true" )
  BUILD_CMDS=( "pytest -q" )
- For firmware (Makefile or platformbuild):
  BUILD_CMDS=( "make -j4" "make flash || true" )  # be careful with flash in automated runs

Safety / Advanced
- To limit commit churn you can replace the commit/push logic with `git commit --amend --no-edit` + force push to keep a single commit on the automation branch. Ask me if you want that variant.
- If you want GitHub Actions instead of a systemd timer, I can produce a workflow that runs every minute (note: GitHub Actions minimal interval is 5 minutes for scheduled workflows) or triggers on pushes.
- To avoid failed-build commits, the default behavior is: do not commit if build fails. Fixers changes are staged for manual review in that case.

If you want I can also:
- Generate a fully pre-filled version of sync_and_fix.sh for your repo (fill FIX_CMDS and BUILD_CMDS) — provide repo URL and build commands.
- Switch to `commit --amend` behavior to keep only one automated commit.
- Produce a GitHub Actions workflow instead (if you prefer serverless CI and push-based automation).
- Add an optional notification step (email / webhook / Slack) when builds fail.

Please reply with:
- Repo path or URL and whether machine will have SSH keys configured for pushing.
- Project type and the exact build/test commands to run.
- Whether you want pushes enabled now (PUSH_CHANGES=true) or disabled (recommended until tested).
- Which system user to run the service as.

Once you confirm these details I will:
- fill the script's FIX_CMDS and BUILD_CMDS for your project,
- produce final install commands you can copy/paste to the host,
- optionally produce a variant that uses `--amend` single-commit mode.
```