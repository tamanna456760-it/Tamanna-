package com.tamanna.ai

import android.os.Bundle
import android.widget.*
import androidx.appcompat.app.AppCompatActivity
import okhttp3.*
import java.io.IOException

class TamannaMain : AppCompatActivity() {

    lateinit var resultText: TextView
    lateinit var scanBtn: Button
    val client = OkHttpClient()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.tamanna_main)

        resultText = findViewById(R.id.resultText)
        scanBtn = findViewById(R.id.scanBtn)

        scanBtn.setOnClickListener {
            runAI()
        }
    }

    private fun runAI() {
        val request = Request.Builder()
            .url("https://api.github.com")
            .build()

        client.newCall(request).enqueue(object : Callback {
            override fun onFailure(call: Call, e: IOException) {
                runOnUiThread {
                    resultText.text = "❌ Network Error!"
                }
            }

            override fun onResponse(call: Call, response: Response) {
                runOnUiThread {
                    resultText.text = "🌐 AI Connected!"

val chatBtn = findViewById<Button>(R.id.chatBtn)

chatBtn.setOnClickListener {
    startActivity(Intent(this, TamannaChat::class.java))
}
                }
            }
        })
    }
}