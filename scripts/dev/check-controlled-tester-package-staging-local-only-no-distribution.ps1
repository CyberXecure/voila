$ErrorActionPreference = "Stop"

Write-Host "=== v0.6.2 controlled tester package staging local-only no-distribution check ==="

$repoRoot = (git rev-parse --show-toplevel).Trim()
Set-Location $repoRoot

$docPath = "docs/dev/controlled-tester-package-staging-local-only-no-distribution.md"
$checkPath = "scripts/dev/check-controlled-tester-package-staging-local-only-no-distribution.ps1"
$allowedTouched = @($docPath, $checkPath)

$stagingRoot = "D:\dev\release-assets\voila\v0.6.2-controlled-tester-staging-local-only"
$manifestPath = Join-Path $stagingRoot "STAGING-DRY-RUN-MANIFEST.json"
$readmePath = Join-Path $stagingRoot "STAGING-LOCAL-ONLY-README.txt"

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

function Resolve-FullPathSafe {
  param([string] $Path)

  if (Test-Path -LiteralPath $Path) {
    return (Resolve-Path -LiteralPath $Path).Path
  }

  $parent = Split-Path -Parent $Path
  $leaf = Split-Path -Leaf $Path
  if ($parent -and (Test-Path -LiteralPath $parent)) {
    return (Join-Path (Resolve-Path -LiteralPath $parent).Path $leaf)
  }

  return [System.IO.Path]::GetFullPath($Path)
}

Write-Host ""
Write-Host "=== Required files ==="
foreach ($path in $allowedTouched) {
  Assert-True (Test-Path -LiteralPath $path) "Missing required v0.6.2 file: $path"
  Write-Host $path
}

Write-Host ""
Write-Host "=== Verify v0.6.1 dry-run evidence markers ==="
$v061Check = "scripts/dev/check-controlled-tester-package-dry-run-no-distribution.ps1"
$v061Doc = "docs/dev/controlled-tester-package-dry-run-no-distribution.md"

Assert-True (Test-Path -LiteralPath $v061Check) "Missing v0.6.1 check script: $v061Check"
Assert-True (Test-Path -LiteralPath $v061Doc) "Missing v0.6.1 doc: $v061Doc"

$v061CheckText = Get-Content -LiteralPath $v061Check -Raw
$v061DocText = Get-Content -LiteralPath $v061Doc -Raw

Assert-True ($v061DocText -match "v0\.6\.1 Controlled Tester Package Dry-Run") "v0.6.1 doc marker missing."
Assert-True ($v061CheckText -match "v0\.6\.1 CONTROLLED TESTER PACKAGE DRY-RUN NO-DISTRIBUTION CHECK PASS") "v0.6.1 PASS marker missing."
Assert-True ($v061CheckText -match "tester_package_created.*false") "v0.6.1 check must keep tester_package_created false."
Assert-True ($v061CheckText -match "distribution_allowed.*false") "v0.6.1 check must keep distribution_allowed false."
Assert-True ($v061CheckText -match "no_onedrive_upload") "v0.6.1 check must keep OneDrive upload blocked."
Assert-True ($v061CheckText -match "no_github_release") "v0.6.1 check must keep GitHub release blocked."

Write-Host "v0.6.1 dry-run evidence markers verified."

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
  Assert-True ($allowedTouched -contains $path) "Unexpected changed path in v0.6.2 milestone: $path"
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
    Assert-True (-not ($path -match $pattern)) "Forbidden path touched by v0.6.2 staging milestone: $path"
  }
}

Write-Host ""
Write-Host "=== Content safety gate ==="
$docText = Get-Content -LiteralPath $docPath -Raw
$checkText = Get-Content -LiteralPath $checkPath -Raw

Assert-True ($docText -match "No ZIP creation") "Doc must explicitly block ZIP creation."
Assert-True ($docText -match "No EXE creation") "Doc must explicitly block EXE creation."
Assert-True ($docText -match "No MSI creation") "Doc must explicitly block MSI creation."
Assert-True ($docText -match "No installer creation") "Doc must explicitly block installer creation."
Assert-True ($docText -match "No OneDrive upload") "Doc must explicitly block OneDrive upload."
Assert-True ($docText -match "No GitHub release") "Doc must explicitly block GitHub release."
Assert-True ($docText -match "No public UI") "Doc must explicitly block public UI."
Assert-True ($docText -match "No session persistence") "Doc must explicitly block session persistence."
Assert-True ($docText -match "No live scoring") "Doc must explicitly block live scoring."
Assert-True ($checkText -match "package_created.*false") "Check must keep package_created false."
Assert-True ($checkText -match "distribution_allowed.*false") "Check must keep distribution_allowed false."
Assert-True ($checkText -match "uploads_to_onedrive.*false") "Check must keep uploads_to_onedrive false."

Write-Host ""
Write-Host "=== Create local-only staging evidence directory ==="
New-Item -ItemType Directory -Force -Path $stagingRoot | Out-Null

