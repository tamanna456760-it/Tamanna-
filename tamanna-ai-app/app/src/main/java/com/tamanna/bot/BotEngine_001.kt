package com.tamanna.bot

import okhttp3.*
import org.json.JSONObject
import java.io.IOException

class BotEngine_001(private val apiKey: String) {

    private val client = OkHttpClient()

    fun sendMessage(message: String, callback: (String) -> Unit) {
        val json = JSONObject()
        json.put("model", "gpt-3.5-turbo")
        json.put("messages", listOf(mapOf("role" to "user", "content" to message)))

        val body = RequestBody.create(MediaType.parse("application/json"), json.toString())
        val request = Request.Builder()
            .url("https://api.openai.com/v1/chat/completions")
            .addHeader("Authorization", "Bearer $apiKey")
            .addHeader("Content-Type", "application/json")
            .post(body)
            .build()

        client.newCall(request).enqueue(object: Callback {
            override fun onFailure(call: Call, e: IOException) {
                callback("❌ Bot Error: ${e.message}")
            }
            override fun onResponse(call: Call, response: Response) {
                val res = response.body()?.string()
                try {
                    val reply = JSONObject(res)
                        .getJSONArray("choices")
                        .getJSONObject(0)
                        .getJSONObject("message")
                        .getString("content")
                    callback(reply)
                } catch (e: Exception) {
                    callback("❌ Parse Error")
                }
            }
        })
    }
}