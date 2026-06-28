param()

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

Write-Host "=== LOCAL BANK FIRST LIVE TRIAL PLANNING DOCUMENT CHECK v0.4.76 ==="

$ProjectRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
Set-Location $ProjectRoot

$DocPath = "docs/dev/local-bank-first-live-trial-planning-document.md"
if (-not (Test-Path $DocPath)) {
  throw "Missing planning document: $DocPath"
}

$Text = Get-Content -Raw -Path $DocPath

$version_ok = ($Text -match "v0\.4\.76")
$planning_only_ok = ($Text -match "planning-only" -and $Text -match "No live code path is changed")
$definition_ok = ($Text -match 'Definition of "live"' -and $Text -match "real study session receives local-bank questions")
$legacy_ok = ($Text -match "effective_source = legacy_fallback" -and $Text -match "effective_source remains legacy_fallback")
$abort_ok = ($Text -match "abort/fallback" -and $Text -match "legacy_fallback")
$fallback_ok = ($Text -match "effective_source_after_abort = legacy_fallback")
$attempt_ok = ($Text -match "Attempt persistence criteria" -and $Text -match "will_persist_attempts = false")
$progress_ok = ($Text -match "Progress update criteria" -and $Text -match "will_update_progress = false" -and $Text -match "will_persist_progress = false")
$scoring_ok = ($Text -match "Scoring criteria" -and $Text -match "will_score_live_session = false")
$leakage_ok = (
  $Text -match "correct_answer_preview" -and
  $Text -match "explanation_preview" -and
  $Text -match "raw snapshots" -and
  $Text -match "dry_run_items" -and
  $Text -match "selected_questions"
)
$xss_ok = (
  $Text -match "safe DOM rendering" -and
  $Text -match "no innerHTML" -and
  $Text -match "CodeQL"
)
$filesystem_ok = ($Text -match "no user-provided filesystem root" -or $Text -match "user-provided filesystem roots")
$next_ok = ($Text -match "v0.4.77" -and $Text -match "contract skeleton")
$no_live_ok = (
  $Text -match "local-bank questions are not delivered live" -and
  $Text -match "consume local-bank questions live" -and
  $Text -match "replace effective source"
)

$statusNames = @(
  git status --porcelain | ForEach-Object {
    $line = [string]$_
    if ($line.Length -ge 4) {
      ($line.Substring(3).Trim() -replace "\\", "/")
    }
  } | Where-Object { $_ }
)

$statusNameText = ($statusNames -join "`n")

$expectedFiles = @(
  "docs/dev/local-bank-first-live-trial-planning-document.md",
  "scripts/dev/check-local-bank-first-live-trial-planning-document.ps1",
  "docs/dev/exam-prep-middleware-consolidation-plan.md",
  "scripts/dev/check-exam-prep-health.ps1"
)

$unexpectedFiles = @($statusNames | Where-Object { $expectedFiles -notcontains $_ })
$missingExpectedFiles = @($expectedFiles | Where-Object { $statusNames -notcontains $_ })

$no_web_app_change_ok = ($statusNameText -notmatch '(^|`n)services/api/web_app\.py($|`n)')
$no_runtime_py_change_ok = ($statusNameText -notmatch '(^|`n)services/api/.*\.py($|`n)')
$expected_files_only_ok = (@($unexpectedFiles).Count -eq 0 -and @($missingExpectedFiles).Count -eq 0)

Write-Host "version_ok $version_ok"
Write-Host "planning_only_ok $planning_only_ok"
Write-Host "definition_ok $definition_ok"
Write-Host "legacy_ok $legacy_ok"
Write-Host "abort_ok $abort_ok"
Write-Host "fallback_ok $fallback_ok"
Write-Host "attempt_ok $attempt_ok"
Write-Host "progress_ok $progress_ok"
Write-Host "scoring_ok $scoring_ok"
Write-Host "leakage_ok $leakage_ok"
Write-Host "xss_ok $xss_ok"
Write-Host "filesystem_ok $filesystem_ok"
Write-Host "next_ok $next_ok"
Write-Host "no_live_ok $no_live_ok"
Write-Host "no_web_app_change_ok $no_web_app_change_ok"
Write-Host "no_runtime_py_change_ok $no_runtime_py_change_ok"
Write-Host "expected_files_only_ok $expected_files_only_ok"

if (-not ($version_ok -and $planning_only_ok -and $definition_ok -and $legacy_ok -and $abort_ok -and $fallback_ok -and $attempt_ok -and $progress_ok -and $scoring_ok -and $leakage_ok -and $xss_ok -and $filesystem_ok -and $next_ok -and $no_live_ok -and $no_web_app_change_ok -and $no_runtime_py_change_ok -and $expected_files_only_ok)) {
  throw "LOCAL BANK FIRST LIVE TRIAL PLANNING DOCUMENT CHECK v0.4.76 FAILED"
}

Write-Host "LOCAL BANK FIRST LIVE TRIAL PLANNING DOCUMENT CHECK v0.4.76 PASS"
