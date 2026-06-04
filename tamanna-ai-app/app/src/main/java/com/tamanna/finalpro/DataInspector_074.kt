package com.tamanna.finalpro

class DataInspector_074 {

    fun inspect(data: String): String {
        return if (data.contains("error")) "⚠️ Issue detected" else "✅ Data OK"
    }
}