package com.tamanna.web

class ReportBuilder_058 {

    fun buildReport(data: String, analysis: Map<String, Any>): String {
        return """
            📄 Report
            
            Data Size: ${analysis["length"]}
            Word Count: ${analysis["words"]}
            HTML Detected: ${analysis["containsHTML"]}
            
            Preview:
            ${data.take(200)}
        """.trimIndent()
    }
}