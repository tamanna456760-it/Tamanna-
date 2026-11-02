@echo off
title 🔥 Tamanna Build + Push System

:: ===== CONFIG =====
set PROJECT_PATH=C:\Users\YourName\YourProject
set APK_PATH=app\build\outputs\apk\debug\app-debug.apk
set LOG_FILE=build_log.txt
set BRANCH=main

:: ===== START LOG =====
echo =============================== >> %LOG_FILE%
echo 🔨 Build started at %date% %time% >> %LOG_FILE%
echo =============================== >> %LOG_FILE%

cd /d %PROJECT_PATH%

:: ===== CHECK GRADLE =====
if not exist gradlew.bat (
    echo ❌ gradlew not found!
    pause
    exit
)

:: ===== BUILD APK =====
echo 🔨 Building APK...
call gradlew assembleDebug >> %LOG_FILE% 2>&1

if errorlevel 1 (
    echo ❌ Build failed!
    pause
    exit
)

echo ✅ APK Build Complete!

:: ===== CHECK APK =====
if not exist %APK_PATH% (
    echo ❌ APK not found!
    pause
    exit
)

echo 📦 APK Ready: %APK_PATH%

:: ===== GIT ADD =====
echo 🔄 Adding files...
git add . >> %LOG_FILE% 2>&1

:: ===== COMMIT =====
set MSG=🔥 Build commit %date% %time%
git commit -m "%MSG%" >> %LOG_FILE% 2>&1

:: ===== PUSH =====
echo 🚀 Pushing to GitHub...
git push origin %BRANCH% >> %LOG_FILE% 2>&1

if errorlevel 1 (
    echo ⚠️ Push failed! Retrying...
    timeout /t 5 >nul
    git push origin %BRANCH% >> %LOG_FILE% 2>&1
)

:: ===== END =====
echo ===============================
echo ✅ Build + Push Done!
echo ===============================

pause