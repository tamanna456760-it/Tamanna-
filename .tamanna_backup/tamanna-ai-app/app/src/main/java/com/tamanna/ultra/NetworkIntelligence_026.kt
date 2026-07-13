package com.tamanna.ultra

import android.content.Context
import android.net.ConnectivityManager

class NetworkIntelligence_026(private val context: Context) {

    fun isOnline(): Boolean {
        val cm = context.getSystemService(Context.CONNECTIVITY_SERVICE) as ConnectivityManager
        val network = cm.activeNetworkInfo
        return network != null && network.isConnected
    }

    fun getStatus(): String {
        return if (isOnline()) "🌐 Online Mode" else "📴 Offline Mode"
    }
}