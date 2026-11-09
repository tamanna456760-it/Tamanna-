/* Tamanna AI chat: authenticated local-model API + persistent conversations. */
(() => {
  "use strict";
  const $ = (id) => document.getElementById(id);
  const input = $("messageInput"), sendButton = $("sendButton"), chatBox = $("chatBox");
  const newChatButton = $("newChatButton"), conversationSelect = $("conversationSelect");
  const deleteButton = $("deleteConversationButton");
  if (!input || !sendButton || !chatBox) return;

  let conversationId = null;
  let busy = false;
  const isGitHubPagesPreview = location.hostname.endsWith(".github.io");

  if (isGitHubPagesPreview) {
    input.placeholder = "GitHub Pages Preview — backend সংযুক্ত হলে chat চালু হবে";
    addMessage("assistant", "GitHub Pages Preview Mode: ওয়েবসাইটের interface চালু আছে। বাস্তব AI উত্তর, login ও chat history চালাতে private FastAPI backend এবং local Ollama server সংযুক্ত করতে হবে।");
  }

  async function api(path, options = {}) {
    const response = await fetch("/tamanna-ai" + path, {
      credentials: "same-origin",
      ...options,
      headers: { Accept: "application/json", "Content-Type": "application/json", ...(options.headers || {}) }
    });
    const payload = await response.json().catch(() => ({}));
    if (!response.ok) {
      const detail = payload.detail;
      throw new Error(typeof detail === "string" ? detail : detail?.message || "HTTP " + response.status);
    }
    return payload;
  }

  function addMessage(role, text) {
    const article = document.createElement("div");
    article.className = "message " + (role === "user" ? "user-message" : "ai-message");
    const name = document.createElement("div");
    name.className = "message-name";
    name.textContent = role === "user" ? "আপনি" : "Tamanna AI";
    const body = document.createElement("div");
    body.className = "message-text";
    body.textContent = String(text ?? "");
    article.append(name, body);
    chatBox.append(article);
    chatBox.scrollTop = chatBox.scrollHeight;
    return article;
  }

  function setConversation(id) {
    conversationId = id || null;
    if (conversationSelect) conversationSelect.value = conversationId || "";
    if (deleteButton) deleteButton.disabled = !conversationId;
  }

  async function refreshConversations() {
    if (!window.TamannaAuth?.getUser() || !conversationSelect) return;
    try {
      const result = await api("/conversations");
      const selected = conversationId;
      conversationSelect.replaceChildren();
      const fresh = document.createElement("option");
      fresh.value = "";
      fresh.textContent = "নতুন কথোপকথন";
      conversationSelect.append(fresh);
      (result.conversations || []).forEach((item) => {
        const option = document.createElement("option");
        option.value = item.id;
        option.textContent = item.title || ("কথোপকথন · " + new Date(item.updated_at).toLocaleString());
        conversationSelect.append(option);
      });
      if (selected && [...conversationSelect.options].some(option => option.value === selected)) {
        conversationSelect.value = selected;
      }
      if (deleteButton) deleteButton.disabled = !conversationId;
    } catch (error) {
      addMessage("assistant", "কথোপকথনের তালিকা লোড হয়নি: " + error.message);
    }
  }

  async function openConversation(id) {
    if (!id) {
      setConversation(null);
      chatBox.replaceChildren();
      addMessage("assistant", "নতুন কথোপকথন শুরু হলো। কীভাবে সাহায্য করতে পারি?");
      return;
    }
    try {
      const result = await api("/conversations/" + encodeURIComponent(id));
      chatBox.replaceChildren();
      (result.messages || []).slice().reverse().forEach((pair) => {
        if (pair.user !== undefined) addMessage("user", pair.user);
        if (pair.assistant !== undefined) addMessage("assistant", pair.assistant);
      });
      setConversation(result.conversation_id);
    } catch (error) {
      addMessage("assistant", "কথোপকথন খোলা যায়নি: " + error.message);
    }
  }

  async function sendMessage() {
    const prompt = input.value.trim();
    if (!prompt || busy) return;
    if (isGitHubPagesPreview) {
      addMessage("assistant", "এই GitHub Pages preview-তে AI request পাঠানো হচ্ছে না। Backend host ও নিরাপদ API route সংযুক্ত হলে chat চালু হবে।");
      return;
    }
    if (!window.TamannaAuth?.getUser()) {
      addMessage("assistant", "চ্যাট করতে প্রথমে লগইন করুন। উপরের লগইন বোতাম চাপুন।");
      return;
    }
    addMessage("user", prompt);
    input.value = "";
    input.style.height = "auto";
    busy = true;
    sendButton.disabled = true;
    sendButton.textContent = "অপেক্ষা করুন…";
    const waiting = addMessage("assistant", "স্থানীয় AI মডেল উত্তর তৈরি করছে…");
    try {
      const payload = await api("/chat", {
        method: "POST",
        body: JSON.stringify({ prompt, conversation_id: conversationId, use_knowledge: true })
      });
      waiting.querySelector(".message-text").textContent =
        typeof payload.response === "string" ? payload.response : "Tamanna AI উত্তর দেয়নি।";
      if (payload.conversation_id) setConversation(payload.conversation_id);
      await refreshConversations();
    } catch (error) {
      waiting.querySelector(".message-text").textContent =
        "উত্তর পাওয়া যায়নি: " + error.message +
        (error.message.includes("401") ? " — আবার লগইন করুন।" : "");
      waiting.querySelector(".message-text").classList.add("tamanna-error");
    } finally {
      busy = false;
      sendButton.disabled = false;
      sendButton.textContent = "↑";
      input.focus();
      chatBox.scrollTop = chatBox.scrollHeight;
    }
  }

  sendButton.addEventListener("click", sendMessage);
  newChatButton?.addEventListener("click", () => {
    setConversation(null);
    if (conversationSelect) conversationSelect.value = "";
    chatBox.replaceChildren();
    addMessage("assistant", "নতুন কথোপকথন শুরু হলো। কীভাবে সাহায্য করতে পারি?");
    input.value = "";
    input.focus();
  });
  conversationSelect?.addEventListener("change", () => openConversation(conversationSelect.value));
  deleteButton?.addEventListener("click", async () => {
    if (!conversationId || !window.confirm("এই কথোপকথন এবং এর বার্তা স্থায়ীভাবে মুছে ফেলবেন?")) return;
    deleteButton.disabled = true;
    try {
      await api("/conversations/" + encodeURIComponent(conversationId), { method: "DELETE" });
      setConversation(null);
      await refreshConversations();
      await openConversation(null);
    } catch (error) {
      addMessage("assistant", "কথোপকথন মুছতে ব্যর্থ: " + error.message);
      deleteButton.disabled = false;
    }
  });
  input.addEventListener("input", () => {
    input.style.height = "auto";
    input.style.height = Math.min(input.scrollHeight, 180) + "px";
  });
  input.addEventListener("keydown", event => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      sendMessage();
    }
  });
  window.addEventListener("tamanna:authenticated", refreshConversations);
  window.addEventListener("tamanna:loggedout", () => {
    setConversation(null);
    if (conversationSelect) conversationSelect.replaceChildren();
    chatBox.replaceChildren();
    addMessage("assistant", "আপনি লগআউট করেছেন। আবার চ্যাট করতে লগইন করুন।");
  });
  if (window.TamannaAuth?.getUser()) refreshConversations();
})();
