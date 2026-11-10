"use strict";

const express = require("express");
const net = require("node:net");
const crypto = require("node:crypto");

const app = express();
app.disable("x-powered-by");
app.use(express.json({ limit: "16kb", strict: true }));

const PORT = Number.parseInt(process.env.TAMANNA_FIREWALL_PORT || "3000", 10);
const blocked = new Set();
let rules = Object.create(null);

function safeTokenEqual(provided, expected) {
  if (typeof provided !== "string" || typeof expected !== "string") return false;
  const a = Buffer.from(provided);
  const b = Buffer.from(expected);
  return a.length === b.length && crypto.timingSafeEqual(a, b);
}

function requireAdmin(req, res, next) {
  const expected = process.env.TAMANNA_FIREWALL_ADMIN_TOKEN;
  if (!expected) {
    return res.status(503).json({ error: "Firewall admin token is not configured." });
  }
  if (!safeTokenEqual(req.get("x-tamanna-admin-token"), expected)) {
    return res.status(401).json({ error: "Unauthorized." });
  }
  return next();
}

app.use((req, res, next) => {
  if (blocked.has(req.ip)) {
    return res.status(403).send("Blocked by Tamanna Firewall");
  }
  return next();
});

app.get("/", (_req, res) => {
  res.send("Node firewall service is running.");
});

app.get("/health", (_req, res) => {
  res.json({ status: "ok", service: "tamanna-firewall" });
});

// Administrative endpoints require a private token; never accept arbitrary IP strings.
app.post("/block", requireAdmin, (req, res) => {
  const ip = req.body && req.body.ip;
  if (typeof ip !== "string" || net.isIP(ip) === 0) {
    return res.status(400).json({ error: "A valid IPv4 or IPv6 address is required." });
  }
  blocked.add(ip);
  return res.json({ status: "blocked" });
});

app.post("/rules", requireAdmin, (req, res) => {
  const nextRules = req.body;
  if (!nextRules || typeof nextRules !== "object" || Array.isArray(nextRules)) {
    return res.status(400).json({ error: "Rules must be a JSON object." });
  }
  rules = Object.assign(Object.create(null), nextRules);
  return res.json({ status: "updated", ruleCount: Object.keys(rules).length });
});

if (require.main === module) {
  app.listen(PORT, "127.0.0.1", () => {
    console.log(`Tamanna Firewall API listening on 127.0.0.1:${PORT}`);
  });
}

module.exports = { app, safeTokenEqual };
