/* Tamanna AI settings: validated local preferences + authenticated account sync. */
(() => {
  "use strict";

  const STORAGE_KEY = "tamanna.app.preferences.v1";
  const defaults = Object.freeze({
    theme: "dark",
    accent: "purple",
    language: "bn",
    fontSize: "medium",
    chatHistory: true,
    notifications: false,
    compactMode: false
  });
  const choices = {
    theme: ["dark", "light"],
    accent: ["purple", "blue", "teal"],
    language: ["bn", "en", "hi", "ar"],
    fontSize: ["small", "medium", "large"]
  };
  const $ = (id) => document.getElementById(id);

  function normalizePreferences(value) {
    const clean = { ...defaults };
    if (!value || typeof value !== "object" || Array.isArray(value)) return clean;
    for (const key of Object.keys(choices)) {
      if (choices[key].includes(value[key])) clean[key] = value[key];
    }
    for (const key of ["chatHistory", "notifications", "compactMode"]) {
      if (typeof value[key] === "boolean") clean[key] = value[key];
    }
    return clean;
  }

  function readPreferences() {
    try {
      return normalizePreferences(JSON.parse(localStorage.getItem(STORAGE_KEY) || "{}"));
    } catch {
      return { ...defaults };
    }
  }

  let preferences = readPreferences();
  let saveQueue = Promise.resolve();
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

  function syncControls() {
    document.querySelectorAll("[data-setting]").forEach((control) => {
      const key = control.dataset.setting;
      if (!(key in preferences)) return;
      if (control.type === "checkbox") control.checked = preferences[key];
      else control.value = preferences[key];
    });
  }

  function updateAccountStatus() {
    const target = $("settingsAccountStatus");
    if (!target) return;
    const user = window.TamannaAuth?.getUser();
    target.textContent = user
      ? "লগইন করা আছে: " + user.name + " (" + user.email + ")"
      : "আপনি এখনো লগইন করেননি। অ্যাকাউন্ট sync ও chat ব্যবহার করতে লগইন করুন।";
  }

  function savePreferences() {
    const snapshot = { ...preferences };
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(snapshot));
    } catch {
      if (status) status.textContent = "এই ডিভাইসে সেটিংস সংরক্ষণ করা যায়নি (storage unavailable)।";
      return;
    }
    applyPreferences();

    const user = window.TamannaAuth?.getUser();
    if (!user) {
      if (status) status.textContent = "এই ডিভাইসে সংরক্ষিত হয়েছে। লগইন করলে অ্যাকাউন্টে sync হবে।";
      return;
    }

    saveQueue = saveQueue.catch(() => {}).then(async () => {
      await window.TamannaAuth.api("/preferences", {
        method: "PUT",
        body: JSON.stringify({ preferences: snapshot })
      });
      if (status) status.textContent = "সেটিংস এই ডিভাইস ও অ্যাকাউন্টে সংরক্ষিত হয়েছে।";
    }).catch((error) => {
      if (status) status.textContent = "ডিভাইসে সংরক্ষিত; cloud sync ব্যর্থ: " + error.message;
    });
  }

  async function loadAccountPreferences() {
    updateAccountStatus();
    if (!window.TamannaAuth?.getUser()) return;
    try {
      const result = await window.TamannaAuth.api("/preferences");
      preferences = normalizePreferences(result.preferences);
      localStorage.setItem(STORAGE_KEY, JSON.stringify(preferences));
      syncControls();
      applyPreferences();
      if (status) status.textContent = "অ্যাকাউন্টের সেটিংস sync হয়েছে।";
    } catch (error) {
      if (status) status.textContent = "অ্যাকাউন্টের সেটিংস লোড হয়নি: " + error.message;
    }
  }

  function openSettings() {
    if (!panel || !backdrop) return;
    panel.hidden = false;
    backdrop.hidden = false;
    document.body.classList.add("settings-open");
    closeButton?.focus();
    updateAccountStatus();
  }

  function closeSettings() {
    if (!panel || !backdrop) return;
    panel.hidden = true;
    backdrop.hidden = true;
    document.body.classList.remove("settings-open");
    openButton?.focus();
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
    if (!(key in preferences)) return;
    preferences[key] = control.type === "checkbox" ? control.checked : control.value;
    preferences = normalizePreferences(preferences);
    syncControls();
    savePreferences();
  });

  $("resetSettings")?.addEventListener("click", () => {
    preferences = { ...defaults };
    syncControls();
    savePreferences();
  });

  $("manageAccountButton")?.addEventListener("click", () => {
    $("openAuth")?.click();
  });

  $("clearLocalChat")?.addEventListener("click", () => {
    if (!window.confirm("শুধু বর্তমান স্ক্রিনের কথোপকথন পরিষ্কার করবেন? সার্ভারে সংরক্ষিত ইতিহাস অক্ষত থাকবে।")) return;
    const box = $("chatBox");
    if (box) {
      box.replaceChildren();
      const message = document.createElement("div");
      message.className = "message ai-message";
      const name = document.createElement("div");
      name.className = "message-name";
      name.textContent = "Tamanna AI";
      const body = document.createElement("div");
      body.className = "message-text";
      body.textContent = "স্ক্রিন পরিষ্কার করা হয়েছে। নতুন কথোপকথন শুরু করুন।";
      message.append(name, body);
      box.append(message);
    }
    if (status) status.textContent = "বর্তমান স্ক্রিন পরিষ্কার হয়েছে; সার্ভার history মুছে যায়নি।";
  });

  window.addEventListener("tamanna:authenticated", loadAccountPreferences);
  window.addEventListener("tamanna:loggedout", () => {
    preferences = readPreferences();
    syncControls();
    applyPreferences();
    updateAccountStatus();
  });

  applyPreferences();
  syncControls();
  updateAccountStatus();
  if (window.TamannaAuth?.getUser()) loadAccountPreferences();
})();