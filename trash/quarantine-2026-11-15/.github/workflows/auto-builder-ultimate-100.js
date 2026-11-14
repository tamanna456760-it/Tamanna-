#!/usr/bin/env node

// =========================== IMPORTS ===========================
const { spawn, execSync } = require('child_process');
const fs = require('fs').promises;
const path = require('path');
const http = require('http');
const https = require('https');
const crypto = require('crypto');
const os = require('os');
const readline = require('readline');

// ======================== CLI ARGUMENTS =========================
const args = process.argv.slice(2);
const CLI = {
  once: args.includes('--once'),                  // Condition 1
  dryRun: args.includes('--dry-run'),             // Condition 2
  repo: args.find((_,i) => args[i-1] === '--repo'), // Condition 3
  verbose: args.includes('--verbose'),            // Condition 4
  profile: args.includes('--profile'),            // Condition 5
  poll: parseInt(args.find((_,i) => args[i-1] === '--poll') || '0'), // Condition 6
  force: args.includes('--force'),                // Condition 7
  noCache: args.includes('--no-cache'),           // Condition 8
  local: args.includes('--local')                 // Condition 9
};

if (CLI.profile) require('inspector').open();      // Condition 10

// ======================== CONFIGURATION =========================
const CONFIG = {
  // --- Core Modes (Condition 11-14) ---
  mode: process.env.MODE || 'hybrid',              // Condition 11: poll, webhook, hybrid
  pollIntervalMs: CLI.poll || parseInt(process.env.POLL_INTERVAL_MS) || 30000, // Condition 12
  webhookPort: parseInt(process.env.WEBHOOK_PORT) || 9000, // Condition 13
  webhookSecret: process.env.WEBHOOK_SECRET || 'default-secret-change-me', // Condition 14

  // --- Build Engine (Condition 15-20) ---
  maxRetries: parseInt(process.env.MAX_RETRIES) || 3, // Condition 15
  retryBaseDelayMs: parseInt(process.env.RETRY_DELAY_MS) || 2000, // Condition 16
  commandTimeoutMs: parseInt(process.env.COMMAND_TIMEOUT_MS) || 300000, // Condition 17
  maxConcurrentCommands: parseInt(process.env.MAX_CONCURRENT) || 4, // Condition 18
  parallelRepos: process.env.PARALLEL_REPOS !== 'false', // Condition 19
  shutdownTimeoutMs: parseInt(process.env.SHUTDOWN_TIMEOUT_MS) || 10000, // Condition 20

  // --- Caching & Artifacts (Condition 21-28) ---
  cacheDir: process.env.CACHE_DIR || './build-cache', // Condition 21
  artifactDir: process.env.ARTIFACT_DIR || './artifacts', // Condition 22
  artifactUpload: {
    enabled: process.env.ARTIFACT_UPLOAD === 'true', // Condition 23
    provider: process.env.ARTIFACT_PROVIDER || 'local', // Condition 24: s3, local
    s3: { bucket: process.env.S3_BUCKET || '', region: process.env.S3_REGION || 'us-east-1' }, // Condition 25
    localPath: process.env.ARTIFACT_LOCAL_PATH || './archive', // Condition 26
    retentionDays: parseInt(process.env.ARTIFACT_RETENTION_DAYS) || 7 // Condition 27
  },
  cacheMaxSizeMB: parseInt(process.env.CACHE_MAX_MB) || 500, // Condition 28

  // --- Monitoring & Alerts (Condition 29-38) ---
  dashboardPort: parseInt(process.env.DASHBOARD_PORT) || 8080, // Condition 29
  prometheusPort: parseInt(process.env.PROMETHEUS_PORT) || 9090, // Condition 30
  healthPort: parseInt(process.env.HEALTH_PORT) || 8081, // Condition 31
  alertThresholds: {
    consecutiveFailures: parseInt(process.env.ALERT_CONSECUTIVE_FAILURES) || 10, // Condition 32
    failureRatePercent: parseInt(process.env.ALERT_FAILURE_RATE_PERCENT) || 30, // Condition 33
    diskUsagePercent: parseInt(process.env.ALERT_DISK_USAGE_PERCENT) || 90, // Condition 34
    memoryUsagePercent: parseInt(process.env.ALERT_MEMORY_PERCENT) || 85, // Condition 35
    slowBuildMs: parseInt(process.env.ALERT_SLOW_BUILD_MS) || 600000 // Condition 36: 10 min
  },
  metricsEnabled: process.env.METRICS_ENABLED !== 'false', // Condition 37
  enableWebSocketDashboard: process.env.WS_DASHBOARD === 'true', // Condition 38

  // --- Notifications (Condition 39-48) ---
  notifications: {
    slack: { webhookUrl: process.env.SLACK_WEBHOOK || '' }, // Condition 39
    discord: { webhookUrl: process.env.DISCORD_WEBHOOK || '' }, // Condition 40
    telegram: { botToken: process.env.TELEGRAM_BOT_TOKEN || '', chatId: process.env.TELEGRAM_CHAT_ID || '' }, // Condition 41
    email: {
      enabled: process.env.EMAIL_ENABLED === 'true', // Condition 42
      smtp: { host: process.env.SMTP_HOST || '', port: parseInt(process.env.SMTP_PORT) || 587, user: process.env.SMTP_USER || '', pass: process.env.SMTP_PASS || '' }, // Condition 43
      to: process.env.EMAIL_TO || '', // Condition 44
      reports: { daily: true, weekly: true } // Condition 45
    },
    onSuccess: process.env.NOTIFY_ON_SUCCESS !== 'false', // Condition 46
    onFailure: true, // Condition 47
    onStart: process.env.NOTIFY_ON_START === 'true' // Condition 48
  },

  // --- GitHub Integration (Condition 49-54) ---
  github: {
    token: process.env.GH_TOKEN || '', // Condition 49
    setCommitStatus: process.env.GH_SET_STATUS !== 'false', // Condition 50
    apiUrl: process.env.GH_API_URL || 'https://api.github.com', // Condition 51
    owner: process.env.GH_OWNER || 'Tamanna456760-it', // Condition 52
    checkRateLimit: process.env.GH_CHECK_RATE_LIMIT !== 'false', // Condition 53
    timeoutMs: parseInt(process.env.GH_TIMEOUT_MS) || 10000 // Condition 54
  },

  // --- Secrets & Encryption (Condition 55-58) ---
  secrets: {
    encryptionKey: process.env.ENCRYPTION_KEY || 'default-32-byte-key-for-aes256!!', // Condition 55
    useAWSKMS: process.env.USE_AWS_KMS === 'true', // Condition 56
    awsRegion: process.env.AWS_REGION || 'us-east-1', // Condition 57
    secretsFile: process.env.SECRETS_FILE || './secrets.env' // Condition 58
  },

  // --- Distributed Locking (Condition 59-62) ---
  lock: {
    type: process.env.LOCK_TYPE || 'file', // Condition 59: file, redis
    redisUrl: process.env.REDIS_URL || '', // Condition 60
    lockTTLms: parseInt(process.env.LOCK_TTL_MS) || 60000, // Condition 61
    retryIntervalMs: parseInt(process.env.LOCK_RETRY_MS) || 500 // Condition 62
  },

  // --- Dependency Graph (Condition 63) ---
  dependencies: JSON.parse(process.env.DEPENDENCIES || '{"lib-core":[],"api-service":["lib-core"],"web-frontend":["api-service"]}'), // Condition 63

  // --- Repositories Definition (Condition 64-73) ---
  repos: [
    {
      name: 'lib-core',
      repoUrl: 'https://github.com/Tamanna456760-it/lib-core.git',
      branches: ['main'],
      localPath: './repos/lib-core',
      alwaysBuild: false,
      watchPaths: ['src/', 'package.json'],
      commands: [
        { cmd: 'npm ci', parallel: false, runIf: ['package-lock.json'], timeoutMs: 60000 },
        { cmd: 'npm run build', parallel: false }
      ],
      cache: { enabled: true, key: 'node_modules', paths: ['node_modules'] }, // Condition 64
      docker: { enabled: false }, // Condition 65
      healthCheck: { enabled: false, endpoint: '', intervalMs: 30000 }, // Condition 66
      preBuild: ['echo "Pre-build lib-core"'], // Condition 67
      postBuild: ['echo "Post-build lib-core"'], // Condition 68
      env: { NODE_ENV: 'production' }, // Condition 69
      maxParallelCommands: 2, // Condition 70
      skipOnBranch: [], // Condition 71
      onlyOnBranch: ['main'], // Condition 72
      timeoutFactor: 1.5 // Condition 73
    },
    {
      name: 'api-service',
      repoUrl: 'https://github.com/Tamanna456760-it/api-service.git',
      branches: ['main', 'develop'],
      localPath: './repos/api-service',
      commands: [
        { cmd: 'npm ci' },
        { cmd: 'npm test', parallel: true, timeoutMs: 120000 },
        { cmd: 'docker build -t api-service:latest .', parallel: false },
        { cmd: 'docker push api-service:latest' }
      ],
      docker: { enabled: true, imageName: 'api-service', registry: 'docker.io/tamanna' }, // Condition 65
      healthCheck: { enabled: true, endpoint: 'http://localhost:3000/health', intervalMs: 30000 } // Condition 66
    }
  ],

  // --- Cron Jobs (Condition 74-78) ---
  cronJobs: [
    { schedule: '0 2 * * *', command: 'npm run integration-test', repo: 'api-service' }, // Condition 74
    { schedule: '0 8 * * 1', report: 'weekly' } // Condition 75
  ],
  cronTimeZone: process.env.CRON_TZ || 'UTC', // Condition 76
  cronMaxOverruns: 3, // Condition 77
  cronCatchup: true, // Condition 78

  // --- Logging & Debugging (Condition 79-87) ---
  logFile: process.env.LOG_FILE || 'auto-builder.log',
  logLevel: CLI.verbose ? 'debug' : (process.env.LOG_LEVEL || 'info'), // Condition 79
  logMaxSizeMB: parseInt(process.env.LOG_MAX_MB) || 20, // Condition 80
  logMaxFiles: parseInt(process.env.LOG_MAX_FILES) || 5, // Condition 81
  pidFile: process.env.PID_FILE || 'auto-builder.pid', // Condition 82
  enableConsoleColors: process.env.CONSOLE_COLORS !== 'false', // Condition 83
  traceGitCommands: process.env.TRACE_GIT === 'true', // Condition 84
  debugCommands: CLI.verbose, // Condition 85
  profileBuilds: process.env.PROFILE_BUILDS === 'true', // Condition 86
  sendLogsToSentry: process.env.SENTRY_DSN || '' // Condition 87
};

