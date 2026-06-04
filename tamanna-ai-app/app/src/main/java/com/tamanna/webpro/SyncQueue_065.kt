package com.tamanna.webpro

import java.util.*

class SyncQueue_065 {

    private val queue: Queue<String> = LinkedList()

    fun add(data: String) {
        queue.add(data)
    }

    fun process(): String {
        val item = queue.poll() ?: return "No data"
        return "🔄 Synced: $item"
    }
}