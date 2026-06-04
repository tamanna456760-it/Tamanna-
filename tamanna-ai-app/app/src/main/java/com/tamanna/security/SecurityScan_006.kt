package com.tamanna.security

import android.os.Bundle
import android.widget.Button
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import java.io.File

class SecurityScan_006 : AppCompatActivity() {

    lateinit var scanBtn: Button
    lateinit var resultText: TextView

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_security_scan)

        scanBtn = findViewById(R.id.scanBtn)
        resultText = findViewById(R.id.resultText)

        scanBtn.setOnClickListener { runSecurityScan() }
    }

    private fun runSecurityScan() {
        val suspiciousFiles = mutableListOf<String>()

        // Example scan: Check app directory for suspicious files
        val appDir = filesDir
        scanDirectory(appDir, suspiciousFiles)

        resultText.text = if (suspiciousFiles.isEmpty()) {
            "✅ No suspicious files found"
        } else {
            "⚠️ Suspicious files:\n" + suspiciousFiles.joinToString("\n")
        }
    }

    private fun scanDirectory(dir: File, suspiciousFiles: MutableList<String>) {
        val files = dir.listFiles() ?: return
        for (file in files) {
            if (file.isDirectory) scanDirectory(file, suspiciousFiles)
            else {
                // Example: mark unknown .exe or .tmp as suspicious
                if (file.extension in listOf("exe", "tmp", "bat")) {
                    suspiciousFiles.add(file.absolutePath)
                }
            }
        }
    }
}