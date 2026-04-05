package com.tamanna.intelli

import com.tamanna.bot.BotManager_002
import com.tamanna.bot.BotEngine_001

class MultiBotController_020 {

    private val botManager = BotManager_002()

    fun initBots(number: Int, apiKey: String) {
        repeat(number) {
            val bot = BotEngine_001(apiKey)
            botManager.addBot(bot)
        }
    }

    fun broadcastMessage(message: String, callback: (String) -> Unit) {
        botManager.broadcastMessage(message) { reply ->
            callback(reply)
        }
    }
}