"use strict";

// Legacy autonomous code-generation agent disabled pending a reviewed local
// inference adapter and explicit, path-scoped user approval.
async function run() {
  throw new Error(
    "Autonomous code generation is disabled. No files are written and no Git operations are performed."
  );
}

if (require.main === module) {
  console.error("Disabled: autonomous code generation is not configured.");
  process.exitCode = 1;
}

module.exports = { run };
