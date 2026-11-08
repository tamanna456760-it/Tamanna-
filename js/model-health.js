/* Tamanna AI local model and knowledge health dashboard. */
(() => {
  "use strict";
  const $ = (id) => document.getElementById(id);
  const refreshButton = $("refreshModelHealth");
  const updated = $("modelHealthUpdated");
  const modelSelect = $("localModelSelect");
  const saveModelButton = $("saveLocalModel");
  const modelSelectStatus = $("modelSelectStatus");
  if (!refreshButton || !updated) return;

  function set(id, value) {
    const node = $(id);
    if (node) node.textContent = value;
  }

  async function getJson(url) {
    const response = await fetch(url, {
      method: "GET",
      credentials: "same-origin",
      headers: { Accept: "application/json" },
      cache: "no-store"
    });
    const data = await response.json().catch(() => ({}));
    if (!response.ok) {
      const detail = data.detail;
      throw new Error(typeof detail === "string" ? detail : detail?.message || "HTTP " + response.status);
    }
    return data;
  }

  async function refresh() {
    refreshButton.disabled = true;
    updated.textContent = "System status পরীক্ষা হচ্ছে…";
    set("healthChatStatus", "যাচাই হচ্ছে…");
    set("healthEmbeddingStatus", "যাচাই হচ্ছে…");
    set("healthOllamaStatus", "যাচাই হচ্ছে…");
    try {
      const model = await getJson("/tamanna-ai/model/status");
      const models = Array.isArray(model.installed_models) ? model.installed_models : [];
      if (modelSelect) {
        const current = model.selected_model || "";
        modelSelect.replaceChildren();
        models.forEach((name) => {
          const option = document.createElement("option");
          option.value = name;
          option.textContent = name;
          modelSelect.append(option);
        });
        if (current && models.includes(current)) modelSelect.value = current;
        modelSelect.disabled = models.length === 0;
        if (saveModelButton) saveModelButton.disabled = models.length === 0;
        if (modelSelectStatus) modelSelectStatus.textContent = models.length
          ? "নির্বাচিত: " + (current || "কোনো installed model নয়")
          : "Ollama-তে কোনো model installed নেই।";
      }
      const chatReady = Boolean(model.selected_model_installed);
      set("healthChatStatus", chatReady ? "Ready" : "Model unavailable");
      set("healthChatDetail", (model.provider || "Unknown provider") + " · " + (model.selected_model || "No model selected"));
      set("healthOllamaStatus", model.status === "ready" ? "Connected" : "Connected · no models");
      set("healthOllamaDetail", models.length + " installed model(s)");

      const embedding = model.embedding || {};
      const embeddingReady = embedding.provider === "local-feature"
        ? Boolean(embedding.configured)
        : Boolean(embedding.configured && embedding.installed);
      set("healthEmbeddingStatus", embeddingReady ? "Ready" : "Unavailable");
      set("healthEmbeddingDetail", embedding.model || embedding.provider || "Not configured");

      if (window.TamannaAuth?.getUser()) {
        try {
          const knowledge = await getJson("/tamanna-ai/knowledge");
          const documents = Array.isArray(knowledge.documents) ? knowledge.documents : [];
          const chunks = documents.reduce((sum, item) => sum + (Number(item.chunks) || 0), 0);
          set("healthKnowledgeStatus", documents.length + " document(s)");
          set("healthKnowledgeDetail", chunks + " indexed chunk(s) · private account");
        } catch (error) {
          set("healthKnowledgeStatus", "Unavailable");
          set("healthKnowledgeDetail", error.message);
        }
      } else {
        set("healthKnowledgeStatus", "লগইন প্রয়োজন");
        set("healthKnowledgeDetail", "Private index শুধু account owner দেখতে পারবেন");
      }
      updated.textContent = "সর্বশেষ পরীক্ষা: " + new Date().toLocaleString();
    } catch (error) {
      set("healthChatStatus", "Unavailable");
      set("healthChatDetail", error.message);
      set("healthOllamaStatus", "Not verified");
      set("healthOllamaDetail", "Local runtime status পাওয়া যায়নি");
      set("healthEmbeddingStatus", "Not verified");
      set("healthEmbeddingDetail", "Model status endpoint unavailable");
      updated.textContent = "Status পরীক্ষা ব্যর্থ: " + error.message;
    } finally {
      refreshButton.disabled = false;
    }
  }

  saveModelButton?.addEventListener("click", async () => {
    if (!window.TamannaAuth?.getUser()) {
      if (modelSelectStatus) modelSelectStatus.textContent = "Model পরিবর্তনের জন্য প্রথমে লগইন করুন।";
      return;
    }
    const model = modelSelect?.value;
    if (!model) return;
    saveModelButton.disabled = true;
    if (modelSelectStatus) modelSelectStatus.textContent = "Model selection সংরক্ষণ হচ্ছে…";
    try {
      const response = await fetch("/tamanna-ai/model/select", {
        method: "POST",
        credentials: "same-origin",
        headers: { Accept: "application/json", "Content-Type": "application/json" },
        body: JSON.stringify({ model })
      });
      const result = await response.json().catch(() => ({}));
      if (!response.ok) {
        const detail = result.detail;
        throw new Error(typeof detail === "string" ? detail : detail?.message || "HTTP " + response.status);
      }
      if (modelSelectStatus) modelSelectStatus.textContent = "সক্রিয় Chat Model: " + result.selected_model;
      await refresh();
    } catch (error) {
      if (modelSelectStatus) modelSelectStatus.textContent = "Model পরিবর্তন ব্যর্থ: " + error.message;
    } finally {
      saveModelButton.disabled = !modelSelect || modelSelect.options.length === 0;
    }
  });

  refreshButton.addEventListener("click", refresh);
  $("openSettings")?.addEventListener("click", refresh);
  window.addEventListener("tamanna:authenticated", refresh);
  window.addEventListener("tamanna:loggedout", () => {
    set("healthKnowledgeStatus", "লগইন প্রয়োজন");
    set("healthKnowledgeDetail", "Private index শুধু account owner দেখতে পারবেন");
  });
  refresh();
})();
