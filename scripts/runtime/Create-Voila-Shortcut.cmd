@echo off
setlocal
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0Create-Voila-Shortcut.ps1"
echo.
pause
