"use strict";

require("dotenv").config();

const TelegramBot = require("node-telegram-bot-api");
const { askAI } = require("./ai.js");
const { githubSync } = require("./github.js");

const token = process.env.BOT_TOKEN;
if (!token) {
  throw new Error("BOT_TOKEN is required to start the Telegram bot.");
}

const adminIds = new Set(
  (process.env.TAMANNA_TELEGRAM_ADMIN_IDS || "")
    .split(",")
    .map((id) => id.trim())
    .filter(Boolean)
);

const bot = new TelegramBot(token, { polling: true });

bot.onText(/\/start/, (msg) =>
  bot.sendMessage(msg.chat.id, "🤖 Tamanna AI Bot Started")
);

bot.onText(/\/sync(?:@\w+)?$/, async (msg) => {
  const senderId = String(msg.from && msg.from.id ? msg.from.id : "");
  if (!senderId || !adminIds.has(senderId)) {
    await bot.sendMessage(msg.chat.id, "⛔ এই কমান্ড ব্যবহারের অনুমতি নেই।");
    return;
  }

  try {
    const result = await githubSync();
    const reply = result && result.pushed
      ? "✅ অনুমোদিত ফাইলগুলো GitHub-এ sync হয়েছে।"
      : `ℹ️ GitHub push করা হয়নি: ${(result && result.reason) || "কোনো পরিবর্তন নেই।"}`;
    await bot.sendMessage(msg.chat.id, reply);
  } catch (error) {
    console.error("Telegram /sync failed:", error);
    await bot.sendMessage(msg.chat.id, "❌ নিরাপত্তা যাচাই বা sync ব্যর্থ হয়েছে। বিস্তারিত সার্ভার লগে আছে।");
  }
});

bot.on("message", async (msg) => {
  if (typeof msg.text !== "string" || msg.text.startsWith("/")) return;

  try {
    const reply = await askAI(msg.text);
    await bot.sendMessage(msg.chat.id, reply);
  } catch (error) {
    console.error("Telegram AI reply failed:", error.message);
    await bot.sendMessage(
      msg.chat.id,
      "স্থানীয় AI runtime এখনো কনফিগার করা হয়নি। বাহ্যিক AI API বন্ধ আছে।"
    );
  }
});

module.exports = { bot };
