package com.tamanna.intelli

import android.content.Context
import java.util.*

class AdvancedScheduler_019(private val context: Context) {

    private val timer = Timer()
    private val core = IntelliCore_018(context)

    fun start(intervalMs: Long = 5000) {
        timer.scheduleAtFixedRate(object : TimerTask() {
            override fun run() {
                core.analyzeAndDecide()
            }
        }, 0, intervalMs)
    }

    fun stop() {
        timer.cancel()
    }
}