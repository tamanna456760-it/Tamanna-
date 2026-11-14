adb shell pm disable-user --user 0 com.infinix.xoslauncher
adb shell pm suspend --user 0 com.infinix.xoslauncher
adb shell cmd role remove-role-holder android.app.role.HOME com.infinix.xoslauncher