"use strict";

/**
 * Tamanna AI local-only safety adapter.
 *
 * External model providers are intentionally disabled in this project.
 * This module does not make network requests and never reads API keys.
 *
 * A real local model/knowledge-store adapter can be connected here once its
 * runtime and data format are selected and tested.
 */
async function askAI(message) {
  if (typeof message !== "string" || !message.trim()) {
    throw new TypeError("message must be a non-empty string");
  }

  throw new Error(
    "Local AI runtime is not configured. External model APIs (including Gemini) are disabled."
  );
}

module.exports = { askAI };
