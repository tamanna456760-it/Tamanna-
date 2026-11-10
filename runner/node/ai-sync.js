// API-free, read-only repository monitor.
// This script never pulls, stages, commits, or pushes files.
const simpleGit = require("simple-git");
const git = simpleGit();
const POLL_INTERVAL_MS = Math.max(
  60_000,
  Number.parseInt(process.env.TAMANNA_SYNC_POLL_MS || "60000", 10) || 60_000
);

let checking = false;

async function checkRepo() {
  if (checking) return;
  checking = true;
  try {
    const status = await git.status();
    if (status.current !== "main") {
      console.warn(`[Tamanna Sync] Read-only check: expected main, found ${status.current || "detached"}.`);
      return;
    }

    const changed = status.files.map((file) => file.path);
    console.log(JSON.stringify({
      service: "tamanna-api-free-sync-monitor",
      mode: "read-only",
      branch: status.current,
      clean: changed.length === 0,
      changedFiles: changed
    }));
  } catch (error) {
    console.error("[Tamanna Sync] Repository check failed:", error.message);
  } finally {
    checking = false;
  }
}

checkRepo();
setInterval(checkRepo, POLL_INTERVAL_MS);
