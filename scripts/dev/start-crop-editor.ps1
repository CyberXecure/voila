$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = [System.IO.Path]::GetFullPath((Join-Path $ScriptDir "..\.."))
$Python = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
$Port = 8790

Write-Host "=== Voila! Crop Editor ==="

if (-not (Test-Path $Python)) {
    Write-Host "Python venv not found:" $Python
    exit 1
}

$Listening = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue

if ($Listening) {
    Write-Host "Crop editor already running on port $Port."
    exit 0
}

Write-Host "Starting crop editor on http://127.0.0.1:$Port ..."

Start-Process pwsh -ArgumentList @(
    "-NoExit",
    "-Command",
    "cd `"$ProjectRoot`"; .\.venv\Scripts\python.exe -m uvicorn crop_editor_app:app --app-dir .\services\api --host 127.0.0.1 --port 8790 --log-level info"
)

Start-Sleep -Seconds 3

$Listening = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue

if ($Listening) {
    Write-Host "Crop editor started successfully."
} else {
    Write-Host "Crop editor did not start. Check the new PowerShell window."
    exit 1
}
