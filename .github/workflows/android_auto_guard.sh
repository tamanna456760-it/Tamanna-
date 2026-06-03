#!/bin/bash
# ANDROID AUTO THIRD-PARTY GUARD (DEFENSIVE)

ADB=adb

echo "[*] Connected devices:"
$ADB devices

# -----------------------------
# 1. Disable ALL non-system apps
# -----------------------------
for pkg in $($ADB shell pm list packages -3 | cut -d: -f2); do
  echo "[BLOCK] $pkg"
  $ADB shell pm disable-user --user 0 "$pkg"
done

# -----------------------------
# 2. Kill accessibility services
# -----------------------------
$ADB shell settings put secure accessibility_enabled 0

# -----------------------------
# 3. Disable device admin apps
# -----------------------------
for admin in $($ADB shell dpm list | grep "ComponentInfo" | awk '{print $1}'); do
  $ADB shell dpm remove-active-admin "$admin" 2>/dev/null
done

# -----------------------------
# 4. Block unknown app install
# -----------------------------
$ADB shell settings put secure install_non_market_apps 0

# -----------------------------
# 5. Background execution kill
# -----------------------------
$ADB shell settings put global background_check 1

echo "[✓] Android auto-guard active"