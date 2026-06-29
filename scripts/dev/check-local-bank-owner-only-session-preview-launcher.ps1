$ErrorActionPreference = "Stop"

$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
Set-Location $RepoRoot

Write-Host "=== v0.5.7 owner preview launcher check ===" -ForegroundColor Cyan

$Launcher = "scripts/dev/start-owner-session-preview-page.ps1"
$Doc = "docs/dev/local-bank-owner-only-session-preview-launcher.md"

Write-Host "`n=== Verify launcher and docs exist ===" -ForegroundColor Yellow
if (!(Test-Path $Launcher)) {
  throw "Missing launcher: $Launcher"
}
if (!(Test-Path $Doc)) {
  throw "Missing doc: $Doc"
}

Write-Host "`n=== Launcher static safety checks ===" -ForegroundColor Yellow
$launcherContent = Get-Content $Launcher -Raw -Encoding UTF8

$required = @(
  "VOILA_ENABLE_EXAM_PREP_OWNER_ONLY_SESSION_PREVIEW_PAGE",
  "VOILA_ENABLE_EXAM_PREP_OWNER_ONLY_SESSION_PREVIEW_ROUTE",
  "/owner/exam-prep/session-preview",
  "/owner/exam-prep/session-preview.json",
  "127.0.0.1",
  "NoStart",
  "OpenBrowser"
)

foreach ($needle in $required) {
  if ($launcherContent -notmatch [regex]::Escape($needle)) {
    throw "Launcher missing expected marker: $needle"
  }
}

$forbidden = @(
  "VOILA_ENABLE_EXAM_PREP_PUBLIC",
  "VOILA_ENABLE_EXAM_PREP_TESTER",
  "persist_attempt",
  "persist_session",
  "update_progress",
  "score_live_session"
)

foreach ($needle in $forbidden) {
  if ($launcherContent -match $needle) {
    throw "Launcher contains forbidden marker: $needle"
  }
}

Write-Host "`n=== Launcher dry-run ===" -ForegroundColor Yellow
& $Launcher -NoStart

Write-Host "`n=== Existing hidden route/page checks ===" -ForegroundColor Yellow
scripts/dev/check-local-bank-owner-only-session-preview-route.ps1

if (Test-Path ".tmp") {
  Remove-Item ".tmp" -Recurse -Force
}

scripts/dev/check-local-bank-owner-only-session-preview-page.ps1

if (Test-Path ".tmp") {
  Remove-Item ".tmp" -Recurse -Force
}

Write-Host "`n=== Ensure no public UI/template/static asset was added ===" -ForegroundColor Yellow
$changed = git diff --name-only
$changed | Out-Host
$changedText = $changed -join "`n"

if ($changedText -match "templates|static|assets") {
  throw "Unexpected public UI/template/static asset change in v0.5.7"
}
if ($changedText -match "services/api/web_app.py") {
  throw "v0.5.7 must not patch web_app.py"
}

Write-Host "`n=== Diff whitespace check ===" -ForegroundColor Yellow
git diff --check

Write-Host "`n=== v0.5.7 OWNER PREVIEW LAUNCHER CHECK PASS ===" -ForegroundColor Green
