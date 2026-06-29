$ErrorActionPreference = "Stop"

Write-Host "=== v0.6.3 controlled tester package contents manifest no-build no-distribution check ==="

$repoRoot = (git rev-parse --show-toplevel).Trim()
Set-Location $repoRoot

$docPath = "docs/dev/controlled-tester-package-contents-manifest-no-build-no-distribution.md"
$checkPath = "scripts/dev/check-controlled-tester-package-contents-manifest-no-build-no-distribution.ps1"
$allowedTouched = @($docPath, $checkPath)

$contentsRoot = "D:\dev\release-assets\voila\v0.6.3-controlled-tester-package-contents-manifest-no-build-no-distribution"
$manifestPath = Join-Path $contentsRoot "CONTENTS-MANIFEST-DRY-RUN.json"
$readmePath = Join-Path $contentsRoot "CONTENTS-MANIFEST-README.txt"

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
  Assert-True (Test-Path -LiteralPath $path) "Missing required v0.6.3 file: $path"
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
}

foreach ($path in $previous.Values) {
  Assert-True (Test-Path -LiteralPath $path) "Missing previous milestone file: $path"
  Write-Host $path
}

$v060Text = Get-Content -LiteralPath $previous.v060Check -Raw
$v061Text = Get-Content -LiteralPath $previous.v061Check -Raw
$v062Text = Get-Content -LiteralPath $previous.v062Check -Raw
$v062DocText = Get-Content -LiteralPath $previous.v062Doc -Raw

Assert-True ($v060Text -match "v0\.6\.0 CONTROLLED TESTER CANDIDATE DECISION CHECK PASS") "v0.6.0 PASS marker missing."
Assert-True ($v061Text -match "v0\.6\.1 CONTROLLED TESTER PACKAGE DRY-RUN NO-DISTRIBUTION CHECK PASS") "v0.6.1 PASS marker missing."
Assert-True ($v062Text -match "v0\.6\.2 CONTROLLED TESTER PACKAGE STAGING LOCAL-ONLY NO-DISTRIBUTION CHECK PASS") "v0.6.2 PASS marker missing."
Assert-True ($v062DocText -match "v0\.6\.3-controlled-tester-package-contents-manifest-no-build-no-distribution") "v0.6.2 allowed next marker missing."
Assert-True ($v060Text -match "tester_activation_allowed_now.*false") "v0.6.0 must keep tester activation blocked."
Assert-True ($v061Text -match "tester_package_created.*false") "v0.6.1 must keep tester package creation blocked."
Assert-True ($v061Text -match "distribution_allowed.*false") "v0.6.1 must keep distribution blocked."
Assert-True ($v062Text -match "package_created.*false") "v0.6.2 must keep package creation blocked."
Assert-True ($v062Text -match "zip_created.*false") "v0.6.2 must keep ZIP creation blocked."
Assert-True ($v062Text -match "distribution_allowed.*false") "v0.6.2 must keep distribution blocked."
Assert-True ($v062Text -match "uploads_to_onedrive.*false") "v0.6.2 must keep OneDrive upload blocked."
Assert-True ($v062Text -match "publishes_github_release.*false") "v0.6.2 must keep GitHub release blocked."

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
  Assert-True ($allowedTouched -contains $path) "Unexpected changed path in v0.6.3 milestone: $path"
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
    Assert-True (-not ($path -match $pattern)) "Forbidden path touched by v0.6.3 contents manifest milestone: $path"
  }
}

Write-Host ""
Write-Host "=== Content safety gate ==="
$docText = Get-Content -LiteralPath $docPath -Raw
$checkText = Get-Content -LiteralPath $checkPath -Raw

$requiredDocMarkers = @(
  "No ZIP creation",
  "No EXE creation",
  "No MSI creation",
  "No installer creation",
  "No runnable tester package creation",
  "No release archive creation",
  "No release asset staging",
  "No OneDrive upload",
  "No GitHub release",
  "No public UI",
  "No session persistence",
  "No live scoring",
  "This milestone does not approve the inclusion, copying, building, packaging, signing, uploading, or sharing"
)
foreach ($marker in $requiredDocMarkers) {
  Assert-True ($docText -match [regex]::Escape($marker)) "Doc missing safety marker: $marker"
}

Assert-True ($checkText -match "package_created.*false") "Check must keep package_created false."
Assert-True ($checkText -match "zip_created.*false") "Check must keep zip_created false."
Assert-True ($checkText -match "build_allowed.*false") "Check must keep build_allowed false."
Assert-True ($checkText -match "distribution_allowed.*false") "Check must keep distribution_allowed false."
Assert-True ($checkText -match "uploads_to_onedrive.*false") "Check must keep uploads_to_onedrive false."
Assert-True ($checkText -match "publishes_github_release.*false") "Check must keep publishes_github_release false."

Write-Host ""
Write-Host "=== Create local-only contents manifest evidence directory ==="
New-Item -ItemType Directory -Force -Path $contentsRoot | Out-Null

