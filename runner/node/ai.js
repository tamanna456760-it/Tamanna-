"use strict";

require("dotenv").config();

const OpenAI = require("openai");

let client;

function getClient() {
  if (client) return client;

  const apiKey = process.env.OPENAI_API_KEY;
  if (!apiKey) {
    throw new Error("OPENAI_API_KEY is not configured.");
  }

  client = new OpenAI({ apiKey });
  return client;
}

async function askAI(message) {
  if (typeof message !== "string" || !message.trim()) {
    throw new TypeError("message must be a non-empty string.");
  }

  const response = await getClient().chat.completions.create({
    model: process.env.OPENAI_MODEL || "gpt-4o-mini",
    messages: [
      { role: "system", content: "You are Tamanna AI assistant." },
      { role: "user", content: message.trim() },
    ],
  });

  return response.choices?.[0]?.message?.content || "";
}

exports.askAI = askAI;
