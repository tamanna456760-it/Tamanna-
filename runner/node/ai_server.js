"use strict";

const express = require("express");
const cors = require("cors");
const helmet = require("helmet");
const crypto = require("node:crypto");

const PORT = Number.parseInt(process.env.TAMANNA_AI_PORT || process.env.PORT || "3002", 10);
const RATE_WINDOW_MS = 60_000;
const RATE_LIMIT = 10;
const MAX_MESSAGE_LENGTH = 4000;
const allowedOrigins = (process.env.TAMANNA_AI_ALLOWED_ORIGINS || "")
  .split(",").map((item) => item.trim()).filter(Boolean);
const requestCounts = new Map();

const app = express();
app.disable("x-powered-by");
app.use(helmet());
app.use(cors({ origin: allowedOrigins.length ? allowedOrigins : false }));
app.use(express.json({ limit: "16kb", strict: true }));

function safeKeyEqual(provided, expected) {
  if (typeof provided !== "string" || typeof expected !== "string") return false;
  const a = Buffer.from(provided);
  const b = Buffer.from(expected);
  return a.length === b.length && crypto.timingSafeEqual(a, b);
}

function authenticateInternal(req, res, next) {
  const expectedKey = process.env.AI_SERVICE_API_KEY;
  if (!expectedKey) {
    return res.status(503).json({
      error: "Service not configured",
      message: "Set AI_SERVICE_API_KEY in the private environment before enabling internal access."
    });
  }
  if (!safeKeyEqual(req.get("x-api-key"), expectedKey)) {
    return res.status(401).json({ error: "Unauthorized", message: "Invalid API key" });
  }
  return next();
}

function consumeRateLimit(key, now = Date.now()) {
  if (typeof key !== "string" || !key) return false;
  let entry = requestCounts.get(key);
  if (!entry || now - entry.startedAt >= RATE_WINDOW_MS) {
    if (requestCounts.size >= 10_000) {
      for (const [candidate, value] of requestCounts) {
        if (now - value.startedAt >= RATE_WINDOW_MS) requestCounts.delete(candidate);
      }
      if (requestCounts.size >= 10_000) return false;
    }
    entry = { startedAt: now, count: 0 };
    requestCounts.set(key, entry);
  }
  entry.count += 1;
  return entry.count <= RATE_LIMIT;
}

app.post("/api/chat", authenticateInternal, (req, res) => {
  if (!consumeRateLimit(req.ip)) {
    return res.status(429).json({
      error: "Rate limit exceeded",
      message: "Too many requests. Please try again in a minute."
    });
  }

  const { message } = req.body || {};
  if (typeof message !== "string" || !message.trim() || message.length > MAX_MESSAGE_LENGTH) {
    return res.status(400).json({
      error: "Invalid message",
      message: "Message must be a non-empty string of at most 4000 characters."
    });
  }

  return res.status(503).json({
    error: "Local AI runtime unavailable",
    message: "No local model or knowledge database is configured. External model APIs are disabled."
  });
});

app.get("/health", (_req, res) => {
  res.json({
    status: "degraded",
    service: "Tamanna local AI gateway",
    model: null,
    externalProviders: "disabled",
    localRuntime: "not_configured",
    timestamp: new Date().toISOString()
  });
});

if (require.main === module) {
  app.listen(PORT, "127.0.0.1", () => {
    console.log(`Tamanna local AI gateway listening on 127.0.0.1:${PORT}; local runtime not configured`);
  });
}

module.exports = { app, safeKeyEqual, consumeRateLimit, authenticateInternal };
