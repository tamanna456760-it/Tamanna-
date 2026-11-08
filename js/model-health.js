/* Tamanna AI local model and knowledge health dashboard. */
(() => {
  "use strict";
  const $ = (id) => document.getElementById(id);
  const refreshButton = $("refreshModelHealth");
  const updated = $("modelHealthUpdated");
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

  refreshButton.addEventListener("click", refresh);
  $("openSettings")?.addEventListener("click", refresh);
  window.addEventListener("tamanna:authenticated", refresh);
  window.addEventListener("tamanna:loggedout", () => {
    set("healthKnowledgeStatus", "লগইন প্রয়োজন");
    set("healthKnowledgeDetail", "Private index শুধু account owner দেখতে পারবেন");
  });
  refresh();
})();