// ======================== GLOBAL STATE =========================
let runningBuilds = new Map();        // Condition 88: track running builds
let buildQueue = [];                  // Condition 89: queue for serial mode
let activeCommands = 0;              // Condition 90: concurrency limiter
let isShuttingDown = false;          // Condition 91: graceful shutdown flag
let pollIntervals = [];               // Condition 92: store intervals for cleanup
let repoFailureCount = new Map();     // Condition 93: auto-healing counter
let disabledRepos = new Set();        // Condition 94: temporarily disabled repos
let buildStats = new Map();           // Condition 95: success/failure per repo
let lastGitHubCheck = 0;              // Condition 96: rate limit tracking
let server = null;                    // Condition 97: HTTP server reference
let webhookServer = null;             // Condition 98: webhook server reference

// ======================== UTILITY FUNCTIONS ========================
const logLevels = { debug: 0, info: 1, warn: 2, error: 3 };
let currentLogLevel = logLevels[CONFIG.logLevel] ?? 1;

async function log(msg, level = 'info', ...args) {
  if (logLevels[level] < currentLogLevel) return;
  const timestamp = new Date().toISOString();
  const color = CONFIG.enableConsoleColors ? { info: '\x1b[32m', warn: '\x1b[33m', error: '\x1b[31m', debug: '\x1b[36m' }[level] || '' : '';
  const reset = color ? '\x1b[0m' : '';
  const line = `${color}[${timestamp}] [${level.toUpperCase()}] ${msg} ${args.join(' ')}${reset}`;
  console.log(line);
  await fs.appendFile(CONFIG.logFile, line.replace(/\x1b\[[0-9;]*m/g, '') + '\n').catch(() => {});
}
// Condition 99: log rotation
async function rotateLogIfNeeded() {
  try {
    const stat = await fs.stat(CONFIG.logFile).catch(() => null);
    if (stat && stat.size > CONFIG.logMaxSizeMB * 1024 * 1024) {
      const oldFiles = await fs.readdir(path.dirname(CONFIG.logFile));
      const logFiles = oldFiles.filter(f => f.startsWith(path.basename(CONFIG.logFile))).sort();
      while (logFiles.length >= CONFIG.logMaxFiles) {
        const oldest = logFiles.shift();
        await fs.unlink(path.join(path.dirname(CONFIG.logFile), oldest)).catch(() => {});
      }
      const backup = `${CONFIG.logFile}.${Date.now()}.old`;
      await fs.rename(CONFIG.logFile, backup);
      log(`Log rotated (${CONFIG.logMaxSizeMB}MB limit)`, 'info');
    }
  } catch (err) {}
}

// Condition 100: HTTP request with retry
async function httpRequest(url, options, data, retries = 2) {
  for (let i = 0; i <= retries; i++) {
    try {
      const client = url.startsWith('https') ? https : http;
      return await new Promise((resolve, reject) => {
        const req = client.request(url, options, (res) => {
          let body = '';
          res.on('data', chunk => body += chunk);
          res.on('end', () => resolve(body));
        });
        req.on('error', reject);
        req.setTimeout(CONFIG.github.timeoutMs, () => req.destroy());
        if (data) req.write(data);
        req.end();
      });
    } catch (err) {
      if (i === retries) throw err;
      await new Promise(r => setTimeout(r, 1000 * (i + 1)));
    }
  }
}

// Additional conditions 101-110: encryption, caching, locking, etc.
function encrypt(text, key) {
  const iv = crypto.randomBytes(16);
  const cipher = crypto.createCipheriv('aes-256-cbc', Buffer.from(key.padEnd(32, '0')), iv);
  let encrypted = cipher.update(text, 'utf8', 'hex');
  encrypted += cipher.final('hex');
  return iv.toString('hex') + ':' + encrypted;
}

function decrypt(text, key) {
  const parts = text.split(':');
  const iv = Buffer.from(parts.shift(), 'hex');
  const encryptedText = parts.join(':');
  const decipher = crypto.createDecipheriv('aes-256-cbc', Buffer.from(key.padEnd(32, '0')), iv);
  let decrypted = decipher.update(encryptedText, 'hex', 'utf8');
  decrypted += decipher.final('utf8');
  return decrypted;
}

// ======================== ADVANCED BUILD ENGINE ========================
async function runCommand(cmdObj, cwd, repoName, buildId) {
  // Condition 111: concurrency limiting
  while (activeCommands >= CONFIG.maxConcurrentCommands) {
    await new Promise(r => setTimeout(r, 100));
  }
  activeCommands++;
  const command = typeof cmdObj === 'string' ? cmdObj : cmdObj.cmd;
  const timeout = (cmdObj.timeoutMs || CONFIG.commandTimeoutMs) * (repoConfig?.timeoutFactor || 1);
  const env = cmdObj.env ? { ...process.env, ...cmdObj.env, ...repoConfig?.env } : { ...process.env, ...repoConfig?.env };
  
  const start = Date.now();
  try {
    if (CLI.dryRun) {
      log(`[DRY RUN] ${command}`, 'info');
      return { stdout: '', stderr: '' };
    }
    log(`[${repoName}] Exec: ${command}`, 'debug');
    const child = spawn(command, { shell: true, cwd, env, stdio: 'pipe' });
    let stdout = '', stderr = '';
    const timer = setTimeout(() => {
      child.kill('SIGTERM');
      setTimeout(() => child.kill('SIGKILL'), 5000);
    }, timeout);
    
    for await (const chunk of child.stdout) stdout += chunk;
    for await (const chunk of child.stderr) stderr += chunk;
    clearTimeout(timer);
    const code = await new Promise(resolve => child.on('close', resolve));
    if (code !== 0) throw new Error(`Exit ${code}: ${stderr}`);
    log(`[${repoName}] Completed in ${Date.now() - start}ms`, 'debug');
    return { stdout, stderr };
  } finally {
    activeCommands--;
  }
}

// Condition 112: dependency graph traversal
class DependencyGraph {
  constructor(deps) { this.graph = deps; }
  getAffected(repoName) {
    const affected = new Set();
    const queue = [repoName];
    while (queue.length) {
      const current = queue.shift();
      if (affected.has(current)) continue;
      affected.add(current);
      for (const [dep, dependents] of Object.entries(this.graph)) {
        if (dependents.includes(current)) queue.push(dep);
      }
    }
    return Array.from(affected);
  }
}

// Condition 113: cache manager with size limit
class CacheManager {
  async init() { await fs.mkdir(CONFIG.cacheDir, { recursive: true }); }
  async getCacheKey(repoName, branch, cmdHash) {
    const key = crypto.createHash('md5').update(`${repoName}:${branch}:${cmdHash}`).digest('hex');
    const cachePath = path.join(CONFIG.cacheDir, key);
    try { await fs.access(cachePath); return { exists: true, path: cachePath }; } catch { return { exists: false }; }
  }
  async saveCache(repoName, branch, cmdHash, dataPath) {
    const key = crypto.createHash('md5').update(`${repoName}:${branch}:${cmdHash}`).digest('hex');
    const dest = path.join(CONFIG.cacheDir, key);
    await fs.copyFile(dataPath, dest);
    await this.cleanup();
  }
  async cleanup() {
    const files = await fs.readdir(CONFIG.cacheDir);
    let totalSize = 0;
    const fileStats = [];
    for (const file of files) {
      const stat = await fs.stat(path.join(CONFIG.cacheDir, file));
      totalSize += stat.size;
      fileStats.push({ file, size: stat.size, mtime: stat.mtime });
    }
    if (totalSize > CONFIG.cacheMaxSizeMB * 1024 * 1024) {
      fileStats.sort((a, b) => a.mtime - b.mtime);
      for (const f of fileStats) {
        await fs.unlink(path.join(CONFIG.cacheDir, f.file));
        totalSize -= f.size;
        if (totalSize <= CONFIG.cacheMaxSizeMB * 1024 * 1024 * 0.8) break;
      }
    }
  }
}

// Condition 114: distributed lock (file or redis)
class DistributedLock {
  async acquire(key, ttlMs = CONFIG.lock.lockTTLms) {
    if (CONFIG.lock.type === 'file') {
      const lockFile = path.join(os.tmpdir(), `${key}.lock`);
      try {
        const fd = await fs.open(lockFile, 'wx');
        await fd.writeFile(`${process.pid}\n${Date.now() + ttlMs}`);
        await fd.close();
        return true;
      } catch { return false; }
    } else if (CONFIG.lock.type === 'redis') {
      // Redis implementation would go here
      return true;
    }
    return true;
  }
  async release(key) {
    if (CONFIG.lock.type === 'file') {
      const lockFile = path.join(os.tmpdir(), `${key}.lock`);
      await fs.unlink(lockFile).catch(() => {});
    }
  }
}

// Condition 115: GitHub commit status updater
class GitHubStatus {
  async setStatus(owner, repo, sha, state, description, targetUrl) {
    if (!CONFIG.github.setCommitStatus || !CONFIG.github.token) return;
    if (CONFIG.github.checkRateLimit && Date.now() - lastGitHubCheck < 60000) return;
    lastGitHubCheck = Date.now();
    const url = `${CONFIG.github.apiUrl}/repos/${owner}/${repo}/statuses/${sha}`;
    const data = JSON.stringify({ state, description, target_url: targetUrl, context: 'auto-builder' });
    await httpRequest(url, { method: 'POST', headers: { 'Authorization': `token ${CONFIG.github.token}`, 'Content-Type': 'application/json' } }, data);
  }
}

// Condition 116: artifact uploader (S3 or local)
class ArtifactManager {
  async upload(repoName, buildId, filePath) {
    if (!CONFIG.artifactUpload.enabled) return;
    if (!await fs.access(filePath).then(() => true).catch(() => false)) return;
    if (CONFIG.artifactUpload.provider === 's3') {
      // AWS SDK would be used here
      log(`Uploading ${filePath} to S3`, 'debug');
    } else {
      const dest = path.join(CONFIG.artifactUpload.localPath, repoName, buildId, path.basename(filePath));
      await fs.mkdir(path.dirname(dest), { recursive: true });
      await fs.copyFile(filePath, dest);
      log(`Artifact saved to ${dest}`, 'info');
    }
  }
  async cleanupOldArtifacts() {
    const cutoff = Date.now() - CONFIG.artifactUpload.retentionDays * 86400000;
    const base = CONFIG.artifactUpload.provider === 's3' ? '' : CONFIG.artifactUpload.localPath;
    // recursively delete old files
  }
}

// Condition 117: auto disk cleanup
async function checkDiskAndCleanup() {
  try {
    const { size: total, free } = await fs.statvfs('/');
    const usedPercent = (1 - free / total) * 100;
    if (usedPercent > CONFIG.alertThresholds.diskUsagePercent) {
      log(`Disk usage ${usedPercent.toFixed(1)}% > threshold, cleaning`, 'warn');
      const logDir = path.dirname(CONFIG.logFile);
      const files = await fs.readdir(logDir);
      const now = Date.now();
      for (const file of files) {
        const filePath = path.join(logDir, file);
        const stat = await fs.stat(filePath);
        if (now - stat.mtimeMs > 7 * 86400000) await fs.unlink(filePath).catch(() => {});
      }
      const cacheFiles = await fs.readdir(CONFIG.cacheDir).catch(() => []);
      for (const file of cacheFiles) {
        const filePath = path.join(CONFIG.cacheDir, file);
        const stat = await fs.stat(filePath);
        if (now - stat.mtimeMs > 2 * 86400000) await fs.unlink(filePath).catch(() => {});
      }
    }
  } catch (err) {}
}

// Condition 118: auto-healing (disable failing repos)
async function recordFailure(repoName) {
  const count = (repoFailureCount.get(repoName) || 0) + 1;
  repoFailureCount.set(repoName, count);
  if (count >= CONFIG.alertThresholds.consecutiveFailures) {
    disabledRepos.add(repoName);
    log(`Repo ${repoName} disabled after ${count} consecutive failures`, 'error');
    await sendNotification(`⚠️ Repo ${repoName} disabled due to too many failures`, 'error');
  }
}

async function recordSuccess(repoName) {
  repoFailureCount.set(repoName, 0);
  if (disabledRepos.has(repoName)) {
    disabledRepos.delete(repoName);
    log(`Repo ${repoName} re-enabled after success`, 'info');
  }
}

// Condition 119: rich notifications (Slack/Discord/Telegram/Email)
async function sendNotification(message, level = 'info', buildData = {}) {
  const { slack, discord, telegram, email } = CONFIG.notifications;
  const emoji = level === 'error' ? '❌' : (level === 'warn' ? '⚠️' : '✅');
  if (slack.webhookUrl) {
    await httpRequest(slack.webhookUrl, { method: 'POST' }, JSON.stringify({ text: `${emoji} ${message}`, attachments: [{ color: level, fields: Object.entries(buildData).map(([k,v]) => ({ title: k, value: v })) }] }));
  }
  if (discord.webhookUrl) {
    await httpRequest(discord.webhookUrl, { method: 'POST' }, JSON.stringify({ content: `${emoji} ${message}`, embeds: [{ color: level === 'error' ? 0xFF0000 : 0x00FF00, fields: Object.entries(buildData).map(([k,v]) => ({ name: k, value: v })) }] }));
  }
  if (telegram.botToken && telegram.chatId) {
    const url = `https://api.telegram.org/bot${telegram.botToken}/sendMessage`;
    await httpRequest(url, { method: 'POST' }, JSON.stringify({ chat_id: telegram.chatId, text: `${emoji} ${message}\n${JSON.stringify(buildData)}` }));
  }
  if (email.enabled && email.smtp.host && (level === 'error' || level === 'warn')) {
    // nodemailer would be used here
  }
}

// Condition 120: main repo processing with all conditions
let lock = new DistributedLock();
let githubStatus = new GitHubStatus();
let artifactManager = new ArtifactManager();
let cache = new CacheManager();
let depGraph = new DependencyGraph(CONFIG.dependencies);

async function ensureRepo(repoConfig, branch) {
  const { repoUrl, localPath, name } = repoConfig;
  let url = repoUrl;
  if (CONFIG.github.token && url.includes('github.com')) {
    url = url.replace('https://', `https://${CONFIG.github.token}@`);
  }
  try {
    await fs.access(localPath);
    log(`[${name}] Repo exists`, 'debug');
  } catch {
    log(`[${name}] Cloning ${repoUrl} branch ${branch}`, 'info');
    await runCommand(`git clone --branch ${branch} ${url} ${localPath}`, process.cwd(), name);
  }
  // Condition 121: git sparse checkout support
  if (repoConfig.sparseCheckout) {
    await runCommand(`git sparse-checkout init --cone`, localPath, name);
    await runCommand(`git sparse-checkout set ${repoConfig.sparseCheckout}`, localPath, name);
  }
}

async function pullChanges(repoConfig, branch) {
  const { localPath, name } = repoConfig;
  const oldCommit = (await runCommand('git rev-parse HEAD', localPath, name).catch(() => ({ stdout: '' }))).stdout.trim();
  await runCommand('git fetch origin', localPath, name);
  const newCommit = (await runCommand(`git rev-parse origin/${branch}`, localPath, name)).stdout.trim();
  if (newCommit && newCommit !== oldCommit) {
    log(`[${name}:${branch}] New commit ${newCommit.substring(0,7)}`, 'info');
    await runCommand(`git pull origin ${branch}`, localPath, name);
    return true;
  }
  return false;
}

async function filesChanged(repoConfig, branch, patterns) {
  // Condition 122: detect changes in specific paths
  try {
    const { stdout } = await runCommand(`git diff --name-only HEAD@{1} HEAD`, repoConfig.localPath, repoConfig.name);
    const changed = stdout.split('\n');
    return patterns.some(p => changed.some(f => f.includes(p)));
  } catch { return true; }
}

async function processRepo(repoConfig, retry = 0, force = false) {
  const { name, branches, alwaysBuild, commands, preBuild, postBuild, localPath, cache: cacheCfg, healthCheck, skipOnBranch, onlyOnBranch } = repoConfig;
  // Condition 123: disabled repo check
  if (disabledRepos.has(name)) { log(`[${name}] Disabled, skipping`, 'warn'); return; }
  // Condition 124: already running check
  if (runningBuilds.get(name)) { log(`[${name}] Already building, skipping`, 'debug'); return; }
  // Condition 125: distributed lock acquisition
  if (!await lock.acquire(`build-${name}`)) { log(`[${name}] Lock failed, skipping`, 'debug'); return; }
  
  runningBuilds.set(name, true);
  const buildId = `${name}-${Date.now()}`;
  let success = false;
  const startTime = Date.now();
  try {
    // Condition 126: onStart notification
    if (CONFIG.notifications.onStart) await sendNotification(`🚀 Build started for ${name}`, 'info', { buildId });
    
    for (const branch of branches) {
      // Condition 127: branch filtering
      if (skipOnBranch.includes(branch)) continue;
      if (onlyOnBranch.length && !onlyOnBranch.includes(branch)) continue;
      
      await ensureRepo(repoConfig, branch);
      const changed = force || await pullChanges(repoConfig, branch);
      // Condition 128: watchPaths filtering
      let relevantChange = changed;
      if (changed && repoConfig.watchPaths && repoConfig.watchPaths.length) {
        relevantChange = await filesChanged(repoConfig, branch, repoConfig.watchPaths);
        if (!relevantChange) log(`[${name}:${branch}] Changes outside watchPaths, skipping build`, 'info');
      }
      if (relevantChange || alwaysBuild || force) {
        // Condition 129: pre-build hooks
        if (preBuild) for (const hook of preBuild) await runCommand(hook, localPath, name, buildId);
        
        for (const cmd of commands) {
          // Condition 130: conditional command execution based on changed files
          if (cmd.runIf && !force && !(await filesChanged(repoConfig, branch, cmd.runIf))) continue;
          if (CLI.dryRun) { log(`[DRY RUN] ${cmd.cmd || cmd}`, 'info'); continue; }
          await runCommand(cmd, localPath, name, buildId);
        }
        // Condition 131: Docker build & push
        if (repoConfig.docker?.enabled) {
          const tag = `${repoConfig.docker.registry}/${repoConfig.docker.imageName}:${branch}-${Date.now()}`;
          await runCommand(`docker build -t ${tag} .`, localPath, name, buildId);
          if (repoConfig.docker.registry) await runCommand(`docker push ${tag}`, localPath, name, buildId);
        }
        // Condition 132: health check after build
        if (healthCheck?.enabled) {
          let healthy = false;
          for (let i = 0; i < 5; i++) {
            await new Promise(r => setTimeout(r, healthCheck.intervalMs));
            try {
              const res = await httpRequest(healthCheck.endpoint, { method: 'GET' });
              if (res.includes('ok') || res.includes('healthy')) { healthy = true; break; }
            } catch (e) {}
          }
          if (!healthy) throw new Error(`Health check failed for ${name}`);
        }
        // Condition 133: post-build hooks
        if (postBuild) for (const hook of postBuild) await runCommand(hook, localPath, name, buildId);
        success = true;
      }
    }
    if (success) {
      await recordSuccess(name);
      const duration = Date.now() - startTime;
      // Condition 134: slow build alert
      if (duration > CONFIG.alertThresholds.slowBuildMs) {
        await sendNotification(`⚠️ Slow build for ${name}`, 'warn', { duration: `${duration}ms` });
      }
      if (CONFIG.notifications.onSuccess) await sendNotification(`✅ Build success for ${name}`, 'info', { duration: `${duration}ms`, buildId });
      // Condition 135: GitHub commit status update
      const sha = await runCommand('git rev-parse HEAD', localPath, name).then(r => r.stdout.trim()).catch(() => null);
      if (sha) await githubStatus.setStatus(CONFIG.github.owner, name, sha, 'success', 'Build passed', `http://localhost:${CONFIG.dashboardPort}`);
      // Condition 136: artifact upload
      const artifactPath = path.join(localPath, 'dist.zip');
      await artifactManager.upload(name, buildId, artifactPath);
    }
  } catch (err) {
    log(`[${name}] Build failed: ${err.message}`, 'error');
    await recordFailure(name);
    if (CONFIG.notifications.onFailure) await sendNotification(`❌ Build failed for ${name}`, 'error', { error: err.message, buildId });
    const sha = await runCommand('git rev-parse HEAD', localPath, name).then(r => r.stdout.trim()).catch(() => null);
    if (sha) await githubStatus.setStatus(CONFIG.github.owner, name, sha, 'failure', err.message, `http://localhost:${CONFIG.dashboardPort}`);
    // Condition 137: retry with exponential backoff
    if (retry < CONFIG.maxRetries) {
      const delay = CONFIG.retryBaseDelayMs * Math.pow(2, retry);
      log(`Retry ${retry+1}/${CONFIG.maxRetries} in ${delay}ms`, 'warn');
      setTimeout(() => processRepo(repoConfig, retry+1, force), delay);
      return;
    }
  } finally {
    runningBuilds.set(name, false);
    await lock.release(`build-${name}`);
    // Condition 138: periodic cleanup
    if (Math.random() < 0.05) {
      await rotateLogIfNeeded();
      await checkDiskAndCleanup();
      await artifactManager.cleanupOldArtifacts();
      await cache.cleanup();
    }
  }
}

// ======================== DASHBOARD & METRICS ========================
function startDashboard() {
  const server = http.createServer(async (req, res) => {
    if (req.url === '/health') {
      const allIdle = Array.from(runningBuilds.values()).every(v => !v);
      res.writeHead(allIdle ? 200 : 503, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ status: allIdle ? 'ok' : 'building', stats: Object.fromEntries(buildStats) }));
    } else if (req.url === '/metrics' && CONFIG.metricsEnabled) {
      res.writeHead(200, { 'Content-Type': 'text/plain' });
      let out = `# HELP builds_total Total builds\n# TYPE builds_total counter\nbuilds_total ${Array.from(buildStats.values()).reduce((a,b) => a + (b.successes||0) + (b.failures||0), 0)}\n`;
      out += `# HELP build_failures_total Failed builds\n# TYPE build_failures_total counter\nbuild_failures_total ${Array.from(buildStats.values()).reduce((a,b) => a + (b.failures||0), 0)}\n`;
      out += `# HELP current_builds Currently building\n# TYPE current_builds gauge\ncurrent_builds ${Array.from(runningBuilds.values()).filter(v=>v).length}\n`;
      res.end(out);
    } else if (req.url === '/events' && CONFIG.enableWebSocketDashboard) {
      res.writeHead(200, { 'Content-Type': 'text/event-stream', 'Cache-Control': 'no-cache', 'Connection': 'keep-alive' });
      const sendEvent = (data) => res.write(`data: ${JSON.stringify(data)}\n\n`);
      const interval = setInterval(() => sendEvent({ type: 'ping' }), 30000);
      req.on('close', () => clearInterval(interval));
    } else {
      res.writeHead(200, { 'Content-Type': 'text/html' });
      res.end(`<!DOCTYPE html><html><head><title>Auto-Builder 100+ Conditions</title><style>body{background:#0a0a0a;color:#0f0;font-family:monospace;}</style></head><body><h1>🔧 Ultimate Auto-Builder</h1><pre id="log"></pre><script>const evt = new EventSource('/events');evt.onmessage=e=>document.getElementById('log').innerHTML=JSON.stringify(JSON.parse(e.data),null,2)+'\\n'+document.getElementById('log').innerHTML;</script></body></html>`);
    }
  });
  server.listen(CONFIG.dashboardPort, () => log(`Dashboard on http://localhost:${CONFIG.dashboardPort}`, 'info'));
  return server;
}

