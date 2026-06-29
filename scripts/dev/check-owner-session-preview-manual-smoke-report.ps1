$ErrorActionPreference = "Stop"

$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
Set-Location $RepoRoot

Write-Host "=== v0.5.9 owner preview manual smoke report check ===" -ForegroundColor Cyan

$ReportRoot = ".tmp\v059-owner-preview-manual-smoke-report"
$ReportPath = Join-Path $ReportRoot "owner_preview_manual_smoke_report.json"

if (Test-Path $ReportRoot) {
  Remove-Item $ReportRoot -Recurse -Force
}

Write-Host "`n=== Build manual smoke report ===" -ForegroundColor Yellow
$reportJson = python "scripts/dev/build-owner-session-preview-manual-smoke-report.py" `
  --root "." `
  --output $ReportPath `
  --expect-pass

$reportJson | Out-Host

if (!(Test-Path $ReportPath)) {
  throw "Manual smoke report was not created"
}

$report = Get-Content $ReportPath -Raw -Encoding UTF8 | ConvertFrom-Json

if ($report.status -ne "pass") {
  throw "Manual smoke report status is not pass"
}
if ($report.report_version -ne "v0.5.9") {
  throw "Manual smoke report version is not v0.5.9"
}
if ($report.question_count -ne 5) {
  throw "Manual smoke report question_count is not 5"
}
if ($report.effective_source -ne "local_bank") {
  throw "Manual smoke report effective_source is not local_bank"
}
if ($report.rollback_source -ne "legacy_fallback") {
  throw "Manual smoke report rollback_source is not legacy_fallback"
}
if ($report.manual_screenshot_required -ne $true) {
  throw "Manual screenshot required marker is not true"
}
if ($report.manual_screenshot_should_be_committed -ne $false) {
  throw "Manual screenshot should not be committed by default"
}
if ($report.safety.adds_public_ui -ne $false) {
  throw "adds_public_ui is not false"
}
if ($report.safety.has_form -ne $false) {
  throw "has_form is not false"
}
if ($report.safety.has_input -ne $false) {
  throw "has_input is not false"
}
if ($report.safety.has_submit_button -ne $false) {
  throw "has_submit_button is not false"
}
if ($report.safety.persists_attempts -ne $false) {
  throw "persists_attempts is not false"
}
if ($report.safety.updates_progress -ne $false) {
  throw "updates_progress is not false"
}
if ($report.safety.scores_live_session -ne $false) {
  throw "scores_live_session is not false"
}

Write-Host "`n=== Existing hidden preview checks ===" -ForegroundColor Yellow
scripts/dev/check-local-bank-owner-only-session-preview-route.ps1

if (Test-Path ".tmp") {
  Remove-Item ".tmp" -Recurse -Force
}

scripts/dev/check-local-bank-owner-only-session-preview-page.ps1

if (Test-Path ".tmp") {
  Remove-Item ".tmp" -Recurse -Force
}

scripts/dev/check-local-bank-owner-only-session-preview-page-polish.ps1

if (Test-Path ".tmp") {
  Remove-Item ".tmp" -Recurse -Force
}

Write-Host "`n=== Ensure no public UI/template/static asset was added ===" -ForegroundColor Yellow
$changed = git diff --name-only
$changed | Out-Host
$changedText = $changed -join "`n"

if ($changedText -match "templates|static|assets") {
  throw "Unexpected public UI/template/static asset change in v0.5.9"
}
if ($changedText -match "services/api/web_app.py") {
  throw "v0.5.9 must not patch web_app.py"
}

Write-Host "`n=== Compile report helper ===" -ForegroundColor Yellow
python -m compileall "scripts/dev/build-owner-session-preview-manual-smoke-report.py"

Write-Host "`n=== Clean temporary report data ===" -ForegroundColor Yellow
if (Test-Path ".tmp") {
  Remove-Item ".tmp" -Recurse -Force
}

Write-Host "`n=== Diff whitespace check ===" -ForegroundColor Yellow
git diff --check

Write-Host "`n=== v0.5.9 OWNER MANUAL SMOKE REPORT CHECK PASS ===" -ForegroundColor Green
