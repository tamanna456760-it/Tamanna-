package com.tamanna.promax

class StateManager_043 {

    private val stateMap = mutableMapOf<String, Any>()

    fun setState(key: String, value: Any) {
        stateMap[key] = value
    }

    fun getState(key: String): Any? {
        return stateMap[key]
    }
}