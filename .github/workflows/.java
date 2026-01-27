@Override
public void onReceive(Context context, Intent intent) {
    if (Intent.ACTION_BOOT_COMPLETED.equals(intent.getAction())) {
        dpm.setApplicationHidden(admin, "com.infinix.xoslauncher", true);
    }
}