package com.tamanna.ultra2

interface Module_048 {
    fun start()
    fun stop()
}

class ModuleLoader_048 {

    private val modules = mutableListOf<Module_048>()

    fun load(module: Module_048) {
        modules.add(module)
        module.start()
    }

    fun unload(module: Module_048) {
        module.stop()
        modules.remove(module)
    }

    fun getActiveModules(): Int = modules.size
}