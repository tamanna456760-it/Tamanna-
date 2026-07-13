@echo off
title 🚀 Tamanna System Launcher

:: ===== CONFIG =====
set PROJECT_PATH=C:\Users\YourName\YourProject
set ANDROID_STUDIO_PATH=C:\Program Files\Android\Android Studio\bin\studio64.exe

:: ===== START =====
echo ===============================
echo 🚀 Starting Tamanna AI System
echo ===============================

:: ===== OPEN PROJECT FOLDER =====
echo 📂 Opening Project Folder...
start "" %PROJECT_PATH%

:: ===== OPEN CMD IN PROJECT =====
echo 🖥 Opening Command Prompt...
start cmd /k "cd /d %PROJECT_PATH%"

:: ===== OPEN ANDROID STUDIO =====
if exist "%ANDROID_STUDIO_PATH%" (
    echo 🧠 Opening Android Studio...
    start "" "%ANDROID_STUDIO_PATH%" %PROJECT_PATH%
) else (
    echo ⚠️ Android Studio path not found!
)

:: ===== GIT STATUS =====
cd /d %PROJECT_PATH%
echo 📊 Checking Git Status...
git status

:: ===== OPTIONAL BUILD =====
echo.
set /p runBuild=Do you want to build APK? (y/n): 

if /i "%runBuild%"=="y" (
    echo 🔨 Building APK...
    call gradlew assembleDebug
)

:: ===== END =====
echo ===============================
echo ✅ System Ready!
echo ===============================

pause