$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = [System.IO.Path]::GetFullPath((Join-Path $ScriptDir "..\.."))

Set-Location $ProjectRoot

$Python = Join-Path $ProjectRoot ".venv\Scripts\python.exe"

if (-not (Test-Path $Python)) {
    throw "Virtual environment Python not found. Run: python -m venv .venv"
}

Write-Host ""
Write-Host "Voila! local UI"
Write-Host "URL: http://127.0.0.1:8787"
Write-Host ""

Start-Job -ScriptBlock {
    Start-Sleep -Seconds 2
    Start-Process "http://127.0.0.1:8787"
} | Out-Null

& $Python -m uvicorn web_app:app --app-dir .\services\api --host 127.0.0.1 --port 8787

Write-Host ""
Write-Host "Starting Voila! crop editor on port 8790..."

$CropPort = 8790
$CropListening = Get-NetTCPConnection -LocalPort $CropPort -State Listen -ErrorAction SilentlyContinue

if (-not $CropListening) {
    Start-Process pwsh -ArgumentList @(
        "-NoExit",
        "-Command",
        "cd `"$ProjectRoot`"; .\.venv\Scripts\python.exe -m uvicorn crop_editor_app:app --app-dir .\services\api --host 127.0.0.1 --port 8790 --log-level info"
    )
    Start-Sleep -Seconds 2
} else {
    Write-Host "Crop editor already running on port 8790."
}


Write-Host ""
Write-Host "=== Starting crop editor ==="
& (Join-Path $ProjectRoot "scripts\dev\start-crop-editor.ps1")

