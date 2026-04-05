package com.tamanna.finalpro

import java.util.*
import kotlin.concurrent.schedule

class TaskScheduler_078 {

    private val timer = Timer()

    fun schedule(task: () -> Unit, delayMs: Long) {
        timer.schedule(delayMs) {
            task()
        }
    }
}