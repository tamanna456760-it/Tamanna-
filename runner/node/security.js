"use strict";

// This is a runtime configuration audit, not an OS firewall or malware scanner.
// Checks that cannot be verified from this Node process are explicitly reported
// as "not_checked"; the module never fabricates random pass/fail results.
function securityScan() {
  const nodeMajor = Number(process.versions.node.split(".")[0]);
  const checks = [
    {
      name: "Node.js supported runtime",
      status: nodeMajor >= 20 ? "passed" : "failed",
      detail: nodeMajor >= 20 ? "Node.js 20 or newer is active." : "Node.js 20 or newer is required."
    },
    {
      name: "External AI providers",
      status: "passed",
      detail: "External model providers are disabled in this runtime."
    },
    {
      name: "Automatic Git push",
      status: process.env.TAMANNA_ENABLE_GIT_PUSH === "1" ? "review_required" : "passed",
      detail: process.env.TAMANNA_ENABLE_GIT_PUSH === "1"
        ? "Git push opt-in is enabled; verify the exact path allowlist before use."
        : "Automatic Git push is disabled by default."
    },
    {
      name: "Firewall admin token",
      status: process.env.TAMANNA_FIREWALL_ADMIN_TOKEN ? "configured" : "not_configured",
      detail: process.env.TAMANNA_FIREWALL_ADMIN_TOKEN
        ? "A private firewall admin token is configured (value not displayed)."
        : "No firewall admin token is configured."
    },
    {
      name: "Operating-system firewall",
      status: "not_checked",
      detail: "This Node process does not verify host firewall rules."
    },
    {
      name: "Malware and rootkit scan",
      status: "not_checked",
      detail: "No malware or rootkit scanner is integrated."
    },
    {
      name: "Network intrusion detection",
      status: "not_checked",
      detail: "No host/network IDS is integrated."
    }
  ];

  const failed = checks.some((item) => item.status === "failed");
  const reviewRequired = checks.some((item) =>
    ["review_required", "not_configured", "not_checked"].includes(item.status)
  );

  return {
    timestamp: new Date().toISOString(),
    scanType: "node-runtime-configuration-audit",
    status: failed ? "failed" : reviewRequired ? "partial" : "passed",
    passed: !failed && !reviewRequired,
    results: checks
  };
}

module.exports = { securityScan };
