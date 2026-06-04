const crypto = require("crypto");

module.exports = async (mode = "normal") => {
  // Power modes
  const modes = {
    normal: "Underground Power Activated",
    turbo: "⚡ TURBO Underground Power Engaged",
    godmode: "🔥 GOD‑LEVEL POWER UNLEASHED",
  };

  // Random surge generator
  const surge = Math.floor(Math.random() * 5000) + 1000;

  // Diagnostics system
  const diagnostics = {
    cpu: "Stable",
    coreTemp: `${40 + Math.random() * 10}°C`,
    shield: "Reinforced",
    reactorLoad: `${50 + Math.random() * 40}%`,
  };

  // ASCII aura
  const aura = `
  ⚡⚡⚡ POWER AURA ONLINE ⚡⚡⚡
  [██████████████████████]
  Mode: ${mode.toUpperCase()}
  Surge: ${surge}
  `;

  // Base payload
  const payload = {
    status: "OK",
    power: modes[mode] || modes.normal,
    mode,
    surgeLevel: surge,
    diagnostics,
    environment: process.env.NODE_ENV || "development",
    timestamp: new Date().toISOString(),
    aura,
  };

  // Security signature
  const signature = crypto
    .createHash("sha256")
    .update(JSON.stringify(payload))
    .digest("hex");

  return {
    ...payload,
    signature,
  };
};