package com.tamanna.intelli

import android.os.Bundle
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity

class AdvancedAIInterface_022 : AppCompatActivity() {

    lateinit var monitorText: TextView
    private lateinit var logger: SystemLogger_021

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_advanced_ai_interface)

        monitorText = findViewById(R.id.monitorText)
        logger = SystemLogger_021(this)

        val logs = logger.getLogs()
        monitorText.text = "🧠 Advanced AI Logs:\n${logs.joinToString("\n")}"
    }
}