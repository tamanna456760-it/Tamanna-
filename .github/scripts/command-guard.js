// command-guard.js

const fs = require("fs");

const SECURITY_CONFIG = {
  maxCommandLength: 500,
  maxCommandsPerMinute: 20,
  blockedPatterns: [
    /rm\s+-rf/i,
    /mkfs/i,
    /shutdown/i,
    /reboot/i,
    /poweroff/i,
    />\s*\/dev\/sd/i,
    /:\(\)\s*\{\s*:\|:\&\s*\};:/i
  ],
  allowedCommands: [
    "ls",
    "pwd",
    "cat",
    "echo",
    "grep",
    "find"
  ]
};

function calculateRisk(command) {
  let score = 0;

  if (command.length > 100) score += 10;
  if (command.includes("&&")) score += 15;
  if (command.includes("|")) score += 10;
  if (command.includes(">")) score += 20;
  if (command.includes("$(")) score += 25;

  return score;
}

function auditLog(data) {
  fs.appendFileSync(
    "security-audit.log",
    JSON.stringify({
      timestamp: new Date().toISOString(),
      ...data
    }) + "\n"
  );
}

function validateCommand(command) {
  if (!command || command.length > SECURITY_CONFIG.maxCommandLength) {
    return { safe: false, reason: "Invalid command length" };
  }

  for (const pattern of SECURITY_CONFIG.blockedPatterns) {
    if (pattern.test(command)) {
      return { safe: false, reason: "Dangerous pattern detected" };
    }
  }

  const riskScore = calculateRisk(command);

  return {
    safe: true,
    riskScore,
    reason: "Validation passed"
  };
}

const cmd = process.argv.slice(2).join(" ");

const result = validateCommand(cmd);

auditLog({
  command: cmd,
  result
});

if (!result.safe) {
  console.error("❌ BLOCKED:", result.reason);
  process.exit(1);
}

console.log("✅ ALLOWED");
console.log("Risk Score:", result.riskScore);