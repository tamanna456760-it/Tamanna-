package com.tamanna.web

import android.content.Context
import java.io.File

class FileExporter_059(private val context: Context) {

    fun saveReport(fileName: String, content: String): String {
        val file = File(context.filesDir, fileName)
        file.writeText(content)
        return file.absolutePath
    }
}