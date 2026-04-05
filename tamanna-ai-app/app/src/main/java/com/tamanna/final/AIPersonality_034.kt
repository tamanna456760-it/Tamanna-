package com.tamanna.final

class AIPersonality_034 {

    var mode = "normal"

    fun setMode(newMode: String) {
        mode = newMode
    }

    fun respond(input: String): String {
        return when (mode) {
            "friendly" -> "😊 Hey! $input"
            "strict" -> "⚠️ Follow rules: $input"
            "smart" -> "🧠 Analyzing deeply: $input"
            else -> "🤖 $input"
        }
    }
}