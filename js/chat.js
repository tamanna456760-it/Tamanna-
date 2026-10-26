/* Tamanna AI Chat Client */
(() => {
  "use strict";

  const input = document.getElementById("messageInput");
  const sendButton = document.getElementById("sendButton");
  const chatBox = document.getElementById("chatBox");

  if (!input || !sendButton || !chatBox) return;

  function addMessage(role, text) {
    const article = document.createElement("div");

    article.className =
      "message " +
      (role === "user" ? "user-message" : "ai-message");

    const name = document.createElement("div");
    name.className = "message-name";
    name.textContent =
      role === "user" ? "আপনি" : "Tamanna AI";

    const body = document.createElement("div");
    body.className = "message-text";
    body.textContent = String(text ?? "");

    article.append(name, body);
    chatBox.appendChild(article);
    chatBox.scrollTop = chatBox.scrollHeight;

    return article;
  }

  async function sendMessage() {
    const message = input.value.trim();

    if (!message || sendButton.disabled) return;

    addMessage("user", message);

    input.value = "";
    sendButton.disabled = true;
    sendButton.textContent = "অপেক্ষা করুন…";

    const waiting = addMessage(
      "assistant",
      "উত্তর তৈরি হচ্ছে…"
    );

    try {
      const response = await fetch("/api/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Accept": "application/json"
        },
        body: JSON.stringify({ message })
      });

      const payload = await response.json().catch(
        () => ({})
      );

      if (!response.ok) {
        throw new Error(
          payload.detail ||
          payload.error ||
          ("HTTP " + response.status)
        );
      }

      const reply =
        typeof payload.reply === "string"
          ? payload.reply
          : "Tamanna AI থেকে উত্তর পাওয়া যায়নি।";

      waiting.querySelector(
        ".message-text"
      ).textContent = reply;

    } catch (error) {
      const body = waiting.querySelector(
        ".message-text"
      );

      body.textContent =
        "সার্ভারের সঙ্গে সংযোগ করা যায়নি। " +
        "FastAPI server চালু আছে কি না দেখুন.\n" +
        "বিস্তারিত: " +
        (error.message || "Network error");

      body.classList.add("tamanna-error");

    } finally {
      sendButton.disabled = false;
      sendButton.textContent = "Send";
      input.focus();
      chatBox.scrollTop = chatBox.scrollHeight;
    }
  }

  sendButton.addEventListener("click", sendMessage);

  input.addEventListener("keydown", event => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      sendMessage();
    }
  });
})();
