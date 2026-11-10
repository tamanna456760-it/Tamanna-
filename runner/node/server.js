"use strict";

const express = require("express");
const WebSocket = require("ws");
const cors = require("cors");
const http = require("node:http");
const { URL } = require("node:url");

const PORT = Number.parseInt(process.env.TAMANNA_SERVER_PORT || process.env.PORT || "3000", 10);
const MAX_CLIENTS = 100;
const MAX_MESSAGE_BYTES = 16 * 1024;
const MAX_TEXT_LENGTH = 4000;
const MESSAGE_WINDOW_MS = 10_000;
const MAX_MESSAGES_PER_WINDOW = 20;
const allowedOrigins = (process.env.TAMANNA_ALLOWED_ORIGINS || "")
  .split(",").map((item) => item.trim()).filter(Boolean);

console.log("[AI] Local-only mode; inference runtime not configured");

const app = express();
app.disable("x-powered-by");
app.use(cors({ origin: allowedOrigins.length ? allowedOrigins : false }));
app.use(express.json({ limit: "16kb", strict: true }));
app.use(express.static("public"));

const clients = new Set();
const wsServer = new WebSocket.Server({
  noServer: true,
  maxPayload: MAX_MESSAGE_BYTES,
  perMessageDeflate: false
});

function makeError(message) {
  return JSON.stringify({ type: "error", message, timestamp: new Date().toISOString() });
}

function extractMessage(data, isBinary) {
  if (isBinary) throw new Error("Binary messages are not supported.");
  const raw = data.toString("utf8");
  let value = raw;
  let json = false;
  try {
    const parsed = JSON.parse(raw);
    if (!parsed || typeof parsed !== "object" || Array.isArray(parsed) ||
        typeof parsed.text !== "string") {
      throw new Error("JSON messages must contain a string text field.");
    }
    value = parsed.text;
    json = true;
  } catch (error) {
    if (error.message === "JSON messages must contain a string text field.") throw error;
    // Plain-text messages remain supported; malformed JSON-looking input is rejected.
    if (/^\s*[\[{]/.test(raw)) throw new Error("Malformed or unsupported JSON message.");
  }
  if (typeof value !== "string" || !value.trim() || value.length > MAX_TEXT_LENGTH) {
    throw new Error("Message must contain 1–4000 characters.");
  }
  return { text: value.trim(), json };
}

async function generateReply(userMessage) {
  const cmd = userMessage.toLowerCase().trim();
  if (cmd === "/help") {
    return "Available commands:\n/help – Show help\n/ai <question> – Local AI (currently unavailable)\n/echo <text> – Echo\n/server – Server info";
  }
  if (cmd === "/server") {
    return `Tamanna Server v1.0\nActive clients: ${clients.size}\nAI mode: local runtime not configured; external providers disabled`;
  }
  if (cmd.startsWith("/ai ")) {
    return "Local AI is not configured yet. External model APIs are disabled; connect and test a local model or knowledge database first.";
  }
  if (cmd.startsWith("/echo ")) return `Echo: ${userMessage.slice(6)}`;
  return `🤖 Tamanna: You said “${userMessage}” – try /help for available commands.`;
}

wsServer.on("connection", (socket) => {
  if (clients.size >= MAX_CLIENTS) {
    socket.close(1013, "Server is at capacity");
    return;
  }

  const client = { socket, windowStart: Date.now(), count: 0 };
  clients.add(client);

  const send = (payload) => {
    if (socket.readyState === WebSocket.OPEN) socket.send(payload);
  };

  send(JSON.stringify({
    type: "welcome",
    message: "Connected to Tamanna Server 🤖",
    timestamp: new Date().toISOString()
  }));

  socket.on("message", async (data, isBinary) => {
    const now = Date.now();
    if (now - client.windowStart >= MESSAGE_WINDOW_MS) {
      client.windowStart = now;
      client.count = 0;
    }
    client.count += 1;
    if (client.count > MAX_MESSAGES_PER_WINDOW) {
      send(makeError("Rate limit exceeded. Please wait before sending more messages."));
      socket.close(1008, "Message rate limit exceeded");
      return;
    }

    try {
      const { text, json } = extractMessage(data, isBinary);
      const reply = await generateReply(text);
      send(json
        ? JSON.stringify({ type: "reply", text: reply, timestamp: new Date().toISOString() })
        : reply);
    } catch (error) {
      send(makeError(error.message || "Invalid message."));
    }
  });

  socket.on("error", () => {
    // Avoid logging message contents or connection secrets.
  });
  socket.on("close", () => clients.delete(client));
});

const server = http.createServer(app);
server.on("upgrade", (req, socket, head) => {
  let pathname;
  let origin;
  try {
    const parsed = new URL(req.url, "http://localhost");
    pathname = parsed.pathname;
    origin = req.headers.origin;
  } catch {
    socket.destroy();
    return;
  }

  if (pathname !== "/ws" || clients.size >= MAX_CLIENTS ||
      (allowedOrigins.length && origin && !allowedOrigins.includes(origin))) {
    socket.write("HTTP/1.1 403 Forbidden\r\nConnection: close\r\n\r\n");
    socket.destroy();
    return;
  }

  wsServer.handleUpgrade(req, socket, head, (ws) => wsServer.emit("connection", ws, req));
});

app.get("/api/status", (_req, res) => {
  res.json({
    server: "Tamanna Server",
    status: "running",
    clients: clients.size,
    aiEnabled: false,
    aiMode: "local-runtime-not-configured",
    externalProviders: "disabled",
    timestamp: new Date().toISOString()
  });
});

if (require.main === module) {
  server.listen(PORT, "0.0.0.0", () => {
    console.log(`Tamanna HTTP/WebSocket server listening on port ${PORT}`);
  });
}

module.exports = { app, server, wsServer, generateReply, extractMessage };
