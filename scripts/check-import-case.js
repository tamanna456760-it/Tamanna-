'use strict';

const fs = require('node:fs');
const path = require('node:path');

const sourceRoot = path.resolve(
  __dirname,
  '..',
  'bd-king-r7',
  'website',
  'frontend',
  'src',
);
const sourceExtensions = new Set(['.js', '.jsx', '.ts', '.tsx', '.mjs', '.cjs']);
const resolveExtensions = ['', '.js', '.jsx', '.ts', '.tsx', '.mjs', '.cjs', '.css', '.json'];

function walk(directory) {
  return fs.readdirSync(directory, { withFileTypes: true }).flatMap((entry) => {
    const absolute = path.join(directory, entry.name);
    if (entry.isDirectory()) return walk(absolute);
    return sourceExtensions.has(path.extname(entry.name)) ? [absolute] : [];
  });
}

function candidatePaths(base) {
  return resolveExtensions.map((extension) => base + extension);
}

function findCaseInsensitivePath(base) {
  const parent = path.dirname(base);
  const wanted = path.basename(base).toLowerCase();
  if (!fs.existsSync(parent) || !fs.statSync(parent).isDirectory()) return null;
  const match = fs.readdirSync(parent).find((name) => name.toLowerCase() === wanted);
  return match ? path.join(parent, match) : null;
}

if (!fs.existsSync(path.join(sourceRoot, 'main.jsx'))) {
  console.error('FAIL: frontend source entry not found:', sourceRoot);
  process.exit(1);
}

const errors = [];
let importsChecked = 0;

for (const file of walk(sourceRoot)) {
  const source = fs.readFileSync(file, 'utf8');
  const expression = /(?:\bfrom\s*|\bimport\s*)['"]([^'"]+)['"]/g;
  let match;

  while ((match = expression.exec(source)) !== null) {
    const specifier = match[1];
    if (!specifier.startsWith('.')) continue;

    importsChecked += 1;
    const base = path.resolve(path.dirname(file), specifier);
    const candidates = candidatePaths(base);
    if (candidates.some((candidate) => fs.existsSync(candidate))) continue;

    const insensitiveMatch = findCaseInsensitivePath(base);
    const relativeFile = path.relative(sourceRoot, file);
    if (insensitiveMatch) {
      errors.push(
        `CASE MISMATCH: ${relativeFile}: "${specifier}" should match "${path.relative(path.dirname(file), insensitiveMatch)}"`,
      );
    } else {
      errors.push(`MISSING IMPORT: ${relativeFile}: "${specifier}" does not resolve`);
    }
  }
}

if (errors.length) {
  console.error(errors.join('\n'));
  console.error(`FAIL: ${errors.length} import path issue(s) across ${importsChecked} relative imports.`);
  process.exit(1);
}

console.log(`PASS: ${importsChecked} relative imports resolve with exact case.`);
