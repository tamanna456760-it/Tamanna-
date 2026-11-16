"use strict";

const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const { spawnSync } = require("node:child_process");

const root = path.resolve(__dirname, "../..");

test("GitHub Pages build emits chat/admin pages and required assets without custom-domain CNAME", () => {
  const result = spawnSync(process.execPath, [path.join(root, "scripts/build-static.js")], {
    cwd: root,
    encoding: "utf8",
    env: { ...process.env, GITHUB_PAGES_BASE_PATH: "Tamanna-" },
  });
  assert.equal(result.status, 0, `${result.stdout}\n${result.stderr}`);

  for (const relative of [
    "index.html", "admin.html", "admin/index.html",
    "css/style.css", "css/admin.css", "js/chat.js", "js/admin.js", ".nojekyll",
  ]) {
    assert.ok(fs.existsSync(path.join(root, "dist", relative)), `Missing dist/${relative}`);
  }
  assert.equal(fs.existsSync(path.join(root, "dist", "CNAME")), false);
});


test("Cloudflare build and payload validation work without an unverified custom domain", () => {
  const build = spawnSync(process.execPath, [path.join(root, "scripts/build-static.js")], {
    cwd: root,
    encoding: "utf8",
    env: { ...process.env, GITHUB_PAGES_BASE_PATH: "" },
  });
  assert.equal(build.status, 0, `${build.stdout}\\n${build.stderr}`);
  const verify = spawnSync(process.execPath, [path.join(root, "scripts/verify-cloudflare-deploy.js")], {
    cwd: root,
    encoding: "utf8",
  });
  assert.equal(verify.status, 0, `${verify.stdout}\\n${verify.stderr}`);
  assert.match(verify.stdout, /No CNAME configured/);
});
