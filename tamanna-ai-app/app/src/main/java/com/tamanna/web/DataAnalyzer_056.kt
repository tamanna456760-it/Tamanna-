package com.tamanna.web

class DataAnalyzer_056 {

    fun analyze(data: String): Map<String, Any> {
        return mapOf(
            "length" to data.length,
            "words" to data.split(" ").size,
            "containsHTML" to data.contains("<html>")
        )
    }
}