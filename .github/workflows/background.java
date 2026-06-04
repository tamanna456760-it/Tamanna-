public class Firewall {

    private static final List<String> ALLOWED_APPS = Arrays.asList(
            "com.yourapp",
            "com.android.systemui"
    );

    public static boolean isAllowed(String packageName) {
        return ALLOWED_APPS.contains(packageName);
    }

    public static void checkAndBlock(String packageName) {
        if (!isAllowed(packageName)) {
            android.os.Process.killProcess(android.os.Process.myPid());
        }
    }
}
