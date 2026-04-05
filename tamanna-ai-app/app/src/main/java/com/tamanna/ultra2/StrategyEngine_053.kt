package com.tamanna.ultra2

class StrategyEngine_053 {

    fun decideStrategy(input: String): String {
        return when {
            input.contains("error") -> "REPAIR_MODE"
            input.contains("slow") -> "OPTIMIZE_MODE"
            input.contains("network") -> "SYNC_MODE"
            else -> "NORMAL_MODE"
        }
    }
}