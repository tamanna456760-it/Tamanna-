#!/usr/bin/env node

const fs = require("fs");
const path = require("path");

const WATCH_DIR = process.argv[2] || ".";

console.log("======================================");
console.log("👀 Tamanna File Watcher");
console.log("======================================");
console.log("Watching:", path.resolve(WATCH_DIR));
console.log("Press Ctrl+C to stop.\n");

const known = new Map();

function scan(dir) {
    const items = fs.readdirSync(dir, { withFileTypes: true });

    for (const item of items) {
        if (
            item.name === ".git" ||
            item.name === "node_modules" ||
            item.name === "__pycache__"
        ) {
            continue;
        }

        const full = path.join(dir, item.name);

        if (item.isDirectory()) {
            scan(full);
        } else {
            const stat = fs.statSync(full);

            if (!known.has(full)) {
                known.set(full, stat.mtimeMs);
                console.log(`[NEW] ${full}`);
            } else if (known.get(full) !== stat.mtimeMs) {
                known.set(full, stat.mtimeMs);
                console.log(`[MODIFIED] ${full}`);
            }
        }
    }
}

function removeDeleted() {
    for (const file of [...known.keys()]) {
        if (!fs.existsSync(file)) {
            console.log(`[DELETED] ${file}`);
            known.delete(file);
        }
    }
}

scan(WATCH_DIR);

setInterval(() => {
    try {
        scan(WATCH_DIR);
        removeDeleted();
    } catch (err) {
        console.error(err.message);
    }
}, 2000);
