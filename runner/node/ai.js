"use strict";

const fs = require("node:fs");
const path = require("node:path");

const MODEL_SETTINGS_PATH = path.resolve(__dirname, "../../data/model_settings.json");
const MODEL_NAME_PATTERN = /^[A-Za-z0-9][A-Za-z0-9._:/-]{0,199}$/;

function selectedModel() {
  const configured = process.env.TAMANNA_OLLAMA_MODEL;
  if (typeof configured === "string" && configured.trim()) {
    return configured.trim();
  }

  try {
    const settings = JSON.parse(fs.readFileSync(MODEL_SETTINGS_PATH, "utf8"));
    if (settings && typeof settings.selected_model === "string") {
      return settings.selected_model;
    }
  } catch (error) {
    if (error.code !== "ENOENT" && !(error instanceof SyntaxError)) {
      throw new Error("Cannot read Tamanna's local model settings.");
    }
  }

  return "qwen2.5:7b";
}

function localRuntimeUrl() {
  const raw = (process.env.TAMANNA_OLLAMA_URL || "http://127.0.0.1:11434").trim();
  let parsed;
  try {
    parsed = new URL(raw);
  } catch {
    throw new Error("TAMANNA_OLLAMA_URL must be an absolute HTTP(S) URL.");
  }
  if (!["http:", "https:"].includes(parsed.protocol) || !parsed.hostname ||
      parsed.username || parsed.password || parsed.search || parsed.hash) {
    throw new Error("TAMANNA_OLLAMA_URL must be an HTTP(S) URL without credentials or query parameters.");
  }
  return parsed.toString().replace(/\/$/, "");
}

async function askAI(message, options = {}) {
  if (typeof message !== "string" || !message.trim()) {
    throw new TypeError("message must be a non-empty string");
  }
  if (message.length > 20000) {
    throw new RangeError("message exceeds the 20000-character limit");
  }

  const model = selectedModel();
  if (!MODEL_NAME_PATTERN.test(model)) {
    throw new Error("Tamanna's configured local model name is invalid.");
  }

  const timeoutMs = Number.parseInt(process.env.TAMANNA_OLLAMA_TIMEOUT_MS || "120000", 10);
  if (!Number.isInteger(timeoutMs) || timeoutMs < 1000 || timeoutMs > 300000) {
    throw new Error("TAMANNA_OLLAMA_TIMEOUT_MS must be between 1000 and 300000.");
  }

  const fetchImpl = options.fetchImpl || globalThis.fetch;
  if (typeof fetchImpl !== "function") {
    throw new Error("This Node.js runtime does not provide fetch; use Node.js 20 or newer.");
  }

  let response;
  try {
    response = await fetchImpl(`${localRuntimeUrl()}/api/chat`, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({
        model,
        messages: [{ role: "user", content: message.trim() }],
        stream: false,
        options: { temperature: 0.2, num_predict: 1024 }
      }),
      signal: AbortSignal.timeout(timeoutMs)
    });
  } catch (error) {
    if (error && error.name === "TimeoutError") {
      throw new Error("Local AI runtime timed out. Check Ollama and try again.");
    }
    throw new Error("Cannot reach the local AI runtime. Check that Ollama is running.");
  }

  if (!response || !response.ok) {
    const status = response && Number.isInteger(response.status) ? response.status : "unknown";
    throw new Error(`Local AI runtime returned HTTP ${status}. Check that Ollama is running and the selected model is installed.`);
  }

  let payload;
  try {
    payload = await response.json();
  } catch {
    throw new Error("Local AI runtime returned an invalid response.");
  }
  const answer = payload && payload.message && payload.message.content;
  if (typeof answer !== "string" || !answer.trim()) {
    throw new Error("Local AI runtime returned an empty response.");
  }
  return answer.trim();
}

module.exports = { askAI, selectedModel, localRuntimeUrl };
