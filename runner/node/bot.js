"use strict";

const { askAI } = require("./ai.js");
const { githubSync } = require("./github.js");

function parseAdminIds(value = "") {
  return new Set(
    String(value).split(",").map((id) => id.trim()).filter((id) => /^\d+$/.test(id))
  );
}

function isAdminId(senderId, adminIds) {
  return typeof senderId === "string" && adminIds instanceof Set && adminIds.has(senderId);
}

function createBot({ token = process.env.BOT_TOKEN, adminIds = parseAdminIds(process.env.TAMANNA_TELEGRAM_ADMIN_IDS), polling = false } = {}) {
  if (typeof token !== "string" || !token.trim()) {
    throw new Error("BOT_TOKEN is required to start the Telegram bot.");
  }

  // Load Telegram SDK only when an explicitly started bot is requested.
  const TelegramBot = require("node-telegram-bot-api");
  const bot = new TelegramBot(token, { polling });

  bot.onText(/^\/start(?:@\w+)?$/, (msg) =>
    bot.sendMessage(msg.chat.id, "🤖 Tamanna AI Bot Started")
  );

  bot.onText(/^\/sync(?:@\w+)?$/, async (msg) => {
    const senderId = String(msg.from && msg.from.id ? msg.from.id : "");
    if (!isAdminId(senderId, adminIds)) {
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
      console.error("Telegram /sync failed:", error.message);
      await bot.sendMessage(msg.chat.id, "❌ নিরাপত্তা যাচাই বা sync ব্যর্থ হয়েছে।");
    }
  });

  bot.on("message", async (msg) => {
    if (typeof msg.text !== "string" || msg.text.startsWith("/") || !msg.text.trim()) return;
    if (msg.text.length > 4000) {
      await bot.sendMessage(msg.chat.id, "বার্তাটি অনেক বড়। সর্বোচ্চ ৪০০০ অক্ষর পাঠান।");
      return;
    }

    try {
      const reply = await askAI(msg.text);
      await bot.sendMessage(msg.chat.id, reply);
    } catch (error) {
      console.error("Telegram AI reply unavailable:", error.message);
      await bot.sendMessage(
        msg.chat.id,
        "স্থানীয় AI runtime এখনো কনফিগার করা হয়নি। বাহ্যিক AI API বন্ধ আছে।"
      );
    }
  });

  bot.on("polling_error", (error) => {
    console.error("Telegram polling error:", error.message);
  });

  return bot;
}

if (require.main === module) {
  require("dotenv").config();
  try {
    createBot({ polling: true });
  } catch (error) {
    console.error("Telegram bot startup failed:", error.message);
    process.exitCode = 1;
  }
}

module.exports = { createBot, parseAdminIds, isAdminId };
