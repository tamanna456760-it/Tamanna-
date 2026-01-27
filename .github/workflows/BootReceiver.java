public void onReceive(Context c, Intent i) {
    if (i.getAction().equals(Intent.ACTION_BOOT_COMPLETED)) {
        PolicyController.enforce(c, admin);
    }
}