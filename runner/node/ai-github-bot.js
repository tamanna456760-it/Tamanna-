"use strict";

// Legacy OpenAI-powered auto-editor intentionally disabled.
// This module must never pull, rewrite, stage, commit, or push repository files.
async function aiEdit() {
  throw new Error(
    "Legacy AI GitHub bot is disabled. Tamanna uses the API-free local runtime; " +
    "automated repository editing and Git push require a separately reviewed workflow."
  );
}

if (require.main === module) {
  console.error("Disabled: legacy OpenAI/Git auto-editor is not available.");
  process.exitCode = 1;
}

module.exports = { aiEdit };
