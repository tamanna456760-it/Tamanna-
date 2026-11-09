'use strict';

const fs = require('node:fs');
const path = require('node:path');

const root = path.resolve(__dirname, '..');
const output = path.join(root, 'dist');
const requiredFiles = [
  'index.html',
  'admin.html',
  'css/admin.css',
  'js/admin.js',
  'CNAME',
  'css/style.css',
  'js/auth.js',
  'js/chat.js',
  'js/settings.js',
];

function fail(message) {
  console.error(`BUILD FAILED: ${message}`);
  process.exit(1);
}

for (const relative of requiredFiles) {
  if (!fs.existsSync(path.join(root, relative))) {
    fail(`Required website file is missing: ${relative}`);
  }
}

const hostname = fs.readFileSync(path.join(root, 'CNAME'), 'utf8').trim();
if (hostname !== 'www.bd-king-r7.com') {
  fail('CNAME must contain exactly www.bd-king-r7.com');
}

const html = fs.readFileSync(path.join(root, 'index.html'), 'utf8');
for (const asset of ['css/style.css', 'js/auth.js', 'js/chat.js', 'js/settings.js']) {
  if (!html.includes(asset)) {
    fail(`index.html does not reference required asset: ${asset}`);
  }
}

const adminHtml = fs.readFileSync(path.join(root, 'admin.html'), 'utf8');
for (const asset of ['css/admin.css', 'js/admin.js']) {
  if (!adminHtml.includes(asset)) {
    fail(`admin.html does not reference required asset: ${asset}`);
  }
}

fs.rmSync(output, { recursive: true, force: true });
fs.mkdirSync(output, { recursive: true });
fs.mkdirSync(path.join(output, 'admin'), { recursive: true });

for (const file of ['index.html', 'admin.html', '404.html', 'CNAME']) {
  fs.copyFileSync(path.join(root, file), path.join(output, file));
}
// Cloudflare static assets can now resolve the clean /admin path.
fs.copyFileSync(path.join(root, 'admin.html'), path.join(output, 'admin', 'index.html'));

for (const directory of ['css', 'js', 'assets', 'static']) {
  const source = path.join(root, directory);
  if (fs.existsSync(source) && fs.statSync(source).isDirectory()) {
    fs.cpSync(source, path.join(output, directory), { recursive: true });
  }
}

// GitHub project Pages is hosted below /<repository>/, unlike a custom domain.
// Keep the normal root paths for Cloudflare, but prefix static paths for Pages.
const rawBasePath = (process.env.GITHUB_PAGES_BASE_PATH || '').trim();
const basePath = rawBasePath ? `/${rawBasePath.replace(/^\/+|\/+$/g, '')}` : '';
if (basePath && !/^\/[A-Za-z0-9._-]+$/.test(basePath)) {
  fail('GITHUB_PAGES_BASE_PATH must be one safe repository path segment, e.g. /Tamanna-.');
}
if (basePath) {
  const htmlFiles = ['index.html', 'admin.html', '404.html', 'admin/index.html'];
  const staticPrefixes = ['/css/', '/js/', '/assets/', '/static/', '/admin/'];
  for (const relative of htmlFiles) {
    const target = path.join(output, relative);
    if (!fs.existsSync(target)) continue;
    let page = fs.readFileSync(target, 'utf8');
    for (const prefix of staticPrefixes) {
      page = page.split(`="${prefix}`).join(`="${basePath}${prefix}`);
      page = page.split(`='${prefix}`).join(`='${basePath}${prefix}`);
    }
    page = page.split('="/admin.html').join(`="${basePath}/admin.html`);
    page = page.split('="/404.html').join(`="${basePath}/404.html`);
    fs.writeFileSync(target, page);
  }
  const manifestPath = path.join(output, 'assets', 'site.webmanifest');
  if (fs.existsSync(manifestPath)) {
    let manifest = fs.readFileSync(manifestPath, 'utf8');
    manifest = manifest.replace(/"start_url"\s*:\s*"\/"/, `"start_url": "${basePath}/"`);
    fs.writeFileSync(manifestPath, manifest);
  }
}

fs.writeFileSync(path.join(output, '.nojekyll'), '');
for (const relative of ['index.html', 'admin.html', 'admin/index.html', '404.html', 'CNAME', '.nojekyll', 'css/style.css', 'css/admin.css', 'js/chat.js', 'js/admin.js']) {
  if (!fs.existsSync(path.join(output, relative))) {
    fail(`Build output is incomplete: dist/${relative}`);
  }
}

console.log('PASS: Static website build completed.');
console.log('Output: dist/');
console.log(`Domain: ${hostname}`);
