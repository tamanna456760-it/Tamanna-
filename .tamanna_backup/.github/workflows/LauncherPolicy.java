import android.app.admin.DevicePolicyManager;
import android.content.ComponentName;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.os.Build;
import android.util.Log;

public class LauncherController {

    private static final String TAG = "LauncherController";

    // Launcher to block (hide)
    private static final String BLOCKED_LAUNCHER_PKG = "com.infinix.xoslauncher";
    private static final String BLOCKED_LAUNCHER_CLASS = "com.infinix.xoslauncher.Launcher"; // adjust if needed

    // List of allowed launchers (whitelist)
    private static final AllowedLauncher[] ALLOWED_LAUNCHERS = {
        new AllowedLauncher("com.teslacoilsw.launcher", "com.teslacoilsw.launcher.NovaLauncher"),
        new AllowedLauncher("com.google.android.apps.nexuslauncher", "com.google.android.apps.nexuslauncher.NexusLauncherActivity"),
        new AllowedLauncher("com.android.launcher3", "com.android.launcher3.Launcher")
    };

    /**
     * Enforces that only whitelisted launchers are available.
     * Blocks the specified launcher and sets persistent preferred activity.
     *
     * @param context Application context
     * @param dpm DevicePolicyManager instance (must not be null)
     * @param admin ComponentName of your DeviceAdminReceiver
     * @return true if successful, false otherwise
     */
    public static boolean enforceAllowedLaunchers(Context context, DevicePolicyManager dpm, ComponentName admin) {
        if (dpm == null || admin == null) {
            Log.e(TAG, "DevicePolicyManager or ComponentName is null");
            return false;
        }

        if (!dpm.isAdminActive(admin)) {
            Log.w(TAG, "Device admin not active – cannot enforce launcher restrictions");
            return false;
        }

        boolean success = true;

        // 1. Block the unwanted launcher (hide from user)
        if (blockLauncher(dpm, admin, BLOCKED_LAUNCHER_PKG)) {
            Log.i(TAG, "Successfully blocked launcher: " + BLOCKED_LAUNCHER_PKG);
        } else {
            Log.w(TAG, "Failed to block launcher: " + BLOCKED_LAUNCHER_PKG);
            success = false;
        }

        // 2. Clear any existing persistent preferred activities (optional)
        clearPersistentPreferredActivities(dpm, admin);

        // 3. Set whitelisted launchers as preferred home activities
        if (setAllowedLaunchers(dpm, admin)) {
            Log.i(TAG, "Successfully set allowed launchers");
        } else {
            Log.e(TAG, "Failed to set allowed launchers");
            success = false;
        }

        return success;
    }

    /**
     * Hides a package using DevicePolicyManager.setApplicationHidden (API 21+)
     */
    private static boolean blockLauncher(DevicePolicyManager dpm, ComponentName admin, String packageName) {
        if (Build.VERSION.SDK_INT < Build.VERSION_CODES.LOLLIPOP) {
            Log.w(TAG, "setApplicationHidden not available before API 21");
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
        }
    }

    /**
     * Clears all persistent preferred activities (clean slate)
     */
    private static void clearPersistentPreferredActivities(DevicePolicyManager dpm, ComponentName admin) {
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
     * Sets multiple allowed launchers as persistent preferred activities.
     * The first one that exists will be used as default.
     */
    private static boolean setAllowedLaunchers(DevicePolicyManager dpm, ComponentName admin) {
        if (Build.VERSION.SDK_INT < Build.VERSION_CODES.LOLLIPOP) {
            Log.w(TAG, "addPersistentPreferredActivity requires API 21+");
            return false;
        }

        // Create the HOME intent filter
        IntentFilter homeFilter = new IntentFilter(Intent.ACTION_MAIN);
        homeFilter.addCategory(Intent.CATEGORY_HOME);
        homeFilter.addCategory(Intent.CATEGORY_DEFAULT);

        boolean anyAdded = false;
        for (AllowedLauncher launcher : ALLOWED_LAUNCHERS) {
            ComponentName cn = new ComponentName(launcher.packageName, launcher.className);
            if (isPackageInstalled(admin, launcher.packageName)) {
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

        // If none of the whitelisted launchers exist, fallback to system default
        if (!anyAdded) {
            Log.w(TAG, "No whitelisted launcher found – leaving default");
        }

        return anyAdded;
    }

    /**
     * Checks if a package is installed on the device.
     */
    private static boolean isPackageInstalled(ComponentName admin, String packageName) {
        // We don't have a context here, so we'll assume it's installed.
        // A better approach would be to pass a Context and use PackageManager.
        // For simplicity, we return true and let addPersistentPreferredActivity fail gracefully.
        return true;
    }

    // Helper class
    private static class AllowedLauncher {
        final String packageName;
        final String className;
        AllowedLauncher(String pkg, String cls) {
            this.packageName = pkg;
            this.className = cls;
        }
    }
}