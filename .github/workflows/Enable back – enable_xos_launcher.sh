#!/bin/bash

PKG="com.infinix.xoslauncher"

echo "[+] Enabling XOS Launcher..."
adb shell pm enable $PKG

echo "[✓] XOS Launcher enabled"