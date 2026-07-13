package com.tamanna.upgrade

import android.os.Bundle
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import java.io.File

class SelfUpgradeMonitor_012 : AppCompatActivity() {

    lateinit var monitorText: TextView

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_self_upgrade_monitor)

        monitorText = findViewById(R.id.monitorText)

        val dir = File(filesDir, "kotlin_files")
        val files = dir.listFiles()?.map { it.name } ?: emptyList()

        monitorText.text = "Generated Files:\n${files.joinToString("\n")}"
    }
}