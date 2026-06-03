#!/usr/bin/env node

// =========================== IMPORTS ===========================
const { spawn, execSync } = require('child_process');
const fs = require('fs').promises;
const path = require('path');
const http = require('http');
const https = require('https');
const crypto = require('crypto');
const os = require('os');
const yaml = require('js-yaml');  // npm install js-yaml

// ======================== CLI ARGUMENTS =========================
const args = process.argv.slice(2);
const CLI = {
  once: args.includes('--once'),
  dryRun: args.includes('--dry-run'),
  repo: args.find((_,i) => args[i-1] === '--repo'),
  verbose: args.includes('--verbose'),
  poll: parseInt(args.find((_,i) => args[i-1] === '--poll') || '0'),
  force: args.includes('--force'),
  workflow: args.find((_,i) => args[i-1] === '--workflow'), // specific workflow file
  event: args.find((_,i) => args[i-1] === '--event') || 'push'
};

// ======================== CONFIGURATION =========================
const CONFIG = {
  mode: process.env.MODE || 'hybrid',
  pollIntervalMs: CLI.poll || parseInt(process.env.POLL_INTERVAL_MS) || 60000, // 60 sec default
  webhookPort: parseInt(process.env.WEBHOOK_PORT) || 9000,
  webhookSecret: process.env.WEBHOOK_SECRET || 'change-me',
  maxRetries: parseInt(process.env.MAX_RETRIES) || 2,
  commandTimeoutMs: parseInt(process.env.COMMAND_TIMEOUT_MS) || 600000,
  maxConcurrentCommands: parseInt(process.env.MAX_CONCURRENT) || 4,
  parallelRepos: process.env.PARALLEL_REPOS !== 'false',
  cacheDir: process.env.CACHE_DIR || './build-cache',
  logFile: process.env.LOG_FILE || 'auto-builder-workflow.log',
  logLevel: CLI.verbose ? 'debug' : (process.env.LOG_LEVEL || 'info'),
  dashboardPort: parseInt(process.env.DASHBOARD_PORT) || 8080,
  prometheusPort: parseInt(process.env.PROMETHEUS_PORT) || 9090,
  github: {
    token: process.env.GH_TOKEN || '',
    setCommitStatus: process.env.GH_SET_STATUS !== 'false',
    owner: process.env.GH_OWNER || 'Tamanna456760-it'
  },
  notifications: {
    slack: process.env.SLACK_WEBHOOK || '',
    discord: process.env.DISCORD_WEBHOOK || ''
  },
  // Repositories to watch – now auto-detects workflows
  repos: (() => {
    // Parse from env or default list
    const repoList = process.env.REPOS ? JSON.parse(process.env.REPOS) : [
      {
        name: 'my-app',
        repoUrl: 'https://github.com/Tamanna456760-it/my-app.git',
        branches: ['main'],
        localPath: './repos/my-app',
        autoDetectWorkflow: true,   // NEW: parse .github/workflows/*.yml
        workflowFile: null,         // if null, use first found; else specific
        alwaysSync: true,           // always git pull before building
        commands: []                // optional fallback if no workflow found
      }
    ];
    return repoList;
  })(),
  runner: {
    os: 'ubuntu-latest',          // emulate GitHub runner OS
    arch: 'x64',
    cache: {
      enabled: true,
      path: './runner-cache'
    },
    actions: {
      checkout: 'actions/checkout@v3',   // custom action support (simplified)
      setupNode: 'actions/setup-node@v3',
      setupPython: 'actions/setup-python@v4'
    }
  }
};

// ======================== GLOBAL STATE =========================
let runningBuilds = new Map();
let activeCommands = 0;
let isShuttingDown = false;
let pollIntervals = [];
let buildStats = new Map();
let server = null;
let webhookServer = null;

// ======================== UTILITIES ========================
const logLevels = { debug: 0, info: 1, warn: 2, error: 3 };
let currentLogLevel = logLevels[CONFIG.logLevel] ?? 1;

