"use strict";

/*
 * Automatic Git writes are deliberately disabled.
 * Use reviewed pull requests for repository changes; this module only reads
 * Git metadata and never stages, commits, or pushes files.
 */
const { execFile } = require("node:child_process");
const { promisify } = require("node:util");

const execFileAsync = promisify(execFile);

class AutoCommitter {
  constructor(options = {}) {
    this.cwd = options.cwd || process.cwd();
  }

  async getGitInfo() {
    try {
      const [branch, remote] = await Promise.all([
        execFileAsync("git", ["branch", "--show-current"], { cwd: this.cwd }),
        execFileAsync("git", ["remote", "get-url", "origin"], { cwd: this.cwd }),
      ]);

      return {
        branch: branch.stdout.trim() || "detached",
        remote: remote.stdout.trim() || "none",
      };
    } catch {
      return { branch: "unknown", remote: "none" };
    }
  }

  async commit() {
    throw new Error(
      "Automatic Git commit/push is disabled. Review changes and use an approved pull request."
    );
  }
}

module.exports = AutoCommitter;
