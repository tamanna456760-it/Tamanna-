package com.tamanna.ai

import android.Manifest
import android.annotation.SuppressLint
import android.content.Intent
import android.content.pm.PackageManager
import android.graphics.Color
import android.os.Bundle
import android.speech.RecognitionListener
import android.speech.RecognizerIntent
import android.speech.SpeechRecognizer
import android.speech.tts.TextToSpeech
import android.webkit.JavascriptInterface
import android.webkit.WebChromeClient
import android.webkit.WebResourceRequest
import android.webkit.WebView
import android.webkit.WebViewClient
import android.widget.FrameLayout
import android.view.ViewGroup
import androidx.appcompat.app.AppCompatActivity
import org.json.JSONObject
import java.util.Locale

/**
 * Web application launcher with an explicit native speech bridge.
 * The bridge is exposed only while the trusted Tamanna HTTPS origin is loaded.
 */
class TamannaWebActivity : AppCompatActivity(), TextToSpeech.OnInitListener {
    private lateinit var webView: WebView
    private var speechRecognizer: SpeechRecognizer? = null
    private var textToSpeech: TextToSpeech? = null
    private var ttsReady = false
    private var pendingLanguage = "bn-BD"

    companion object {
        private const val REQUEST_AUDIO_PERMISSION = 4102
        private const val TRUSTED_HOST = "www.bd-king-r7.com"
        private const val APEX_HOST = "bd-king-r7.com"
    }

    inner class TamannaVoiceBridge {
        @JavascriptInterface
        fun startListening(languageTag: String?) {
            runOnUiThread {
                pendingLanguage = languageTag?.takeIf { it.isNotBlank() } ?: "bn-BD"
                if (checkSelfPermission(Manifest.permission.RECORD_AUDIO) == PackageManager.PERMISSION_GRANTED) {
                    startRecognition()
                } else {
                    requestPermissions(arrayOf(Manifest.permission.RECORD_AUDIO), REQUEST_AUDIO_PERMISSION)
                }
            }
        }

        @JavascriptInterface
        fun speak(text: String?, languageTag: String?) {
            runOnUiThread {
                val phrase = text?.trim().orEmpty()
                if (phrase.isEmpty()) {
                    notifyWeb("onError", "পড়ার মতো কোনো উত্তর নেই।")
                    return@runOnUiThread
                }
                if (!ttsReady || textToSpeech == null) {
                    notifyWeb("onError", "Text-to-Speech এখনো প্রস্তুত নয়।")
                    return@runOnUiThread
                }
                val locale = Locale.forLanguageTag(languageTag?.takeIf { it.isNotBlank() } ?: "bn-BD")
                val result = textToSpeech?.setLanguage(locale)
                if (result == TextToSpeech.LANG_MISSING_DATA || result == TextToSpeech.LANG_NOT_SUPPORTED) {
                    notifyWeb("onError", "এই ভাষার Text-to-Speech voice ডিভাইসে নেই।")
                    return@runOnUiThread
                }
                textToSpeech?.speak(phrase.take(4000), TextToSpeech.QUEUE_FLUSH, null, "tamanna-response")
            }
        }

        @JavascriptInterface
        fun stopSpeaking() {
            runOnUiThread { textToSpeech?.stop() }
        }
    }

    @SuppressLint("SetJavaScriptEnabled")
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        textToSpeech = TextToSpeech(this, this)

        window.statusBarColor = Color.rgb(12, 10, 30)
        window.navigationBarColor = Color.rgb(12, 10, 30)

