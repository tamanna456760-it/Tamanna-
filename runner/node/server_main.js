"use strict";

const express = require("express");
const cors = require("cors");
const crypto = require("node:crypto");

const app = express();
const PORT = Number(process.env.POWERHUB_PORT || 8080);
const ReactorState = {
  totalRequests: 0,
  moduleUsage: Object.create(null),
  lastSurge: null,
  healthScore: 100,
  chaosMode: false,
};

const allowedOrigins = new Set(
  (process.env.POWERHUB_ALLOWED_ORIGINS || "")
    .split(",")
    .map((value) => value.trim())
    .filter(Boolean)
);

app.use(cors({
  origin(origin, callback) {
    if (!origin || allowedOrigins.has(origin)) {
      return callback(null, true);
    }
    return callback(new Error("Origin is not allowed."));
  },
}));
app.use(express.json({ limit: "32kb" }));

const powerModules = {
  normal: require("./normal"),
  medium: require("./medium"),
  deep: require("./deep"),
  underground: require("./underground"),
  stone_spirit: require("./stone_spirit"),
};

function wrap(mode, payload) {
  return {
    status: "OK",
    mode,
    timestamp: new Date().toISOString(),
    reactorHealth: ReactorState.healthScore,
    payload,
  };
}

app.get("/health", (_req, res) => {
  res.json({ status: "ok", service: "tamanna-powerhub" });
});

app.get("/power/random", (_req, res) => {
  const modes = Object.keys(powerModules);
  const mode = modes[crypto.randomInt(modes.length)];
  res.redirect(307, "/power/" + encodeURIComponent(mode));
});

app.get("/power/:mode", async (req, res, next) => {
  const { mode } = req.params;
  const powerModule = powerModules[mode];
  if (!powerModule) {
    return res.status(404).json({ status: "ERROR", message: "Unknown power mode." });
  }

  try {
    const payload = await powerModule();
    ReactorState.totalRequests += 1;
    ReactorState.moduleUsage[mode] = (ReactorState.moduleUsage[mode] || 0) + 1;
    return res.json(wrap(mode, payload));
  } catch (error) {
    ReactorState.healthScore = Math.max(0, ReactorState.healthScore - 1);
    return next(error);
  }
});

app.get("/reactor/status", (_req, res) => {
  res.json({
    uptime: process.uptime(),
    totalRequests: ReactorState.totalRequests,
    moduleUsage: ReactorState.moduleUsage,
    lastSurge: ReactorState.lastSurge,
    healthScore: ReactorState.healthScore,
    chaosMode: ReactorState.chaosMode,
  });
});

function requireAdmin(req, res, next) {
  const expected = process.env.POWERHUB_ADMIN_TOKEN;
  const supplied = (req.get("authorization") || "").replace(/^Bearer\s+/i, "");
  if (!expected || !supplied) {
    return res.status(404).json({ error: "Not found." });
  }
  const expectedBuffer = Buffer.from(expected);
  const suppliedBuffer = Buffer.from(supplied);
  if (
    expectedBuffer.length !== suppliedBuffer.length ||
    !crypto.timingSafeEqual(expectedBuffer, suppliedBuffer)
  ) {
    return res.status(403).json({ error: "Forbidden." });
  }
  return next();
}

app.post("/reactor/chaos", requireAdmin, (_req, res) => {
  ReactorState.chaosMode = !ReactorState.chaosMode;
  res.json({ status: "OK", chaosMode: ReactorState.chaosMode });
});

app.get("/docs", (_req, res) => {
  res.json({
    name: "Tamanna PowerHub API",
    version: "8.0",
    endpoints: ["/health", "/power/:mode", "/power/random", "/reactor/status", "/reactor/chaos", "/docs"],
    availableModes: Object.keys(powerModules),
  });
});

app.get("/", (_req, res) => {
  res.json({ service: "Tamanna PowerHub", health: "/health", documentation: "/docs" });
});

app.use((error, _req, res, _next) => {
  res.status(500).json({
    status: "ERROR",
    message: "PowerHub request failed.",
  });
});

if (require.main === module) {
  app.listen(PORT, "127.0.0.1", () => {
    console.log("Tamanna PowerHub listening on 127.0.0.1:" + PORT);
  });
}

module.exports = { app, ReactorState };
