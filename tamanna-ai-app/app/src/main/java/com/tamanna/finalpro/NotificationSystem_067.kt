package com.tamanna.finalpro

import android.content.Context
import android.widget.Toast

class NotificationSystem_067(private val context: Context) {

    fun notify(message: String) {
        Toast.makeText(context, message, Toast.LENGTH_SHORT).show()
    }
}