adb devices
adb shell settings put global stay_on_while_plugged_in 0

# Disable user apps
adb shell pm disable-user --user 0 com.android.chrome
adb shell pm disable-user --user 0 com.google.android.youtube
adb shell pm disable-user --user 0 com.google.android.gms

# Disable settings access
adb shell pm disable-user --user 0 com.android.settings

# Disable accessibility abuse
adb shell settings put secure accessibility_enabled 0

# Disable install from unknown sources
adb shell settings put secure install_non_market_apps 0

# Lock screen pin
adb shell settings put secure lock_to_app_enabled 1