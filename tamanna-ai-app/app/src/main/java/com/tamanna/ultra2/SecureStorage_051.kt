package com.tamanna.ultra2

import android.content.Context

class SecureStorage_051(context: Context) {

    private val prefs = context.getSharedPreferences("secure_data", Context.MODE_PRIVATE)

    fun save(key: String, value: String) {
        prefs.edit().putString(key, value).apply()
    }

    fun load(key: String): String? {
        return prefs.getString(key, null)
    }
}