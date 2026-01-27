DevicePolicyManager dpm;
ComponentName admin;

String XOS = "com.infinix.xoslauncher";
String ALLOWED = "com.teslacoilsw.launcher"; // Nova example

// Force disable XOS Launcher
dpm.setApplicationHidden(admin, XOS, true);

// Whitelist only one launcher
IntentFilter filter = new IntentFilter(Intent.ACTION_MAIN);
filter.addCategory(Intent.CATEGORY_HOME);
filter.addCategory(Intent.CATEGORY_DEFAULT);

dpm.addPersistentPreferredActivity(
    admin,
    filter,
    new ComponentName(ALLOWED, "com.teslacoilsw.launcher.NovaLauncher")
);