"use strict";

const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");

const { validatePath, parseAllowlist } = require("../git.js");
const { askAI } = require("../ai.js");
const { safeTokenEqual } = require("../node_server.js");
const { extractMessage, generateReply } = require("../server.js");

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

test("firewall admin token comparison rejects missing and mismatched tokens", () => {
  assert.equal(safeTokenEqual(undefined, "secret"), false);
  assert.equal(safeTokenEqual("wrong", "secret"), false);
  assert.equal(safeTokenEqual("secret", "secret"), true);
});

test("WebSocket parser accepts bounded text and structured JSON only", () => {
  assert.deepEqual(extractMessage(Buffer.from("hello"), false), { text: "hello", json: false });
  assert.deepEqual(
    extractMessage(Buffer.from(JSON.stringify({ text: " hello " })), false),
    { text: "hello", json: true }
  );
  assert.throws(() => extractMessage(Buffer.from(""), false), /1–4000/);
  assert.throws(() => extractMessage(Buffer.from("x".repeat(4001)), false), /1–4000/);
  assert.throws(() => extractMessage(Buffer.from(JSON.stringify({ text: 123 })), false), /string text field/);
  assert.throws(() => extractMessage(Buffer.from("{bad json"), false), /Malformed/);
  assert.throws(() => extractMessage(Buffer.from("binary"), true), /Binary messages/);
});

test("WebSocket reply never claims an unconfigured local model is running", async () => {
  assert.match(await generateReply("/ai hello"), /Local AI is not configured/);
});
