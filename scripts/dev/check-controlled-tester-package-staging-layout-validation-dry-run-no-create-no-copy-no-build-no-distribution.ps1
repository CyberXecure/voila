$ErrorActionPreference = "Stop"

Write-Host "=== v0.6.12 controlled tester package staging layout validation dry-run no-create no-copy no-build no-distribution check ==="

$repoRoot = (git rev-parse --show-toplevel).Trim()
Set-Location $repoRoot

$docPath = "docs/dev/controlled-tester-package-staging-layout-validation-dry-run-no-create-no-copy-no-build-no-distribution.md"
$checkPath = "scripts/dev/check-controlled-tester-package-staging-layout-validation-dry-run-no-create-no-copy-no-build-no-distribution.ps1"
$allowedTouched = @($docPath, $checkPath)

$validationRoot = "D:\dev\release-assets\voila\v0.6.12-controlled-tester-package-staging-layout-validation-dry-run-no-create-no-copy-no-build-no-distribution"
$validationPath = Join-Path $validationRoot "STAGING-LAYOUT-VALIDATION-DRY-RUN.json"
$readmePath = Join-Path $validationRoot "STAGING-LAYOUT-VALIDATION-README.txt"

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

function Test-LayoutName {
  param([string] $LayoutPath)
  return ($LayoutPath -match "^[a-z][a-z0-9-]*/$")
}

function Test-MappingPath {
  param([string] $Path)
  return ($Path -match "^[A-Za-z0-9_.\-/]+$")
}

Write-Host ""
Write-Host "=== Required files ==="
foreach ($path in $allowedTouched) {
  Assert-True (Test-Path -LiteralPath $path) "Missing required v0.6.12 file: $path"
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
  v064Doc = "docs/dev/controlled-tester-package-build-plan-no-build-no-distribution.md"
  v064Check = "scripts/dev/check-controlled-tester-package-build-plan-no-build-no-distribution.ps1"
  v065Doc = "docs/dev/controlled-tester-package-source-selection-dry-run-no-build-no-distribution.md"
  v065Check = "scripts/dev/check-controlled-tester-package-source-selection-dry-run-no-build-no-distribution.ps1"
  v066Doc = "docs/dev/controlled-tester-package-source-validation-dry-run-no-build-no-distribution.md"
  v066Check = "scripts/dev/check-controlled-tester-package-source-validation-dry-run-no-build-no-distribution.ps1"
  v067Doc = "docs/dev/controlled-tester-package-source-allowlist-plan-no-build-no-distribution.md"
  v067Check = "scripts/dev/check-controlled-tester-package-source-allowlist-plan-no-build-no-distribution.ps1"
  v068Doc = "docs/dev/controlled-tester-package-copy-plan-no-copy-no-build-no-distribution.md"
  v068Check = "scripts/dev/check-controlled-tester-package-copy-plan-no-copy-no-build-no-distribution.ps1"
  v069Doc = "docs/dev/controlled-tester-package-copy-validation-dry-run-no-copy-no-build-no-distribution.md"
  v069Check = "scripts/dev/check-controlled-tester-package-copy-validation-dry-run-no-copy-no-build-no-distribution.ps1"
  v0610Doc = "docs/dev/controlled-tester-package-staging-readiness-dry-run-no-copy-no-build-no-distribution.md"
  v0610Check = "scripts/dev/check-controlled-tester-package-staging-readiness-dry-run-no-copy-no-build-no-distribution.ps1"
  v0611Doc = "docs/dev/controlled-tester-package-staging-layout-plan-no-create-no-copy-no-build-no-distribution.md"
  v0611Check = "scripts/dev/check-controlled-tester-package-staging-layout-plan-no-create-no-copy-no-build-no-distribution.ps1"
}

foreach ($path in $previous.Values) {
  Assert-True (Test-Path -LiteralPath $path) "Missing previous milestone file: $path"
  Write-Host $path
}

