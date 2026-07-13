package com.tamanna.pro

import java.util.*

class AdvancedAuth_033 {

    fun generateToken(userId: String): String {
        return Base64.getEncoder().encodeToString("$userId:${System.currentTimeMillis()}".toByteArray())
    }

    fun validateToken(token: String): Boolean {
        return token.isNotEmpty()
    }
}