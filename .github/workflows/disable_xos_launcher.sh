#!/bin/bash

# XOS Launcher package name
PKG="com.infinix.xoslauncher"

echo "[+] Disabling XOS Launcher..."
adb shell pm disable-user --user 0 $PKG

echo "[✓] XOS Launcher disabled successfully"