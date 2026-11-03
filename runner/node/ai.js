"use strict";

/**
 * Tamanna AI Gemini client.
 * Requires GEMINI_API_KEY (or TAMANNA_MODEL_API_KEY) in the private environment.
 * Uses Node.js 20+ native fetch; no SDK or dotenv dependency is required.
 */
const API_BASE = "https://generativelanguage.googleapis.com/v1beta/models";
const DEFAULT_MODEL = "gemini-2.5-flash";

async function askAI(message, options = {}) {
  if (typeof message !== "string" || !message.trim()) {
    throw new TypeError("message must be a non-empty string");
  }

  const apiKey = (
    process.env.TAMANNA_MODEL_API_KEY ||
    process.env.GEMINI_API_KEY ||
    ""
  ).trim();

  if (!apiKey) {
    throw new Error("GEMINI_API_KEY is not configured.");
  }

  const model = (
    options.model ||
    process.env.GEMINI_MODEL ||
    DEFAULT_MODEL
  ).trim();

  if (!/^[A-Za-z0-9._-]+$/.test(model)) {
    throw new Error("Invalid Gemini model identifier.");
  }

  const response = await fetch(
    `${API_BASE}/${encodeURIComponent(model)}:generateContent`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "x-goog-api-key": apiKey
      },
      body: JSON.stringify({
        contents: [{ role: "user", parts: [{ text: message.trim() }] }],
        generationConfig: {
          temperature: Number.isFinite(options.temperature)
            ? options.temperature
            : 0.2,
          maxOutputTokens: Number.isInteger(options.maxOutputTokens)
            ? options.maxOutputTokens
            : 1024
        }
      }),
      signal: AbortSignal.timeout(
        Number.isFinite(options.timeoutMs) ? options.timeoutMs : 30000
      )
    }
  );

  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    const detail = data?.error?.message || `HTTP ${response.status}`;
    throw new Error(`Gemini request failed: ${detail}`);
  }

  const reply = (data?.candidates?.[0]?.content?.parts || [])
    .map((part) => part?.text)
    .filter((part) => typeof part === "string")
    .join("\n")
    .trim();

  if (!reply) {
    throw new Error("Gemini returned an empty response.");
  }

  return reply;
}

module.exports = { askAI };
