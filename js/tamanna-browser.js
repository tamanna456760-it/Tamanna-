/* Tamanna AI Web Browser: user-initiated HTTPS navigation and search.
 * Remote pages run in a sandboxed, cross-origin iframe. This app cannot read
 * their contents, bypass site frame restrictions, or access local/private hosts.
 */
(() => {
  "use strict";
  const $ = id => document.getElementById(id);
  const panel = $("tamannaBrowserPanel");
  const toggle = $("openBrowser");
  const close = $("closeBrowser");
  const address = $("browserAddress");
  const go = $("browserGo");
  const newTab = $("browserNewTab");
  const frame = $("browserFrame");
  const searchInput = $("browserSearch");
  const searchButton = $("browserSearchButton");
  const status = $("browserStatus");
  if (!panel || !toggle || !address || !frame || !status) return;

  function setStatus(message, error = false) {
    status.textContent = message;
    status.dataset.state = error ? "error" : "ok";
  }

  function safeUrl(value) {
    let url;
    try {
      url = new URL(value.trim().includes("://") ? value.trim() : "https://" + value.trim());
    } catch (_) {
      throw new Error("একটি সঠিক website address লিখুন।");
    }
    if (url.protocol !== "https:") throw new Error("নিরাপত্তার জন্য শুধু HTTPS website খোলা যাবে।");
    if (url.username || url.password) throw new Error("URL-এর মধ্যে username/password গ্রহণ করা হয় না।");
    const host = url.hostname.toLowerCase().replace(/^\[|\]$/g, "");
    if (!host || host === "localhost" || host.endsWith(".localhost") || host.endsWith(".local") ||
        host === "0.0.0.0" || host === "::1" || host === "::" ||
        /^127\./.test(host) || /^10\./.test(host) || /^192\.168\./.test(host) ||
        /^169\.254\./.test(host) || /^172\.(1[6-9]|2\d|3[01])\./.test(host)) {
      throw new Error("Local বা private network address এই browser-এ অনুমোদিত নয়।");
    }
    return url;
  }

  function navigate(openInNewTab) {
    try {
      const url = safeUrl(address.value);
      if (openInNewTab) {
        const opened = window.open(url.href, "_blank", "noopener,noreferrer");
        if (!opened) setStatus("Popup বন্ধ আছে। Browser permission দিন অথবা Go চাপুন।", true);
        else setStatus("নতুন tab-এ website খোলা হয়েছে।");
      } else {
        frame.src = url.href;
        setStatus("Website load হচ্ছে। কিছু site iframe embedding বন্ধ রাখতে পারে; তখন Open in new tab ব্যবহার করুন।");
      }
    } catch (error) {
      setStatus(error.message, true);
    }
  }

  function searchWeb() {
    const query = searchInput?.value.trim();
    if (!query) {
      setStatus("Search করার জন্য একটি শব্দ লিখুন।", true);
      searchInput?.focus();
      return;
    }
    const url = "https://duckduckgo.com/?q=" + encodeURIComponent(query);
    const opened = window.open(url, "_blank", "noopener,noreferrer");
    if (!opened) setStatus("Popup বন্ধ আছে। Search tab খোলার অনুমতি দিন।", true);
    else setStatus("DuckDuckGo search নতুন tab-এ খোলা হয়েছে।");
  }

  function showPanel() {
    panel.hidden = false;
    toggle.setAttribute("aria-expanded", "true");
    address.focus();
  }
  function hidePanel() {
    panel.hidden = true;
    toggle.setAttribute("aria-expanded", "false");
    toggle.focus();
  }

  toggle.addEventListener("click", showPanel);
  close?.addEventListener("click", hidePanel);
  go?.addEventListener("click", () => navigate(false));
  newTab?.addEventListener("click", () => navigate(true));
  searchButton?.addEventListener("click", searchWeb);
  address.addEventListener("keydown", event => {
    if (event.key === "Enter") navigate(false);
  });
  searchInput?.addEventListener("keydown", event => {
    if (event.key === "Enter") searchWeb();
  });
  frame.addEventListener("load", () => {
    if (frame.src && frame.src !== "about:blank") setStatus("Page load শেষ। Cross-origin page-এর content এই app পড়তে পারে না।");
  });
  panel.addEventListener("keydown", event => {
    if (event.key === "Escape") hidePanel();
  });
  window.TamannaBrowser = Object.freeze({
    open: showPanel,
    close: hidePanel,
    navigate: value => {
      address.value = String(value || "");
      navigate(false);
    }
  });
})();