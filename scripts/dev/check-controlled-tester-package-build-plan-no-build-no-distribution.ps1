$ErrorActionPreference = "Stop"

Write-Host "=== v0.6.4 controlled tester package build plan no-build no-distribution check ==="

$repoRoot = (git rev-parse --show-toplevel).Trim()
Set-Location $repoRoot

$docPath = "docs/dev/controlled-tester-package-build-plan-no-build-no-distribution.md"
$checkPath = "scripts/dev/check-controlled-tester-package-build-plan-no-build-no-distribution.ps1"
$allowedTouched = @($docPath, $checkPath)

$planRoot = "D:\dev\release-assets\voila\v0.6.4-controlled-tester-package-build-plan-no-build-no-distribution"
$planPath = Join-Path $planRoot "BUILD-PLAN-DRY-RUN.json"
$readmePath = Join-Path $planRoot "BUILD-PLAN-README.txt"

function Assert-True {
  param([bool] $Condition, [string] $Message)
  if (-not $Condition) { throw $Message }
}

function Get-StatusPath {
  param([string] $Line)
  if ($Line.Length -lt 4) { return "" }
  $path = $Line.Substring(3)
  if ($path -match " -> ") { return (($path -split " -> ")[-1]) }
  return $path
}

function Resolve-FullPathSafe {
  param([string] $Path)
  if (Test-Path -LiteralPath $Path) { return (Resolve-Path -LiteralPath $Path).Path }
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
  Assert-True (Test-Path -LiteralPath $path) "Missing required v0.6.4 file: $path"
  Write-Host $path
}

Write-Host ""
Write-Host "=== Verify previous milestone evidence markers ==="
$previous = @{
  v060Doc = "docs/dev/controlled-tester-candidate-decision.md"
  v060Check = "scripts/dev/check-controlled-tester-candidate-decision.ps1"
  v061Doc = "docs/dev/controlled-tester-package-dry-run-no-distribution.md"
  v061Check = "scripts/dev/check-controlled-tester-package-dry-run-no-distribution.ps1"
  v062Doc = "docs/dev/controlled-tester-package-staging-local-only-no-distribution.md"
  v062Check = "scripts/dev/check-controlled-tester-package-staging-local-only-no-distribution.ps1"
  v063Doc = "docs/dev/controlled-tester-package-contents-manifest-no-build-no-distribution.md"
  v063Check = "scripts/dev/check-controlled-tester-package-contents-manifest-no-build-no-distribution.ps1"
}

foreach ($path in $previous.Values) {
  Assert-True (Test-Path -LiteralPath $path) "Missing previous milestone file: $path"
  Write-Host $path
}

$v060Text = Get-Content -LiteralPath $previous.v060Check -Raw
$v061Text = Get-Content -LiteralPath $previous.v061Check -Raw
$v062Text = Get-Content -LiteralPath $previous.v062Check -Raw
$v063Text = Get-Content -LiteralPath $previous.v063Check -Raw
$v063DocText = Get-Content -LiteralPath $previous.v063Doc -Raw

Assert-True ($v060Text -match "v0\.6\.0 CONTROLLED TESTER CANDIDATE DECISION CHECK PASS") "v0.6.0 PASS marker missing."
Assert-True ($v061Text -match "v0\.6\.1 CONTROLLED TESTER PACKAGE DRY-RUN NO-DISTRIBUTION CHECK PASS") "v0.6.1 PASS marker missing."
Assert-True ($v062Text -match "v0\.6\.2 CONTROLLED TESTER PACKAGE STAGING LOCAL-ONLY NO-DISTRIBUTION CHECK PASS") "v0.6.2 PASS marker missing."
Assert-True ($v063Text -match "v0\.6\.3 CONTROLLED TESTER PACKAGE CONTENTS MANIFEST NO-BUILD NO-DISTRIBUTION CHECK PASS") "v0.6.3 PASS marker missing."
Assert-True ($v063DocText -match "v0\.6\.4-controlled-tester-package-build-plan-no-build-no-distribution") "v0.6.3 allowed next marker missing."

Assert-True ($v060Text -match "tester_activation_allowed_now.*false") "v0.6.0 must keep tester activation blocked."
Assert-True ($v061Text -match "tester_package_created.*false") "v0.6.1 must keep tester package creation blocked."
Assert-True ($v062Text -match "package_created.*false") "v0.6.2 must keep package creation blocked."
Assert-True ($v063Text -match "package_created.*false") "v0.6.3 must keep package creation blocked."
Assert-True ($v063Text -match "build_allowed.*false") "v0.6.3 must keep build blocked."
Assert-True ($v063Text -match "copies_runtime_files.*false") "v0.6.3 must keep runtime copy blocked."
Assert-True ($v063Text -match "distribution_allowed.*false") "v0.6.3 must keep distribution blocked."
Assert-True ($v063Text -match "uploads_to_onedrive.*false") "v0.6.3 must keep OneDrive upload blocked."
Assert-True ($v063Text -match "publishes_github_release.*false") "v0.6.3 must keep GitHub release blocked."

