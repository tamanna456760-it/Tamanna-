package com.tamanna.bot

import android.os.Bundle
import android.widget.Button
import android.widget.EditText
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity

class BotChatActivity_005 : AppCompatActivity() {

    lateinit var input: EditText
    lateinit var sendBtn: Button
    lateinit var chatBox: TextView
    private val bot = BotEngine_001(BotConfig_003.BOT_API_KEY)

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_bot_chat)

        input = findViewById(R.id.inputText)
        sendBtn = findViewById(R.id.sendBtn)
        chatBox = findViewById(R.id.chatBox)

        sendBtn.setOnClickListener {
            val msg = input.text.toString()
            chatBox.append("You: $msg\nBot: ...\n")
            bot.sendMessage(msg) { reply ->
                runOnUiThread { chatBox.append("Bot: $reply\n") }
            }
        }
    }
}