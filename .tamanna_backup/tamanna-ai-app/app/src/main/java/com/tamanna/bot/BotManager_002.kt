package com.tamanna.bot

class BotManager_002 {

    private val bots = mutableListOf<BotEngine_001>()

    fun addBot(bot: BotEngine_001) {
        bots.add(bot)
    }

    fun broadcastMessage(message: String, callback: (String) -> Unit) {
        for (bot in bots) {
            bot.sendMessage(message) { reply ->
                callback(reply)
            }
        }
    }

    fun getBotCount(): Int = bots.size
}