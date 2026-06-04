package com.tamanna.tiai

object TIBot {
    fun getReply(userMessage: String): String {
        val msg = userMessage.lowercase().trim()
        return when {
            msg.contains("hello") || msg.contains("hi") -> "Hello! I'm TI. How can I help?"
            msg.contains("how are you") -> "I'm functioning perfectly!"
            msg.contains("joke") -> getRandomJoke()
            msg.contains("your name") -> "I am TI – Turing Intelligence."
            msg.contains("help") -> "Commands: joke, weather, news, quote, math <num1> <num2>"
            msg.contains("weather") -> "🌦️ Real weather API can be added. Demo: Sunny, 25°C"
            msg.contains("news") -> "📰 Connect NewsAPI for live news."
            msg.contains("quote") -> "💡 'The only limit is your imagination.' – TI"
            msg.contains("math") -> handleMath(userMessage)
            else -> "Tell me more. You can teach me by editing TIBot.kt"
        }
    }

    private fun getRandomJoke(): String {
        val jokes = listOf(
            "Why don't scientists trust atoms? Because they make up everything!",
            "What do you call a fake noodle? An impasta!",
            "Why did the AI go to art school? To draw better conclusions."
        )
        return jokes.random()
    }

    private fun handleMath(input: String): String {
        val nums = Regex("\\d+").findAll(input).map { it.value.toInt() }.toList()
        return if (nums.size >= 2) {
            "🧮 ${nums[0]} + ${nums[1]} = ${nums[0] + nums[1]}"
        } else "Give two numbers, e.g., 'math 5 10'"
    }
}