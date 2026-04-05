package com.tamanna.promax

import java.util.*

class TaskQueue_042 {

    private val queue: Queue<() -> Unit> = LinkedList()

    fun addTask(task: () -> Unit) {
        queue.add(task)
    }

    fun runNext() {
        val task = queue.poll()
        task?.invoke()
    }

    fun size(): Int = queue.size
}