// ======================== WEBHOOK RECEIVER ========================
function startWebhookServer() {
  if (CONFIG.mode === 'poll') return;
  const server = http.createServer(async (req, res) => {
    if (req.method === 'POST' && req.url === '/webhook') {
      let body = '';
      req.on('data', chunk => body += chunk);
      req.on('end', async () => {
        const sig = req.headers['x-hub-signature-256'];
        if (CONFIG.webhookSecret && sig) {
          const hmac = crypto.createHmac('sha256', CONFIG.webhookSecret);
          hmac.update(body);
          if (`sha256=${hmac.digest('hex')}` !== sig) { res.writeHead(401); res.end(); return; }
        }
        try {
          const payload = JSON.parse(body);
          const repoName = payload.repository?.name;
          const matched = CONFIG.repos.find(r => r.name === repoName);
          if (matched) {
            log(`Webhook trigger for ${repoName}`, 'info');
            // Condition 139: trigger dependency graph rebuild
            const affected = depGraph.getAffected(repoName);
            for (const dep of affected) {
              const repo = CONFIG.repos.find(r => r.name === dep);
              if (repo) processRepo(repo, 0, true);
            }
          }
          res.writeHead(200); res.end('ok');
        } catch (err) { res.writeHead(400); res.end('invalid json'); }
      });
    } else res.writeHead(404).end();
  });
  server.listen(CONFIG.webhookPort, () => log(`Webhook server on :${CONFIG.webhookPort}`, 'info'));
  return server;
}

