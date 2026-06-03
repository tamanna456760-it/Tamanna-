package com.tamanna.app;

import android.os.Bundle;
import android.util.Log;
import android.widget.Toast;

import androidx.annotation.NonNull;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.view.WindowCompat;

public class MainActivity extends AppCompatActivity {

    private static final String TAG = "TamannaApp";

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        // Modern edge-to-edge support
        WindowCompat.setDecorFitsSystemWindows(getWindow(), false);

        setContentView(R.layout.activity_main);

        initializeApp();

        Log.i(TAG, "Application Started Successfully");
    }

    private void initializeApp() {

        Toast.makeText(
                this,
                "Tamanna AI System Initialized",
                Toast.LENGTH_SHORT
        ).show();

        loadConfiguration();
        startMonitoring();
    }

    private void loadConfiguration() {
        Log.d(TAG, "Loading Configuration...");
    }

    private void startMonitoring() {
        Log.d(TAG, "Monitoring Service Ready...");
    }

    @Override
    protected void onStart() {
        super.onStart();
        Log.d(TAG, "onStart()");
    }

    @Override
    protected void onResume() {
        super.onResume();
        Log.d(TAG, "onResume()");
    }

    @Override
    protected void onPause() {
        super.onPause();
        Log.d(TAG, "onPause()");
    }

    @Override
    protected void onStop() {
        super.onStop();
        Log.d(TAG, "onStop()");
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
        Log.d(TAG, "onDestroy()");
    }

    @Override
    public void onBackPressed() {
        Toast.makeText(
                this,
                "Press back again to exit",
                Toast.LENGTH_SHORT
        ).show();

        super.onBackPressed();
    }
}