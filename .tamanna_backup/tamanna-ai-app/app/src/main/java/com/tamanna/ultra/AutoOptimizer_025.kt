package com.tamanna.ultra

class AutoOptimizer_025 {

    fun optimizeSystem(logs: List<String>): String {
        return if (logs.size > 100) {
            "⚡ Optimization: Cleaning old logs & reducing load"
        } else {
            "✅ System running optimally"
        }
    }
}