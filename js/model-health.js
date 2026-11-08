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

  const benchmarkButton = $("runModelBenchmark");

  async function requestBenchmark() {
    const response = await fetch("/tamanna-ai/model/benchmark", {
      method: "POST",
      credentials: "same-origin",
      headers: { Accept: "application/json" }
    });
    const result = await response.json().catch(() => ({}));
    if (!response.ok) {
      const detail = result.detail;
      throw new Error(typeof detail === "string" ? detail : detail?.message || "HTTP " + response.status);
    }
    return result.benchmark || {};
  }

  function benchmarkRegressed(current, baseline) {
    if (!current || !baseline) return false;
    const speedNow = current.generation_tokens_per_second;
    const speedBefore = baseline.generation_tokens_per_second;
    if (Number.isFinite(speedNow) && Number.isFinite(speedBefore) && speedBefore > 0 &&
        (speedBefore - speedNow) / speedBefore >= 0.20) return true;
    const latencyNow = current.wall_time_ms;
    const latencyBefore = baseline.wall_time_ms;
    if (Number.isFinite(latencyNow) && Number.isFinite(latencyBefore) && latencyBefore > 0 &&
        (latencyNow - latencyBefore) / latencyBefore >= 0.25) return true;
    return Number.isFinite(current.passed_checks) && Number.isFinite(baseline.passed_checks) &&
      current.passed_checks < baseline.passed_checks;
  }

  function displayBenchmark(metrics, prefix) {
    const display = (value, suffix) => Number.isFinite(value) ? value + suffix : "Unavailable";
    set("benchmarkLatency", display(metrics.wall_time_ms, " ms"));
    set("benchmarkGeneration", display(metrics.generation_tokens_per_second, " tok/s"));
    set("benchmarkPrompt", display(metrics.prompt_tokens_per_second, " tok/s"));
    set("benchmarkTokens", display(metrics.output_tokens, ""));
    const checks = Array.isArray(metrics.checks) ? metrics.checks : [];
    const checkSummary = checks.length
      ? " · Instruction checks: " + (metrics.passed_checks ?? 0) + "/" + (metrics.total_checks ?? checks.length)
      : "";
    set("benchmarkDetails", "Model: " + (metrics.model || "Unknown") +
      " · Prompt: " + (metrics.prompt_tokens ?? "—") + " tokens" +
      " · Ollama total: " + display(metrics.total_duration_ms, " ms") +
      " · Model load: " + display(metrics.model_load_ms, " ms") + checkSummary);
    set("benchmarkStatus", (prefix || "Benchmark সম্পন্ন") + " · " +
      (metrics.passed_checks ?? "—") + "/" + (metrics.total_checks ?? "—") +
      " basic instruction checks pass · " + new Date().toLocaleString());
  }

  benchmarkButton?.addEventListener("click", async () => {
    if (!window.TamannaAuth?.getUser()) {
      set("benchmarkStatus", "Benchmark চালাতে প্রথমে লগইন করুন।");
      return;
    }
    benchmarkButton.disabled = true;
    set("benchmarkStatus", "Local model benchmark চলছে… প্রথমবার model load হতে সময় লাগতে পারে।");
    ["benchmarkLatency", "benchmarkGeneration", "benchmarkPrompt", "benchmarkTokens"].forEach((id) => set(id, "পরীক্ষা হচ্ছে…"));
    try {
      let baseline = null;
      try {
        const history = await getJson("/tamanna-ai/model/benchmark/history?limit=100");
        const rows = Array.isArray(history.runs) ? history.runs : [];
        let selected = modelSelect?.value;
        if (!selected) {
          const status = await getJson("/tamanna-ai/model/status");
          selected = status.selected_model || "";
        }
        const previous = selected ? rows.find((row) => row.model === selected) : null;
        baseline = previous?.result || null;
      } catch (_) {
        // Benchmark still runs when history is unavailable; no automatic retry without a baseline.
      }

      let metrics = await requestBenchmark();
      displayBenchmark(metrics);
      if (baseline && benchmarkRegressed(metrics, baseline)) {
        set("benchmarkStatus", "সম্ভাব্য regression শনাক্ত · একবার confirmation benchmark চলছে…");
        try {
          const confirmation = await requestBenchmark();
          const persistent = benchmarkRegressed(confirmation, baseline);
          metrics = confirmation;
          displayBenchmark(metrics, persistent
            ? "দ্বিতীয় পরীক্ষাতেও regression নিশ্চিত"
            : "পুনরায় পরীক্ষায় regression নিশ্চিত হয়নি");
          if (persistent) {
            set("benchmarkRegressionStatus", "দুটি ধারাবাহিক run-এ baseline-এর তুলনায় regression রয়ে গেছে। Model, resource load ও runtime পরীক্ষা করুন।");
          } else {
            set("benchmarkRegressionStatus", "প্রথম regression signal পুনরায় benchmark-এ নিশ্চিত হয়নি; সাময়িক variation হতে পারে।");
          }
        } catch (retryError) {
          set("benchmarkStatus", "প্রথম benchmark সফল; confirmation ব্যর্থ: " + retryError.message);
        }
      }
      await refreshBenchmarkHistory();
    } catch (error) {
      ["benchmarkLatency", "benchmarkGeneration", "benchmarkPrompt", "benchmarkTokens"].forEach((id) => set(id, "—"));
      set("benchmarkStatus", "Benchmark ব্যর্থ: " + error.message);
    } finally {
      benchmarkButton.disabled = false;
    }
  });

  async function refreshBenchmarkHistory() {
    const list = $("benchmarkHistoryList");
    if (!list) return;
    if (!window.TamannaAuth?.getUser()) {
      set("benchmarkHistoryStatus", "ইতিহাস দেখতে admin account-এ লগইন করুন।");
      list.replaceChildren();
      return;
    }
    try {
      const data = await getJson("/tamanna-ai/model/benchmark/history?limit=100");
      const runs = Array.isArray(data.runs) ? data.runs : [];
      list.replaceChildren();
      runs.forEach((run) => {
        const item = document.createElement("li");
        const result = run.result || {};
        const date = document.createElement("time");
        date.textContent = run.created_at ? new Date(run.created_at).toLocaleString() : "তারিখ অজানা";
        const summary = document.createElement("span");
        summary.textContent = " · " + (run.model || "Unknown model") + " · " +
          (result.passed_checks ?? "—") + "/" + (result.total_checks ?? "—") +
          " checks · " + (Number.isFinite(result.wall_time_ms) ? result.wall_time_ms + " ms" : "latency unavailable") +
          " · " + (Number.isFinite(result.generation_tokens_per_second) ? result.generation_tokens_per_second + " tok/s" : "speed unavailable");
        item.append(date, summary);
        list.append(item);
      });
      set("benchmarkHistoryStatus", runs.length ? runs.length + "টি সাম্প্রতিক benchmark" : "এখনো কোনো benchmark সংরক্ষিত নেই।");
      renderBenchmarkComparison(runs);
      renderBenchmarkRegressions(runs);
    } catch (error) {
      list.replaceChildren();
      renderBenchmarkComparison([]);
      renderBenchmarkRegressions([]);
      set("benchmarkHistoryStatus", "History unavailable: " + error.message);
    }
  }

  function renderBenchmarkComparison(runs) {
    const container = $("benchmarkComparisonList");
    if (!container) return;
    container.replaceChildren();
    const grouped = new Map();
    runs.forEach((run) => {
      const model = String(run.model || "Unknown model");
      const result = run.result || {};
      if (!grouped.has(model)) grouped.set(model, []);
      const bucket = grouped.get(model);
      if (bucket.length < 5) bucket.push(result);
    });
    const summaries = Array.from(grouped, ([model, results]) => {
      const average = (key) => {
        const values = results.map((item) => item[key]).filter(
          (value) => typeof value === "number" && Number.isFinite(value) && value >= 0
        );
        return values.length ? values.reduce((sum, value) => sum + value, 0) / values.length : null;
      };
      return {
        model,
        samples: results.length,
        latency: average("wall_time_ms"),
        speed: average("generation_tokens_per_second"),
        checks: average("instruction_following_percent")
      };
    }).sort((a, b) => (b.speed ?? -1) - (a.speed ?? -1));
    const maxSpeed = Math.max(0, ...summaries.map((item) => item.speed || 0));
    summaries.forEach((item) => {
      const card = document.createElement("article");
      card.className = "benchmark-comparison-item";
      const heading = document.createElement("strong");
      heading.textContent = item.model;
      const sample = document.createElement("small");
      sample.textContent = item.samples + " recent run(s)";
      const speedLabel = document.createElement("span");
      speedLabel.textContent = "Generation speed: " +
        (item.speed === null ? "Unavailable" : item.speed.toFixed(2) + " tok/s");
      const track = document.createElement("div");
      track.className = "benchmark-bar-track";
      track.setAttribute("role", "img");
      track.setAttribute("aria-label", item.speed === null
        ? "Generation speed unavailable"
        : "Generation speed relative to fastest listed model");
      const bar = document.createElement("div");
      bar.className = "benchmark-bar";
      bar.style.width = maxSpeed > 0 && item.speed !== null
        ? Math.max(0, Math.min(100, item.speed / maxSpeed * 100)) + "%"
        : "0%";
      track.append(bar);
      const details = document.createElement("small");
      details.textContent = "Average latency: " +
        (item.latency === null ? "Unavailable" : Math.round(item.latency) + " ms") +
        " · Instruction checks: " +
        (item.checks === null ? "Unavailable" : item.checks.toFixed(1) + "%");
      card.append(heading, sample, speedLabel, track, details);
      container.append(card);
    });
    set("benchmarkComparisonStatus", summaries.length
      ? summaries.length + "টি local model-এর তুলনা · দ্রুততম generation speed উপরে"
      : "তুলনার জন্য benchmark history নেই।");
  }

  function renderBenchmarkRegressions(runs) {
    const list = $("benchmarkRegressionList");
    if (!list) return;
    list.replaceChildren();
    const grouped = new Map();
    runs.forEach((run) => {
      const model = String(run.model || "Unknown model");
      if (!grouped.has(model)) grouped.set(model, []);
      grouped.get(model).push(run.result || {});
    });
    let compared = 0;
    let warnings = 0;
    grouped.forEach((results, model) => {
      if (results.length < 2) return;
      compared += 1;
      const latest = results[0];
      const previous = results[1];
      const issues = [];
      const latestSpeed = latest.generation_tokens_per_second;
      const previousSpeed = previous.generation_tokens_per_second;
      if (Number.isFinite(latestSpeed) && Number.isFinite(previousSpeed) && previousSpeed > 0) {
        const drop = (previousSpeed - latestSpeed) / previousSpeed * 100;
        if (drop >= 20) issues.push("Generation speed কমেছে " + drop.toFixed(1) + "%");
      }
      const latestLatency = latest.wall_time_ms;
      const previousLatency = previous.wall_time_ms;
      if (Number.isFinite(latestLatency) && Number.isFinite(previousLatency) && previousLatency > 0) {
        const rise = (latestLatency - previousLatency) / previousLatency * 100;
        if (rise >= 25) issues.push("Latency বেড়েছে " + rise.toFixed(1) + "%");
      }
      if (Number.isFinite(latest.passed_checks) && Number.isFinite(previous.passed_checks) &&
          latest.passed_checks < previous.passed_checks) {
        issues.push("Instruction checks কমেছে " + previous.passed_checks + " → " + latest.passed_checks);
      }
      if (!issues.length) return;
      warnings += 1;
      const item = document.createElement("li");
      const title = document.createElement("strong");
      title.textContent = model + ": ";
      const detail = document.createElement("span");
      detail.textContent = issues.join(" · ");
      item.append(title, detail);
      list.append(item);
    });
    set("benchmarkRegressionStatus", warnings
      ? warnings + "টি model-এ regression signal পাওয়া গেছে। নতুন benchmark দিয়ে পুনরায় যাচাই করুন।"
      : compared
        ? compared + "টি model তুলনা করা হয়েছে; নির্ধারিত threshold-এ regression signal নেই।"
        : "প্রতিটি model-এর অন্তত ২টি benchmark দরকার।");
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

  function renderResourceAdvice(metrics) {
    const list = $("resourceAdviceList");
    if (!list) return;
    list.replaceChildren();
    const suggestions = [];
    const cpu = metrics.cpu || {};
    const memory = metrics.memory || {};
    const disk = metrics.disk || {};
    const gpu = metrics.gpu || {};
    if (Number.isFinite(cpu.usage_percent)) {
      if (cpu.usage_percent >= 90) suggestions.push("CPU খুব ব্যস্ত (" + cpu.usage_percent + "%): একসঙ্গে চলা inference/job কমান এবং দীর্ঘ কাজ queue-তে চালান।");
      else if (cpu.usage_percent >= 75) suggestions.push("CPU load উঁচু (" + cpu.usage_percent + "%): concurrent chat request সীমিত রাখুন এবং benchmark idle সময়ে চালান।");
    }
    if (Number.isFinite(memory.usage_percent)) {
      if (memory.usage_percent >= 90) suggestions.push("RAM চাপের মধ্যে (" + memory.usage_percent + "%): কম parameter-এর quantized model বিবেচনা করুন এবং অপ্রয়োজনীয় process বন্ধ করুন।");
      else if (memory.usage_percent >= 80) suggestions.push("RAM ব্যবহার বেশি (" + memory.usage_percent + "%): model context length ও parallel request কমিয়ে পরীক্ষা করুন।");
    }
    if (Number.isFinite(disk.usage_percent)) {
      if (disk.usage_percent >= 95) suggestions.push("Disk প্রায় পূর্ণ (" + disk.usage_percent + "%): backup যাচাই করে পুরোনো log/cache পরিষ্কার করার পরিকল্পনা করুন; model data না বুঝে মুছবেন না।");
      else if (disk.usage_percent >= 85) suggestions.push("Disk usage বাড়ছে (" + disk.usage_percent + "%): model storage, logs ও backup-এর জায়গা পর্যবেক্ষণ করুন।");
    }
    if (gpu.available && Number.isFinite(gpu.utilization_percent) && gpu.utilization_percent >= 95) {
      suggestions.push("NVIDIA GPU utilization খুব বেশি (" + gpu.utilization_percent + "%): request queue ও batch size পর্যালোচনা করুন।");
    } else if (!gpu.available) {
      suggestions.push("NVIDIA GPU telemetry পাওয়া যায়নি: CPU inference হতে পারে ধীর; GPU আছে কি না এবং runtime support আলাদাভাবে যাচাই করুন।");
    }
    suggestions.forEach((message) => {
      const item = document.createElement("li");
      item.textContent = message;
      list.append(item);
    });
    set("resourceAdviceStatus", suggestions.length
      ? suggestions.length + "টি optimization suggestion পাওয়া গেছে।"
      : "বর্তমান metrics-এ নির্ধারিত high-resource threshold অতিক্রম করেনি।");
  }

  function renderModelRecommendations(data) {
    const advice = $("modelResourceAdvice");
    if (!advice) return;
    advice.replaceChildren();
    const host = data.host || {};
    const memory = host.memory || {};
    const gpu = host.gpu || {};
    const total = memory.total_bytes;
    const used = memory.used_bytes;
    const free = Number.isFinite(total) && Number.isFinite(used) ? Math.max(0, total - used) : null;
    const gpuFree = Number.isFinite(gpu.memory_total_mb) && Number.isFinite(gpu.memory_used_mb)
      ? Math.max(0, gpu.memory_total_mb - gpu.memory_used_mb) * 1024 * 1024 : null;
    const installed = Array.isArray(data.installed_models) ? data.installed_models : [];
    const loaded = Array.isArray(data.models) ? data.models : [];
    const loadedNames = new Set(loaded.map((item) => item.name));
    const recommendations = [];
    installed.forEach((model) => {
      const size = model.size_bytes;
      if (!Number.isFinite(size) || size <= 0) return;
      // Model file size is only a rough lower-bound proxy, not a runtime memory guarantee.
      const estimated = size * 1.35;
      const fitsRam = Number.isFinite(free) && estimated <= free * 0.70;
      const fitsGpu = Number.isFinite(gpuFree) && estimated <= gpuFree * 0.70;
      const status = loadedNames.has(model.name) ? "ইতিমধ্যে loaded"
        : fitsGpu ? "GPU memory headroom অনুযায়ী সম্ভাব্য candidate"
        : fitsRam ? "System RAM headroom অনুযায়ী সম্ভাব্য candidate"
        : "বর্তমান free memory অনুযায়ী সুপারিশ নয়";
      const item = document.createElement("li");
      const name = document.createElement("strong");
      name.textContent = model.name;
      const detail = document.createElement("span");
      detail.textContent = "Model file " + formatBytes(size) +
        " · আনুমানিক planning footprint " + formatBytes(estimated) + " · " + status;
      item.append(name, detail);
      advice.append(item);
      recommendations.push({ fitsRam, fitsGpu, loaded: loadedNames.has(model.name) });
    });
    set("modelResourceAdviceStatus", installed.length
      ? "Installed model size ও বর্তমান free RAM/GPU memory দিয়ে conservative shortlist তৈরি হয়েছে।"
      : "Installed model size পাওয়া যায়নি; recommendation করা সম্ভব নয়।");
    if (!Number.isFinite(free)) {
      const note = document.createElement("li");
      note.textContent = "Host RAM availability পাওয়া যায়নি; RAM-based fit নির্ধারণ করা হয়নি।";
      advice.append(note);
    }
    if (!Number.isFinite(gpuFree)) {
      const note = document.createElement("li");
      note.textContent = "GPU free memory telemetry পাওয়া যায়নি; GPU suitability যাচাই করা যায়নি।";
      advice.append(note);
    }
  }

  async function refreshModelResources() {
    const list = $("modelResourceList");
    const button = $("refreshModelResources");
    if (!list) return;
    if (!window.TamannaAuth?.getUser()) {
      list.replaceChildren();
      set("modelResourceStatus", "Resource তথ্য দেখতে admin account-এ লগইন করুন।");
      if (button) button.disabled = true;
      return;
    }
    if (button) button.disabled = true;
    set("modelResourceStatus", "Loaded ও installed model resource পরীক্ষা হচ্ছে…");
    try {
      const data = await getJson("/tamanna-ai/model/resources");
      const models = Array.isArray(data.models) ? data.models : [];
      list.replaceChildren();
      models.forEach((model) => {
        const item = document.createElement("li");
        const name = document.createElement("strong");
        name.textContent = model.name || "Unknown model";
        const details = document.createElement("span");
        const format = (value) => Number.isFinite(value) && value >= 0 ? formatBytes(value) : "Unavailable";
        const parts = ["Model size: " + format(model.size_bytes), "Runtime memory: " + format(model.memory_bytes)];
        if (Number.isFinite(model.context_length)) parts.push("Context: " + model.context_length);
        if (model.expires_at) parts.push("Expires: " + model.expires_at);
        details.textContent = " · " + parts.join(" · ");
        item.append(name, details);
        list.append(item);
      });
      set("modelResourceStatus", models.length
        ? models.length + "টি model বর্তমানে memory-তে loaded আছে।"
        : "এখন কোনো model memory-তে loaded নেই।");
      renderModelRecommendations(data);
    } catch (error) {
      list.replaceChildren();
      set("modelResourceStatus", "Resource তথ্য পাওয়া যায়নি: " + error.message);
      set("modelResourceAdviceStatus", "Resource তথ্য ছাড়া model recommendation তৈরি করা হয়নি।");
      $("modelResourceAdvice")?.replaceChildren();
    } finally {
      if (button) button.disabled = false;
    }
  }

  $("refreshModelResources")?.addEventListener("click", refreshModelResources);

  async function refreshModelRecovery() {
    const button = $("refreshModelRecovery");
    const actions = $("modelRecoveryActions");
    if (!actions) return;
    if (!window.TamannaAuth?.getUser()) {
      actions.replaceChildren();
      set("modelRecoveryStatus", "Recovery diagnostics দেখতে admin account-এ লগইন করুন।");
      if (button) button.disabled = true;
      return;
    }
    if (button) button.disabled = true;
    set("modelRecoveryStatus", "Local runtime ও host resource পরীক্ষা হচ্ছে…");
    try {
      const report = await getJson("/tamanna-ai/model/recovery");
      actions.replaceChildren();
      (Array.isArray(report.actions) ? report.actions : []).forEach((message) => {
        const item = document.createElement("li");
        item.textContent = message;
        actions.append(item);
      });
      const label = report.status === "healthy" ? "Healthy"
        : report.status === "offline" ? "Offline" : "Attention required";
      set("modelRecoveryStatus", label + " · " + (report.code || "unknown") +
        " · " + (report.installed_model_count ?? 0) + " installed model(s)");
    } catch (error) {
      actions.replaceChildren();
      const item = document.createElement("li");
      item.textContent = error.message;
      actions.append(item);
      set("modelRecoveryStatus", "Recovery check সম্পন্ন হয়নি।");
    } finally {
      if (button) button.disabled = false;
    }
  }

  $("refreshModelRecovery")?.addEventListener("click", refreshModelRecovery);


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
      renderResourceAdvice(metrics);
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
      await refreshModelResources();
      await refreshModelRecovery();
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
      const preflightResponse = await fetch("/tamanna-ai/model/preflight", {
        method: "POST",
        credentials: "same-origin",
        headers: { Accept: "application/json", "Content-Type": "application/json" },
        body: JSON.stringify({ model })
      });
      const preflight = await preflightResponse.json().catch(() => ({}));
      if (!preflightResponse.ok) {
        const detail = preflight.detail;
        throw new Error(typeof detail === "string" ? detail : detail?.message || "Preflight HTTP " + preflightResponse.status);
      }
      const estimate = Number.isFinite(preflight.estimated_memory_bytes)
        ? formatBytes(preflight.estimated_memory_bytes) : "অজানা";
      const available = Number.isFinite(preflight.available_memory_bytes)
        ? formatBytes(preflight.available_memory_bytes) : "অজানা";
      const warning = preflight.status === "likely_fit" ? "" : "\\n\\nসতর্কতা: " + preflight.message;
      if (!window.confirm("Model: " + model + "\\nআনুমানিক memory: " + estimate +
          "\\nবর্তমান free RAM: " + available + "\\n" + preflight.message +
          warning + "\\n\\nএটি শুধু model selection; এখনই model load হবে না। চালিয়ে যাবেন?")) {
        if (modelSelectStatus) modelSelectStatus.textContent = "Model selection বাতিল করা হয়েছে।";
        return;
      }
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
  window.addEventListener("tamanna:authenticated", refreshBenchmarkHistory);
  window.addEventListener("tamanna:loggedout", () => {
    set("healthKnowledgeStatus", "লগইন প্রয়োজন");
    set("healthKnowledgeDetail", "Private index শুধু account owner দেখতে পারবেন");
  });
  refresh();
  refreshBenchmarkHistory();
})();
