package com.tamanna.ai

import android.os.Bundle
import android.widget.*
import androidx.appcompat.app.AppCompatActivity
import okhttp3.*
import java.io.IOException

class TamannaChat : AppCompatActivity() {

    lateinit var input: EditText
    lateinit var sendBtn: Button
    lateinit var chatBox: TextView

    val client = OkHttpClient()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.tamanna_chat)

        input = findViewById(R.id.inputText)
        sendBtn = findViewById(R.id.sendBtn)
        chatBox = findViewById(R.id.chatBox)

        sendBtn.setOnClickListener {
            val userMsg = input.text.toString()
            chatBox.text = "You: $userMsg\nAI: thinking..."

            sendToAI(userMsg)
        }
    }

    private fun sendToAI(message: String) {
        val request = Request.Builder()
            .url("https://api.github.com") // demo API
            .build()

        client.newCall(request).enqueue(object : Callback {
            override fun onFailure(call: Call, e: IOException) {
                runOnUiThread {
                    chatBox.append("\n❌ Network Error")
                }
            }

            override fun onResponse(call: Call, response: Response) {
                runOnUiThread {
                    chatBox.append("\nAI: Hello! I am Tamanna AI 🤖")
                }
            }
        })
    }
}