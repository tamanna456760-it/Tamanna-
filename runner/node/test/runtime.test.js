"use strict";

const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");

const { validatePath, parseAllowlist } = require("../git.js");
const { askAI } = require("../ai.js");

test("Git sync path policy accepts a safe exact relative path", () => {
  assert.equal(validatePath("docs/STATUS.md"), undefined);
});

test("Git sync path policy rejects secrets and unsafe path syntax", () => {
  for (const candidate of [
    ".env",
    ".env.production",
    "config/credentials.json",
    "keys/server.pem",
    "../outside.txt",
    "/absolute/path.txt",
    "src/*.js",
    "src/[abc].js",
    "src\\\\secret.txt"
  ]) {
    assert.throws(() => validatePath(candidate), /Refusing unsafe sync path/);
  }
});

test("Git sync allowlist trims entries and removes duplicates", () => {
  assert.deepEqual(
    parseAllowlist(" docs/STATUS.md,runner/node/README.md, docs/STATUS.md "),
    ["docs/STATUS.md", "runner/node/README.md"]
  );
  assert.deepEqual(parseAllowlist(""), []);
});

test("local AI adapter fails honestly while no local runtime is configured", async () => {
  await assert.rejects(
    askAI("hello"),
    /Local AI runtime is not configured/
  );
  await assert.rejects(
    askAI("  "),
    /message must be a non-empty string/
  );
});

test("both compatibility launchers use only the available server entrypoint", () => {
  const root = path.resolve(__dirname, "..");
  for (const name of ["run.js", "run..js"]) {
    const source = fs.readFileSync(path.join(root, name), "utf8");
    assert.match(source, /require\(['"]\.\/server\.js['"]\)/);
    assert.doesNotMatch(source, /\.\/github\/sync\.js|\.\/ai\/ai\.js|\.\/telegram\/bot\.js/);
  }
});
