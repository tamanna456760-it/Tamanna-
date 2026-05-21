// ⚡ PowerHub Core Engine v7.7
// Quantum Orchestrator Edition
// Self‑optimizing • Hot‑Reloading • Metric‑Driven • Event‑Reactive

const express = require("express");
const cors = require("cors");
const fs = require("fs");
const path = require("path");
const EventEmitter = require("events");

const app = express();
app.use(cors());
app.use(express.json());
app.use(express.static("public"));

// ⚡ Global Reactor State
const ReactorState = {
  totalRequests: 0,
  moduleUsage: {},
  lastSurge: null,
  healthScore: 100,
  chaosMode: false
};

// ⚡ Event System
const reactorEvents = new EventEmitter();
reactorEvents.on("surge", (mode) => {
  ReactorState.lastSurge = {
    mode,
    timestamp: Date.now(),
    energy: (Math.random() * 9999).toFixed(2)
  };
  console.log(`⚡ SURGE EVENT: ${mode} reactor spiked!`);
});

// ⚡ Hot‑Reloading Power Modules
const powerDir = path.join(__dirname, "powerhub");
let powerModules = {};

function loadModules() {
  powerModules = {};
  fs.readdirSync(powerDir).forEach((file) => {
    if (file.endsWith(".js")) {
      const name = file.replace(".js", "");
      delete require.cache[require.resolve(path.join(powerDir, file))];
      powerModules[name] = require(path.join(powerDir, file));
    }
  });
  console.log("🔄 Power modules reloaded:", Object.keys(powerModules));
}

loadModules();

// Auto‑reload every 10 seconds
setInterval(loadModules, 10000);

// ⚡ Chaos Mode (optional)
function maybeChaos() {
  if (!ReactorState.chaosMode) return;
  if (Math.random() < 0.05) throw new Error("CHAOS MODE: Reactor instability!");
}

// ⚡ Unified Response Wrapper
function wrap(mode, data) {
  return {
    status: "OK",
    mode,
    timestamp: Date.now(),
    reactorHealth: ReactorState.healthScore,
    payload: data
  };
}

// ⚡ Dynamic Endpoint Generator
Object.keys(powerModules).forEach((mode) => {
  app.get(`/power/${mode}`, (req, res) => {
    try {
      maybeChaos();

      ReactorState.totalRequests++;
      ReactorState.moduleUsage[mode] =
        (ReactorState.moduleUsage[mode] || 0) + 1;

      const result = powerModules[mode]();

      // Random surge event
      if (Math.random() < 0.1) reactorEvents.emit("surge", mode);

      res.json(wrap(mode, result));
    } catch (err) {
      ReactorState.healthScore -= 1;
      res.status(500).json({
        status: "ERROR",
        mode,
        message: "Reactor malfunction detected.",
        error: err.message
      });
    }
  });
});

// ⚡ Random Power Mode
app.get("/power/random", (req, res) => {
  const modes = Object.keys(powerModules);
  const mode = modes[Math.floor(Math.random() * modes.length)];
  res.redirect(`/power/${mode}`);
});

// ⚡ Reactor Diagnostics
app.get("/reactor/status", (req, res) => {
  res.json({
    uptime: `${process.uptime().toFixed(2)}s`,
    totalRequests: ReactorState.totalRequests,
    moduleUsage: ReactorState.moduleUsage,
    lastSurge: ReactorState.lastSurge,
    healthScore: ReactorState.healthScore,
    chaosMode: ReactorState.chaosMode
  });
});

// ⚡ Toggle Chaos Mode
app.post("/reactor/chaos", (req, res) => {
  ReactorState.chaosMode = !ReactorState.chaosMode;
  res.json({
    status: "OK",
    chaosMode: ReactorState.chaosMode
  });
});

// ⚡ Auto‑Documentation
app.get("/docs", (req, res) => {
  res.json({
    name: "PowerHub Quantum API",
    version: "7.7",
    endpoints: [
      "/power/<mode>",
      "/power/random",
      "/reactor/status",
      "/reactor/chaos",
      "/docs"
    ],
    availableModes: Object.keys(powerModules)
  });
});

// Root
app.get("/", (req, res) => {
  res.sendFile(__dirname + "/public/index.html");
});

// Start Server
const PORT = 8080;
app.listen(PORT, () =>
  console.log(`⚡ PowerHub Quantum Orchestrator Running on Port ${PORT}`)
);
const express = require("express");
const app = express();
const cors = require("cors");

app.use(cors());
app.use(express.json());
app.use(express.static("public"));

// Include Power Modules
const normal = require("./powerhub/normal");
const medium = require("./powerhub/medium");
const deep = require("./powerhub/deep");
const dark = require("./powerhub/dark");
const underground = require("./powerhub/underground");
const silent = require("./powerhub/silent_supersonic");
const stone = require("./powerhub/stone_spirit");

// API ENDPOINTS
app.get("/power/normal", (req, res) => res.json(normal()));
app.get("/power/medium", (req, res) => res.json(medium()));
app.get("/power/deep", (req, res) => res.json(deep()));
app.get("/power/dark", (req, res) => res.json(dark()));
app.get("/power/underground", (req, res) => res.json(underground()));
app.get("/power/silent", (req, res) => res.json(silent()));
app.get("/power/stone", (req, res) => res.json(stone()));

app.get("/", (req, res) => {
  res.sendFile(__dirname + "/public/index.html");
});

const PORT = 8080;
app.listen(PORT, () => console.log(`PowerHub Running on Port ${PORT}`));
