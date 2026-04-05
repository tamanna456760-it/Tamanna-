package com.tamanna.webpro

class AIInsight_061 {

    fun generateInsight(data: String): String {
        return when {
            data.length > 1000 -> "📊 Large dataset detected"
            data.contains("error") -> "⚠️ Issue found in data"
            else -> "✅ Normal data"
        }
    }
}