package com.tamanna.promax

class MultiThreadEngine_046 {

    fun runParallel(tasks: List<() -> Unit>) {
        tasks.forEach {
            Thread {
                it()
            }.start()
        }
    }
}