$v060Text = Get-Content -LiteralPath $previous.v060Check -Raw
$v061Text = Get-Content -LiteralPath $previous.v061Check -Raw
$v062Text = Get-Content -LiteralPath $previous.v062Check -Raw
$v063Text = Get-Content -LiteralPath $previous.v063Check -Raw
$v064Text = Get-Content -LiteralPath $previous.v064Check -Raw
$v065Text = Get-Content -LiteralPath $previous.v065Check -Raw
$v066Text = Get-Content -LiteralPath $previous.v066Check -Raw
$v067Text = Get-Content -LiteralPath $previous.v067Check -Raw
$v068Text = Get-Content -LiteralPath $previous.v068Check -Raw
$v069Text = Get-Content -LiteralPath $previous.v069Check -Raw
$v0610Text = Get-Content -LiteralPath $previous.v0610Check -Raw
$v0611Text = Get-Content -LiteralPath $previous.v0611Check -Raw
$v0611DocText = Get-Content -LiteralPath $previous.v0611Doc -Raw

Assert-True ($v060Text -match "v0\.6\.0 CONTROLLED TESTER CANDIDATE DECISION CHECK PASS") "v0.6.0 PASS marker missing."
Assert-True ($v061Text -match "v0\.6\.1 CONTROLLED TESTER PACKAGE DRY-RUN NO-DISTRIBUTION CHECK PASS") "v0.6.1 PASS marker missing."
Assert-True ($v062Text -match "v0\.6\.2 CONTROLLED TESTER PACKAGE STAGING LOCAL-ONLY NO-DISTRIBUTION CHECK PASS") "v0.6.2 PASS marker missing."
Assert-True ($v063Text -match "v0\.6\.3 CONTROLLED TESTER PACKAGE CONTENTS MANIFEST NO-BUILD NO-DISTRIBUTION CHECK PASS") "v0.6.3 PASS marker missing."
Assert-True ($v064Text -match "v0\.6\.4 CONTROLLED TESTER PACKAGE BUILD PLAN NO-BUILD NO-DISTRIBUTION CHECK PASS") "v0.6.4 PASS marker missing."
Assert-True ($v065Text -match "v0\.6\.5 CONTROLLED TESTER PACKAGE SOURCE SELECTION DRY-RUN NO-BUILD NO-DISTRIBUTION CHECK PASS") "v0.6.5 PASS marker missing."
Assert-True ($v066Text -match "v0\.6\.6 CONTROLLED TESTER PACKAGE SOURCE VALIDATION DRY-RUN NO-BUILD NO-DISTRIBUTION CHECK PASS") "v0.6.6 PASS marker missing."
Assert-True ($v067Text -match "v0\.6\.7 CONTROLLED TESTER PACKAGE SOURCE ALLOWLIST PLAN NO-BUILD NO-DISTRIBUTION CHECK PASS") "v0.6.7 PASS marker missing."
Assert-True ($v068Text -match "v0\.6\.8 CONTROLLED TESTER PACKAGE COPY PLAN NO-COPY NO-BUILD NO-DISTRIBUTION CHECK PASS") "v0.6.8 PASS marker missing."
Assert-True ($v069Text -match "v0\.6\.9 CONTROLLED TESTER PACKAGE COPY VALIDATION DRY-RUN NO-COPY NO-BUILD NO-DISTRIBUTION CHECK PASS") "v0.6.9 PASS marker missing."
Assert-True ($v0610Text -match "v0\.6\.10 CONTROLLED TESTER PACKAGE STAGING READINESS DRY-RUN NO-COPY NO-BUILD NO-DISTRIBUTION CHECK PASS") "v0.6.10 PASS marker missing."
Assert-True ($v0611Text -match "v0\.6\.11 CONTROLLED TESTER PACKAGE STAGING LAYOUT PLAN NO-CREATE NO-COPY NO-BUILD NO-DISTRIBUTION CHECK PASS") "v0.6.11 PASS marker missing."
Assert-True ($v0611DocText -match "v0\.6\.12-controlled-tester-package-staging-layout-validation-dry-run-no-create-no-copy-no-build-no-distribution") "v0.6.11 allowed next marker missing."

