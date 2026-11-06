'use strict';

const fs = require('node:fs');
const path = require('node:path');

const root = path.resolve(__dirname, '..');
const dist = path.join(root, 'dist');
const configPath = path.join(root, 'wrangler.jsonc');
const MAX_ASSET_BYTES = 25 * 1024 * 1024;
const requiredFiles = [
  'index.html',
  '404.html',
  'CNAME',
  '.nojekyll',
  'css/style.css',
  'js/auth.js',
  'js/chat.js',
  'js/settings.js',
];

function fail(message) {
  console.error(`CLOUDFLARE PREFLIGHT FAILED: ${message}`);
  process.exit(1);
}

function walk(directory, prefix = '') {
  const files = [];
  for (const entry of fs.readdirSync(directory, { withFileTypes: true })) {
    const relative = prefix ? path.posix.join(prefix, entry.name) : entry.name;
    const absolute = path.join(directory, entry.name);
    if (entry.isSymbolicLink()) {
      fail(`Symlinks are not allowed in static assets: dist/${relative}`);
    }
    if (entry.isDirectory()) {
      files.push(...walk(absolute, relative));
    } else if (entry.isFile()) {
      files.push({ relative, absolute, size: fs.statSync(absolute).size });
    }
  }
  return files;
}

function main() {
  if (!fs.existsSync(configPath)) fail('wrangler.jsonc is missing.');
  let config;
  try {
    config = JSON.parse(fs.readFileSync(configPath, 'utf8'));
  } catch (error) {
    fail(`wrangler.jsonc must contain valid JSON: ${error.message}`);
  }

  if (config.name !== 'titamanna') fail('Unexpected Cloudflare Worker name.');
  if (!config.assets || config.assets.directory !== './dist') {
    fail('Wrangler assets.directory must be exactly ./dist; never upload repository root.');
  }
  if (!fs.existsSync(dist) || !fs.statSync(dist).isDirectory()) {
    fail('dist/ does not exist. Run npm run build first.');
  }

  for (const relative of requiredFiles) {
    if (!fs.existsSync(path.join(dist, relative))) {
      fail(`Required built website file is missing: dist/${relative}`);
    }
  }

  const hostname = fs.readFileSync(path.join(dist, 'CNAME'), 'utf8').trim();
  if (hostname !== 'www.bd-king-r7.com') {
    fail('dist/CNAME must contain exactly www.bd-king-r7.com.');
  }

  const files = walk(dist);
  if (files.length === 0) fail('dist/ is empty.');

  const oversized = files.filter((file) => file.size > MAX_ASSET_BYTES);
  if (oversized.length) {
    for (const file of oversized) {
      console.error(`TOO LARGE: dist/${file.relative} (${(file.size / 1024 / 1024).toFixed(2)} MiB)`);
    }
    fail('Cloudflare static assets must each be no larger than 25 MiB.');
  }

  const forbidden = files.filter((file) =>
    /(^|\/)(tamanna_security|threat_intel|reports)(\/|$)/i.test(file.relative) ||
    /security_report\.json$/i.test(file.relative)
  );
  if (forbidden.length) {
    for (const file of forbidden) console.error(`PRIVATE/GENERATED FILE IN DIST: ${file.relative}`);
    fail('Security reports and threat-intelligence data must not be published as website assets.');
  }

  const totalBytes = files.reduce((sum, file) => sum + file.size, 0);
  console.log('PASS: Wrangler config targets ./dist (not repository root).');
  console.log('PASS: Required website files and custom domain are present.');
  console.log(`PASS: ${files.length} static files checked; no file exceeds 25 MiB.`);
  console.log('PASS: No security/threat-intelligence reports found in deployment assets.');
  console.log(`Deployment payload: ${(totalBytes / 1024 / 1024).toFixed(2)} MiB`);
}

main();
