// chat.js
const chatbox = document.getElementById("chatbox");
const messageInput = document.getElementById("message");
const sendBtn = document.getElementById("send");
const modeSpan = document.getElementById("mode");

let messages = []; // { role: 'user'|'assistant', content: '...' }

function appendBubble(who, text) {
  const el = document.createElement("div");
  el.className = "bubble " + (who === "user" ? "user" : "assistant");
  el.innerText = text;
  chatbox.appendChild(el);
  chatbox.scrollTop = chatbox.scrollHeight;
}

async function sendMessage() {
  const text = messageInput.value.trim();
  if (!text) return;
  appendBubble("user", text);
  messages.push({ role: "user", content: text });
  messageInput.value = "";

  appendBubble("assistant", "..."); // placeholder
  try {
    const res = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ messages }),
    });
    const data = await res.json();
    // remove last placeholder
    const placeholders = Array.from(
      document.querySelectorAll(".bubble.assistant"),
    ).filter((b) => b.innerText === "...");
    if (placeholders.length) placeholders[placeholders.length - 1].remove();

    if (data.reply) {
      appendBubble("assistant", data.reply);
      messages.push({ role: "assistant", content: data.reply });
    } else {
      appendBubble("assistant", "No reply received.");
    }
    if (data.mode) modeSpan.innerText = data.mode;
  } catch (err) {
    console.error(err);
    appendBubble("assistant", "Error contacting server.");
  }
}

sendBtn.onclick = sendMessage;
messageInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter") sendMessage();
});
