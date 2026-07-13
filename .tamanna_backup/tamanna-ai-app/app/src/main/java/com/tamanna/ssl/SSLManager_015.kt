package com.tamanna.ssl

import java.net.URL
import javax.net.ssl.HttpsURLConnection

class SSLManager_015 {

    fun checkHttpsConnection(urlStr: String): Boolean {
        return try {
            val url = URL(urlStr)
            val conn = url.openConnection() as HttpsURLConnection
            conn.connect()
            val code = conn.responseCode
            conn.disconnect()
            code in 200..299
        } catch (e: Exception) {
            false
        }
    }
}