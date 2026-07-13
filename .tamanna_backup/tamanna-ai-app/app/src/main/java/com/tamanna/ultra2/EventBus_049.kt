package com.tamanna.ultra2

class EventBus_049 {

    private val listeners = mutableMapOf<String, MutableList<(Any) -> Unit>>()

    fun subscribe(event: String, listener: (Any) -> Unit) {
        listeners.getOrPut(event) { mutableListOf() }.add(listener)
    }

    fun publish(event: String, data: Any) {
        listeners[event]?.forEach { it(data) }
    }
}