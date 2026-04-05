package com.tamanna.pro

interface Plugin_032 {
    fun execute(): String
}

class PluginSystem_032 {

    private val plugins = mutableListOf<Plugin_032>()

    fun register(plugin: Plugin_032) {
        plugins.add(plugin)
    }

    fun runAll(): List<String> {
        return plugins.map { it.execute() }
    }
}