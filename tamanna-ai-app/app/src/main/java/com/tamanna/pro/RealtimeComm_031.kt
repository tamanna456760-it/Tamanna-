package com.tamanna.pro

import java.util.*

class RealtimeComm_031 {

    private val listeners = mutableListOf<(String) -> Unit>()

    fun sendMessage(message: String) {
        for (listener in listeners) {
            listener(message)
        }
    }

    fun registerListener(listener: (String) -> Unit) {
        listeners.add(listener)
    }
}