package com.tamanna.webpro

import org.json.JSONObject

class JsonReport_062 {

    fun createReport(data: String, insight: String): String {
        val json = JSONObject()
        json.put("data_length", data.length)
        json.put("insight", insight)
        return json.toString(2)
    }
}