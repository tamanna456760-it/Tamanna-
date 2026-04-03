// server.js
require("dotenv").config();
const express = require("express");
const cors = require("cors");
const fetch = require("node-fetch");
const path = require("path");

const app = express();
app.use(cors());
app.use(express.json());
app.use(express.static("public"));

const PORT = process.env.PORT || 8080;
const AI_MODE = (process.env.AI_MODE || "local").toLowerCase();
const OPENAI_API_KEY = process.env.OPENAI_API_KEY || "";

// ---------- power modules (existing) ----------
const normal = require("./powerhub/normal");
const medium = require("./powerhub/medium");
const deep = require("./powerhub/deep");
const dark = require("./powerhub/dark");
const underground = require("./powerhub/underground");
const silent = require("./powerhub/silent_supersonic");
const stone = require("./powerhub/stone_spirit");

app.get("/power/normal", (req, res) => res.json(normal()));
app.get("/power/medium", (req, res) => res.json(medium()));
app.get("/power/deep", (req, res) => res.json(deep()));
app.get("/power/dark", (req, res) => res.json(dark()));
app.get("/power/underground", (req, res) => res.json(underground()));
app.get("/power/silent", (req, res) => res.json(silent()));
app.get("/power/stone", (req, res) => res.json(stone()));

// Serve landing & chat pages
app.get("/", (req, res) =>
  res.sendFile(path.join(__dirname, "public/index.html")),
);
app.get("/chat", (req, res) =>
  res.sendFile(path.join(__dirname, "public/chat.html")),
);

// ---------- Chat API ----------
/*
Request:
  POST /api/chat
  { "messages": [ { "role":"user", "content":"..." }, ... ] }
Response:
  { "reply": "text", "mode": "openai|local" }
*/
app.post("/api/chat", async (req, res) => {
  try {
    const messages = req.body.messages || [];
    if (!Array.isArray(messages))
      return res.status(400).json({ error: "messages must be an array" });

    // Build prompt text from messages (simple)
    const conversation = messages
      .map((m) => `${m.role === "user" ? "User" : "Assistant"}: ${m.content}`)
      .join("\n");

    if (AI_MODE === "openai" && OPENAI_API_KEY) {
      // Call OpenAI REST API (chat completion) — keep minimal to avoid library dependency
      const payload = {
        model: "gpt-4o-mini", // generic example; you can change to gpt-4o or gpt-4o-mini
        messages: messages,
        max_tokens: 600,
        temperature: 0.7,
      };

      const resp = await fetch("https://api.openai.com/v1/chat/completions", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${OPENAI_API_KEY}`,
        },
        body: JSON.stringify(payload),
      });

      if (!resp.ok) {
        const txt = await resp.text();
        console.error("OpenAI error:", resp.status, txt);
        return res
          .status(502)
          .json({ error: "OpenAI API error", details: txt });
      }

      const data = await resp.json();
      const reply =
        (data.choices &&
          data.choices[0] &&
          data.choices[0].message &&
          data.choices[0].message.content) ||
        "Sorry — no response.";
      return res.json({ reply, mode: "openai" });
    }

    // ---------- Local fallback bot ----------
    const reply = localBotReply(
      conversation,
      messages[messages.length - 1]
        ? messages[messages.length - 1].content
        : "",
    );
    return res.json({ reply, mode: "local" });
  } catch (err) {
    console.error("Chat error:", err);
    res.status(500).json({ error: "Server error" });
  }
});

// ---------- Local simple bot logic ----------
function localBotReply(conversationText, lastUserContent) {
  // Simple rule-based replies for common queries.
  const lc = lastUserContent.toLowerCase();

  if (!lastUserContent || lc.trim().length === 0) {
    return "Hello — I'm Tamanna AI. Ask me anything about BD-KING-R7 or type 'help'.";
  }
  if (lc.includes("hello") || lc.includes("hi"))
    return "Hi! Tamanna AI here. How can I assist your BD-KING-R7 today?";
  if (lc.includes("power") && lc.includes("normal"))
    return "Normal Power selected — lightweight mode active.";
  if (lc.includes("power") && lc.includes("deep"))
    return "Deep Power engaged — increasing compute and persistence.";
  if (lc.includes("deploy") || lc.includes("deploying"))
    return "To deploy, push to main and pipelines will trigger. Need a deployment script?";
  if (lc.includes("help"))
    return "I can: show power modes, run builds, or explain system files. Try: 'Show power modes' or 'Run auto-sync'.";
  if (lc.includes("tamanna"))
    return "Tamanna AI — your BD-KING-R7 assistant. Ask me to run scripts, explain code, or manage power levels.";
  if (lc.includes("who are you"))
    return "I am Tamanna AI, an assistant for the BD-KING-R7 system.";

  // fallback short creative reply:
  return "Got it. Tamanna AI thinks: " + summarizeShort(lastUserContent);
}

function summarizeShort(text) {
  if (text.length > 120) return text.slice(0, 117) + "...";
  return "» " + text;
}

// ---------- Start server ----------
app.listen(PORT, () => {
  console.log(`PowerHub + AI running on port ${PORT}  (AI_MODE=${AI_MODE})`);
});
