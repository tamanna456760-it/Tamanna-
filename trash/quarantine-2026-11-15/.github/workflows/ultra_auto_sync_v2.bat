@echo off
title 🔥 Tamanna Ultra Auto Sync V2

:: ===== CONFIG =====
set REPO_PATH=C:\Users\YourName\YourProject
set LOG_FILE=sync_log.txt
set BRANCH=main

:: ===== START LOG =====
echo =============================== >> %LOG_FILE%
echo 🔄 Sync started at %date% %time% >> %LOG_FILE%
echo =============================== >> %LOG_FILE%

:: ===== GO TO PROJECT =====
cd /d %REPO_PATH%

echo 📂 Current Directory:
cd

:: ===== CHECK GIT =====
git --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Git not installed!
    pause
    exit
)

:: ===== NETWORK CHECK =====
ping github.com -n 1 >nul
if errorlevel 1 (
    echo ❌ No internet connection!
    echo ❌ Network error at %date% %time% >> %LOG_FILE%
    pause
    exit
)

:: ===== ADD FILES =====
echo 🔄 Adding changes...
git add . >> %LOG_FILE% 2>&1

:: ===== COMMIT =====
set MSG=🔥 Auto commit %date% %time%
echo 💾 Committing...
git commit -m "%MSG%" >> %LOG_FILE% 2>&1

:: ===== PULL (SYNC FIRST) =====
echo 🔄 Pulling latest updates...
git pull origin %BRANCH% >> %LOG_FILE% 2>&1

:: ===== PUSH WITH RETRY =====
echo 🚀 Pushing to GitHub...
git push origin %BRANCH% >> %LOG_FILE% 2>&1

if errorlevel 1 (
    echo ⚠️ Push failed! Retrying...
    timeout /t 5 >nul
    git push origin %BRANCH% >> %LOG_FILE% 2>&1
)

:: ===== STATUS =====
echo 📊 Git Status:
git status

:: ===== AUTO CLEAN LOG (LIMIT SIZE) =====
for %%F in (%LOG_FILE%) do if %%~zF gtr 100000 del %LOG_FILE%

:: ===== END =====
echo ===============================
echo ✅ Sync Completed Successfully!
echo ===============================

pause