@Override
public void onReceive(Context context, Intent intent) {
    final String action = intent.getAction();
    if (action == null) return;

    // List of packages to hide on boot (can be extended)
    final String[] PACKAGES_TO_HIDE = {
        "com.infinix.xoslauncher",
        "com.android.chrome",          // example – add more as needed
        "com.facebook.katana"
    };

    // Handle multiple boot‑related intents (including OEM variants)
    switch (action) {
        case Intent.ACTION_BOOT_COMPLETED:
        case Intent.ACTION_LOCKED_BOOT_COMPLETED:      // Android 7+
        case "android.intent.action.QUICKBOOT_POWERON": // MIUI / Xiaomi
        case "com.samsung.android.knox.intent.action.KNOX_BOOT_COMPLETED":
            // Delay execution slightly to let system settle
            new Handler(Looper.getMainLooper()).postDelayed(() -> {
                hidePackages(context, PACKAGES_TO_HIDE);
            }, 3000);
            break;
        default:
            // ignore other actions
            break;
    }
}

/**
 * Hides a list of packages using DevicePolicyManager (or falls back to PackageManager).
 */
private void hidePackages(Context context, String[] packageNames) {
    // Get DevicePolicyManager and ComponentName
    DevicePolicyManager dpm = (DevicePolicyManager) context.getSystemService(Context.DEVICE_POLICY_SERVICE);
    ComponentName admin = new ComponentName(context, YourDeviceAdminReceiver.class);

    // Check if admin is active
    if (!dpm.isAdminActive(admin)) {
        Log.w("MDMBlocker", "Device admin not active – cannot hide packages");
        return;
    }

    for (String pkg : packageNames) {
        try {
            // Use setApplicationHidden (API 21+)
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.LOLLIPOP) {
                boolean success = dpm.setApplicationHidden(admin, pkg, true);
                if (success) {
                    Log.i("MDMBlocker", "Hidden package: " + pkg);
                } else {
                    Log.w("MDMBlocker", "Failed to hide " + pkg + " (maybe already hidden)");
                }
            } else {
                // Fallback for older Android: use PackageManager to disable
                PackageManager pm = context.getPackageManager();
                pm.setApplicationEnabledSetting(pkg,
                        PackageManager.COMPONENT_ENABLED_STATE_DISABLED,
                        PackageManager.DONT_KILL_APP);
                Log.i("MDMBlocker", "Disabled package (pre-L): " + pkg);
            }
        } catch (SecurityException e) {
            Log.e("MDMBlocker", "Security exception hiding " + pkg + ": " + e.getMessage());
        } catch (IllegalArgumentException e) {
            Log.e("MDMBlocker", "Package not found: " + pkg);
        } catch (Exception e) {
            Log.e("MDMBlocker", "Unexpected error hiding " + pkg + ": " + e.getMessage());
        }
    }
}