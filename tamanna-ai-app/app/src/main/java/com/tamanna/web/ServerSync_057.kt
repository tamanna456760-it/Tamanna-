package com.tamanna.web

import okhttp3.*

class ServerSync_057 {

    private val client = OkHttpClient()

    fun sync(url: String, json: String) {
        val body = RequestBody.create(
            MediaType.parse("application/json"), json
        )

        val request = Request.Builder()
            .url(url)
            .post(body)
            .build()

        client.newCall(request).execute()
    }
}