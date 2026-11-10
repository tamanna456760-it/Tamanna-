"use strict";

// API-free placeholder. This module intentionally performs no file writes.
async function generateProject() {
  throw new Error(
    "Project generation is unavailable: no tested local inference runtime is configured."
  );
}

module.exports = { generateProject };
