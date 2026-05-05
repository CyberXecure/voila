$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = [System.IO.Path]::GetFullPath((Join-Path $ScriptDir "..\.."))

Set-Location $ProjectRoot

$Python = Join-Path $ProjectRoot ".venv\Scripts\python.exe"

Write-Host ""
Write-Host "Voila! Crop Editor"
Write-Host "URL: http://127.0.0.1:8790"
Write-Host ""

Start-Job -ScriptBlock {
    Start-Sleep -Seconds 2
    Start-Process "http://127.0.0.1:8790"
} | Out-Null

& $Python -m uvicorn crop_editor_app:app --app-dir .\services\api --host 127.0.0.1 --port 8790
