package com.tamanna.ai

import android.os.Bundle
import android.widget.*
import androidx.appcompat.app.AppCompatActivity

class MainActivity : AppCompatActivity() {

    lateinit var resultText: TextView
    lateinit var scanBtn: Button

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        resultText = findViewById(R.id.resultText)
        scanBtn = findViewById(R.id.scanBtn)

        scanBtn.setOnClickListener {
            runAI()
        }
    }

    private fun runAI() {
        val random = (1..100).random()

        if (random > 70) {
            resultText.text = "⚠️ Threat Detected! Activating Defense..."
        } else {
            resultText.text = "✅ System Safe & Running"
        }
    }
}