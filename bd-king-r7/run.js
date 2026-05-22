import 'dotenv/config'
import { startAI } from './ai.js'
import { githubSync } from './github-sync.js'
import { systemMonitor } from './monitor.js'
import { securityScan } from './security.js'

console.log("🌸 Tamanna AI OS — Boot Sequence Initializing...\n")

// Utility: colored logs
const log = {
  info:  (msg) => console.log(`\x1b[36m[INFO]\x1b[0m ${msg}`),
  ok:    (msg) => console.log(`\x1b[32m[OK]\x1b[0m ${msg}`),
  warn:  (msg) => console.log(`\x1b[33m[WARN]\x1b[0m ${msg}`),
  error: (msg) => console.log(`\x1b[31m[ERROR]\x1b[0m ${msg}`)
}

// Utility: safe executor
async function safeRun(name, fn) {
  log.info(`Starting: ${name}`)
  const start = performance.now()

  try {
    await fn()
    const end = performance.now()
    log.ok(`${name} completed in ${(end - start).toFixed(1)}ms`)
  } catch (err) {
    log.error(`${name} failed: ${err.message}`)
  }
}

// Boot sequence
async function startSystem() {
  const bootStart = performance.now()
  log.info("Boot sequence started...\n")

  // Step 1 — Security first
  await safeRun("Security Scan", securityScan)

  // Step 2 — GitHub Sync (can run in parallel with monitor)
  const syncPromise = safeRun("GitHub Sync", githubSync)

  // Step 3 — System Monitor (non-blocking)
  safeRun("System Monitor", systemMonitor)

  // Wait for GitHub sync to finish
  await syncPromise

  // Step 4 — Start AI Core
  await safeRun("AI Core Startup", startAI)

  const bootEnd = performance.now()
  log.ok(`\n🌸 Tamanna AI OS Boot Completed in ${(bootEnd - bootStart).toFixed(1)}ms`)
}

// Graceful shutdown
process.on("SIGINT", () => {
  log.warn("\nTamanna AI OS shutting down gracefully...")
  process.exit(0)
})

startSystem()