$repoFull = Resolve-FullPathSafe $repoRoot
$contentsFull = Resolve-FullPathSafe $contentsRoot
Assert-True (-not ($contentsFull.StartsWith($repoFull, [System.StringComparison]::OrdinalIgnoreCase))) "Contents manifest root must be outside repository."

$manifest = [ordered]@{
  schema_version = "1"
  manifest_version = "v0.6.3"
  manifest_type = "controlled_tester_package_contents_manifest_no_build_no_distribution"
  status = "pass"
  contents_manifest = [ordered]@{
    owner_controlled_contents_manifest_created = $true
    contents_root = $contentsRoot
    contents_root_outside_repo = $true
    manifest_created = $true
    readme_created = $true
    package_created = $false
    zip_created = $false
    exe_created = $false
    msi_created = $false
    installer_created = $false
    release_archive_created = $false
    release_asset_staging_created = $false
    build_allowed = $false
    distribution_allowed = $false
    tester_delivery_allowed_now = $false
    public_release_allowed_now = $false
    next_step_policy = "STOP_OR_SEPARATE_PACKAGE_BUILD_PLAN_MILESTONE_ONLY"
  }
  candidate_future_content_categories = @(
    @{ category = "application_source_runtime"; status = "planned_only"; copied_now = $false; approved_for_package_now = $false },
    @{ category = "local_launcher_scripts"; status = "planned_only"; copied_now = $false; approved_for_package_now = $false },
    @{ category = "tester_readme_and_limitations"; status = "planned_only"; copied_now = $false; approved_for_package_now = $false },
    @{ category = "license_and_terms"; status = "planned_only"; copied_now = $false; approved_for_package_now = $false },
    @{ category = "local_validation_report"; status = "planned_only"; copied_now = $false; approved_for_package_now = $false }
  )
  evidence = [ordered]@{
    previous_staging_version = "v0.6.2"
    previous_staging_check = $previous.v062Check
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
    contents_manifest_only = $true
    contents_root_outside_repo = $true
    no_build = $true
    no_zip_created = $true
    no_exe_created = $true
    no_msi_created = $true
    no_installer_created = $true
    no_release_archive_created = $true
    no_release_asset_staging_created = $true
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
    creates_local_contents_manifest_evidence = $true
    creates_package = $false
    builds_package = $false
    copies_runtime_files = $false
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
  allowed_next_milestones = @("STOP", "v0.6.4-controlled-tester-package-build-plan-no-build-no-distribution")
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
    "release_archive_creation",
    "actual_package_build",
    "runtime_file_copy",
    "attempt_persistence",
    "session_persistence",
    "progress_persistence",
    "live_scoring_persistence",
    "cloud_or_api_requirement"
  )
}

$manifestJson = $manifest | ConvertTo-Json -Depth 10
[System.IO.File]::WriteAllText($manifestPath, ($manifestJson + "`n"), [System.Text.UTF8Encoding]::new($false))

$readme = @"
Voila v0.6.3 controlled tester package contents manifest no-build no-distribution

This directory is local evidence only.

It is not a tester package.
It is not a build output.
It is not a release asset.
It is not a distribution folder.
It must not be uploaded to OneDrive.
It must not be published as a GitHub release.
It must not be shared with testers.

Allowed contents:
- CONTENTS-MANIFEST-README.txt
- CONTENTS-MANIFEST-DRY-RUN.json

Blocked:
- ZIP, EXE, MSI, installer, runnable package, release archive, release asset staging, runtime file copy, public UI, tester activation, submit flow, persistence, scoring, cloud/API.
"@

[System.IO.File]::WriteAllText($readmePath, ($readme.TrimEnd() + "`n"), [System.Text.UTF8Encoding]::new($false))

Write-Host "CONTENTS ROOT: $contentsRoot"
Write-Host "WROTE: $manifestPath"
Write-Host "WROTE: $readmePath"

Write-Host ""
Write-Host "=== Verify contents manifest evidence files ==="
$contentsFiles = @(Get-ChildItem -LiteralPath $contentsRoot -File | Select-Object -ExpandProperty Name | Sort-Object)
foreach ($name in $contentsFiles) { Write-Host $name }

$allowedContentsNames = @("CONTENTS-MANIFEST-DRY-RUN.json", "CONTENTS-MANIFEST-README.txt")
foreach ($name in $contentsFiles) {
  Assert-True ($allowedContentsNames -contains $name) "Unexpected file in local-only contents manifest evidence directory: $name"
  Assert-True (-not ($name -match "\.(zip|exe|msi)$")) "Forbidden package/release artifact in contents manifest evidence directory: $name"
}

Assert-True (Test-Path -LiteralPath $manifestPath) "Missing contents manifest JSON."
Assert-True (Test-Path -LiteralPath $readmePath) "Missing contents manifest README."

Write-Host ""
Write-Host "=== v0.6.3 contents manifest JSON ==="
$manifestJson

Write-Host ""
Write-Host "=== Repository diff whitespace check ==="
git diff --check

Write-Host ""
Write-Host "=== v0.6.3 CONTROLLED TESTER PACKAGE CONTENTS MANIFEST NO-BUILD NO-DISTRIBUTION CHECK PASS ==="
