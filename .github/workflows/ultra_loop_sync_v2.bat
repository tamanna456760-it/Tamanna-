@echo off
title 🔄 Tamanna Auto Loop Sync V2

set INTERVAL=60

:loop
echo 🔁 Running Auto Sync...
call ultra_auto_sync_v2.bat

echo ⏳ Waiting %INTERVAL% seconds...
timeout /t %INTERVAL% >nul

goto loop