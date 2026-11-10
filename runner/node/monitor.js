"use strict";

const os = require("node:os");

function collectSystemMetrics() {
  const totalMemoryBytes = os.totalmem();
  const freeMemoryBytes = os.freemem();
  const loadAverage = os.loadavg();
  const cpus = os.cpus();
  const usedMemoryBytes = Math.max(0, totalMemoryBytes - freeMemoryBytes);

  return {
    timestamp: new Date().toISOString(),
    platform: process.platform,
    nodeVersion: process.version,
    cpuCores: cpus.length,
    loadAverage: loadAverage.map((value) => Number(value.toFixed(2))),
    memory: {
      totalBytes: totalMemoryBytes,
      freeBytes: freeMemoryBytes,
      usedBytes: usedMemoryBytes,
      usedPercent: totalMemoryBytes
        ? Number(((usedMemoryBytes / totalMemoryBytes) * 100).toFixed(2))
        : null
    },
    uptimeSeconds: Math.floor(os.uptime())
  };
}

// One snapshot by default. Pass an interval to opt into periodic logging.
function systemMonitor({ intervalMs = 0, onMetrics = null } = {}) {
  const emit = typeof onMetrics === "function" ? onMetrics : (metrics) => {
    process.stdout.write(`[Tamanna monitor] ${JSON.stringify(metrics)}\n`);
  };

  emit(collectSystemMetrics());
  if (!Number.isInteger(intervalMs) || intervalMs < 0) {
    throw new TypeError("intervalMs must be a non-negative integer");
  }
  if (intervalMs === 0) return () => {};

  const timer = setInterval(() => {
    try {
      emit(collectSystemMetrics());
    } catch (error) {
      process.stderr.write(`[Tamanna monitor] ${error.message}\n`);
    }
  }, intervalMs);
  if (typeof timer.unref === "function") timer.unref();
  return () => clearInterval(timer);
}

module.exports = { collectSystemMetrics, systemMonitor };
