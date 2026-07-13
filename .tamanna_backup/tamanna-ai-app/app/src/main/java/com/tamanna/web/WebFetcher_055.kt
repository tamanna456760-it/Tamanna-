package com.tamanna.web

import okhttp3.*
import java.io.IOException

class WebFetcher_055 {

    private val client = OkHttpClient()

    fun fetch(url: String, callback: (String) -> Unit) {
        val request = Request.Builder().url(url).build()

        client.newCall(request).enqueue(object : Callback {
            override fun onFailure(call: Call, e: IOException) {
                callback("❌ Error: ${e.message}")
            }

            override fun onResponse(call: Call, response: Response) {
                callback(response.body()?.string() ?: "")
            }
        })
    }
}