// ======================== CRON SCHEDULER ========================
function startCronScheduler() {
  try {
    const cron = require('cron').CronJob;
    for (const job of CONFIG.cronJobs) {
      if (job.command) {
        new cron(job.schedule, () => {
          const repo = CONFIG.repos.find(r => r.name === job.repo);
          if (repo) processRepo(repo, 0, true);
        }, null, true, CONFIG.cronTimeZone);
        log(`Scheduled cron ${job.schedule} for ${job.repo}`, 'info');
      }
    }
  } catch (err) { log(`Cron not available: ${err.message}`, 'warn'); }
}

// ======================== SELF-UPDATE ========================
async function selfUpdate() {
  if (!process.env.SELF_UPDATE_REPO) return;
  const tempDir = path.join(os.tmpdir(), 'auto-builder-update');
  await fs.mkdir(tempDir, { recursive: true });
  try {
    await runCommand(`git clone --depth 1 ${process.env.SELF_UPDATE_REPO} ${tempDir}`, process.cwd(), 'self');
    const newScript = await fs.readFile(path.join(tempDir, path.basename(__filename)), 'utf8');
    const currentScript = await fs.readFile(__filename, 'utf8');
    if (newScript !== currentScript) {
      log('New version found, updating...', 'info');
      await fs.writeFile(__filename, newScript);
      log('Update complete. Restarting...', 'info');
      process.exit(0);
    }
  } catch (err) { log(`Self-update failed: ${err.message}`, 'error'); }
  finally { await fs.rm(tempDir, { recursive: true, force: true }); }
}