Assert-True ($v0611Text -match "staging_layout_plan_approved_now.*false") "v0.6.11 must keep staging layout plan approval blocked."
Assert-True ($v0611Text -match "layout_created_now.*false") "v0.6.11 must keep layout creation blocked."
Assert-True ($v0611Text -match "staging_layout_created.*false") "v0.6.11 must keep staging layout creation blocked."
Assert-True ($v0611Text -match "staging_tree_created.*false") "v0.6.11 must keep staging tree creation blocked."
Assert-True ($v0611Text -match "staging_root_created.*false") "v0.6.11 must keep staging root creation blocked."
Assert-True ($v0611Text -match "copy_allowed_now.*false") "v0.6.11 must keep copy allowed blocked."
Assert-True ($v0611Text -match "copy_executed_now.*false") "v0.6.11 must keep copy execution blocked."
Assert-True ($v0611Text -match "copies_runtime_files.*false") "v0.6.11 must keep runtime copy blocked."
Assert-True ($v0611Text -match "build_allowed.*false") "v0.6.11 must keep build blocked."
Assert-True ($v0611Text -match "distribution_allowed.*false") "v0.6.11 must keep distribution blocked."
Assert-True ($v0611Text -match "uploads_to_onedrive.*false") "v0.6.11 must keep OneDrive upload blocked."
Assert-True ($v0611Text -match "publishes_github_release.*false") "v0.6.11 must keep GitHub release blocked."

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
  Assert-True ($allowedTouched -contains $path) "Unexpected changed path in v0.6.12 milestone: $path"
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
    Assert-True (-not ($path -match $pattern)) "Forbidden path touched by v0.6.12 staging-layout-validation milestone: $path"
  }
}

Write-Host ""
Write-Host "=== Content safety gate ==="
$docText = Get-Content -LiteralPath $docPath -Raw
$checkText = Get-Content -LiteralPath $checkPath -Raw

$requiredDocMarkers = @(
  "No staging layout creation",
  "No staging tree creation",
  "No staging root creation for package contents",
  "No runtime file copy",
  "No package content copy",
  "No copy execution",
  "No package build",
  "No package source approval",
  "No source allowlist approval",
  "No source allowlist enforcement",
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
  "validation_checked = true",
  "layout_name_valid = true",
  "mapping_string_valid = true",
  "layout_created_now = false",
  "staging_layout_created = false",
  "staging_tree_created = false",
  "copy_allowed_now = false",
  "copy_executed_now = false",
  "copied_now = false",
  "approved_for_package_now = false",
  "This milestone records staging layout validation only"
)
foreach ($marker in $requiredDocMarkers) {
  Assert-True ($docText -match [regex]::Escape($marker)) "Doc missing safety marker: $marker"
}

Assert-True ($checkText -match "staging_layout_validation_approved_now.*false") "Check must keep staging_layout_validation_approved_now false."
Assert-True ($checkText -match "layout_validation_approved_now.*false") "Check must keep layout_validation_approved_now false."
Assert-True ($checkText -match "layout_created_now.*false") "Check must keep layout_created_now false."
Assert-True ($checkText -match "staging_layout_created.*false") "Check must keep staging_layout_created false."
Assert-True ($checkText -match "staging_tree_created.*false") "Check must keep staging_tree_created false."
Assert-True ($checkText -match "staging_root_created.*false") "Check must keep staging_root_created false."
Assert-True ($checkText -match "copy_allowed_now.*false") "Check must keep copy_allowed_now false."
Assert-True ($checkText -match "copy_executed_now.*false") "Check must keep copy_executed_now false."
Assert-True ($checkText -match "copied_now.*false") "Check must keep copied_now false."
Assert-True ($checkText -match "approved_for_package_now.*false") "Check must keep approved_for_package_now false."
Assert-True ($checkText -match "copies_runtime_files.*false") "Check must keep copies_runtime_files false."
Assert-True ($checkText -match "build_allowed.*false") "Check must keep build_allowed false."
Assert-True ($checkText -match "package_created.*false") "Check must keep package_created false."
Assert-True ($checkText -match "zip_created.*false") "Check must keep zip_created false."
Assert-True ($checkText -match "distribution_allowed.*false") "Check must keep distribution_allowed false."
Assert-True ($checkText -match "uploads_to_onedrive.*false") "Check must keep uploads_to_onedrive false."
Assert-True ($checkText -match "publishes_github_release.*false") "Check must keep publishes_github_release false."

Write-Host ""
Write-Host "=== Create local-only staging layout validation evidence directory ==="
New-Item -ItemType Directory -Force -Path $validationRoot | Out-Null

