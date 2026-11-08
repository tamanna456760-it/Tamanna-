/* Authenticated private-memory dashboard. */
(() => {
  "use strict";
  const $ = (id) => document.getElementById(id);
  const list = $("memoryList"), form = $("memoryForm"), input = $("memoryContent");
  const status = $("memoryStatus");
  if (!list || !form || !input || !status) return;

  const api = async (path, options = {}) => {
    const response = await fetch("/tamanna-ai/memories" + path, {
      credentials: "same-origin",
      ...options,
      headers: { Accept: "application/json", "Content-Type": "application/json", ...(options.headers || {}) }
    });
    const body = await response.json().catch(() => ({}));
    if (!response.ok) {
      const detail = typeof body.detail === "string" ? body.detail : "HTTP " + response.status;
      throw new Error(detail);
    }
    return body;
  };

  function setStatus(message, error = false) {
    status.textContent = message;
    status.classList.toggle("tamanna-error", error);
  }

  function render(records) {
    list.replaceChildren();
    if (!records.length) {
      const empty = document.createElement("p");
      empty.className = "settings-note";
      empty.textContent = "এখনো কোনো Memory সংরক্ষিত নেই।";
      list.append(empty);
      return;
    }
    records.forEach((record) => {
      const item = document.createElement("article");
      item.className = "memory-item";
      const editor = document.createElement("textarea");
      editor.rows = 3;
      editor.maxLength = 10000;
      editor.value = record.content;
      editor.setAttribute("aria-label", "Memory সম্পাদনা");
      const meta = document.createElement("p");
      meta.className = "settings-note";
      meta.textContent = "Memory #" + record.id + (record.created_at ? " · " + new Date(record.created_at).toLocaleString() : "");
      const actions = document.createElement("div");
      actions.className = "memory-actions";
      const save = document.createElement("button");
      save.type = "button";
      save.textContent = "পরিবর্তন সংরক্ষণ";
      save.addEventListener("click", async () => {
        if (!editor.value.trim()) return setStatus("Memory খালি রাখা যাবে না।", true);
        save.disabled = true;
        try {
          await api("/" + record.id, { method: "PATCH", body: JSON.stringify({ content: editor.value }) });
          setStatus("Memory আপডেট হয়েছে।");
          await load();
        } catch (error) { setStatus(error.message, true); save.disabled = false; }
      });
      const remove = document.createElement("button");
      remove.type = "button";
      remove.className = "settings-secondary";
      remove.textContent = "মুছুন";
      remove.addEventListener("click", async () => {
        if (!window.confirm("এই Memory স্থায়ীভাবে মুছে ফেলবেন?")) return;
        remove.disabled = true;
        try {
          await api("/" + record.id, { method: "DELETE" });
          setStatus("Memory মুছে ফেলা হয়েছে।");
          await load();
        } catch (error) { setStatus(error.message, true); remove.disabled = false; }
      });
      actions.append(save, remove);
      item.append(meta, editor, actions);
      list.append(item);
    });
  }

  async function load() {
    if (!window.TamannaAuth?.getUser()) {
      list.replaceChildren();
      setStatus("Memory পরিচালনা করতে প্রথমে লগইন করুন।");
      return;
    }
    setStatus("Memory লোড হচ্ছে…");
    try {
      const result = await api("");
      render(Array.isArray(result.memories) ? result.memories : []);
      setStatus("আপনার ব্যক্তিগত Memory লোড হয়েছে।");
    } catch (error) {
      list.replaceChildren();
      setStatus("Memory লোড করা যায়নি: " + error.message, true);
    }
  }

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    if (!window.TamannaAuth?.getUser()) return setStatus("প্রথমে লগইন করুন।", true);
    const content = input.value.trim();
    if (!content) return setStatus("Memory খালি রাখা যাবে না।", true);
    const submit = form.querySelector('button[type="submit"]');
    submit.disabled = true;
    try {
      await api("", { method: "POST", body: JSON.stringify({ content }) });
      input.value = "";
      setStatus("নতুন Memory সংরক্ষিত হয়েছে।");
      await load();
    } catch (error) {
      setStatus("Memory সংরক্ষণ করা যায়নি: " + error.message, true);
    } finally { submit.disabled = false; }
  });

  window.addEventListener("tamanna:authenticated", load);
  window.addEventListener("tamanna:loggedout", () => {
    list.replaceChildren();
    setStatus("Memory পরিচালনা করতে প্রথমে লগইন করুন।");
  });
  $("openSettings")?.addEventListener("click", load);
  if (window.TamannaAuth?.getUser()) load();
})();
