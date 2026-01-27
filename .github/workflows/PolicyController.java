public class PolicyController {
    static String XOS = "com.infinix.xoslauncher";
    static String ALLOWED = "com.teslacoilsw.launcher"; // Nova

    public static void enforce(Context c, ComponentName admin) {
        DevicePolicyManager dpm =
          (DevicePolicyManager) c.getSystemService(Context.DEVICE_POLICY_SERVICE);

        // 1️⃣ XOS completely hidden
        dpm.setApplicationHidden(admin, XOS, true);

        // 2️⃣ Prevent default home hijack
        IntentFilter f = new IntentFilter(Intent.ACTION_MAIN);
        f.addCategory(Intent.CATEGORY_HOME);
        f.addCategory(Intent.CATEGORY_DEFAULT);

        dpm.addPersistentPreferredActivity(
            admin,
            f,
            new ComponentName(ALLOWED,
            "com.teslacoilsw.launcher.NovaLauncher")
        );
    }
}