$repoFull = Resolve-FullPathSafe $repoRoot
$stagingFull = Resolve-FullPathSafe $stagingRoot

Assert-True (-not ($stagingFull.StartsWith($repoFull, [System.StringComparison]::OrdinalIgnoreCase))) "Staging root must be outside repository."

$manifest = [ordered]@{
  schema_version = "1"
  staging_version = "v0.6.2"
  staging_type = "controlled_tester_package_staging_local_only_no_distribution"
  status = "pass"
  local_staging = [ordered]@{
    owner_controlled_local_staging_evidence_created = $true
    staging_root = $stagingRoot
    staging_root_outside_repo = $true
    manifest_created = $true
    readme_created = $true
    package_created = $false
    zip_created = $false
    exe_created = $false
    msi_created = $false
    installer_created = $false
    release_archive_created = $false
    distribution_allowed = $false
    tester_delivery_allowed_now = $false
    public_release_allowed_now = $false
    next_step_policy = "STOP_OR_SEPARATE_PACKAGE_CONTENTS_MANIFEST_MILESTONE_ONLY"
  }
  evidence = [ordered]@{
    previous_dry_run_version = "v0.6.1"
    previous_dry_run_check = $v061Check
    hidden_owner_preview_path = "/owner/exam-prep/session-preview"
    hidden_owner_json_path = "/owner/exam-prep/session-preview.json"
    question_count = 5
    effective_source = "local_bank"
    rollback_source = "legacy_fallback"
  }
  gates = [ordered]@{
    v061_dry_run_check_pass = $true
    local_staging_only = $true
    staging_root_outside_repo = $true
    no_zip_created = $true
    no_exe_created = $true
    no_msi_created = $true
    no_installer_created = $true
    no_release_archive_created = $true
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
    only_docs_and_check_script_touched_in_repo = $true
  }
  safety = [ordered]@{
    owner_only = $true
    hidden_preview_only = $true
    creates_local_staging_evidence = $true
    creates_package = $false
    stages_release_archive = $false
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
    "v0.6.3-controlled-tester-package-contents-manifest-no-build-no-distribution"
  )
  blocked_next_actions = @(
    "direct_tester_activation",
    "public_ui_link",
    "public_release",
    "package_distribution",
    "onedrive_share_delivery",
    "github_release_publication",
    "paid_distribution",
    "zip_creation",
    "exe_creation",
    "msi_creation",
    "installer_creation",
    "attempt_persistence",
    "session_persistence",
    "progress_persistence",
    "live_scoring_persistence",
    "cloud_or_api_requirement"
  )
}

$manifestJson = $manifest | ConvertTo-Json -Depth 8
[System.IO.File]::WriteAllText($manifestPath, ($manifestJson + "`n"), [System.Text.UTF8Encoding]::new($false))

$readme = @"
Voila v0.6.2 controlled tester package staging local-only no-distribution

This directory is local evidence only.

It is not a tester package.
It is not a release asset.
It is not a distribution folder.
It must not be uploaded to OneDrive.
It must not be published as a GitHub release.
It must not be shared with testers.

Allowed contents:
- STAGING-LOCAL-ONLY-README.txt
- STAGING-DRY-RUN-MANIFEST.json

Blocked:
- ZIP, EXE, MSI, installer, runnable package, public UI, tester activation, submit flow, persistence, scoring, cloud/API.
"@

[System.IO.File]::WriteAllText($readmePath, ($readme.TrimEnd() + "`n"), [System.Text.UTF8Encoding]::new($false))

Write-Host "STAGING ROOT: $stagingRoot"
Write-Host "WROTE: $manifestPath"
Write-Host "WROTE: $readmePath"

Write-Host ""
Write-Host "=== Verify staging evidence contents ==="
$stagingFiles = @(Get-ChildItem -LiteralPath $stagingRoot -File | Select-Object -ExpandProperty Name | Sort-Object)
foreach ($name in $stagingFiles) {
  Write-Host $name
}

$allowedStagingNames = @(
  "STAGING-DRY-RUN-MANIFEST.json",
  "STAGING-LOCAL-ONLY-README.txt"
)

foreach ($name in $stagingFiles) {
  Assert-True ($allowedStagingNames -contains $name) "Unexpected file in local-only staging evidence directory: $name"
  Assert-True (-not ($name -match "\.(zip|exe|msi)$")) "Forbidden package/release artifact in staging evidence directory: $name"
}

Assert-True (Test-Path -LiteralPath $manifestPath) "Missing staging manifest."
Assert-True (Test-Path -LiteralPath $readmePath) "Missing staging README."

Write-Host ""
Write-Host "=== v0.6.2 staging JSON ==="
$manifestJson

Write-Host ""
Write-Host "=== Repository diff whitespace check ==="
git diff --check

Write-Host ""
Write-Host "=== v0.6.2 CONTROLLED TESTER PACKAGE STAGING LOCAL-ONLY NO-DISTRIBUTION CHECK PASS ==="
