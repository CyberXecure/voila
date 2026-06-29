$ErrorActionPreference = "Stop"

$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
Set-Location $RepoRoot

Write-Host "=== v0.5.2 owner-only real-course delivery report check ===" -ForegroundColor Cyan

$ApiPath = Join-Path $RepoRoot "services\api"
$env:PYTHONPATH = $ApiPath

$WorkRoot = Join-Path $RepoRoot ".tmp\v052-owner-only-real-course-delivery-report"
$ReportPath = Join-Path $WorkRoot "owner_only_real_course_delivery_report.json"

if (Test-Path $WorkRoot) {
  Remove-Item $WorkRoot -Recurse -Force
}

Write-Host "`n=== Build v0.5.2 report ===" -ForegroundColor Yellow
$reportJson = python "scripts/dev/build-local-bank-owner-only-real-course-delivery-report.py" `
  --root "." `
  --work-root $WorkRoot `
  --output $ReportPath `
  --expect-pass

$reportJson | Out-Host
$report = $reportJson | ConvertFrom-Json

Write-Host "`n=== Validate report file exists ===" -ForegroundColor Yellow
if (!(Test-Path $ReportPath)) {
  throw "Report file was not created: $ReportPath"
}

$reportFromFile = Get-Content $ReportPath -Raw -Encoding UTF8 | ConvertFrom-Json

if ($reportFromFile.status -ne "pass") {
  throw "Report status is not pass"
}
if ($reportFromFile.delivery_result.effective_source -ne "local_bank") {
  throw "Report delivery effective_source is not local_bank"
}
if ($reportFromFile.delivery_result.delivery_performed -ne $true) {
  throw "Report delivery_performed is not true"
}
if ([int]$reportFromFile.delivery_result.delivered_question_count -ne 5) {
  throw "Report delivered_question_count is not 5"
}
if ($reportFromFile.rollback_result.effective_source -ne "legacy_fallback") {
  throw "Report rollback effective_source is not legacy_fallback"
}
if ($reportFromFile.rollback_result.delivery_performed -ne $false) {
  throw "Report rollback delivery_performed is not false"
}
if ($reportFromFile.safety_confirmations.adds_public_ui -ne $false) {
  throw "Report adds_public_ui is not false"
}
if ($reportFromFile.safety_confirmations.patches_web_app -ne $false) {
  throw "Report patches_web_app is not false"
}
if ($reportFromFile.safety_confirmations.persists_attempts -ne $false) {
  throw "Report persists_attempts is not false"
}
if ($reportFromFile.safety_confirmations.scores_live_session -ne $false) {
  throw "Report scores_live_session is not false"
}
if ($reportFromFile.safety_confirmations.no_answers_in_report -ne $true) {
  throw "Report no_answers_in_report is not true"
}

Write-Host "`n=== Ensure no public UI / web_app.py patch ===" -ForegroundColor Yellow
$changed = git diff --name-only
$changed | Out-Host

if ($changed -match "services/api/web_app.py") {
  throw "web_app.py was modified, which is not allowed for v0.5.2"
}

Write-Host "`n=== Clean temporary report data ===" -ForegroundColor Yellow
if (Test-Path $WorkRoot) {
  Remove-Item $WorkRoot -Recurse -Force
}
if (Test-Path ".tmp") {
  $remaining = Get-ChildItem ".tmp" -Force -ErrorAction SilentlyContinue
  if (-not $remaining) {
    Remove-Item ".tmp" -Force
  }
}

Write-Host "`n=== Compile report helper ===" -ForegroundColor Yellow
python -m compileall "scripts/dev/build-local-bank-owner-only-real-course-delivery-report.py"

Write-Host "`n=== Diff whitespace check ===" -ForegroundColor Yellow
git diff --check

Write-Host "`n=== v0.5.2 REPORT CHECK PASS ===" -ForegroundColor Green

