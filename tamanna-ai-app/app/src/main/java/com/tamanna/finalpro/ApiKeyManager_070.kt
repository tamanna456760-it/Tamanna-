package com.tamanna.finalpro

class ApiKeyManager_070 {

    private val keys = mutableMapOf<String, String>()

    fun saveKey(name: String, key: String) {
        keys[name] = key
    }

    fun getKey(name: String): String? {
        return keys[name]
    }
}