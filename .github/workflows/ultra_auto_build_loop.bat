@echo off
title 🔄 Auto Build Loop

set INTERVAL=300

:loop
echo 🔁 Running Build + Push...
call ultra_build_push.bat

echo ⏳ Waiting %INTERVAL% seconds...
timeout /t %INTERVAL% >nul

goto loop