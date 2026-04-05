package com.tamanna.ultra2

class CacheSystem_050 {

    private val cache = mutableMapOf<String, Any>()

    fun put(key: String, value: Any) {
        cache[key] = value
    }

    fun get(key: String): Any? {
        return cache[key]
    }

    fun clear() {
        cache.clear()
    }
}