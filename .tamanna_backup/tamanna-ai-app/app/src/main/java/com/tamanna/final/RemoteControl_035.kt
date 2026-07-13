package com.tamanna.final

class RemoteControl_035 {

    private val listeners = mutableListOf<(String) -> Unit>()

    fun sendCommand(cmd: String) {
        listeners.forEach { it(cmd) }
    }

    fun onReceive(listener: (String) -> Unit) {
        listeners.add(listener)
    }
}