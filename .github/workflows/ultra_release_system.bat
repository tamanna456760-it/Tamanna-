@echo off
title 🚀 Tamanna Ultra Release System

:: ===== CONFIG =====
set PROJECT_PATH=C:\Users\YourName\YourProject
set APK_PATH=app\build\outputs\apk\debug\app-debug.apk
set LOG_FILE=release_log.txt
set BRANCH=main
set VERSION=v1.%random%

cd /d %PROJECT_PATH%

echo =============================== >> %LOG_FILE%
echo 🚀 Release started at %date% %time% >> %LOG_FILE%
echo =============================== >> %LOG_FILE%

:: ===== BUILD APK =====
echo 🔨 Building APK...
call gradlew assembleDebug >> %LOG_FILE% 2>&1

if errorlevel 1 (
    echo ❌ Build failed!
    pause
    exit
)

:: ===== CHECK APK =====
if not exist %APK_PATH% (
    echo ❌ APK not found!
    pause
    exit
)

echo 📦 APK Ready!

:: ===== GIT ADD =====
git add . >> %LOG_FILE% 2>&1

:: ===== COMMIT =====
set MSG=🚀 Release %VERSION% %date% %time%
git commit -m "%MSG%" >> %LOG_FILE% 2>&1

:: ===== PUSH =====
git push origin %BRANCH% >> %LOG_FILE% 2>&1

:: ===== CREATE TAG =====
git tag %VERSION%
git push origin %VERSION%

:: ===== UPLOAD TO GITHUB RELEASE =====
echo 🌐 Uploading to GitHub Release...

curl -X POST ^
-H "Accept: application/vnd.github+json" ^
-H "Authorization: Bearer %GITHUB_TOKEN%" ^
https://api.github.com/repos/USERNAME/REPO/releases ^
-d "{\"tag_name\":\"%VERSION%\",\"name\":\"Release %VERSION%\"}" >> %LOG_FILE%

echo ===============================
echo ✅ RELEASE COMPLETE!
echo ===============================

pause