async function log(msg, level = 'info', ...args) {
  if (logLevels[level] < currentLogLevel) return;
  const timestamp = new Date().toISOString();
  const line = `[${timestamp}] [${level.toUpperCase()}] ${msg} ${args.join(' ')}`;
  console.log(line);
  await fs.appendFile(CONFIG.logFile, line + '\n').catch(() => {});
}

async function runCommand(cmd, cwd, repoName, env = {}) {
  while (activeCommands >= CONFIG.maxConcurrentCommands) {
    await new Promise(r => setTimeout(r, 100));
  }
  activeCommands++;
  const fullEnv = { ...process.env, ...env };
  try {
    if (CLI.dryRun) {
      log(`[DRY RUN] ${cmd}`, 'info');
      return { stdout: '', stderr: '' };
    }
    log(`[${repoName}] Exec: ${cmd}`, 'debug');
    const child = spawn(cmd, { shell: true, cwd, env: fullEnv, stdio: 'pipe' });
    let stdout = '', stderr = '';
    const timer = setTimeout(() => {
      child.kill('SIGTERM');
      setTimeout(() => child.kill('SIGKILL'), 5000);
    }, CONFIG.commandTimeoutMs);
    for await (const chunk of child.stdout) stdout += chunk;
    for await (const chunk of child.stderr) stderr += chunk;
    clearTimeout(timer);
    const code = await new Promise(resolve => child.on('close', resolve));
    if (code !== 0) throw new Error(`Exit ${code}: ${stderr}`);
    return { stdout, stderr };
  } finally {
    activeCommands--;
  }
}

// ======================== GITHUB ACTIONS WORKFLOW PARSER ========================
class WorkflowParser {
  constructor(workflowYaml, repoPath, eventName = 'push') {
    this.workflow = yaml.load(workflowYaml);
    this.repoPath = repoPath;
    this.eventName = eventName;
    this.jobs = this.workflow.jobs || {};
  }

  // Check if workflow should run based on 'on' trigger
  shouldRun() {
    const on = this.workflow.on;
    if (!on) return true;
    if (typeof on === 'string') return on === this.eventName;
    if (on[this.eventName]) return true;
    // handle branches, paths, etc. (simplified)
    if (on.push && on.push.branches) {
      // would check current branch
      return true;
    }
    return false;
  }

  // Extract steps from a job
  async getSteps(jobId) {
    const job = this.jobs[jobId];
    if (!job) return [];
    const steps = job.steps || [];
    const commands = [];
    for (const step of steps) {
      if (step.run) {
        // Direct shell command
        commands.push({ cmd: step.run, name: step.name, env: step.env || {} });
      } else if (step.uses) {
        // GitHub Action – we map to local equivalents
        const action = step.uses;
        const withParams = step.with || {};
        const mapped = await this.mapActionToCommand(action, withParams);
        if (mapped) commands.push(mapped);
      }
    }
    return commands;
  }

  // Map common GitHub Actions to shell commands
  async mapActionToCommand(action, withParams) {
    // actions/checkout
    if (action === 'actions/checkout@v3' || action === 'actions/checkout@v2') {
      return { cmd: 'git pull origin HEAD', name: 'checkout' };
    }
    // actions/setup-node
    if (action.includes('setup-node')) {
      const nodeVersion = withParams['node-version'] || '18';
      return { cmd: `nvm install ${nodeVersion} && nvm use ${nodeVersion}`, name: 'setup-node' };
    }
    // actions/setup-python
    if (action.includes('setup-python')) {
      const pyVersion = withParams['python-version'] || '3.11';
      return { cmd: `pyenv install ${pyVersion} -s && pyenv local ${pyVersion}`, name: 'setup-python' };
    }
    // actions/cache
    if (action.includes('cache')) {
      const path = withParams.path;
      const key = withParams.key;
      if (path && key) {
        return { cmd: `echo "Cache would be restored from ${key}"`, name: 'cache-restore' };
      }
    }
    // Unsupported action – log warning
    log(`Unsupported action: ${action}`, 'warn');
    return null;
  }

