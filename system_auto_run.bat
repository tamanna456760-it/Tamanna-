@echo off
title ⚡ Tamanna Auto System Run

set PROJECT_PATH=C:\Users\YourName\YourProject

cd /d %PROJECT_PATH%

echo 🚀 Running Full System...

:: Open folder
start "" %PROJECT_PATH%

:: Open CMD
start cmd /k "cd /d %PROJECT_PATH%"

:: Run Git Sync
call ultra_auto_sync_v2.bat

:: Build APK
call gradlew assembleDebug

echo ✅ All Systems Running!
pause