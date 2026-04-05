package com.tamanna.promax

class PermissionGuard_044 {

    fun isAllowed(action: String): Boolean {
        val blocked = listOf("delete_system", "format", "root_access")
        return !blocked.contains(action)
    }
}