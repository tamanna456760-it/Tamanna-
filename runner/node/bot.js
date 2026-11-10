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

async function createBot({
  token = process.env.BOT_TOKEN,
  adminIds = parseAdminIds(process.env.TAMANNA_TELEGRAM_ADMIN_IDS),
  polling = false,
  BotClass
} = {}) {
  if (typeof token !== "string" || !token.trim()) {
    throw new Error("BOT_TOKEN is required to start the Telegram bot.");
  }

  // grammY's Bot API matches the command/context handlers used below.
  const TelegramBot = BotClass || (await import("grammy")).Bot;
  const bot = new TelegramBot(token);

  bot.command("start", async (ctx) => {
    await ctx.reply("🤖 Tamanna AI Bot Started");
  });

  bot.command("sync", async (ctx) => {
    const senderId = String(ctx.from && ctx.from.id ? ctx.from.id : "");
    if (!isAdminId(senderId, adminIds)) {
      await ctx.reply("⛔ এই কমান্ড ব্যবহারের অনুমতি নেই।");
      return;
    }

    try {
      const result = await githubSync();
      const reply = result && result.pushed
        ? "✅ অনুমোদিত ফাইলগুলো GitHub-এ sync হয়েছে।"
        : `ℹ️ GitHub push করা হয়নি: ${(result && result.reason) || "কোনো পরিবর্তন নেই।"}`;
      await ctx.reply(reply);
    } catch (error) {
      console.error("Telegram /sync failed:", error.message);
      await ctx.reply("❌ নিরাপত্তা যাচাই বা sync ব্যর্থ হয়েছে।");
    }
  });

  bot.on("message:text", async (ctx) => {
    const msg = ctx.message || {};
    if (typeof msg.text !== "string" || msg.text.startsWith("/") || !msg.text.trim()) return;
    if (msg.text.length > 4000) {
      await ctx.reply("বার্তাটি অনেক বড়। সর্বোচ্চ ৪০০০ অক্ষর পাঠান।");
      return;
    }

    try {
      const reply = await askAI(msg.text);
      await ctx.reply(reply);
    } catch (error) {
      console.error("Telegram AI reply unavailable:", error.message);
      await ctx.reply(
        "স্থানীয় AI runtime পাওয়া যাচ্ছে না। Ollama চালু আছে এবং নির্বাচিত model ইনস্টল করা আছে কি না যাচাই করুন। বাহ্যিক AI API বন্ধ আছে।"
      );
    }
  });

  bot.catch((error) => {
    console.error("Telegram bot update failed:", error.message);
  });

  // grammY starts long polling with bot.start(); it has no startPolling() API.
  if (polling) await bot.start();
  return bot;
}

if (require.main === module) {
  require("dotenv").config();
  createBot({ polling: true }).catch((error) => {
    console.error("Telegram bot startup failed:", error.message);
    process.exitCode = 1;
  });
}

module.exports = { createBot, parseAdminIds, isAdminId };