Write-Host "Previous milestone evidence markers verified."

Write-Host ""
Write-Host "=== Changed file safety gate ==="
$statusLines = @(git status --porcelain=v1)
$touchedPaths = @()
foreach ($line in $statusLines) {
  $path = Get-StatusPath $line
  if ($path) { $touchedPaths += $path }
}
$touchedPaths = @($touchedPaths | Sort-Object -Unique)

foreach ($path in $touchedPaths) {
  Write-Host $path
  Assert-True ($allowedTouched -contains $path) "Unexpected changed path in v0.6.4 milestone: $path"
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
    Assert-True (-not ($path -match $pattern)) "Forbidden path touched by v0.6.4 build-plan milestone: $path"
  }
}

Write-Host ""
Write-Host "=== Content safety gate ==="
$docText = Get-Content -LiteralPath $docPath -Raw
$checkText = Get-Content -LiteralPath $checkPath -Raw

$requiredDocMarkers = @(
  "No runtime file copy",
  "No package build",
  "No ZIP creation",
  "No EXE creation",
  "No MSI creation",
  "No installer creation",
  "No runnable tester package creation",
  "No release archive creation",
  "No release asset staging",
  "No code signing",
  "No checksum publication",
  "No OneDrive upload",
  "No GitHub release",
  "No public UI",
  "No session persistence",
  "No live scoring",
  "This milestone does not approve any of those actions"
)
foreach ($marker in $requiredDocMarkers) {
  Assert-True ($docText -match [regex]::Escape($marker)) "Doc missing safety marker: $marker"
}

Assert-True ($checkText -match "build_allowed.*false") "Check must keep build_allowed false."
Assert-True ($checkText -match "package_created.*false") "Check must keep package_created false."
Assert-True ($checkText -match "copies_runtime_files.*false") "Check must keep copies_runtime_files false."
Assert-True ($checkText -match "zip_created.*false") "Check must keep zip_created false."
Assert-True ($checkText -match "distribution_allowed.*false") "Check must keep distribution_allowed false."
Assert-True ($checkText -match "uploads_to_onedrive.*false") "Check must keep uploads_to_onedrive false."
Assert-True ($checkText -match "publishes_github_release.*false") "Check must keep publishes_github_release false."

Write-Host ""
Write-Host "=== Create local-only build plan evidence directory ==="
New-Item -ItemType Directory -Force -Path $planRoot | Out-Null

$repoFull = Resolve-FullPathSafe $repoRoot
$planFull = Resolve-FullPathSafe $planRoot
Assert-True (-not ($planFull.StartsWith($repoFull, [System.StringComparison]::OrdinalIgnoreCase))) "Build plan root must be outside repository."

