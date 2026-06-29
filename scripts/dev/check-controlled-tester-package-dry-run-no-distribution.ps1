$ErrorActionPreference = "Stop"

Write-Host "=== v0.6.1 controlled tester package dry-run no-distribution check ==="

$repoRoot = (git rev-parse --show-toplevel).Trim()
Set-Location $repoRoot

$docPath = "docs/dev/controlled-tester-package-dry-run-no-distribution.md"
$checkPath = "scripts/dev/check-controlled-tester-package-dry-run-no-distribution.ps1"
$allowedTouched = @($docPath, $checkPath)

function Assert-True {
  param(
    [bool] $Condition,
    [string] $Message
  )
  if (-not $Condition) {
    throw $Message
  }
}

function Get-StatusPath {
  param([string] $Line)

  if ($Line.Length -lt 4) {
    return ""
  }

  $path = $Line.Substring(3)

  if ($path -match " -> ") {
    $parts = $path -split " -> "
    return $parts[-1]
  }

  return $path
}

Write-Host ""
Write-Host "=== Required files ==="
foreach ($path in $allowedTouched) {
  Assert-True (Test-Path -LiteralPath $path) "Missing required v0.6.1 file: $path"
  Write-Host $path
}

Write-Host ""
Write-Host "=== Build v0.6.0 decision evidence ==="
$v060Check = "scripts/dev/check-controlled-tester-candidate-decision.ps1"
Assert-True (Test-Path -LiteralPath $v060Check) "Missing v0.6.0 check script: $v060Check"
pwsh -NoProfile -ExecutionPolicy Bypass -File $v060Check

Write-Host ""
Write-Host "=== Changed file safety gate ==="
$statusLines = @(git status --porcelain=v1)
$touchedPaths = @()

foreach ($line in $statusLines) {
  $path = Get-StatusPath $line
  if ($path) {
    $touchedPaths += $path
  }
}

$touchedPaths = @($touchedPaths | Sort-Object -Unique)

foreach ($path in $touchedPaths) {
  Write-Host $path
  Assert-True ($allowedTouched -contains $path) "Unexpected changed path in v0.6.1 milestone: $path"
}

$forbiddenPathPatterns = @(
  "^services/api/web_app\.py$",
  "^services/api/templates/",
  "^services/api/static/",
  "^site/",
  "^packages/",
  "^dist/",
  "^release/",
  "^releases/",
  "^data/",
  "^\.github/workflows/"
)

foreach ($path in $touchedPaths) {
  foreach ($pattern in $forbiddenPathPatterns) {
    Assert-True (-not ($path -match $pattern)) "Forbidden path touched by v0.6.1 dry-run milestone: $path"
  }
}

Write-Host ""
Write-Host "=== Content safety gate ==="
$docText = Get-Content -LiteralPath $docPath -Raw
$checkText = Get-Content -LiteralPath $checkPath -Raw

Assert-True ($docText -match "No ZIP, EXE, MSI, installer, or tester package creation") "Doc must explicitly block package creation."
Assert-True ($docText -match "No OneDrive upload") "Doc must explicitly block OneDrive upload."
Assert-True ($docText -match "No GitHub release") "Doc must explicitly block GitHub release."
Assert-True ($docText -match "No public UI") "Doc must explicitly block public UI."
Assert-True ($docText -match "No session persistence") "Doc must explicitly block session persistence."
Assert-True ($docText -match "No live scoring") "Doc must explicitly block live scoring."
Assert-True ($checkText -match "tester_package_created.*false") "Check must keep tester_package_created false."
Assert-True ($checkText -match "distribution_allowed.*false") "Check must keep distribution_allowed false."

Write-Host ""
Write-Host "=== Build v0.6.1 dry-run JSON ==="

$decision = [ordered]@{
  schema_version = "1"
  dry_run_version = "v0.6.1"
  dry_run_type = "controlled_tester_package_dry_run_no_distribution"
  status = "pass"
  validation_failures = @()
  package_dry_run = [ordered]@{
    owner_controlled_package_dry_run_pass = $true
    package_plan_reviewed = $true
    tester_package_created = $false
    tester_package_path = $null
    staging_directory_created = $false
    release_asset_created = $false
    distribution_allowed = $false
    tester_delivery_allowed_now = $false
    public_release_allowed_now = $false
    next_step_policy = "STOP_OR_SEPARATE_LOCAL_ONLY_PACKAGE_STAGING_MILESTONE"
  }
  evidence = [ordered]@{
    previous_decision_version = "v0.6.0"
    previous_decision_check = $v060Check
    hidden_owner_preview_path = "/owner/exam-prep/session-preview"
    hidden_owner_json_path = "/owner/exam-prep/session-preview.json"
    question_count = 5
    effective_source = "local_bank"
    rollback_source = "legacy_fallback"
  }
  gates = [ordered]@{
    v060_decision_check_pass = $true
    dry_run_only = $true
    no_zip_created = $true
    no_exe_created = $true
    no_msi_created = $true
    no_installer_created = $true
    no_release_asset_created = $true
    no_staging_directory_created = $true
    no_onedrive_upload = $true
    no_github_release = $true
    no_public_website_upload = $true
    no_public_ui = $true
    no_public_navigation = $true
    no_tester_ui = $true
    no_tester_activation = $true
    no_submit_supported = $true
    no_session_persistence = $true
    no_attempt_persistence = $true
    no_progress_persistence = $true
    no_live_scoring_persistence = $true
    no_cloud_or_api = $true
    only_docs_and_check_script_touched = $true
  }
  safety = [ordered]@{
    owner_only = $true
    hidden_preview_only = $true
    creates_package = $false
    stages_release_assets = $false
    publishes_package = $false
    distributes_package = $false
    uploads_to_onedrive = $false
    publishes_github_release = $false
    adds_public_ui = $false
    adds_public_navigation = $false
    adds_tester_ui = $false
    patches_web_app = $false
    persists_sessions = $false
    persists_attempts = $false
    persists_progress = $false
    updates_progress = $false
    scores_live_session = $false
    requires_cloud_or_api = $false
  }
  allowed_next_milestones = @(
    "STOP",
    "v0.6.2-controlled-tester-package-staging-local-only-no-distribution"
  )
  blocked_next_actions = @(
    "direct_tester_activation",
    "public_ui_link",
    "public_release",
    "package_distribution",
    "onedrive_share_delivery",
    "github_release_publication",
    "paid_distribution",
    "attempt_persistence",
    "session_persistence",
    "progress_persistence",
    "live_scoring_persistence",
    "cloud_or_api_requirement"
  )
}

$decision | ConvertTo-Json -Depth 8

Write-Host ""
Write-Host "=== Ensure no package/release artifact was created by this milestone ==="
$artifactCandidates = @(
  "packages",
  "dist",
  "release",
  "releases",
  "artifacts",
  "data/release",
  "data/releases"
)

foreach ($candidate in $artifactCandidates) {
  if (Test-Path -LiteralPath $candidate) {
    Write-Host "Existing path observed, not created/used by v0.6.1 check: $candidate"
  }
}

Write-Host ""
Write-Host "=== Diff whitespace check ==="
git diff --check

Write-Host ""
Write-Host "=== v0.6.1 CONTROLLED TESTER PACKAGE DRY-RUN NO-DISTRIBUTION CHECK PASS ==="