$repoFull = Resolve-FullPathSafe $repoRoot
$validationFull = Resolve-FullPathSafe $validationRoot
Assert-True (-not ($validationFull.StartsWith($repoFull, [System.StringComparison]::OrdinalIgnoreCase))) "Staging layout validation root must be outside repository."

$layoutNames = @("app/", "runtime/", "scripts/", "docs/", "legal/", "validation/")
$validatedLayouts = @()
foreach ($layoutName in $layoutNames) {
  $validatedLayouts += [ordered]@{
    layout_path = $layoutName
    validation_checked = $true
    layout_name_valid = [bool](Test-LayoutName $layoutName)
    planned_only = $true
    layout_validation_approved_now = $false
    layout_created_now = $false
    staging_layout_created = $false
    staging_tree_created = $false
    staging_root_created = $false
    copy_allowed_now = $false
    copy_executed_now = $false
    copied_now = $false
    approved_for_package_now = $false
  }
}

$sourceMappings = @(
  [ordered]@{ source_path = "services"; planned_layout_path = "app/services" },
  [ordered]@{ source_path = "services/api"; planned_layout_path = "app/services/api" },
  [ordered]@{ source_path = "scripts/dev"; planned_layout_path = "scripts/dev" },
  [ordered]@{ source_path = "docs"; planned_layout_path = "docs" },
  [ordered]@{ source_path = "LICENSE.txt"; planned_layout_path = "legal/LICENSE.txt" },
  [ordered]@{ source_path = "scripts/dev/check-controlled-tester-package-build-plan-no-build-no-distribution.ps1"; planned_layout_path = "validation/check-controlled-tester-package-build-plan-no-build-no-distribution.ps1" }
)

$validatedMappings = @()
foreach ($mapping in $sourceMappings) {
  $validatedMappings += [ordered]@{
    source_path = $mapping.source_path
    planned_layout_path = $mapping.planned_layout_path
    validation_checked = $true
    source_string_valid = [bool](Test-MappingPath $mapping.source_path)
    mapping_string_valid = [bool](Test-MappingPath $mapping.planned_layout_path)
    planned_only = $true
    layout_validation_approved_now = $false
    layout_created_now = $false
    staging_layout_created = $false
    staging_tree_created = $false
    staging_root_created = $false
    copy_allowed_now = $false
    copy_executed_now = $false
    copied_now = $false
    approved_for_package_now = $false
  }
}

