package com.tamanna.cmd

import java.io.BufferedReader
import java.io.InputStreamReader

class CMDEngine_014 {

    fun executeCommand(command: String): String {
        return try {
            val process = Runtime.getRuntime().exec(command)
            val reader = BufferedReader(InputStreamReader(process.inputStream))
            val output = reader.readText()
            process.waitFor()
            output
        } catch (e: Exception) {
            "❌ CMD Error: ${e.message}"
        }
    }
}