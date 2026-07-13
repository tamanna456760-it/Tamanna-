package com.tamanna

import android.webkit.JavascriptInterface

class WebAppBridge {

    @JavascriptInterface
    fun sendMessage(msg: String): String {
        return "Reply from Android: $msg"
    }
}