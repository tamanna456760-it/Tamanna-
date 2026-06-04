package com.tamanna.final

import android.content.Context
import android.content.Intent
import android.net.Uri
import java.io.File

class AutoInstaller_037(private val context: Context) {

    fun installApk(filePath: String) {
        val file = File(filePath)
        val intent = Intent(Intent.ACTION_VIEW)
        intent.setDataAndType(Uri.fromFile(file),
            "application/vnd.android.package-archive")
        intent.flags = Intent.FLAG_ACTIVITY_NEW_TASK
        context.startActivity(intent)
    }
}