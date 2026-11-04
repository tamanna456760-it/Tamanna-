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

  const insensitive = findCaseInsensitivePath(base);
  if (insensitive) return { insensitive };

  const parent = findCaseInsensitivePath(path.dirname(base));
  if (parent && fs.statSync(parent).isDirectory()) {
    const wanted = path.basename(base).toLowerCase();
    const match = fs.readdirSync(parent).find((entry) => {
      const candidate = path.join(parent, entry);
      return entry.toLowerCase() === wanted
        && (fs.statSync(candidate).isFile() || fs.statSync(candidate).isDirectory());
    });
    if (match) return { insensitive: path.join(parent, match) };
  }
  return {};
}

if (!fs.existsSync(repoRoot)) {
  console.error('FAIL: repository root not found:', repoRoot);
  process.exit(1);
}

const errors = [];
let importsChecked = 0;
const importPattern = /(?:\bfrom\s*|\bimport\s*\(?\s*|\brequire\s*\(\s*)['"]([^'"]+)['"]/g;

for (const file of walk(repoRoot)) {
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

console.log(`PASS: ${importsChecked} relative imports across the repository resolve with exact case.`);
