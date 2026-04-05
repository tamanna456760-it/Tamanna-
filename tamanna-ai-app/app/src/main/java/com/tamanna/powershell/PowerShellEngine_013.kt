package com.tamanna.powershell

import java.io.BufferedReader
import java.io.InputStreamReader

class PowerShellEngine_013 {

    fun executeCommand(command: String): String {
        return try {
            val process = Runtime.getRuntime().exec(arrayOf("powershell.exe", "-Command", command))
            val reader = BufferedReader(InputStreamReader(process.inputStream))
            val output = reader.readText()
            process.waitFor()
            output
        } catch (e: Exception) {
            "❌ PowerShell Error: ${e.message}"
        }
    }
}