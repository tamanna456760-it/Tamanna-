package com.tamanna.finalpro

interface Module {
    fun start()
    fun stop()
}

class ModuleInstaller_075 {

    private val installed = mutableListOf<Module>()

    fun install(module: Module) {
        installed.add(module)
        module.start()
    }

    fun uninstall(module: Module) {
        module.stop()
        installed.remove(module)
    }

    fun listModules(): List<Module> = installed
}