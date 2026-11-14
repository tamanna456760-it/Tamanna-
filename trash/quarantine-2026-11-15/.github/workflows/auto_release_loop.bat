@echo off

set INTERVAL=600

:loop
call ultra_release_system.bat

timeout /t %INTERVAL% >nul
goto loop