package com.tamanna.webpro

class AccessControl_064 {

    private val roles = mapOf(
        "admin" to listOf("ALL"),
        "user" to listOf("READ", "REPORT")
    )

    fun canAccess(role: String, action: String): Boolean {
        val permissions = roles[role] ?: return false
        return permissions.contains("ALL") || permissions.contains(action)
    }
}