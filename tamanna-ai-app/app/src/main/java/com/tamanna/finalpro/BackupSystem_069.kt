package com.tamanna.finalpro

import android.content.Context
import java.io.File

class BackupSystem_069(private val context: Context) {

    fun backup(fileName: String): String {
        val file = File(context.filesDir, fileName)
        val backup = File(context.filesDir, "backup_$fileName")

        if (file.exists()) {
            file.copyTo(backup, overwrite = true)
            return "✅ Backup created"
        }
        return "❌ File not found"
    }
}