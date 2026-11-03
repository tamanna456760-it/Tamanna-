"use strict";

const { execFile } = require("node:child_process");
const { promisify } = require("node:util");

const execFileAsync = promisify(execFile);
const SECRET_PATH = /(^|\/)(\.env(?:\..*)?|\.ven|credentials\.json|token\.txt)$/i;

/**
 * Explicit, path-scoped Git helper.
 * It never watches files, stages the whole repository, or pushes automatically.
 */
class AutoCommitter {
  async getGitInfo() {
    try {
      const [{ stdout: branch }, { stdout: remote }] = await Promise.all([
        execFileAsync("git", ["branch", "--show-current"]),
        execFileAsync("git", ["remote", "get-url", "origin"])
      ]);
      return { branch: branch.trim(), remote: remote.trim() };
    } catch {
      return { branch: "unknown", remote: "none" };
    }
  }

  async commit(message, paths) {
    if (typeof message !== "string" || !message.trim()) {
      throw new TypeError("A non-empty commit message is required.");
    }
    if (!Array.isArray(paths) || paths.length === 0) {
      throw new TypeError("Pass an explicit list of files to stage.");
    }
    if (paths.some((path) => typeof path !== "string" || !path.trim() || SECRET_PATH.test(path))) {
      throw new Error("Refusing to stage an invalid path or a private credential file.");
    }

    await execFileAsync("git", ["add", "--", ...paths]);
    const { stdout: staged } = await execFileAsync(
      "git",
      ["diff", "--cached", "--name-only"]
    );
    const stagedPaths = staged.split("\n").filter(Boolean);
    if (stagedPaths.some((path) => SECRET_PATH.test(path))) {
      throw new Error("Refusing to commit staged private credentials.");
    }
    if (stagedPaths.length === 0) {
      return { committed: false, reason: "No staged changes." };
    }

    await execFileAsync("git", ["commit", "-m", message.trim()]);
    const { stdout: sha } = await execFileAsync("git", ["rev-parse", "HEAD"]);
    return { committed: true, commit: sha.trim(), pushed: false };
  }
}

module.exports = AutoCommitter;
