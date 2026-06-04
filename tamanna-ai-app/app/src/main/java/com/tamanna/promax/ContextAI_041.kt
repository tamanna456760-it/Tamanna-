package com.tamanna.promax

class ContextAI_041 {

    private val contextMemory = mutableListOf<String>()

    fun addContext(input: String) {
        contextMemory.add(input)
    }

    fun getSmartReply(input: String): String {
        val history = contextMemory.takeLast(3).joinToString(" | ")
        return "🧠 Context: [$history]\n➡️ Reply: Processing '$input'"
    }
}