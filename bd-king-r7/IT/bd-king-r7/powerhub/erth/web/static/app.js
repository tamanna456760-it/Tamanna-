const API_BASE = "/api";

async function fetchModules() {
  const res = await fetch(`${API_BASE}/modules`);
  return await res.json();
}

function el(tag, attrs={}, text="") {
  const e = document.createElement(tag);
  Object.entries(attrs).forEach(([k,v]) => e.setAttribute(k,v));
  if (text) e.textContent = text;
  return e;
}

async function toggleModule(name) {
  const res = await fetch(`${API_BASE}/module/${name}/toggle`, { method: "POST" });
  if (res.ok) {
    await render();
  } else {
    alert("Toggle failed");
  }
}

function buildCard(name, data) {
  const card = el("div", {class:"card"});
  card.appendChild(el("h3", {}, name.replace("_"," ").toUpperCase()));
  card.appendChild(el("div",{class:"meta"}, `Enabled: ${data.enabled} • Last: ${new Date(data.last_update*1000).toLocaleString()}`));
  const btn = document.createElement("button");
  btn.className = "btn " + (data.enabled ? "btn-on" : "btn-off");
  btn.textContent = data.enabled ? "Turn OFF" : "Turn ON";
  btn.onclick = () => toggleModule(name);
  card.appendChild(btn);
  return card;
}

async function render() {
  const container = document.getElementById("modules");
  container.innerHTML = "";
  try {
    const modules = await fetchModules();
    Object.entries(modules).forEach(([k,v]) => {
      container.appendChild(buildCard(k, v));
    });
  } catch (e) {
    container.innerHTML = "<p>Error loading modules. Is the server running?</p>";
  }
}

window.addEventListener("load", () => {
  render();
  // Refresh periodically
  setInterval(render, 5000);
});