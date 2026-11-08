/* Tamanna AI local model and knowledge health dashboard. */
(() => {
  "use strict";
  const $ = (id) => document.getElementById(id);
  const refreshButton = $("refreshModelHealth");
  const updated = $("modelHealthUpdated");
  const modelSelect = $("localModelSelect");
  const saveModelButton = $("saveLocalModel");
  const modelSelectStatus = $("modelSelectStatus");
  const downloadButton = $("downloadLocalModel");
  const downloadInput = $("downloadModelName");
  const downloadProgress = $("modelDownloadProgress");
  const downloadStatus = $("modelDownloadStatus");
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

  function formatBytes(value) {
    if (!Number.isFinite(value) || value < 0) return "Unavailable";
    const units = ["B", "KB", "MB", "GB", "TB"];
    let size = value;
    let unit = 0;
    while (size >= 1024 && unit < units.length - 1) {
      size /= 1024;
      unit += 1;
    }
    return size.toFixed(unit >= 3 ? 2 : 1) + " " + units[unit];
  }

  async function refreshMetrics() {
    const user = window.TamannaAuth?.getUser();
    if (!user) {
      set("metricCpu", "লগইন প্রয়োজন");
      set("metricRam", "লগইন প্রয়োজন");
      set("metricDisk", "লগইন প্রয়োজন");
      set("metricGpu", "লগইন প্রয়োজন");
      set("metricsUpdated", "Metrics দেখতে account-এ লগইন করুন।");
      return;
    }
    try {
      const metrics = await getJson("/tamanna-ai/system/metrics");
      const cpu = metrics.cpu || {};
      const memory = metrics.memory || {};
      const disk = metrics.disk || {};
      const gpu = metrics.gpu || {};
      set("metricCpu", Number.isFinite(cpu.usage_percent) ? cpu.usage_percent + "%" : "Unavailable");
      set("metricCpuDetail", (cpu.logical_cores || "—") + " logical CPU core(s)");
      set("metricRam", Number.isFinite(memory.usage_percent) ? memory.usage_percent + "%" : "Unavailable");
      set("metricRamDetail", formatBytes(memory.used_bytes) + " / " + formatBytes(memory.total_bytes));
      set("metricDisk", Number.isFinite(disk.usage_percent) ? disk.usage_percent + "%" : "Unavailable");
      set("metricDiskDetail", formatBytes(disk.used_bytes) + " used · " + formatBytes(disk.free_bytes) + " free");
      if (gpu.available) {
        set("metricGpu", Number.isFinite(gpu.utilization_percent) ? gpu.utilization_percent + "%" : "Detected");
        set("metricGpuDetail", (gpu.name || "NVIDIA GPU") + " · " +
          formatBytes((gpu.memory_used_mb || 0) * 1048576) + " / " +
          formatBytes((gpu.memory_total_mb || 0) * 1048576));
      } else {
        set("metricGpu", "Not detected");
        set("metricGpuDetail", gpu.vendor === "NVIDIA" ? "NVIDIA telemetry unavailable" : "No NVIDIA nvidia-smi found");
      }
      set("metricsUpdated", "সর্বশেষ metrics: " + new Date().toLocaleString());
    } catch (error) {
      ["metricCpu", "metricRam", "metricDisk", "metricGpu"].forEach((id) => set(id, "Unavailable"));
      const denied = /403|admin/i.test(error.message);
      set("metricsUpdated", denied ? "এই তথ্য শুধু configured Tamanna AI admin দেখতে পারবেন।" : "Metrics সংগ্রহ করা যায়নি: " + error.message);
      if (denied) ["metricCpu", "metricRam", "metricDisk", "metricGpu"].forEach((id) => set(id, "Admin only"));
    }
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
      await refreshMetrics();
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

  downloadButton?.addEventListener("click", async () => {
    if (!window.TamannaAuth?.getUser()) {
      if (downloadStatus) downloadStatus.textContent = "Model download করতে প্রথমে লগইন করুন।";
      return;
    }
    const model = downloadInput?.value.trim();
    if (!model || !/^[A-Za-z0-9][A-Za-z0-9._:/-]{0,199}$/.test(model)) {
      if (downloadStatus) downloadStatus.textContent = "সঠিক Ollama model নাম লিখুন, যেমন qwen2.5:7b।";
      return;
    }
    downloadButton.disabled = true;
    if (downloadProgress) downloadProgress.value = 0;
    if (downloadStatus) downloadStatus.textContent = "Download request পাঠানো হচ্ছে…";
    try {
      const response = await fetch("/tamanna-ai/model/pull", {
        method: "POST",
        credentials: "same-origin",
        headers: { Accept: "application/x-ndjson", "Content-Type": "application/json" },
        body: JSON.stringify({ model })
      });
      if (!response.ok || !response.body) {
        const failure = await response.json().catch(() => ({}));
        const detail = failure.detail;
        throw new Error(typeof detail === "string" ? detail : detail?.message || "HTTP " + response.status);
      }
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";
      let completed = false;
      const processLine = (line) => {
        if (!line.trim()) return;
        const event = JSON.parse(line);
        if (event.error) throw new Error(event.error);
        if (typeof event.total === "number" && event.total > 0 && typeof event.completed === "number") {
          const percent = Math.min(100, Math.floor((event.completed / event.total) * 100));
          if (downloadProgress) downloadProgress.value = percent;
          if (downloadStatus) downloadStatus.textContent =
            (event.status || "Downloading") + " · " + percent + "% (" +
            Math.round(event.completed / 1048576) + " / " +
            Math.round(event.total / 1048576) + " MB)";
        } else if (event.status && downloadStatus) {
          downloadStatus.textContent = event.status;
        }
        if (event.done === true || event.status === "success") completed = true;
      };
      while (true) {
        const part = await reader.read();
        buffer += decoder.decode(part.value || new Uint8Array(), { stream: !part.done });
        const lines = buffer.split("\n");
        buffer = lines.pop() || "";
        lines.forEach(processLine);
        if (part.done) break;
      }
      if (buffer.trim()) processLine(buffer);
      if (!completed) throw new Error("Download stream ended before Ollama confirmed completion.");
      if (downloadProgress) downloadProgress.value = 100;
      if (downloadStatus) downloadStatus.textContent = "Download complete: " + model;
      if (downloadInput) downloadInput.value = "";
      await refresh();
    } catch (error) {
      if (downloadStatus) downloadStatus.textContent = "Download failed: " + error.message;
    } finally {
      downloadButton.disabled = false;
    }
  });

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
  window.setInterval(() => {
    if (document.visibilityState === "visible") refreshMetrics();
  }, 15000);
  window.addEventListener("tamanna:authenticated", refresh);
  window.addEventListener("tamanna:loggedout", () => {
    set("healthKnowledgeStatus", "লগইন প্রয়োজন");
    set("healthKnowledgeDetail", "Private index শুধু account owner দেখতে পারবেন");
  });
  refresh();
})();