  // Get all jobs that should run (order by needs)
  getJobOrder() {
    const jobNames = Object.keys(this.jobs);
    const graph = {};
    for (const job of jobNames) {
      graph[job] = this.jobs[job].needs || [];
    }
    // topological sort
    const visited = new Set();
    const order = [];
    const visit = (job) => {
      if (visited.has(job)) return;
      visited.add(job);
      for (const dep of graph[job]) visit(dep);
      order.push(job);
    };
    for (const job of jobNames) visit(job);
    return order;
  }

  // Main method: run entire workflow
  async run(repoPath, repoName, eventPayload = {}) {
    if (!this.shouldRun()) {
      log(`Workflow ${this.workflow.name} skipped due to trigger conditions`, 'debug');
      return false;
    }
    const jobOrder = this.getJobOrder();
    const results = {};
    for (const jobId of jobOrder) {
      log(`[${repoName}] Running job: ${jobId}`, 'info');
      const steps = await this.getSteps(jobId);
      for (const step of steps) {
        const env = { ...step.env, ...(this.workflow.env || {}) };
        await runCommand(step.cmd, repoPath, repoName, env);
      }
      results[jobId] = 'success';
    }
    return true;
  }
}

// ======================== REPO MANAGEMENT WITH WORKFLOW DETECTION ========================
async function ensureRepo(repoConfig) {
  const { repoUrl, localPath, name, branches } = repoConfig;
  let url = repoUrl;
  if (CONFIG.github.token && url.includes('github.com')) {
    url = url.replace('https://', `https://${CONFIG.github.token}@`);
  }
  try {
    await fs.access(localPath);
    log(`[${name}] Repo exists`, 'debug');
    // Pull latest (sync all files)
    await runCommand(`git fetch origin`, localPath, name);
    await runCommand(`git reset --hard origin/${branches[0]}`, localPath, name);
    await runCommand(`git clean -fdx`, localPath, name); // clean untracked
  } catch {
    log(`[${name}] Cloning ${repoUrl}`, 'info');
    await runCommand(`git clone --branch ${branches[0]} ${url} ${localPath}`, process.cwd(), name);
  }
  // Also fetch other branches
  for (const branch of branches.slice(1)) {
    await runCommand(`git fetch origin ${branch}:${branch}`, localPath, name).catch(() => {});
  }
}

async function findWorkflowFile(repoPath, repoConfig) {
  const workflowDir = path.join(repoPath, '.github', 'workflows');
  try {
    const files = await fs.readdir(workflowDir);
    const ymlFiles = files.filter(f => f.endsWith('.yml') || f.endsWith('.yaml'));
    if (repoConfig.workflowFile) {
      const specific = ymlFiles.find(f => f === repoConfig.workflowFile);
      if (specific) return path.join(workflowDir, specific);
    }
    if (ymlFiles.length) return path.join(workflowDir, ymlFiles[0]);
  } catch (err) {
    log(`No workflow folder found in ${repoPath}`, 'debug');
  }
  return null;
}

async function runWorkflowForRepo(repoConfig, eventName = 'push', force = false) {
  const { name, localPath, alwaysSync, autoDetectWorkflow, commands: fallbackCommands } = repoConfig;
  if (runningBuilds.get(name)) {
    log(`[${name}] Already building`, 'debug');
    return;
  }
  runningBuilds.set(name, true);
  const startTime = Date.now();
  try {
    await ensureRepo(repoConfig);
    let executed = false;
    if (autoDetectWorkflow) {
      const workflowPath = await findWorkflowFile(localPath, repoConfig);
      if (workflowPath) {
        const workflowContent = await fs.readFile(workflowPath, 'utf8');
        const parser = new WorkflowParser(workflowContent, localPath, eventName);
        executed = await parser.run(localPath, name, {});
      } else {
        log(`[${name}] No workflow file found, using fallback commands`, 'warn');
      }
    }
    if (!executed && fallbackCommands.length) {
      for (const cmd of fallbackCommands) {
        await runCommand(cmd, localPath, name);
      }
      executed = true;
    }
    if (executed) {
      const duration = Date.now() - startTime;
      log(`[${name}] Build completed in ${duration}ms`, 'info');
      // Update GitHub commit status
      if (CONFIG.github.setCommitStatus && CONFIG.github.token) {
        const sha = (await runCommand('git rev-parse HEAD', localPath, name)).stdout.trim();
        // POST status to GitHub API (simplified)
        const url = `https://api.github.com/repos/${CONFIG.github.owner}/${name}/statuses/${sha}`;
        const data = JSON.stringify({ state: 'success', context: 'auto-builder-workflow' });
        await httpRequest(url, { method: 'POST', headers: { Authorization: `token ${CONFIG.github.token}` } }, data).catch(() => {});
      }
    }
  } catch (err) {
    log(`[${name}] Workflow failed: ${err.message}`, 'error');
  } finally {
    runningBuilds.set(name, false);
  }
}

