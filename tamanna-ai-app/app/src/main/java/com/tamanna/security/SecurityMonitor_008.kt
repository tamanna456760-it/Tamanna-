package com.tamanna.security

import android.os.Bundle
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity

class SecurityMonitor_008 : AppCompatActivity() {

    lateinit var monitorText: TextView

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_security_monitor)

        monitorText = findViewById(R.id.monitorText)
        monitorText.text = "🔒 Security System Active"
    }
}