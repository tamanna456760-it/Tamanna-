const logs = document.getElementById("logs");
const statusText = document.getElementById("status");

function log(msg) {
    logs.textContent += "\n" + msg;
    logs.scrollTop = logs.scrollHeight;
}

function callAPI(endpoint) {
    fetch("http://localhost:5000/" + endpoint)
        .then(res => res.json())
        .then(data => log(data.log))
        .catch(() => log("❌ Backend not running"));
}

function connectSystem() {
    statusText.textContent = "Connected";
    statusText.style.color = "#22c55e";
    callAPI("connect");
}

function fixFiles() {
    callAPI("fix");
}

function saveCode() {
    callAPI("save");
}

function buildSystem() {
    callAPI("build");
}