package com.tamanna.finalpro

class AuditLog_071 {

    private val logs = mutableListOf<String>()

    fun log(action: String) {
        logs.add("${System.currentTimeMillis()} - $action")
    }

    fun getLogs(): List<String> = logs
}