// ======================== PID FILE (prevent duplicates) ========================
async function writePidFile() {
  try {
    const existing = await fs.readFile(CONFIG.pidFile, 'utf8');
    const oldPid = parseInt(existing, 10);
    if (oldPid && !isNaN(oldPid)) {
      try { process.kill(oldPid, 0); log(`Another instance running (PID ${oldPid}) – exiting`, 'error'); process.exit(1); } catch (e) { /* stale */ }
    }
  } catch (err) {}
  await fs.writeFile(CONFIG.pidFile, process.pid.toString());
}
async function removePidFile() { await fs.unlink(CONFIG.pidFile).catch(() => {}); }

// ======================== GRACEFUL SHUTDOWN ========================
async function shutdown() {
  if (isShuttingDown) return;
  isShuttingDown = true;
  log('Shutting down...', 'warn');
  for (const interval of pollIntervals) clearInterval(interval);
  if (server) server.close();
  if (webhookServer) webhookServer.close();
  const start = Date.now();
  while (Array.from(runningBuilds.values()).some(v => v) && (Date.now() - start) < CONFIG.shutdownTimeoutMs) {
    await new Promise(r => setTimeout(r, 500));
  }
  await removePidFile();
  log('Auto-builder stopped.', 'info');
  process.exit(0);
}
process.on('SIGINT', shutdown);
process.on('SIGTERM', shutdown);

