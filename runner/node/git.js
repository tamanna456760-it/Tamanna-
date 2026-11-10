"use strict";

const simpleGit = require("simple-git");
const path = require("node:path");

const git = simpleGit("./project");

const SECRET_PATH = /(^|\/)(\.env(?:\..*)?|.*\.(?:pem|key|p12|pfx|keystore)|id_rsa|id_ed25519|credentials?(?:\.json)?|secrets?(?:\.|\/|$))/i;

function parseAllowlist(value) {
  if (!value) return [];
  return [...new Set(value.split(",").map((item) => item.trim()).filter(Boolean))];
}

function validatePath(file) {
  if (
    typeof file !== "string" ||
    !file ||
    file.includes("\\") ||
    path.posix.isAbsolute(file) ||
    file.split("/").some((part) => !part || part === "." || part === "..") ||
    /[*?\[\]{}]/.test(file) ||
    SECRET_PATH.test(file)
  ) {
    throw new Error(`Refusing unsafe sync path: ${String(file)}`);
  }
}

async function gitPush() {
  if (process.env.TAMANNA_ENABLE_GIT_PUSH !== "1") {
    return { pushed: false, reason: "Git push is disabled; set TAMANNA_ENABLE_GIT_PUSH=1 to opt in." };
  }

  const allowlist = parseAllowlist(process.env.TAMANNA_SYNC_PATHS);
  if (allowlist.length === 0) {
    throw new Error("TAMANNA_SYNC_PATHS must list exact relative file paths.");
  }
  allowlist.forEach(validatePath);

  const status = await git.status();
  if (status.current !== "main") {
    throw new Error("Refusing Git push: checkout must be on main.");
  }
  if (status.files.length === 0) {
    return { pushed: false, reason: "No changes to sync." };
  }

  const allowed = new Set(allowlist);
  const changed = status.files.map((file) => file.path);
  const denied = changed.filter((file) => !allowed.has(file));
  if (denied.length) {
    throw new Error(`Refusing Git push: changed paths are not allowlisted: ${denied.join(", ")}`);
  }

  const remotes = await git.getRemotes(true);
  if (!remotes.some((remote) => remote.name === "origin")) {
    throw new Error("Refusing Git push: origin remote is not configured.");
  }

  await git.add(changed);
  const staged = await git.diff(["--cached", "--name-only"]);
  if (!staged.trim()) {
    return { pushed: false, reason: "No staged changes to commit." };
  }

  await git.commit("Tamanna AI approved sync");
  await git.push("origin", "main");
  return { pushed: true, paths: changed };
}

module.exports = { gitPush, validatePath, parseAllowlist };
