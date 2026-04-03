import TelegramBot from 'node-telegram-bot-api'
import { askAI } from '../ai/ai.js'
import { githubSync } from '../github/sync.js'

const bot = new TelegramBot(process.env.BOT_TOKEN,{polling:true})

bot.onText(/\/start/, msg => bot.sendMessage(msg.chat.id,"🤖 Tamanna AI Bot Started"))
bot.onText(/\/sync/, async msg => {
await githubSync()
bot.sendMessage(msg.chat.id,"🌐 GitHub Synced")
})
bot.on("message", async msg => {
if(msg.text.startsWith("/")) return
const reply = await askAI(msg.text)
bot.sendMessage(msg.chat.id, reply)
})