package com.tamanna.ultra

import android.content.Context
import java.io.File

class MemoryBrain_024(context: Context) {

    private val memoryFile = File(context.filesDir, "memory_brain.txt")

    fun saveMemory(data: String) {
        memoryFile.appendText(data + "\n")
    }

    fun loadMemory(): List<String> {
        if (!memoryFile.exists()) return emptyList()
        return memoryFile.readLines()
    }
}