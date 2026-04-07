package com.tamanna

import android.os.Bundle
import androidx.appcompat.app.AppCompatActivity
import com.tamanna.system.SystemLauncher_085

class MainActivity : AppCompatActivity() {

    private lateinit var systemLauncher: SystemLauncher_085

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        systemLauncher = SystemLauncher_085(this)

        // Start full system
        systemLauncher.startSystem()
    }

    override fun onDestroy() {
        super.onDestroy()
        systemLauncher.stopSystem()
    }
}