// ======================== WEBHOOK & POLLING ========================
async function httpRequest(url, options, data) {
  const client = url.startsWith('https') ? https : http;
  return new Promise((resolve, reject) => {
    const req = client.request(url, options, (res) => {
      let body = '';
      res.on('data', chunk => body += chunk);
      res.on('end', () => resolve(body));
    });
    req.on('error', reject);
    if (data) req.write(data);
    req.end();
  });
}

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
          if (`sha256=${hmac.digest('hex')}` !== sig) {
            res.writeHead(401); res.end(); return;
          }
        }
        try {
          const payload = JSON.parse(body);
          const repoName = payload.repository?.name;
          const matched = CONFIG.repos.find(r => r.name === repoName);
          if (matched) {
            log(`Webhook trigger for ${repoName}`, 'info');
            await runWorkflowForRepo(matched, 'push', true);
          }
          res.writeHead(200); res.end('ok');
        } catch (err) { res.writeHead(400); res.end('invalid'); }
      });
    } else res.writeHead(404).end();
  });
  server.listen(CONFIG.webhookPort, () => log(`Webhook server on :${CONFIG.webhookPort}`, 'info'));
  return server;
}

function startDashboard() {
  const srv = http.createServer((req, res) => {
    if (req.url === '/health') {
      const idle = Array.from(runningBuilds.values()).every(v => !v);
      res.writeHead(idle ? 200 : 503);
      res.end(JSON.stringify({ status: idle ? 'ok' : 'building' }));
    } else if (req.url === '/metrics') {
      res.writeHead(200, { 'Content-Type': 'text/plain' });
      let out = `builds_total ${Array.from(buildStats.values()).reduce((a,b)=>a+(b.count||0),0)}\n`;
      res.end(out);
    } else {
      res.writeHead(200, { 'Content-Type': 'text/html' });
      res.end(`<html><body><h1>Auto-Builder Workflow</h1><pre>${JSON.stringify(buildStats, null, 2)}</pre></body></html>`);
    }
  });
  srv.listen(CONFIG.dashboardPort, () => log(`Dashboard on :${CONFIG.dashboardPort}`, 'info'));
  return srv;
}

// ======================== MAIN ========================
async function main() {
  log('=== GitHub Actions Workflow Auto-Builder ===', 'info');
  log('Watches repos, reads .github/workflows/*.yml, executes steps', 'info');
  startDashboard();
  startWebhookServer();

  // Initial run
  for (const repo of CONFIG.repos) {
    if (CLI.repo && repo.name !== CLI.repo) continue;
    await runWorkflowForRepo(repo, 'push', CLI.force);
  }
  if (CLI.once) process.exit(0);

  // Polling
  if (CONFIG.mode !== 'webhook') {
    const interval = setInterval(async () => {
      for (const repo of CONFIG.repos) {
        await runWorkflowForRepo(repo, 'push', false);
      }
    }, CONFIG.pollIntervalMs);
    pollIntervals.push(interval);
  }

  // Graceful shutdown
  process.on('SIGINT', async () => {
    log('Shutting down...', 'warn');
    for (const i of pollIntervals) clearInterval(i);
    if (server) server.close();
    if (webhookServer) webhookServer.close();
    setTimeout(() => process.exit(0), 1000);
  });
}

main().catch(console.error);