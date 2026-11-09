'use strict';

const fs = require('node:fs');
const path = require('node:path');

const repoRoot = path.resolve(__dirname, '..');
const sourceExtensions = new Set(['.js', '.jsx', '.ts', '.tsx', '.mjs', '.cjs']);
const resolveExtensions = [
  '', '.js', '.jsx', '.ts', '.tsx', '.mjs', '.cjs',
  '.json', '.css', '.scss', '.sass', '.less',
  '.svg', '.png', '.jpg', '.jpeg', '.gif', '.webp',
];
const ignoredDirectories = new Set([
  '.git', 'node_modules', 'dist', 'build', 'coverage',
  '.next', '.turbo', '.venv', 'venv', '__pycache__',
]);

function walk(directory) {
  return fs.readdirSync(directory, { withFileTypes: true }).flatMap((entry) => {
    if (entry.isDirectory() && ignoredDirectories.has(entry.name)) return [];
    const absolute = path.join(directory, entry.name);
    if (entry.isDirectory()) return walk(absolute);
    return sourceExtensions.has(path.extname(entry.name)) ? [absolute] : [];
  });
}

function exactCandidates(base) {
  const candidates = resolveExtensions.map((extension) => base + extension);
  for (const extension of resolveExtensions.slice(1)) {
    candidates.push(path.join(base, 'index' + extension));
  }
  return candidates;
}

function findCaseInsensitivePath(base) {
  const relative = path.relative(repoRoot, base);
  const parts = relative.split(path.sep).filter(Boolean);
  let current = repoRoot;

  for (const part of parts) {
    if (!fs.existsSync(current) || !fs.statSync(current).isDirectory()) return null;
    const entries = fs.readdirSync(current);
    const match = entries.find((entry) => entry.toLowerCase() === part.toLowerCase());
    if (!match) return null;
    current = path.join(current, match);
  }
  return current;
}

function resolveImport(base) {
  const candidates = exactCandidates(base);
  const exact = candidates.find((candidate) => fs.existsSync(candidate));
  if (exact) return { exact };

  for (const candidate of candidates) {
    const insensitive = findCaseInsensitivePath(candidate);
    if (insensitive) return { insensitive };
  }
  return {};
}

if (!fs.existsSync(repoRoot)) {
  console.error('FAIL: repository root not found:', repoRoot);
  process.exit(1);
}

// Validate only the maintained website runtime. Experimental/legacy backend
// trees are not part of the GitHub Pages build and have separate dependency
// and entry-point requirements; scanning them here produced misleading
// repository-wide failures unrelated to the deployed frontend.
const websiteScriptFiles = [
  'scripts/build-static.js',
  'scripts/npm-build-check.js',
  'scripts/serve-static.js',
  'scripts/verify-cloudflare-deploy.js',
].map((relative) => path.join(repoRoot, relative));

const filesToCheck = [
  ...walk(path.join(repoRoot, 'js')),
  ...websiteScriptFiles.filter((file) => fs.existsSync(file)),
];

const errors = [];
let importsChecked = 0;
const importPattern = /(?:\bfrom\s*|\bimport\s*\(?\s*|\brequire\s*\(\s*)['"]([^'"]+)['"]/g;

for (const file of filesToCheck) {
  const source = fs.readFileSync(file, 'utf8');
  let match;

  while ((match = importPattern.exec(source)) !== null) {
    const specifier = match[1];
    if (!specifier.startsWith('.')) continue;

    importsChecked += 1;
    const base = path.resolve(path.dirname(file), specifier);
    const result = resolveImport(base);
    const relativeFile = path.relative(repoRoot, file);

    if (result.exact) continue;
    if (result.insensitive) {
      errors.push(
        `CASE MISMATCH: ${relativeFile}: "${specifier}" should match "${path.relative(path.dirname(file), result.insensitive)}"`,
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

console.log(`PASS: ${importsChecked} relative imports across the maintained website runtime resolve with exact case.`);
