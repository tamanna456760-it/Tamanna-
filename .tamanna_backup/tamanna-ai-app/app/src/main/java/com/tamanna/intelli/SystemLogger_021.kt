package com.tamanna.intelli

import android.content.Context
import java.io.File

class SystemLogger_021(private val context: Context) {

    private val logFile = File(context.filesDir, "system_log.txt")

    fun log(message: String) {
        logFile.appendText("${System.currentTimeMillis()}: $message\n")
    }

    fun getLogs(): List<String> {
        if (!logFile.exists()) return emptyList()
        return logFile.readLines()
    }
}