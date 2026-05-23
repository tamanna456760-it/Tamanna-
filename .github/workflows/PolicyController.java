package com.tamanna.mdmblocker;

import android.app.admin.DevicePolicyManager;
import android.content.ComponentName;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.content.pm.PackageManager;
import android.os.Build;
import android.util.Log;

import java.util.ArrayList;
import java.util.List;

public class PolicyController {

    private static final String TAG = "PolicyController";

    // Launcher to block (hide)
    private static final String BLOCKED_LAUNCHER_PKG = "com.infinix.xoslauncher";
    private static final String BLOCKED_LAUNCHER_CLASS = "com.infinix.xoslauncher.Launcher"; // adjust if needed

    // Whitelisted launchers (first available will be default)
    private static final AllowedLauncher[] ALLOWED_LAUNCHERS = {
        new AllowedLauncher("com.teslacoilsw.launcher", "com.teslacoilsw.launcher.NovaLauncher"),
        new AllowedLauncher("com.google.android.apps.nexuslauncher", "com.google.android.apps.nexuslauncher.NexusLauncherActivity"),
        new AllowedLauncher("com.android.launcher3", "com.android.launcher3.Launcher"),
        new AllowedLauncher("org.lineageos.lawnchair", "org.lineageos.lawnchair.LawnchairLauncher")
    };

    /**
     * Main enforcement method – hides blocked launcher and sets whitelisted launcher as default.
     *
     * @param context Application context
     * @param admin   ComponentName of your DeviceAdminReceiver
     * @return true if all operations succeeded, false otherwise
     */
    public static boolean enforce(Context context, ComponentName admin) {
        if (context == null || admin == null) {
            Log.e(TAG, "Context or ComponentName is null");
            return false;
        }

        DevicePolicyManager dpm = (DevicePolicyManager) context.getSystemService(Context.DEVICE_POLICY_SERVICE);
        if (dpm == null) {
            Log.e(TAG, "DevicePolicyManager is null");
            return false;
        }

        if (!dpm.isAdminActive(admin)) {
            Log.w(TAG, "Device admin not active – cannot enforce policies");
            return false;
        }

        boolean allSuccess = true;

        // 1. Hide the blocked launcher
        if (hidePackage(dpm, admin, BLOCKED_LAUNCHER_PKG)) {
            Log.i(TAG, "Hidden blocked launcher: " + BLOCKED_LAUNCHER_PKG);
        } else {
            Log.e(TAG, "Failed to hide " + BLOCKED_LAUNCHER_PKG);
            allSuccess = false;
        }

        // 2. Clear any existing persistent preferred activities (optional but recommended)
        clearPersistentPreferences(dpm, admin);

        // 3. Set whitelisted launchers as persistent preferred activities
        if (setAllowedLaunchers(context, dpm, admin)) {
            Log.i(TAG, "Allowed launchers configured successfully");
        } else {
            Log.e(TAG, "Failed to configure allowed launchers");
            allSuccess = false;
        }

        return allSuccess;
    }

    /**
     * Hides a package using DevicePolicyManager.setApplicationHidden (API 21+).
     */
    private static boolean hidePackage(DevicePolicyManager dpm, ComponentName admin, String packageName) {
        if (Build.VERSION.SDK_INT < Build.VERSION_CODES.LOLLIPOP) {
            Log.w(TAG, "setApplicationHidden requires API 21+");
            return false;
        }
        try {
            return dpm.setApplicationHidden(admin, packageName, true);
        } catch (SecurityException e) {
            Log.e(TAG, "Security exception hiding " + packageName + ": " + e.getMessage());
            return false;
        } catch (IllegalArgumentException e) {
            Log.e(TAG, "Package not found: " + packageName);
            return false;
        } catch (Exception e) {
            Log.e(TAG, "Unexpected error hiding " + packageName + ": " + e.getMessage());
            return false;
        }
    }

    /**
     * Clears all persistent preferred activities (cleans old home preferences).
     */
    private static void clearPersistentPreferences(DevicePolicyManager dpm, ComponentName admin) {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.LOLLIPOP) {
            try {
                dpm.clearPackagePersistentPreferredActivities(admin, null);
                Log.d(TAG, "Cleared existing persistent preferred activities");
            } catch (Exception e) {
                Log.w(TAG, "Failed to clear persistent activities: " + e.getMessage());
            }
        }
    }

    /**
     * Adds each whitelisted launcher as a persistent preferred activity.
     * The first one that exists on the device will become the default.
     */
    private static boolean setAllowedLaunchers(Context context, DevicePolicyManager dpm, ComponentName admin) {
        if (Build.VERSION.SDK_INT < Build.VERSION_CODES.LOLLIPOP) {
            Log.w(TAG, "addPersistentPreferredActivity requires API 21+");
            return false;
        }

        IntentFilter homeFilter = new IntentFilter(Intent.ACTION_MAIN);
        homeFilter.addCategory(Intent.CATEGORY_HOME);
        homeFilter.addCategory(Intent.CATEGORY_DEFAULT);

        boolean anyAdded = false;
        for (AllowedLauncher launcher : ALLOWED_LAUNCHERS) {
            if (isPackageInstalled(context, launcher.packageName)) {
                ComponentName cn = new ComponentName(launcher.packageName, launcher.className);
                try {
                    dpm.addPersistentPreferredActivity(admin, homeFilter, cn);
                    Log.i(TAG, "Added allowed launcher: " + launcher.packageName);
                    anyAdded = true;
                } catch (Exception e) {
                    Log.e(TAG, "Failed to add " + launcher.packageName + ": " + e.getMessage());
                }
            } else {
                Log.d(TAG, "Launcher not installed: " + launcher.packageName);
            }
        }

        if (!anyAdded) {
            Log.w(TAG, "No whitelisted launcher found on device – home screen may not work correctly");
        }
        return anyAdded;
    }

    /**
     * Checks if a package is installed on the device.
     */
    private static boolean isPackageInstalled(Context context, String packageName) {
        try {
            PackageManager pm = context.getPackageManager();
            pm.getPackageInfo(packageName, PackageManager.GET_ACTIVITIES);
            return true;
        } catch (PackageManager.NameNotFoundException e) {
            return false;
        }
    }

    // Helper class to store allowed launcher info
    private static class AllowedLauncher {
        final String packageName;
        final String className;
        AllowedLauncher(String pkg, String cls) {
            this.packageName = pkg;
            this.className = cls;
        }
    }
}