package com.tamanna.pro

import android.app.Activity
import android.content.Intent
import android.speech.RecognizerIntent

class VoiceControl_028(private val activity: Activity) {

    fun startListening(requestCode: Int = 100) {
        val intent = Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH)
        intent.putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL,
            RecognizerIntent.LANGUAGE_MODEL_FREE_FORM)
        activity.startActivityForResult(intent, requestCode)
    }
}