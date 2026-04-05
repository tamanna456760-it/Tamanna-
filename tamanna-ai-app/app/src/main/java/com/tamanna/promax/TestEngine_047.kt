package com.tamanna.promax

class TestEngine_047 {

    fun runTest(code: () -> String): String {
        return try {
            val result = code()
            "✅ Test Passed: $result"
        } catch (e: Exception) {
            "❌ Test Failed: ${e.message}"
        }
    }
}