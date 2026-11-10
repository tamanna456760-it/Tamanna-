"use strict";

const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");

const { validatePath, parseAllowlist } = require("../git.js");
const { askAI, localRuntimeUrl } = require("../ai.js");
const { safeTokenEqual } = require("../node_server.js");
const { extractMessage, generateReply, isOriginAllowed } = require("../server.js");
const { safeKeyEqual, consumeRateLimit } = require("../ai_server.js");
const { aiEdit } = require("../ai-github-bot.js");
const { run: runAgent } = require("../agent.js");
const { generateProject } = require("../generator.js");
const { collectSystemMetrics, systemMonitor } = require("../monitor.js");
const { securityScan } = require("../security.js");
const { parseAdminIds, isAdminId, createBot } = require("../bot.js");

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


test("Telegram AI adapter sends prompts only to the configured local Ollama runtime", async () => {
  const previousUrl = process.env.TAMANNA_OLLAMA_URL;
  const previousModel = process.env.TAMANNA_OLLAMA_MODEL;
  const previousTimeout = process.env.TAMANNA_OLLAMA_TIMEOUT_MS;
  process.env.TAMANNA_OLLAMA_URL = "http://127.0.0.1:11434";
  process.env.TAMANNA_OLLAMA_MODEL = "test-local-model";
  process.env.TAMANNA_OLLAMA_TIMEOUT_MS = "5000";
  try {
    let requestedUrl;
    let requestedBody;
    const answer = await askAI("  বাংলায় উত্তর দাও  ", {
      fetchImpl: async (url, options) => {
        requestedUrl = url;
        requestedBody = JSON.parse(options.body);
        return {
          ok: true,
          json: async () => ({ message: { content: "  স্থানীয় মডেল থেকে উত্তর  " } })
        };
      }
    });
    assert.equal(answer, "স্থানীয় মডেল থেকে উত্তর");
    assert.equal(requestedUrl, "http://127.0.0.1:11434/api/chat");
    assert.equal(requestedBody.model, "test-local-model");
    assert.deepEqual(requestedBody.messages, [{ role: "user", content: "বাংলায় উত্তর দাও" }]);
    assert.equal(requestedBody.stream, false);
  } finally {
    if (previousUrl === undefined) delete process.env.TAMANNA_OLLAMA_URL;
    else process.env.TAMANNA_OLLAMA_URL = previousUrl;
    if (previousModel === undefined) delete process.env.TAMANNA_OLLAMA_MODEL;
    else process.env.TAMANNA_OLLAMA_MODEL = previousModel;
    if (previousTimeout === undefined) delete process.env.TAMANNA_OLLAMA_TIMEOUT_MS;
    else process.env.TAMANNA_OLLAMA_TIMEOUT_MS = previousTimeout;
  }
});

