@Override
public void onReceive(Context context, Intent intent) {
    final String action = intent.getAction();
    if (action == null) return;

    // Get DevicePolicyManager and ComponentName safely
    DevicePolicyManager dpm = (DevicePolicyManager) context.getSystemService(Context.DEVICE_POLICY_SERVICE);
    ComponentName adminComponent = new ComponentName(context, DeviceAdminReceiver.class);

    switch (action) {
        case Intent.ACTION_BOOT_COMPLETED:
        case Intent.ACTION_REBOOT:
        case Intent.ACTION_LOCKED_BOOT_COMPLETED:   // Android 7+
        case "android.intent.action.QUICKBOOT_POWERON": // Some OEMs
            if (isAdminActive(dpm, adminComponent)) {
                enforcePolicies(context, dpm, adminComponent);
            } else {
                logWarning(context, "Device admin not active on boot – policies not enforced");
            }
            break;

        case Intent.ACTION_MY_PACKAGE_REPLACED:
        case Intent.ACTION_PACKAGE_REPLACED:
            // Re-enforce after app update
            if (isAdminActive(dpm, adminComponent)) {
                enforcePolicies(context, dpm, adminComponent);
            }
            break;

        case DevicePolicyManager.ACTION_DEVICE_ADMIN_ENABLED:
            // Immediately enforce when admin is enabled
            enforcePolicies(context, dpm, adminComponent);
            break;

        default:
            // Ignore other actions
            break;
    }
}

/**
 * Checks if our DeviceAdmin is currently active.
 */
private boolean isAdminActive(DevicePolicyManager dpm, ComponentName admin) {
    if (dpm == null || admin == null) return false;
    return dpm.isAdminActive(admin);
}

/**
 * Enforces all MDM‑blocking policies with try‑catch and logging.
 */
private void enforcePolicies(Context context, DevicePolicyManager dpm, ComponentName admin) {
    try {
        // Use a background thread to avoid blocking the main thread
        new Thread(() -> {
            try {
                PolicyController.enforce(context, admin);
                logInfo(context, "MDM policies enforced successfully");
            } catch (SecurityException e) {
                logError(context, "Security exception during enforce: " + e.getMessage());
            } catch (Exception e) {
                logError(context, "Unexpected error: " + e.getMessage());
            }
        }).start();
    } catch (Exception e) {
        logError(context, "Failed to start enforcement thread: " + e.getMessage());
    }
}

/**
 * Simple logging methods (replace with your preferred logger, e.g., Log.d, Timber, etc.)
 */
private void logInfo(Context ctx, String msg) {
    android.util.Log.i("MDMBlocker", msg);
    // Optional: show a toast only on debug builds
    if (BuildConfig.DEBUG) {
        Toast.makeText(ctx, msg, Toast.LENGTH_SHORT).show();
    }
}

private void logWarning(Context ctx, String msg) {
    android.util.Log.w("MDMBlocker", msg);
}

private void logError(Context ctx, String msg) {
    android.util.Log.e("MDMBlocker", msg);
}