$plan = [ordered]@{
  schema_version = "1"
  plan_version = "v0.6.4"
  plan_type = "controlled_tester_package_build_plan_no_build_no_distribution"
  status = "pass"
  build_plan = [ordered]@{
    owner_controlled_build_plan_created = $true
    plan_root = $planRoot
    plan_root_outside_repo = $true
    plan_json_created = $true
    readme_created = $true
    build_allowed = $false
    package_created = $false
    copies_runtime_files = $false
    zip_created = $false
    exe_created = $false
    msi_created = $false
    installer_created = $false
    release_archive_created = $false
    release_asset_staging_created = $false
    code_signing_allowed = $false
    checksum_publication_allowed = $false
    distribution_allowed = $false
    tester_delivery_allowed_now = $false
    public_release_allowed_now = $false
    next_step_policy = "STOP_OR_SEPARATE_SOURCE_SELECTION_DRY_RUN_MILESTONE_ONLY"
  }
  planned_future_build_phases = @(
    @{ phase = "source_runtime_selection_review"; status = "planned_only"; executed_now = $false; approved_now = $false },
    @{ phase = "package_staging_root_preparation"; status = "planned_only"; executed_now = $false; approved_now = $false },
    @{ phase = "launcher_documentation_inclusion_review"; status = "planned_only"; executed_now = $false; approved_now = $false },
    @{ phase = "legal_license_inclusion_review"; status = "planned_only"; executed_now = $false; approved_now = $false },
    @{ phase = "local_validation_report_generation"; status = "planned_only"; executed_now = $false; approved_now = $false },
    @{ phase = "archive_checksum_creation"; status = "future_only_if_later_approved"; executed_now = $false; approved_now = $false }
  )
  evidence = [ordered]@{
    previous_contents_manifest_version = "v0.6.3"
    previous_contents_manifest_check = $previous.v063Check
    previous_staging_version = "v0.6.2"
    previous_dry_run_version = "v0.6.1"
    previous_decision_version = "v0.6.0"
    hidden_owner_preview_path = "/owner/exam-prep/session-preview"
    hidden_owner_json_path = "/owner/exam-prep/session-preview.json"
    question_count = 5
    effective_source = "local_bank"
    rollback_source = "legacy_fallback"
  }
  gates = [ordered]@{
    previous_milestone_markers_verified = $true
    build_plan_only = $true
    plan_root_outside_repo = $true
    no_build = $true
    no_runtime_file_copy = $true
    no_zip_created = $true
    no_exe_created = $true
    no_msi_created = $true
    no_installer_created = $true
    no_release_archive_created = $true
    no_release_asset_staging_created = $true
    no_code_signing = $true
    no_checksum_publication = $true
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
    creates_local_build_plan_evidence = $true
    creates_package = $false
    builds_package = $false
    copies_runtime_files = $false
    stages_release_archive = $false
    signs_code = $false
    publishes_checksum = $false
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
  allowed_next_milestones = @("STOP", "v0.6.5-controlled-tester-package-source-selection-dry-run-no-build-no-distribution")
  blocked_next_actions = @(
    "direct_tester_activation",
    "public_ui_link",
    "public_release",
    "package_distribution",
    "onedrive_share_delivery",
    "github_release_publication",
    "paid_distribution",
    "runtime_file_copy",
    "zip_creation",
    "exe_creation",
    "msi_creation",
    "installer_creation",
    "release_archive_creation",
    "actual_package_build",
    "code_signing",
    "checksum_publication",
    "attempt_persistence",
    "session_persistence",
    "progress_persistence",
    "live_scoring_persistence",
    "cloud_or_api_requirement"
  )
}

$planJson = $plan | ConvertTo-Json -Depth 10
[System.IO.File]::WriteAllText($planPath, ($planJson + "`n"), [System.Text.UTF8Encoding]::new($false))

$readme = @"
Voila v0.6.4 controlled tester package build plan no-build no-distribution

This directory is local evidence only.

It is not a tester package.
It is not a build output.
It is not a release asset.
It is not a distribution folder.
It must not be uploaded to OneDrive.
It must not be published as a GitHub release.
It must not be shared with testers.

Allowed contents:
- BUILD-PLAN-README.txt
- BUILD-PLAN-DRY-RUN.json

Blocked:
- runtime file copy, package build, ZIP, EXE, MSI, installer, runnable package, release archive, release asset staging, code signing, checksum publication, public UI, tester activation, submit flow, persistence, scoring, cloud/API.
"@

[System.IO.File]::WriteAllText($readmePath, ($readme.TrimEnd() + "`n"), [System.Text.UTF8Encoding]::new($false))

Write-Host "BUILD PLAN ROOT: $planRoot"
Write-Host "WROTE: $planPath"
Write-Host "WROTE: $readmePath"

Write-Host ""
Write-Host "=== Verify build plan evidence files ==="
$planFiles = @(Get-ChildItem -LiteralPath $planRoot -File | Select-Object -ExpandProperty Name | Sort-Object)
foreach ($name in $planFiles) { Write-Host $name }

$allowedPlanNames = @("BUILD-PLAN-DRY-RUN.json", "BUILD-PLAN-README.txt")
foreach ($name in $planFiles) {
  Assert-True ($allowedPlanNames -contains $name) "Unexpected file in local-only build plan evidence directory: $name"
  Assert-True (-not ($name -match "\.(zip|exe|msi)$")) "Forbidden package/release artifact in build plan evidence directory: $name"
}

Assert-True (Test-Path -LiteralPath $planPath) "Missing build-plan JSON."
Assert-True (Test-Path -LiteralPath $readmePath) "Missing build-plan README."

Write-Host ""
Write-Host "=== v0.6.4 build plan JSON ==="
$planJson

Write-Host ""
Write-Host "=== Repository diff whitespace check ==="
git diff --check

Write-Host ""
Write-Host "=== v0.6.4 CONTROLLED TESTER PACKAGE BUILD PLAN NO-BUILD NO-DISTRIBUTION CHECK PASS ==="
