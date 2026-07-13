/**
 * Hook.js - Universal Frontend Hook System
 * For UI events, performance tracking, and analytics (safe use only)
 */

const Hook = {
  config: {
    logToConsole: true,
    sendToServer: false,
    endpoint: "/api/hook"
  },

  // =========================
  // INIT
  // =========================
  init: function () {
    this.trackClicks();
    this.trackErrors();
    this.trackPerformance();
    this.trackPageLoad();

    if (this.config.logToConsole) {
      console.log("🔥 Hook.js initialized");
    }
  },

  // =========================
  // CLICK TRACKING
  // =========================
  trackClicks: function () {
    document.addEventListener("click", (e) => {
      const data = {
        type: "click",
        time: new Date().toISOString(),
        tag: e.target.tagName,
        id: e.target.id || null,
        class: e.target.className || null
      };

      Hook.log(data);
    });
  },

  // =========================
  // ERROR TRACKING
  // =========================
  trackErrors: function () {
    window.addEventListener("error", (e) => {
      const data = {
        type: "error",
        time: new Date().toISOString(),
        message: e.message,
        file: e.filename,
        line: e.lineno
      };

      Hook.log(data);
    });
  },

  // =========================
  // PERFORMANCE TRACKING
  // =========================
  trackPerformance: function () {
    window.addEventListener("load", () => {
      setTimeout(() => {
        const perf = performance.timing;

        const data = {
          type: "performance",
          time: new Date().toISOString(),
          loadTime: perf.loadEventEnd - perf.navigationStart,
          domReady: perf.domContentLoadedEventEnd - perf.navigationStart
        };

        Hook.log(data);
      }, 0);
    });
  },

  // =========================
  // PAGE LOAD TRACKING
  // =========================
  trackPageLoad: function () {
    const data = {
      type: "page_load",
      time: new Date().toISOString(),
      url: window.location.href,
      referrer: document.referrer
    };

    Hook.log(data);
  },

  // =========================
  // LOG HANDLER
  // =========================
  log: function (data) {
    if (this.config.logToConsole) {
      console.log("📊 Hook Event:", data);
    }

    if (this.config.sendToServer) {
      fetch(this.config.endpoint, {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify(data)
      }).catch(err => console.error("Hook send error:", err));
    }
  }
};

// =========================
// AUTO START
// =========================
document.addEventListener("DOMContentLoaded", () => {
  Hook.init();
});