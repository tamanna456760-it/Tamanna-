/* Tamanna AI — read-only status panel */
(() => {
  "use strict";

  function start() {
    if (document.querySelector(".tamanna-system-panel")) {
      return;
    }

    const chat = document.querySelector(".chat-app");

    if (!chat || !chat.parentNode) return;

    const panel = document.createElement("section");
    panel.className = "tamanna-system-panel";
    panel.setAttribute("aria-live", "polite");

    const info = document.createElement("div");

    const title = document.createElement("strong");
    title.textContent = "Tamanna AI Server";

    const status = document.createElement("small");

    const dot = document.createElement("span");
    dot.className = "tamanna-status-dot";

    const label = document.createElement("span");
    label.textContent = "Status পরীক্ষা হচ্ছে…";

    status.append(dot, label);
    info.append(title, status);

    const refresh = document.createElement("button");
    refresh.type = "button";
    refresh.textContent = "Refresh";

    panel.append(info, refresh);
    chat.parentNode.insertBefore(panel, chat);

    async function checkStatus() {
      refresh.disabled = true;
      label.textContent = "Status পরীক্ষা হচ্ছে…";
      dot.className = "tamanna-status-dot";

      try {
        const response = await fetch("/api/status", {
          method: "GET",
          headers: { "Accept": "application/json" },
          cache: "no-store"
        });

        if (!response.ok) {
          throw new Error("HTTP " + response.status);
        }

        const data = await response.json();

        dot.className = "tamanna-status-dot online";
        label.textContent =
          (data.assistant || "Tamanna AI") + " — Online";

      } catch (_) {
        dot.className = "tamanna-status-dot offline";
        label.textContent =
          "Server unavailable — API connection check করুন";

      } finally {
        refresh.disabled = false;
      }
    }

    refresh.addEventListener("click", checkStatus);
    checkStatus();
  }

  if (document.readyState === "loading") {
    document.addEventListener(
      "DOMContentLoaded",
      start,
      { once: true }
    );
  } else {
    start();
  }
})();
