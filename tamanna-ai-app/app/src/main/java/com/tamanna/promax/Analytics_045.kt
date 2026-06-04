package com.tamanna.promax

class Analytics_045 {

    private val events = mutableListOf<String>()

    fun track(event: String) {
        events.add(event)
    }

    fun getReport(): String {
        return "📊 Total Events: ${events.size}"
    }
}