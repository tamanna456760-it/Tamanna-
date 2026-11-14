package com.tamanna.ai

import android.os.Bundle
import android.widget.*
import androidx.appcompat.app.AppCompatActivity
import okhttp3.*
import org.json.JSONObject
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

        val json = JSONObject()
        json.put("model", "gpt-3.5-turbo")
        json.put("messages", listOf(
            mapOf("role" to "user", "content" to message)
        ))

        val body = RequestBody.create(
            MediaType.parse("application/json"),
            json.toString()
        )

        val request = Request.Builder()
            .url("https://api.openai.com/v1/chat/completions")
            .addHeader("Authorization", "Bearer " + ApiConfig.API_KEY)
            .addHeader("Content-Type", "application/json")
            .post(body)
            .build()

        client.newCall(request).enqueue(object : Callback {
            override fun onFailure(call: Call, e: IOException) {
                runOnUiThread {
                    chatBox.append("\n❌ Error: ${e.message}")
                }
            }

            override fun onResponse(call: Call, response: Response) {
                val res = response.body()?.string()

                try {
                    val jsonObj = JSONObject(res)
                    val reply = jsonObj
                        .getJSONArray("choices")
                        .getJSONObject(0)
                        .getJSONObject("message")
                        .getString("content")

                    runOnUiThread {
                        chatBox.append("\nAI: $reply")
                    }
                } catch (e: Exception) {
                    runOnUiThread {
                        chatBox.append("\n❌ Parse Error")
                    }
                }
            }
        })
    }
}