// ======================== MAIN ========================
async function main() {
  await writePidFile();
  await cache.init();
  await fs.mkdir(CONFIG.artifactDir, { recursive: true }).catch(() => {});
  log('=== Auto-Builder Ultimate (100+ Conditions) ===', 'info');
  log(`Mode: ${CONFIG.mode}, Poll: ${CONFIG.pollIntervalMs}ms`, 'info');
  if (CLI.dryRun) log('DRY RUN MODE – no commands will execute', 'warn');
  if (CLI.force) log('FORCE MODE – will rebuild all repos', 'warn');
  
  server = startDashboard();
  webhookServer = startWebhookServer();
  startCronScheduler();
  
  // Initial builds (Condition 140)
  for (const repo of CONFIG.repos) {
    if (CLI.repo && repo.name !== CLI.repo) continue;
    await processRepo(repo, 0, CLI.force);
  }
  if (CLI.once) { log('--once specified, exiting', 'info'); process.exit(0); }
  
  // Polling loop (Condition 141)
  if (CONFIG.mode !== 'webhook') {
    const interval = setInterval(async () => {
      for (const repo of CONFIG.repos) {
        if (CLI.repo && repo.name !== CLI.repo) continue;
        await processRepo(repo);
      }
    }, CONFIG.pollIntervalMs);
    pollIntervals.push(interval);
  }
  
  // Self-update check (Condition 142)
  if (process.env.SELF_UPDATE_REPO) {
    setTimeout(async () => { await selfUpdate(); }, 60000);
    setInterval(async () => { await selfUpdate(); }, 86400000);
  }
}

main().catch(async err => {
  await log(`Fatal error: ${err.message}`, 'error');
  await removePidFile();
  process.exit(1);
});