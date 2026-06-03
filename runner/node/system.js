// Load version from config.json
let version = "v1.0.0";

fetch("config.json")
  .then(response => response.json())
  .then(data => {
    version = data.version;
    document.getElementById("version").textContent = "v" + version;
  })
  .catch(err => console.log("Failed to load version:", err));

function bootSystem() {
  alert("TAMANNA SYSTEM v" + version + " BOOTED ✅");
  console.log("System booted, version:", version);
}