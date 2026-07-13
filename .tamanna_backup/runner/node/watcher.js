const chokidar = require("chokidar");
const { exec } = require("child_process");

console.log("Tamanna Auto Dev System Running...");

const watcher = chokidar.watch(".", {
  ignored: /node_modules|\.git/,
  persistent: true
});

watcher.on("change", (path) => {
  console.log(`File changed: ${path}`);

  // Auto Fix Code
  exec("npm run lint", (err, stdout, stderr) => {
    if (err) console.log("Lint Error:", err);
    else console.log("Auto Fixed Errors");
  });

  // Auto Format
  exec("npm run format", (err, stdout, stderr) => {
    if (err) console.log("Format Error:", err);
    else console.log("Auto Formatted");
  });

  // Auto Build
  exec("npm run build", (err, stdout, stderr) => {
    if (err) console.log("Build Error:", err);
    else console.log("Auto Build Complete");
  });
});