#!/bin/sh

PACKAGES="
com.truecaller
com.smartcaller
com.callapp.contacts
com.eyecon.global
com.hiya.star
com.whoscall.whoscallandroid
"

echo "Starting Android security cleanup..."

for pkg in $PACKAGES
do
    adb shell pm list packages | grep "$pkg" >/dev/null 2>&1
    if [ $? -eq 0 ]; then
        echo "Removing $pkg"
        adb shell pm uninstall --user 0 "$pkg"
    else
        echo "$pkg not found"
    fi
done

echo "Cleanup completed."