        webView = WebView(this).apply {
            layoutParams = FrameLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                ViewGroup.LayoutParams.MATCH_PARENT
            )
            setBackgroundColor(Color.rgb(12, 10, 30))
            settings.javaScriptEnabled = true
            settings.domStorageEnabled = true
            settings.allowFileAccess = false
            settings.allowContentAccess = false
            settings.mixedContentMode = android.webkit.WebSettings.MIXED_CONTENT_NEVER_ALLOW
            addJavascriptInterface(TamannaVoiceBridge(), "TamannaNativeVoice")
            webViewClient = object : WebViewClient() {
                override fun shouldOverrideUrlLoading(view: WebView, request: WebResourceRequest): Boolean {
                    val url = request.url
                    return !(url.scheme == "https" && (url.host == TRUSTED_HOST || url.host == APEX_HOST))
                }

                override fun onPageFinished(view: WebView, url: String) {
                    super.onPageFinished(view, url)
                    val host = android.net.Uri.parse(url).host
                    if (host != TRUSTED_HOST && host != APEX_HOST) {
                        view.removeJavascriptInterface("TamannaNativeVoice")
                    }
                }
            }
            webChromeClient = WebChromeClient()
        }

        setContentView(webView)
        if (savedInstanceState == null) {
            webView.loadUrl("https://www.bd-king-r7.com/")
        } else {
            webView.restoreState(savedInstanceState)
        }
    }

    override fun onInit(status: Int) {
        ttsReady = status == TextToSpeech.SUCCESS
        if (ttsReady) textToSpeech?.language = Locale.forLanguageTag("bn-BD")
    }

    private fun startRecognition() {
        if (!SpeechRecognizer.isRecognitionAvailable(this)) {
            notifyWeb("onError", "এই Android ডিভাইসে Speech Recognition service নেই।")
            return
        }
        speechRecognizer?.destroy()
        speechRecognizer = SpeechRecognizer.createSpeechRecognizer(this).also { recognizer ->
            recognizer.setRecognitionListener(object : RecognitionListener {
                override fun onReadyForSpeech(params: Bundle?) = notifyWeb("onStatus", "বলুন, আমি শুনছি…")
                override fun onBeginningOfSpeech() = Unit
                override fun onRmsChanged(rmsdB: Float) = Unit
                override fun onBufferReceived(buffer: ByteArray?) = Unit
                override fun onEndOfSpeech() = notifyWeb("onStatus", "কথা শনাক্ত করা হচ্ছে…")
                override fun onError(error: Int) = notifyWeb("onError", "Speech Recognition ব্যর্থ হয়েছে (code $error)।")
                override fun onResults(results: Bundle?) {
                    val spoken = results?.getStringArrayList(SpeechRecognizer.RESULTS_RECOGNITION)?.firstOrNull()
                    if (spoken.isNullOrBlank()) notifyWeb("onError", "কোনো কথা শনাক্ত করা যায়নি।")
                    else notifyWeb("onResult", spoken)
                }
                override fun onPartialResults(partialResults: Bundle?) = Unit
                override fun onEvent(eventType: Int, params: Bundle?) = Unit
            })
            val intent = Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH).apply {
                putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL, RecognizerIntent.LANGUAGE_MODEL_FREE_FORM)
                putExtra(RecognizerIntent.EXTRA_LANGUAGE, pendingLanguage)
                putExtra(RecognizerIntent.EXTRA_LANGUAGE_PREFERENCE, pendingLanguage)
                putExtra(RecognizerIntent.EXTRA_PARTIAL_RESULTS, false)
            }
            recognizer.startListening(intent)
        }
    }

    private fun notifyWeb(callback: String, message: String) {
        val safeMessage = JSONObject.quote(message)
        if (::webView.isInitialized) {
            webView.post { webView.evaluateJavascript("window.TamannaVoice && window.TamannaVoice.$callback($safeMessage)", null) }
        }
    }

    override fun onRequestPermissionsResult(requestCode: Int, permissions: Array<out String>, grantResults: IntArray) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults)
        if (requestCode == REQUEST_AUDIO_PERMISSION) {
            if (grantResults.firstOrNull() == PackageManager.PERMISSION_GRANTED) startRecognition()
            else notifyWeb("onError", "মাইক্রোফোন ব্যবহারের অনুমতি দেওয়া হয়নি।")
        }
    }

    override fun onSaveInstanceState(outState: Bundle) {
        webView.saveState(outState)
        super.onSaveInstanceState(outState)
    }

    @Deprecated("Deprecated in Android API; retained for WebView back navigation.")
    override fun onBackPressed() {
        if (::webView.isInitialized && webView.canGoBack()) webView.goBack() else super.onBackPressed()
    }

    override fun onDestroy() {
        speechRecognizer?.destroy()
        textToSpeech?.stop()
        textToSpeech?.shutdown()
        if (::webView.isInitialized) {
            webView.stopLoading()
            webView.removeJavascriptInterface("TamannaNativeVoice")
            webView.destroy()
        }
        super.onDestroy()
    }
}
