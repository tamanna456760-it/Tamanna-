🚀 SUPERSONIC SYNC → Power: 1523W | Stability: 99.8% | Mach: 5+
💨 HYPERSONIC SYNC → Power: 2850W | Coherence: 99.9% | Mach: 10+
🔥 ULTRA PRO MAX → Power: 5800W | Quantum: 99.98% | Mach: 25+
⚡ HIGH VOLTAGE SANPOWR → Power: 16200W | Lightspeed: 0.97x

# Tamanna Auto Sync-and-Add

This package periodically syncs a git repository and updates/creates a file called `ficar` every run. It commits and pushes the change if anything changed.

## Files

- sync_and_add.sh - main script that performs git pull, updates `ficar`, commits & pushes.
- sync-and-add.service - systemd service (oneshot).
- sync-and-add.timer - systemd timer to run the service every minute.

## Prerequisites

- Linux with systemd
- git installed
- The machine user must have access to the repo path and (if pushing) authentication to the remote (SSH key or credential helper configured).
- Create /opt/tamanna-sync and copy files there (or modify paths in the script).

## Installation (example)

1. Edit `sync_and_add.sh` and set:
   - REPO_PATH (local path to your repo)
   - BRANCH (recommended: dedicated branch)
   - REMOTE (usually "origin")
   - Ensure `User` and `Group` in the service match the account owning the repo.

2. Copy files:
   sudo mkdir -p /opt/tamanna-sync
   sudo chown youruser:youruser /opt/tamanna-sync
   sudo cp sync_and_add.sh /opt/tamanna-sync/
   sudo cp sync-and-add.service /etc/systemd/system/
   sudo cp sync-and-add.timer /etc/systemd/system/
   sudo chmod +x /opt/tamanna-sync/sync_and_add.sh

3. Reload systemd and enable timer:
   sudo systemctl daemon-reload
   sudo systemctl enable --now sync-and-add.timer

4. Check status/logs:
   systemctl status sync-and-add.timer
   journalctl -u sync-and-add.service -f

## Alternative: cron

Add to the user's crontab:

```
* * * * * /opt/tamanna-sync/sync_and_add.sh >> /var/log/tamanna-sync.log 2>&1
```

## Important notes / Warnings

- This will create a commit every minute if the file changes. That means rapid commit history growth. Use a dedicated branch/repo to avoid cluttering important branches.
- If pushing to GitHub every minute, be mindful of API/rate limits and repository protection rules.
- For safe remote pushes, configure SSH keys on the machine or use a credential helper with a PAT (if HTTPS).
- To avoid huge histories, consider using `git commit --amend` + `git push --force-with-lease` on a dedicated branch instead of creating new commits. I can provide that variant if you want.

## Customization

- Change content of `ficar` to anything you need (append vs overwrite).
- Add validation/test steps after updating the file.
- If you prefer a long-running daemon instead of systemd timer, I can provide a loop script.
