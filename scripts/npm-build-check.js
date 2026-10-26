
'use strict';

const fs = require('node:fs');
const path = require('node:path');

const requiredFiles = ['Main.py', 'main.py'];

const missing = requiredFiles.filter((file) => {
  return !fs.existsSync(path.resolve(process.cwd(), file));
});

if (missing.length > 0) {
  console.error('Missing Tamanna AI entry files:', missing.join(', '));
  process.exit(1);
}

console.log('PASS: Tamanna AI entry-point files verified.');