test("Telegram AI adapter rejects unsafe runtime URLs and invalid upstream responses", async () => {
  const previousUrl = process.env.TAMANNA_OLLAMA_URL;
  try {
    process.env.TAMANNA_OLLAMA_URL = "https://user:password@example.test";
    assert.throws(() => localRuntimeUrl(), /without credentials/);
    process.env.TAMANNA_OLLAMA_URL = "http://127.0.0.1:11434";
    await assert.rejects(
      askAI("hello", { fetchImpl: async () => ({ ok: false, status: 404 }) }),
      /HTTP 404/
    );
  } finally {
    if (previousUrl === undefined) delete process.env.TAMANNA_OLLAMA_URL;
    else process.env.TAMANNA_OLLAMA_URL = previousUrl;
  }
});
\ntest("local AI adapter validates blank prompts", async () => {
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

test("AI gateway compares private keys safely", () => {
  assert.equal(safeKeyEqual("same-secret", "same-secret"), true);
  assert.equal(safeKeyEqual("wrong", "same-secret"), false);
  assert.equal(safeKeyEqual(undefined, "same-secret"), false);
});

test("AI gateway rate limiter enforces ten requests per minute", () => {
  const key = "unit-test-client";
  const start = 1_800_000_000_000;
  for (let i = 0; i < 10; i += 1) assert.equal(consumeRateLimit(key, start), true);
  assert.equal(consumeRateLimit(key, start), false);
  assert.equal(consumeRateLimit(key, start + 60_000), true);
});

test("legacy AI GitHub editor is disabled and performs no Git operations", async () => {
  await assert.rejects(aiEdit("modify files"), /Legacy AI GitHub bot is disabled/);
});

test("autonomous agent is disabled instead of writing generated code", async () => {
  await assert.rejects(runAgent(), /Autonomous code generation is disabled/);
});

test("project generator reports missing local inference without writing files", async () => {
  await assert.rejects(generateProject("make a server"), /no tested local inference runtime/);
});

test("system monitor returns real bounded OS metrics without starting a timer", () => {
  const metrics = collectSystemMetrics();
  assert.equal(typeof metrics.platform, "string");
  assert.equal(typeof metrics.nodeVersion, "string");
  assert.ok(metrics.cpuCores > 0);
  assert.ok(metrics.memory.totalBytes > 0);
  assert.ok(metrics.memory.usedPercent >= 0 && metrics.memory.usedPercent <= 100);
  assert.equal(typeof systemMonitor({ onMetrics: () => {} }), "function");
});

test("security audit reports unverified host checks instead of random results", () => {
  const report = securityScan();
  assert.equal(report.scanType, "node-runtime-configuration-audit");
  assert.ok(["partial", "failed", "passed"].includes(report.status));
  assert.ok(report.results.some((item) => item.name === "Operating-system firewall" && item.status === "not_checked"));
  assert.ok(report.results.some((item) => item.name === "Malware and rootkit scan" && item.status === "not_checked"));
  assert.ok(report.results.every((item) => !("passed" in item) || typeof item.passed === "boolean"));
});


test("Telegram bot registers grammY handlers and starts long polling with the correct API", async () => {
  class FakeBot {
    constructor(token) {
      this.token = token;
      this.commands = new Map();
      this.handlers = new Map();
      this.started = false;
      this.errorHandler = null;
    }
    command(name, handler) { this.commands.set(name, handler); }
    on(filter, handler) { this.handlers.set(filter, handler); }
    catch(handler) { this.errorHandler = handler; }
    async start() { this.started = true; }
  }

  const bot = await createBot({
    token: "test-token",
    adminIds: new Set(["123"]),
    polling: true,
    BotClass: FakeBot
  });
  assert.equal(bot.token, "test-token");
  assert.equal(bot.started, true);
  assert.equal(typeof bot.errorHandler, "function");
  assert.deepEqual([...bot.commands.keys()], ["start", "sync"]);
  assert.equal(bot.handlers.has("message:text"), true);

  const replies = [];
  await bot.commands.get("start")({ reply: async (message) => replies.push(message) });
  await bot.commands.get("sync")({
    from: { id: 999 },
    reply: async (message) => replies.push(message)
  });
  assert.match(replies[0], /Tamanna AI Bot Started/);
  assert.match(replies[1], /অনুমতি নেই/);
});

test("Telegram bot can be constructed without polling for safe imports and tests", async () => {
  class FakeBot {
    constructor() { this.started = false; }
    command() {}
    on() {}
    catch() {}
    async start() { this.started = true; }
  }
  const bot = await createBot({ token: "test-token", BotClass: FakeBot });
  assert.equal(bot.started, false);
});
\ntest("Telegram bot module validates token and admin IDs", async () => {
  assert.deepEqual([...parseAdminIds("123, bad, 456,123")], ["123", "456"]);
  const admins = parseAdminIds("123,456");
  assert.equal(isAdminId("123", admins), true);
  assert.equal(isAdminId("789", admins), false);
  assert.equal(isAdminId("123", new Set()), false);
  await assert.rejects(createBot({ token: "" }), /BOT_TOKEN is required/);
});

test("WebSocket origin allowlist rejects missing and unlisted origins", () => {
  const origins = ["https://www.bd-king-r7.com", "http://localhost:3000"];
  assert.equal(isOriginAllowed(undefined, origins), false);
  assert.equal(isOriginAllowed("", origins), false);
  assert.equal(isOriginAllowed("https://attacker.example", origins), false);
  assert.equal(isOriginAllowed("https://www.bd-king-r7.com", origins), true);
  assert.equal(isOriginAllowed(undefined, []), true);
});
