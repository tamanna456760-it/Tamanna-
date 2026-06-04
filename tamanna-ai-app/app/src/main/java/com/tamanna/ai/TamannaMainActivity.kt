package com.tamanna.ai

import android.content.Intent
import android.os.Bundle
import android.widget.Button
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import okhttp3.*

class TamannaMainActivity : AppCompatActivity() {

    lateinit var resultText: TextView
    lateinit var scanBtn: Button
    lateinit var chatBtn: Button
    val client = OkHttpClient()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_tamanna_main)

        resultText = findViewById(R.id.resultText)
        scanBtn = findViewById(R.id.scanBtn)
        chatBtn = findViewById(R.id.chatBtn)

        scanBtn.setOnClickListener { runAIScan() }
        chatBtn.setOnClickListener { 
            startActivity(Intent(this, TamannaChatActivity::class.java)) 
        }
    }

    private fun runAIScan() {
        val request = Request.Builder()
            .url("https://api.github.com")
            .build()

        client.newCall(request).enqueue(object : Callback {
            override fun onFailure(call: Call, e: IOException) {
                runOnUiThread { resultText.text = "❌ Network Error!" }
            }
            override fun onResponse(call: Call, response: Response) {
                runOnUiThread { resultText.text = "🌐 AI Connected!" }
            }
        })
    }
}