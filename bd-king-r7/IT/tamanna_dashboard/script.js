function log(id, msg) {
  document.getElementById(id).textContent = msg;
}

// ----------------- Simulated Commands -----------------
function updateStatus() {
  log("status", "Time: " + new Date() + "\nOS: " + navigator.platform);
}

function syncFiles() {
  log("syncLog", "Syncing files...\nDone!");
}

function aiRate() {
  log("aiLog", "🧠 AI Code Rating: 8.5/10");
}

function aiSummary() {
  log("aiLog", "🧠 Total files: 5\nProject looks like a multi-file system");
}

function aiSuggest() {
  log("aiLog", "🧠 Suggestions:\n- Add README.md\n- Use Git\n- Backup regularly");
}

function saveSnapshot() {
  log("snapLog", "💾 Snapshot saved at " + new Date().toLocaleTimeString());
}

function runPython() {
  const file = document.getElementById("runFile").value;
  if(!file.endsWith(".py")) { log("runLog","❌ Only .py files"); return; }
  log("runLog", "⚡ Running " + file + " ...\nDone!");
}