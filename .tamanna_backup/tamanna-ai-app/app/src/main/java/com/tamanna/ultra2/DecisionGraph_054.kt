package com.tamanna.ultra2

class DecisionGraph_054 {

    fun process(input: String): String {
        return when {
            input.contains("repair") -> "🔧 Running repair system"
            input.contains("optimize") -> "⚡ Running optimizer"
            else -> "🤖 Default processing"
        }
    }
}