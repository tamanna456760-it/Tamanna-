/* Tamanna AI chat: authenticated local-model API + persistent conversations. */
(() => {
  "use strict";
  const $ = (id) => document.getElementById(id);
  const input = $("messageInput"), sendButton = $("sendButton"), chatBox = $("chatBox");
  const newChatButton = $("newChatButton"), conversationSelect = $("conversationSelect");
  const deleteButton = $("deleteConversationButton");
  const micButton = $("voiceInputButton"), speakButton = $("speakLatestButton");
  const voiceStatus = $("voiceStatus");
  if (!input || !sendButton || !chatBox) return;

  let conversationId = null;
  let busy = false;
  const isGitHubPagesPreview = location.hostname.endsWith(".github.io");
  const nativeVoice = window.TamannaNativeVoice;
  let browserRecognition = null;

  window.TamannaVoice = {
    onResult(text) {
      input.value = [input.value.trim(), text].filter(Boolean).join(" ");
      input.dispatchEvent(new Event("input", { bubbles: true }));
      if (voiceStatus) voiceStatus.textContent = "কথা শনাক্ত হয়েছে। পাঠাতে ↑ চাপুন।";
      input.focus();
    },
    onStatus(status) { if (voiceStatus) voiceStatus.textContent = status; },
    onError(message) { if (voiceStatus) voiceStatus.textContent = message; }
  };

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
    if (deleteButton) { deleteButton.disabled = !conversationId; deleteButton.hidden = !window.TamannaAuth?.getUser(); }
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
      const guestMode = !window.TamannaAuth?.getUser();
      const result = await api((guestMode ? "/guest/conversations/" : "/conversations/") + encodeURIComponent(id));
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
    addMessage("user", prompt);
    input.value = "";
    input.style.height = "auto";
    busy = true;
    sendButton.disabled = true;
    sendButton.textContent = "অপেক্ষা করুন…";
    const waiting = addMessage("assistant", "স্থানীয় AI মডেল উত্তর তৈরি করছে…");
    try {
      const guestMode = !window.TamannaAuth?.getUser();
      const payload = await api(guestMode ? "/guest/chat" : "/chat", {
        method: "POST",
        body: JSON.stringify({ prompt, conversation_id: conversationId, use_knowledge: true })
      });
      waiting.querySelector(".message-text").textContent =
        typeof payload.response === "string" ? payload.response : "Tamanna AI উত্তর দেয়নি।";
      if (payload.conversation_id) {
        setConversation(payload.conversation_id);
        if (guestMode) sessionStorage.setItem("tamannaGuestConversation", payload.conversation_id);
      }
      if (!guestMode) await refreshConversations();
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

  micButton?.addEventListener("click", () => {
    if (nativeVoice?.startListening) {
      nativeVoice.startListening(document.documentElement.lang === "bn" ? "bn-BD" : "en-US");
      if (voiceStatus) voiceStatus.textContent = "মাইক্রোফোন প্রস্তুত করা হচ্ছে…";
      return;
    }
    const Recognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!Recognition) {
      if (voiceStatus) voiceStatus.textContent = "এই browser-এ Speech Recognition সমর্থিত নয়। Android অ্যাপ ব্যবহার করুন।";
      return;
    }
    browserRecognition?.stop();
    browserRecognition = new Recognition();
    browserRecognition.lang = document.documentElement.lang === "bn" ? "bn-BD" : "en-US";
    browserRecognition.onresult = (event) => window.TamannaVoice.onResult(event.results[0][0].transcript);
    browserRecognition.onerror = () => window.TamannaVoice.onError("কথা শনাক্ত করা যায়নি। আবার চেষ্টা করুন।");
    browserRecognition.start();
    if (voiceStatus) voiceStatus.textContent = "বলুন, আমি শুনছি…";
  });

  speakButton?.addEventListener("click", () => {
    const latest = [...chatBox.querySelectorAll(".ai-message .message-text")].pop()?.textContent?.trim();
    if (!latest) {
      if (voiceStatus) voiceStatus.textContent = "পড়ার মতো কোনো উত্তর নেই।";
      return;
    }
    if (nativeVoice?.speak) {
      nativeVoice.speak(latest, document.documentElement.lang === "bn" ? "bn-BD" : "en-US");
      if (voiceStatus) voiceStatus.textContent = "উত্তর পড়া হচ্ছে…";
    } else if ("speechSynthesis" in window) {
      window.speechSynthesis.cancel();
      window.speechSynthesis.speak(new SpeechSynthesisUtterance(latest));
      if (voiceStatus) voiceStatus.textContent = "উত্তর পড়া হচ্ছে…";
    } else if (voiceStatus) voiceStatus.textContent = "এই browser-এ Text-to-Speech সমর্থিত নয়।";
  });

  sendButton.addEventListener("click", sendMessage);
  newChatButton?.addEventListener("click", () => {
    setConversation(null);
    sessionStorage.removeItem("tamannaGuestConversation");
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
    addMessage("assistant", "আপনি লগআউট করেছেন। এখন অতিথি হিসেবে চ্যাট চালিয়ে যেতে পারেন।");
  });
  if (window.TamannaAuth?.getUser()) refreshConversations();
  else {
    const guestConversation = sessionStorage.getItem("tamannaGuestConversation");
    if (guestConversation) openConversation(guestConversation);
  }
})();
