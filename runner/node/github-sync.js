"use strict";

const { gitPush } = require("./git.js");

// Compatibility wrapper; the underlying sync remains disabled by default
// and requires an explicit path allowlist and opt-in environment setting.
async function githubSync() {
  const result = await gitPush();
  return result;
}

module.exports = { githubSync };
