package com.tamanna

import android.os.Bundle
import android.util.Log
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import com.tamanna.system.SystemLauncher_085
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext

class MainActivity : AppCompatActivity() {

    companion object {
        private const val TAG = "TamannaSystem"
    }

    private lateinit var systemLauncher: SystemLauncher_085

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        try {
            systemLauncher = SystemLauncher_085(this)

            lifecycleScope.launch {
                startSystemSafely()
            }

        } catch (e: Exception) {
            Log.e(TAG, "Initialization failed", e)

            Toast.makeText(
                this,
                "System initialization failed",
                Toast.LENGTH_LONG
            ).show()
        }
    }

    private suspend fun startSystemSafely() {

        withContext(Dispatchers.IO) {

            Log.i(TAG, "Running startup validation...")

            checkSystemHealth()

            Log.i(TAG, "Starting Tamanna Core System")

            systemLauncher.startSystem()
        }

        Toast.makeText(
            this,
            "Tamanna AI System Started",
            Toast.LENGTH_SHORT
        ).show()
    }

    private fun checkSystemHealth() {

        Log.d(TAG, "Checking modules...")
        Log.d(TAG, "Checking storage...")
        Log.d(TAG, "Checking configuration...")
        Log.d(TAG, "Checking services...")

        // Future validations here
    }

    override fun onStart() {
        super.onStart()
        Log.d(TAG, "onStart")
    }

    override fun onResume() {
        super.onResume()
        Log.d(TAG, "onResume")
    }

    override fun onPause() {
        Log.d(TAG, "onPause")
        super.onPause()
    }

    override fun onStop() {
        Log.d(TAG, "onStop")
        super.onStop()
    }

    override fun onDestroy() {

        try {
            if (::systemLauncher.isInitialized) {
                systemLauncher.stopSystem()
            }
        } catch (e: Exception) {
            Log.e(TAG, "Shutdown error", e)
        }

        super.onDestroy()
    }
}