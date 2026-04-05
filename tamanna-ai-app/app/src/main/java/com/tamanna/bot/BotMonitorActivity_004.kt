package com.tamanna.bot

import android.os.Bundle
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity

class BotMonitorActivity_004 : AppCompatActivity() {

    lateinit var monitorText: TextView
    private val manager = BotManager_002()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_bot_monitor)

        monitorText = findViewById(R.id.monitorText)
        monitorText.text = "Active Bots: ${manager.getBotCount()}"
    }
}