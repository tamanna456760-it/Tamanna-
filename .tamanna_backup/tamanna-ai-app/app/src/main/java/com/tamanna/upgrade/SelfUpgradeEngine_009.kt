package com.tamanna.upgrade

import android.content.Context
import java.io.File

class SelfUpgradeEngine_009(private val context: Context) {

    fun createFile(fileName: String, content: String, dir: String = "generated") {
        val folder = File(context.filesDir, dir)
        if (!folder.exists()) folder.mkdirs()
        val file = File(folder, fileName)
        file.writeText(content)
    }

    fun generateKotlinFile(className: String, code: String) {
        val fileName = "${className}_${System.currentTimeMillis()}.kt"
        createFile(fileName, code, "kotlin_files")
    }

    fun generateXMLFile(fileName: String, xmlContent: String) {
        createFile(fileName, xmlContent, "layout_files")
    }
}