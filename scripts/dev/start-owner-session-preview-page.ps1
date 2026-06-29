param(
  [int]$Port = 8787,
  [switch]$OpenBrowser,
  [switch]$NoStart
)

$ErrorActionPreference = "Stop"

$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
Set-Location $RepoRoot

$env:VOILA_ENABLE_EXAM_PREP_OWNER_ONLY_SESSION_PREVIEW_ROUTE = "1"
$env:VOILA_ENABLE_EXAM_PREP_OWNER_ONLY_SESSION_PREVIEW_PAGE = "1"

$PreviewUrl = "http://127.0.0.1:$Port/owner/exam-prep/session-preview"
$JsonUrl = "http://127.0.0.1:$Port/owner/exam-prep/session-preview.json"

Write-Host "=== Voila Owner-Only Exam Prep Session Preview ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "Owner-only preview flags enabled for this PowerShell process:" -ForegroundColor Yellow
Write-Host "VOILA_ENABLE_EXAM_PREP_OWNER_ONLY_SESSION_PREVIEW_PAGE=1"
Write-Host "VOILA_ENABLE_EXAM_PREP_OWNER_ONLY_SESSION_PREVIEW_ROUTE=1"
Write-Host ""
Write-Host "HTML preview:" -ForegroundColor Green
Write-Host $PreviewUrl
Write-Host ""
Write-Host "JSON preview:" -ForegroundColor Green
Write-Host $JsonUrl
Write-Host ""
Write-Host "Safety policy:" -ForegroundColor Yellow
Write-Host "- hidden owner/local route"
Write-Host "- no public navigation"
Write-Host "- no form/input/submit"
Write-Host "- no attempt/session/progress persistence"
Write-Host "- no live scoring"
Write-Host "- max 5 local-bank questions"
Write-Host ""

if ($OpenBrowser) {
  Start-Process $PreviewUrl
}

if ($NoStart) {
  Write-Host "NoStart selected. Environment prepared; Voila was not started." -ForegroundColor Yellow
  return
}

$StartScript = Join-Path $RepoRoot "scripts/dev/start-voila.ps1"

if (Test-Path $StartScript) {
  Write-Host "Starting Voila with existing dev launcher..." -ForegroundColor Yellow
  & $StartScript
} else {
  Write-Host "scripts/dev/start-voila.ps1 not found. Starting FastAPI directly..." -ForegroundColor Yellow
  $env:PYTHONPATH = Join-Path $RepoRoot "services/api"
  python -m uvicorn web_app:app --host 127.0.0.1 --port $Port
}
