package com.tamanna.finalpro

class DashboardEngine_066 {

    fun buildSummary(logs: List<String>): String {
        return """
            📊 System Dashboard
            
            Total Logs: ${logs.size}
            Last Event: ${logs.lastOrNull() ?: "No Data"}
        """.trimIndent()
    }
}