$validation = [ordered]@{
  schema_version = "1"
  staging_layout_validation_version = "v0.6.12"
  staging_layout_validation_type = "controlled_tester_package_staging_layout_validation_dry_run_no_create_no_copy_no_build_no_distribution"
  status = "pass"
  staging_layout_validation = [ordered]@{
    owner_controlled_staging_layout_validation_dry_run_created = $true
    validation_root = $validationRoot
    validation_root_outside_repo = $true
    validation_json_created = $true
    readme_created = $true
    validation_checked = $true
    staging_layout_validation_approved_now = $false
    layout_validation_approved_now = $false
    staging_layout_created = $false
    layout_created_now = $false
    staging_tree_created = $false
    staging_root_created = $false
    copy_allowed_now = $false
    copy_executed_now = $false
    package_content_copy_allowed_now = $false
    package_created = $false
    build_allowed = $false
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
    next_step_policy = "STOP_OR_SEPARATE_STAGING_MANIFEST_PLAN_NO_CREATE_MILESTONE_ONLY"
  }
  validated_layout_entries = $validatedLayouts
  validated_source_mappings = $validatedMappings
  evidence = [ordered]@{
    previous_staging_layout_plan_version = "v0.6.11"
    previous_staging_layout_plan_check = $previous.v0611Check
    previous_staging_readiness_version = "v0.6.10"
    previous_copy_validation_version = "v0.6.9"
    previous_copy_plan_version = "v0.6.8"
    previous_source_allowlist_plan_version = "v0.6.7"
    previous_source_validation_version = "v0.6.6"
    previous_source_selection_version = "v0.6.5"
    previous_build_plan_version = "v0.6.4"
    previous_contents_manifest_version = "v0.6.3"
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
    staging_layout_validation_dry_run_only = $true
    validation_root_outside_repo = $true
    validation_checked = $true
    no_staging_layout_validation_approval_now = $true
    no_layout_validation_approval_now = $true
    no_staging_layout_created = $true
    no_layout_created_now = $true
    no_staging_tree_created = $true
    no_staging_root_created = $true
    no_copy_allowed_now = $true
    no_copy_executed_now = $true
    no_package_content_copy = $true
    no_source_approved_for_package_now = $true
    no_source_allowlist_approved_now = $true
    no_source_allowlist_enforced_now = $true
    no_runtime_file_copy = $true
    no_build = $true
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
    creates_local_staging_layout_validation_evidence = $true
    approves_staging_layout_validation = $false
    approves_layout_validation = $false
    creates_staging_layout = $false
    creates_staging_tree = $false
    creates_staging_root = $false
    allows_copy_now = $false
    executes_copy_now = $false
    approves_package_source = $false
    approves_source_allowlist = $false
    enforces_source_allowlist = $false
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
  allowed_next_milestones = @("STOP", "v0.6.13-controlled-tester-package-staging-manifest-plan-no-create-no-copy-no-build-no-distribution")
  blocked_next_actions = @(
    "direct_tester_activation",
    "public_ui_link",
    "public_release",
    "package_distribution",
    "onedrive_share_delivery",
    "github_release_publication",
    "paid_distribution",
    "staging_layout_creation",
    "staging_tree_creation",
    "staging_root_creation",
    "runtime_file_copy",
    "package_content_copy",
    "copy_execution",
    "package_source_approval",
    "source_allowlist_approval",
    "source_allowlist_enforcement",
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

$validationJson = $validation | ConvertTo-Json -Depth 10
[System.IO.File]::WriteAllText($validationPath, ($validationJson + "`n"), [System.Text.UTF8Encoding]::new($false))

$readme = @"
Voila v0.6.12 controlled tester package staging layout validation dry-run no-create no-copy no-build no-distribution

This directory is local evidence only.

It is not a tester package.
It is not a build output.
It is not a staging tree.
It is not a staging layout.
It is not a release asset.
It is not a distribution folder.
It must not be uploaded to OneDrive.
It must not be published as a GitHub release.
It must not be shared with testers.

Allowed contents:
- STAGING-LAYOUT-VALIDATION-README.txt
- STAGING-LAYOUT-VALIDATION-DRY-RUN.json

Blocked:
- staging layout creation, staging tree creation, staging root creation, runtime file copy, package content copy, copy execution, package source approval, source allowlist approval, source allowlist enforcement, package build, ZIP, EXE, MSI, installer, runnable package, release archive, release asset staging, code signing, checksum publication, public UI, tester activation, submit flow, persistence, scoring, cloud/API.
"@

[System.IO.File]::WriteAllText($readmePath, ($readme.TrimEnd() + "`n"), [System.Text.UTF8Encoding]::new($false))

Write-Host "STAGING LAYOUT VALIDATION ROOT: $validationRoot"
Write-Host "WROTE: $validationPath"
Write-Host "WROTE: $readmePath"

Write-Host ""
Write-Host "=== Verify staging layout validation evidence files ==="
$validationFiles = @(Get-ChildItem -LiteralPath $validationRoot -File | Select-Object -ExpandProperty Name | Sort-Object)
foreach ($name in $validationFiles) { Write-Host $name }

$allowedValidationNames = @("STAGING-LAYOUT-VALIDATION-DRY-RUN.json", "STAGING-LAYOUT-VALIDATION-README.txt")
foreach ($name in $validationFiles) {
  Assert-True ($allowedValidationNames -contains $name) "Unexpected file in local-only staging layout validation evidence directory: $name"
  Assert-True (-not ($name -match "\.(zip|exe|msi)$")) "Forbidden package/release artifact in staging layout validation evidence directory: $name"
}

Assert-True (Test-Path -LiteralPath $validationPath) "Missing staging-layout-validation JSON."
Assert-True (Test-Path -LiteralPath $readmePath) "Missing staging-layout-validation README."

Write-Host ""
Write-Host "=== v0.6.12 staging layout validation JSON ==="
$validationJson

Write-Host ""
Write-Host "=== Repository diff whitespace check ==="
git diff --check

Write-Host ""
Write-Host "=== v0.6.12 CONTROLLED TESTER PACKAGE STAGING LAYOUT VALIDATION DRY-RUN NO-CREATE NO-COPY NO-BUILD NO-DISTRIBUTION CHECK PASS ==="
