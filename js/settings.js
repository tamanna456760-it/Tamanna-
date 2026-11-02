/* Tamanna AI application settings — client preferences only.
   Authentication is intentionally not simulated in the browser. */
(() => {
  "use strict";

  const STORAGE_KEY = "tamanna.app.preferences.v1";
  const defaults = {
    theme: "dark",
    accent: "purple",
    language: "bn",
    fontSize: "medium",
    chatHistory: true,
    notifications: false,
    compactMode: false
  };

  const readPreferences = () => {
    try {
      const value = JSON.parse(localStorage.getItem(STORAGE_KEY) || "{}");
      return { ...defaults, ...(value && typeof value === "object" ? value : {}) };
    } catch {
      return { ...defaults };
    }
  };

  let preferences = readPreferences();
  const $ = (id) => document.getElementById(id);
  const panel = $("settingsPanel");
  const backdrop = $("settingsBackdrop");
  const openButton = $("openSettings");
  const closeButton = $("closeSettings");
  const status = $("settingsSaveStatus");

  function applyPreferences() {
    document.documentElement.dataset.theme = preferences.theme;
    document.documentElement.dataset.accent = preferences.accent;
    document.documentElement.dataset.fontSize = preferences.fontSize;
    document.documentElement.lang = preferences.language;
    document.body.classList.toggle("compact-chat", preferences.compactMode);
  }

  async function savePreferences() {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(preferences));
      applyPreferences();
      if (window.TamannaAuth?.getUser()) {
        await window.TamannaAuth.api("/preferences", {
          method: "PUT",
          body: JSON.stringify({ preferences })
        });
        if (status) status.textContent = "সেটিংস অ্যাকাউন্টে সংরক্ষিত হয়েছে";
      } else if (status) {
        status.textContent = "এই ডিভাইসে সংরক্ষিত হয়েছে। অ্যাকাউন্টে লগইন করলে cloud sync হবে।";
      }
    } catch (error) {
      if (status) status.textContent = "সেটিংস সংরক্ষণে সমস্যা: " + error.message;
    }
  }

  async function loadAccountPreferences() {
    if (!window.TamannaAuth?.getUser()) return;
    try {
      const result = await window.TamannaAuth.api("/preferences");
      preferences = { ...preferences, ...result.preferences };
      localStorage.setItem(STORAGE_KEY, JSON.stringify(preferences));
      syncControls();
      applyPreferences();
    } catch (error) {
      if (status) status.textContent = "অ্যাকাউন্টের সেটিংস লোড করা যায়নি: " + error.message;
    }
  }

  window.addEventListener("tamanna:authenticated", loadAccountPreferences);


  function openSettings() {
    if (!panel || !backdrop) return;
    panel.hidden = false;
    backdrop.hidden = false;
    document.body.classList.add("settings-open");
    closeButton?.focus();
  }

  function closeSettings() {
    if (!panel || !backdrop) return;
    panel.hidden = true;
    backdrop.hidden = true;
    document.body.classList.remove("settings-open");
    openButton?.focus();
  }

  function syncControls() {
    document.querySelectorAll("[data-setting]").forEach((control) => {
      const key = control.dataset.setting;
      if (!(key in preferences)) return;
      if (control.type === "checkbox") control.checked = Boolean(preferences[key]);
      else control.value = String(preferences[key]);
    });
  }

  openButton?.addEventListener("click", openSettings);
  closeButton?.addEventListener("click", closeSettings);
  backdrop?.addEventListener("click", closeSettings);
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && panel && !panel.hidden) closeSettings();
  });

  panel?.addEventListener("change", (event) => {
    const control = event.target.closest("[data-setting]");
    if (!control) return;
    const key = control.dataset.setting;
    preferences[key] = control.type === "checkbox" ? control.checked : control.value;
    savePreferences();
  });

  $("resetSettings")?.addEventListener("click", () => {
    preferences = { ...defaults };
    syncControls();
    savePreferences();
  });

  $("clearLocalChat")?.addEventListener("click", () => {
    if (!window.confirm("এই ব্রাউজারে সংরক্ষিত চ্যাট মুছতে চান? সার্ভারের chat_history.json এতে মুছবে না।")) return;
    const box = $("chatBox");
    if (box) box.replaceChildren();
    if (status) status.textContent = "বর্তমান স্ক্রিনের চ্যাট পরিষ্কার হয়েছে";
  });

  applyPreferences();
  syncControls();
  window.addEventListener("tamanna:loggedout", () => {
    preferences = readPreferences();
    syncControls();
    applyPreferences();
  });
  window.addEventListener("tamanna:authenticated", loadAccountPreferences);
})();
