/* Tamanna AI private knowledge-base dashboard. */
(() => {
  "use strict";
  const $ = (id) => document.getElementById(id);
  const form = $("knowledgeForm");
  const filenameInput = $("knowledgeFilename");
  const contentInput = $("knowledgeContent");
  const list = $("knowledgeList");
  const status = $("knowledgeStatus");
  if (!form || !filenameInput || !contentInput || !list || !status) return;

  async function api(path = "", options = {}) {
    const response = await fetch("/tamanna-ai/knowledge" + path, {
      credentials: "same-origin",
      ...options,
      headers: { Accept: "application/json", "Content-Type": "application/json", ...(options.headers || {}) }
    });
    const body = await response.json().catch(() => ({}));
    if (!response.ok) {
      const detail = body.detail;
      throw new Error(typeof detail === "string" ? detail : detail?.message || "HTTP " + response.status);
    }
    return body;
  }

  function setStatus(message, error = false) {
    status.textContent = message;
    status.classList.toggle("tamanna-error", error);
  }

  function render(documents) {
    list.replaceChildren();
    if (!documents.length) {
      const empty = document.createElement("p");
      empty.className = "settings-note";
      empty.textContent = "এখনো কোনো Knowledge document index করা হয়নি।";
      list.append(empty);
      return;
    }
    documents.forEach((documentInfo) => {
      const item = document.createElement("article");
      item.className = "knowledge-item";
      const details = document.createElement("div");
      const title = document.createElement("strong");
      title.textContent = documentInfo.title || documentInfo.source || "Untitled document";
      const meta = document.createElement("small");
      const chunks = Number.isFinite(Number(documentInfo.chunks)) ? Number(documentInfo.chunks) + " chunks" : "Indexed document";
      meta.textContent = (documentInfo.source || "") + " · " + chunks;
      details.append(title, meta);
      const remove = document.createElement("button");
      remove.type = "button";
      remove.className = "settings-secondary";
      remove.textContent = "মুছুন";
      remove.addEventListener("click", async () => {
        const source = String(documentInfo.source || "");
        if (!source || !window.confirm("এই Knowledge document এবং এর indexed chunks মুছে ফেলবেন?")) return;
        remove.disabled = true;
        try {
          await api("/" + encodeURIComponent(source), { method: "DELETE" });
          setStatus("Knowledge document মুছে ফেলা হয়েছে।");
          await load();
        } catch (error) {
          setStatus("মুছতে ব্যর্থ: " + error.message, true);
          remove.disabled = false;
        }
      });
      item.append(details, remove);
      list.append(item);
    });
  }

  async function load() {
    if (!window.TamannaAuth?.getUser()) {
      list.replaceChildren();
      setStatus("Knowledge Base পরিচালনা করতে প্রথমে লগইন করুন।");
      return;
    }
    setStatus("Knowledge documents লোড হচ্ছে…");
    try {
      const result = await api();
      render(Array.isArray(result.documents) ? result.documents : []);
      setStatus("আপনার ব্যক্তিগত Knowledge Base আপডেট হয়েছে।");
    } catch (error) {
      list.replaceChildren();
      setStatus("Knowledge লোড হয়নি: " + error.message, true);
    }
  }

  const reindexButton = $("reindexKnowledgeButton");
  reindexButton?.addEventListener("click", async () => {
    if (!window.TamannaAuth?.getUser()) return setStatus("প্রথমে লগইন করুন।", true);
    reindexButton.disabled = true;
    setStatus("আপনার Knowledge Base-এর embedding পুনরায় তৈরি হচ্ছে…");
    try {
      const result = await api("/reindex", { method: "POST", body: JSON.stringify({}) });
      setStatus("Reindex সম্পন্ন: " + result.documents + " documents, " + result.chunks_reindexed + " chunks।");
      await load();
    } catch (error) {
      setStatus("Reindex ব্যর্থ: " + error.message, true);
    } finally {
      reindexButton.disabled = false;
    }
  });

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    if (!window.TamannaAuth?.getUser()) return setStatus("প্রথমে লগইন করুন।", true);
    const filename = filenameInput.value.trim();
    const content = contentInput.value;
    if (!filename || !content.trim()) return setStatus("ফাইলের নাম ও নথির লেখা দিন।", true);
    if (!/\.(txt|md|markdown|json)$/i.test(filename)) {
      return setStatus("শুধু .txt, .md, .markdown অথবা .json ফাইল সমর্থিত।", true);
    }
    const submit = form.querySelector('button[type="submit"]');
    submit.disabled = true;
    setStatus("নথি index করা হচ্ছে…");
    try {
      const result = await api("/import", {
        method: "POST",
        body: JSON.stringify({ filename, content })
      });
      contentInput.value = "";
      setStatus("Index সম্পন্ন: " + result.filename + " (" + result.chunks_indexed + " chunks)।");
      await load();
    } catch (error) {
      setStatus("Index করা যায়নি: " + error.message, true);
    } finally {
      submit.disabled = false;
    }
  });

  window.addEventListener("tamanna:authenticated", load);
  window.addEventListener("tamanna:loggedout", () => {
    list.replaceChildren();
    setStatus("Knowledge Base পরিচালনা করতে প্রথমে লগইন করুন।");
  });
  $("openSettings")?.addEventListener("click", load);
  if (window.TamannaAuth?.getUser()) load();
})();
