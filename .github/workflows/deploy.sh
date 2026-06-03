#!/bin/bash
PKG=com.tamanna.mdm
APK=android-mdm/app-release.apk

adb install $APK
adb shell dpm set-device-owner $PKG/.AdminReceiver
adb shell reboot