'use strict';

const fs = require('node:fs');
const path = require('node:path');

const root = path.resolve(__dirname, '..');
const output = path.join(root, 'dist');
const requiredFiles = [
  'index.html',
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

fs.rmSync(output, { recursive: true, force: true });
fs.mkdirSync(output, { recursive: true });

for (const file of ['index.html', 'CNAME']) {
  fs.copyFileSync(path.join(root, file), path.join(output, file));
}

for (const directory of ['css', 'js', 'assets', 'static']) {
  const source = path.join(root, directory);
  if (fs.existsSync(source) && fs.statSync(source).isDirectory()) {
    fs.cpSync(source, path.join(output, directory), { recursive: true });
  }
}

fs.writeFileSync(path.join(output, '.nojekyll'), '');
for (const relative of ['index.html', 'CNAME', '.nojekyll', 'css/style.css', 'js/chat.js']) {
  if (!fs.existsSync(path.join(output, relative))) {
    fail(`Build output is incomplete: dist/${relative}`);
  }
}

console.log('PASS: Static website build completed.');
console.log('Output: dist/');
console.log(`Domain: ${hostname}`);
