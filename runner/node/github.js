"use strict";

const { gitPush } = require("./git.js");

// Compatibility wrapper: all push policy is enforced by the hardened Git module.
async function githubSync() {
  return gitPush();
}

module.exports = { githubSync };
