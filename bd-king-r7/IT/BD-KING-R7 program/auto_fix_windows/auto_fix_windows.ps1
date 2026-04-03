# Auto-Fix Windows Script (Run as Administrator)

# 1) Check for admin rights
If (-NOT ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole(`
    [Security.Principal.WindowsBuiltInRole] "Administrator"))
{
    Write-Host "Please run this script as Administrator." -ForegroundColor Red
    Pause
    exit
}

Write-Host "Starting Windows auto-fix routine..." -ForegroundColor Cyan

# 2) System File Checker
Write-Host "`n[1/5] Running SFC (system file check)..." -ForegroundColor Yellow
sfc /scannow

# 3) DISM - Repair Windows image
Write-Host "`n[2/5] Checking Windows image health..." -ForegroundColor Yellow
DISM /Online /Cleanup-Image /CheckHealth

Write-Host "`n[3/5] Scanning Windows image health..." -ForegroundColor Yellow
DISM /Online /Cleanup-Image /ScanHealth

Write-Host "`n[4/5] Restoring Windows image health..." -ForegroundColor Yellow
DISM /Online /Cleanup-Image /RestoreHealth

# 4) Schedule disk check on next reboot
Write-Host "`n[5/5] Scheduling disk check (chkdsk) on C: drive..." -ForegroundColor Yellow
chkdsk C: /F /R /X

Write-Host "`nA disk check has been scheduled. It may run on next restart." -ForegroundColor Green

# 5) Clean temp files
Write-Host "`nCleaning temporary files..." -ForegroundColor Yellow

# Windows temp
Remove-Item -Path "C:\Windows\Temp\*" -Recurse -Force -ErrorAction SilentlyContinue

# User temp
$envTemp = $env:TEMP
Remove-Item -Path "$envTemp\*" -Recurse -Force -ErrorAction SilentlyContinue

Write-Host "`nAuto-fix routine complete. Please restart your PC." -ForegroundColor Green
Pause
