package com.tamanna.api

import okhttp3.*

class ApiClient_087 {

    private val client = OkHttpClient()

    fun sendMessage(msg: String, callback: (String) -> Unit) {

        val body = RequestBody.create(
            MediaType.parse("application/json"),
            """{"message":"$msg"}"""
        )

        val request = Request.Builder()
            .url("http://YOUR_IP:5000/chat")
            .post(body)
            .build()

        client.newCall(request).enqueue(object : Callback {
            override fun onFailure(call: Call, e: java.io.IOException) {
                callback("Error")
            }

            override fun onResponse(call: Call, response: Response) {
                callback(response.body()?.string() ?: "")
            }
        })
    }
}