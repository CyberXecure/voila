@echo off
setlocal
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0Remove-Voila-Shortcut.ps1"
echo.
pause
