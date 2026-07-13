package com.tamanna.webpro

class SmartCrawler_060 {

    private val allowedDomains = listOf("example.com", "api.github.com")

    fun isAllowed(url: String): Boolean {
        return allowedDomains.any { url.contains(it) }
    }

    fun crawl(url: String): String {
        return if (isAllowed(url)) {
            "✅ Crawling allowed: $url"
        } else {
            "❌ Blocked domain"
        }
    }
}