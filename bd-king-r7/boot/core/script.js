const input = document.getElementById("command");
const output = document.getElementById("output");

const FILE_KEY = "tamanna_files";

function print(text) {
  output.innerHTML += `<div>${text}</div>`;
  output.scrollTop = output.scrollHeight;
}

function getFiles() {
  return JSON.parse(localStorage.getItem(FILE_KEY)) || {};
}

function saveFiles(files) {
  localStorage.setItem(FILE_KEY, JSON.stringify(files));
}

print("Welcome to IT Tamanna Terminal");
print("User: tamanna456760-it");
print("Type 'help' for commands");

input.addEventListener("keydown", function (e) {
  if (e.key === "Enter") {
    const cmd = input.value.trim();
    print(`<span class="prompt">IT@tamanna:~$</span> ${cmd}`);
    runCommand(cmd);
    input.value = "";
  }
});

function runCommand(cmd) {
  let files = getFiles();

  if (cmd === "help") {
    print("Commands: help, ls, create <file>, read <file>, sync, clear");
  }

  else if (cmd === "ls") {
    const names = Object.keys(files);
    print(names.length ? names.join("  ") : "No files");
  }

  else if (cmd.startsWith("create ")) {
    const name = cmd.split(" ")[1];
    files[name] = "// Tamanna file";
    saveFiles(files);
    print(`File created: ${name}`);
  }

  else if (cmd.startsWith("read ")) {
    const name = cmd.split(" ")[1];
    print(files[name] || "File not found");
  }

  else if (cmd === "sync") {
    print("🔄 Syncing Tamanna files...");
    setTimeout(() => {
      print("✅ All files synced (local)");
    }, 500);
  }

  else if (cmd === "clear") {
    output.innerHTML = "";
  }

  else {
    print("Command not found");
  }
}