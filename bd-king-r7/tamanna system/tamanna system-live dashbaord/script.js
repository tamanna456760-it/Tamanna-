const logs = document.getElementById("logs");
const statusText = document.getElementById("status");

function log(msg) {
    logs.textContent += "\n" + msg;
    logs.scrollTop = logs.scrollHeight;
}

function connectSystem() {
    statusText.textContent = "Connected";
    statusText.style.color = "#22c55e";
    log("✔ System connected to Git repository");
    log("✔ Git ID: Tamanna456760-it");
}

function fixFiles() {
    log("🔧 Scanning files...");
    setTimeout(() => {
        log("✔ Errors fixed successfully");
    }, 1000);
}

function saveCode() {
    log("💾 Saving new code...");
    setTimeout(() => {
        log("✔ Code saved");
    }, 800);
}

function buildSystem() {
    log("🏗 Building system...");
    setTimeout(() => {
        log("✔ Build completed successfully");
    }, 1500);
}