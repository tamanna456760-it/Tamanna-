const fs = require(“node:fs”);

const requiredFiles = [“Main.py”, “main.py”];
const missing = requiredFiles.filter(
(file) => !fs.existsSync(file)
);

if (missing.length > 0) {
console.error(
“Missing Tamanna AI entry files:”,
missing.join(”, “)
);
process.exit(1);
}

console.log(“Tamanna AI entry-point files verified.”);
