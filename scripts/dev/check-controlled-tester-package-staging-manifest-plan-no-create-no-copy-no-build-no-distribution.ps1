$ErrorActionPreference = "Stop"

Write-Host "=== v0.6.13 controlled tester package staging manifest plan no-create no-copy no-build no-distribution check ==="

$repoRoot = (git rev-parse --show-toplevel).Trim()
Set-Location $repoRoot

$docPath = "docs/dev/controlled-tester-package-staging-manifest-plan-no-create-no-copy-no-build-no-distribution.md"
$checkPath = "scripts/dev/check-controlled-tester-package-staging-manifest-plan-no-create-no-copy-no-build-no-distribution.ps1"
$allowedTouched = @($docPath, $checkPath)

$manifestRoot = "D:\dev\release-assets\voila\v0.6.13-controlled-tester-package-staging-manifest-plan-no-create-no-copy-no-build-no-distribution"
$manifestPath = Join-Path $manifestRoot "STAGING-MANIFEST-PLAN-DRY-RUN.json"
$readmePath = Join-Path $manifestRoot "STAGING-MANIFEST-PLAN-README.txt"

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

function Test-ManifestSectionName {
  param([string] $Name)
  return ($Name -match "^[a-z][a-z0-9_]*$")
}

function Test-ManifestEntryString {
  param([string] $Value)
  return ($Value -match "^[A-Za-z0-9_.\-/ >]+$")
}

Write-Host ""
Write-Host "=== Required files ==="
foreach ($path in $allowedTouched) {
  Assert-True (Test-Path -LiteralPath $path) "Missing required v0.6.13 file: $path"
  Write-Host $path
}

Write-Host ""
Write-Host "=== Verify previous milestone evidence markers ==="
$previous = @(
  @{ version = "v0.6.0"; doc = "docs/dev/controlled-tester-candidate-decision.md"; check = "scripts/dev/check-controlled-tester-candidate-decision.ps1"; pass = "v0\.6\.0 CONTROLLED TESTER CANDIDATE DECISION CHECK PASS" },
  @{ version = "v0.6.1"; doc = "docs/dev/controlled-tester-package-dry-run-no-distribution.md"; check = "scripts/dev/check-controlled-tester-package-dry-run-no-distribution.ps1"; pass = "v0\.6\.1 CONTROLLED TESTER PACKAGE DRY-RUN NO-DISTRIBUTION CHECK PASS" },
  @{ version = "v0.6.2"; doc = "docs/dev/controlled-tester-package-staging-local-only-no-distribution.md"; check = "scripts/dev/check-controlled-tester-package-staging-local-only-no-distribution.ps1"; pass = "v0\.6\.2 CONTROLLED TESTER PACKAGE STAGING LOCAL-ONLY NO-DISTRIBUTION CHECK PASS" },
  @{ version = "v0.6.3"; doc = "docs/dev/controlled-tester-package-contents-manifest-no-build-no-distribution.md"; check = "scripts/dev/check-controlled-tester-package-contents-manifest-no-build-no-distribution.ps1"; pass = "v0\.6\.3 CONTROLLED TESTER PACKAGE CONTENTS MANIFEST NO-BUILD NO-DISTRIBUTION CHECK PASS" },
  @{ version = "v0.6.4"; doc = "docs/dev/controlled-tester-package-build-plan-no-build-no-distribution.md"; check = "scripts/dev/check-controlled-tester-package-build-plan-no-build-no-distribution.ps1"; pass = "v0\.6\.4 CONTROLLED TESTER PACKAGE BUILD PLAN NO-BUILD NO-DISTRIBUTION CHECK PASS" },
  @{ version = "v0.6.5"; doc = "docs/dev/controlled-tester-package-source-selection-dry-run-no-build-no-distribution.md"; check = "scripts/dev/check-controlled-tester-package-source-selection-dry-run-no-build-no-distribution.ps1"; pass = "v0\.6\.5 CONTROLLED TESTER PACKAGE SOURCE SELECTION DRY-RUN NO-BUILD NO-DISTRIBUTION CHECK PASS" },
  @{ version = "v0.6.6"; doc = "docs/dev/controlled-tester-package-source-validation-dry-run-no-build-no-distribution.md"; check = "scripts/dev/check-controlled-tester-package-source-validation-dry-run-no-build-no-distribution.ps1"; pass = "v0\.6\.6 CONTROLLED TESTER PACKAGE SOURCE VALIDATION DRY-RUN NO-BUILD NO-DISTRIBUTION CHECK PASS" },
  @{ version = "v0.6.7"; doc = "docs/dev/controlled-tester-package-source-allowlist-plan-no-build-no-distribution.md"; check = "scripts/dev/check-controlled-tester-package-source-allowlist-plan-no-build-no-distribution.ps1"; pass = "v0\.6\.7 CONTROLLED TESTER PACKAGE SOURCE ALLOWLIST PLAN NO-BUILD NO-DISTRIBUTION CHECK PASS" },
  @{ version = "v0.6.8"; doc = "docs/dev/controlled-tester-package-copy-plan-no-copy-no-build-no-distribution.md"; check = "scripts/dev/check-controlled-tester-package-copy-plan-no-copy-no-build-no-distribution.ps1"; pass = "v0\.6\.8 CONTROLLED TESTER PACKAGE COPY PLAN NO-COPY NO-BUILD NO-DISTRIBUTION CHECK PASS" },
  @{ version = "v0.6.9"; doc = "docs/dev/controlled-tester-package-copy-validation-dry-run-no-copy-no-build-no-distribution.md"; check = "scripts/dev/check-controlled-tester-package-copy-validation-dry-run-no-copy-no-build-no-distribution.ps1"; pass = "v0\.6\.9 CONTROLLED TESTER PACKAGE COPY VALIDATION DRY-RUN NO-COPY NO-BUILD NO-DISTRIBUTION CHECK PASS" },
  @{ version = "v0.6.10"; doc = "docs/dev/controlled-tester-package-staging-readiness-dry-run-no-copy-no-build-no-distribution.md"; check = "scripts/dev/check-controlled-tester-package-staging-readiness-dry-run-no-copy-no-build-no-distribution.ps1"; pass = "v0\.6\.10 CONTROLLED TESTER PACKAGE STAGING READINESS DRY-RUN NO-COPY NO-BUILD NO-DISTRIBUTION CHECK PASS" },
  @{ version = "v0.6.11"; doc = "docs/dev/controlled-tester-package-staging-layout-plan-no-create-no-copy-no-build-no-distribution.md"; check = "scripts/dev/check-controlled-tester-package-staging-layout-plan-no-create-no-copy-no-build-no-distribution.ps1"; pass = "v0\.6\.11 CONTROLLED TESTER PACKAGE STAGING LAYOUT PLAN NO-CREATE NO-COPY NO-BUILD NO-DISTRIBUTION CHECK PASS" },
  @{ version = "v0.6.12"; doc = "docs/dev/controlled-tester-package-staging-layout-validation-dry-run-no-create-no-copy-no-build-no-distribution.md"; check = "scripts/dev/check-controlled-tester-package-staging-layout-validation-dry-run-no-create-no-copy-no-build-no-distribution.ps1"; pass = "v0\.6\.12 CONTROLLED TESTER PACKAGE STAGING LAYOUT VALIDATION DRY-RUN NO-CREATE NO-COPY NO-BUILD NO-DISTRIBUTION CHECK PASS" }
)

foreach ($item in $previous) {
  Assert-True (Test-Path -LiteralPath $item.doc) "Missing previous milestone doc: $($item.doc)"
  Assert-True (Test-Path -LiteralPath $item.check) "Missing previous milestone check: $($item.check)"
  Write-Host $item.doc
  Write-Host $item.check
  $text = Get-Content -LiteralPath $item.check -Raw
  Assert-True ($text -match $item.pass) "$($item.version) PASS marker missing."
}

$v0612Text = Get-Content -LiteralPath "scripts/dev/check-controlled-tester-package-staging-layout-validation-dry-run-no-create-no-copy-no-build-no-distribution.ps1" -Raw
$v0612DocText = Get-Content -LiteralPath "docs/dev/controlled-tester-package-staging-layout-validation-dry-run-no-create-no-copy-no-build-no-distribution.md" -Raw

Assert-True ($v0612DocText -match "v0\.6\.13-controlled-tester-package-staging-manifest-plan-no-create-no-copy-no-build-no-distribution") "v0.6.12 allowed next marker missing."
Assert-True ($v0612Text -match "staging_layout_validation_approved_now.*false") "v0.6.12 must keep staging layout validation approval blocked."
Assert-True ($v0612Text -match "layout_validation_approved_now.*false") "v0.6.12 must keep layout validation approval blocked."
Assert-True ($v0612Text -match "layout_created_now.*false") "v0.6.12 must keep layout creation blocked."
Assert-True ($v0612Text -match "staging_layout_created.*false") "v0.6.12 must keep staging layout creation blocked."
Assert-True ($v0612Text -match "staging_tree_created.*false") "v0.6.12 must keep staging tree creation blocked."
Assert-True ($v0612Text -match "staging_root_created.*false") "v0.6.12 must keep staging root creation blocked."
Assert-True ($v0612Text -match "copy_allowed_now.*false") "v0.6.12 must keep copy allowed blocked."
Assert-True ($v0612Text -match "copy_executed_now.*false") "v0.6.12 must keep copy execution blocked."
Assert-True ($v0612Text -match "copies_runtime_files.*false") "v0.6.12 must keep runtime copy blocked."
Assert-True ($v0612Text -match "build_allowed.*false") "v0.6.12 must keep build blocked."
Assert-True ($v0612Text -match "distribution_allowed.*false") "v0.6.12 must keep distribution blocked."
Assert-True ($v0612Text -match "uploads_to_onedrive.*false") "v0.6.12 must keep OneDrive upload blocked."
Assert-True ($v0612Text -match "publishes_github_release.*false") "v0.6.12 must keep GitHub release blocked."

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
  Assert-True ($allowedTouched -contains $path) "Unexpected changed path in v0.6.13 milestone: $path"
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
    Assert-True (-not ($path -match $pattern)) "Forbidden path touched by v0.6.13 staging-manifest-plan milestone: $path"
  }
}

Write-Host ""
Write-Host "=== Content safety gate ==="
$docText = Get-Content -LiteralPath $docPath -Raw
$checkText = Get-Content -LiteralPath $checkPath -Raw

$requiredDocMarkers = @(
  "No package staging manifest creation",
  "No staging manifest approval",
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
  "planned_only = true",
  "manifest_created_now = false",
  "manifest_approved_now = false",
  "staging_manifest_created = false",
  "staging_layout_created = false",
  "staging_tree_created = false",
  "copy_allowed_now = false",
  "copy_executed_now = false",
  "copied_now = false",
  "approved_for_package_now = false",
  "This milestone records staging manifest intent only"
)
foreach ($marker in $requiredDocMarkers) {
  Assert-True ($docText -match [regex]::Escape($marker)) "Doc missing safety marker: $marker"
}

$requiredCheckMarkers = @(
  "staging_manifest_plan_approved_now.*false",
  "manifest_approved_now.*false",
  "manifest_created_now.*false",
  "staging_manifest_created.*false",
  "staging_layout_created.*false",
  "staging_tree_created.*false",
  "staging_root_created.*false",
  "copy_allowed_now.*false",
  "copy_executed_now.*false",
  "copied_now.*false",
  "approved_for_package_now.*false",
  "copies_runtime_files.*false",
  "build_allowed.*false",
  "package_created.*false",
  "zip_created.*false",
  "distribution_allowed.*false",
  "uploads_to_onedrive.*false",
  "publishes_github_release.*false"
)
foreach ($marker in $requiredCheckMarkers) {
  Assert-True ($checkText -match $marker) "Check missing safety marker: $marker"
}

Write-Host ""
Write-Host "=== Create local-only staging manifest plan evidence directory ==="
New-Item -ItemType Directory -Force -Path $manifestRoot | Out-Null

$repoFull = Resolve-FullPathSafe $repoRoot
$manifestFull = Resolve-FullPathSafe $manifestRoot
Assert-True (-not ($manifestFull.StartsWith($repoFull, [System.StringComparison]::OrdinalIgnoreCase))) "Staging manifest plan root must be outside repository."

$manifestSections = @("metadata", "layout_entries", "source_mappings", "validation", "safety_gates", "blocked_actions")
$plannedSections = @()
foreach ($section in $manifestSections) {
  $plannedSections += [ordered]@{
    section_name = $section
    section_name_valid = [bool](Test-ManifestSectionName $section)
    planned_only = $true
    staging_manifest_plan_approved_now = $false
    manifest_approved_now = $false
    manifest_created_now = $false
    staging_manifest_created = $false
    staging_layout_created = $false
    staging_tree_created = $false
    staging_root_created = $false
    copy_allowed_now = $false
    copy_executed_now = $false
    copied_now = $false
    approved_for_package_now = $false
  }
}

$rawEntries = @(
  @("metadata", "schema_version", "future-only"),
  @("metadata", "package_candidate_version", "future-only"),
  @("layout_entries", "app", "app/"),
  @("layout_entries", "runtime", "runtime/"),
  @("layout_entries", "scripts", "scripts/"),
  @("layout_entries", "docs", "docs/"),
  @("layout_entries", "legal", "legal/"),
  @("layout_entries", "validation", "validation/"),
  @("source_mappings", "services", "services > app/services"),
  @("source_mappings", "services_api", "services/api > app/services/api"),
  @("source_mappings", "scripts_dev", "scripts/dev > scripts/dev"),
  @("source_mappings", "docs", "docs > docs"),
  @("source_mappings", "license", "LICENSE.txt > legal/LICENSE.txt"),
  @("validation", "local_check", "check-controlled-tester-package-build-plan-no-build-no-distribution.ps1"),
  @("safety_gates", "no_copy", "copy_allowed_now false"),
  @("safety_gates", "no_build", "build_allowed false"),
  @("blocked_actions", "distribution", "distribution_allowed false")
)

$plannedEntries = @()
foreach ($entry in $rawEntries) {
  $plannedEntries += [ordered]@{
    section_name = $entry[0]
    entry_name = $entry[1]
    planned_value = $entry[2]
    section_name_valid = [bool](Test-ManifestSectionName $entry[0])
    entry_name_valid = [bool](Test-ManifestSectionName $entry[1])
    entry_value_valid = [bool](Test-ManifestEntryString $entry[2])
    planned_only = $true
    staging_manifest_plan_approved_now = $false
    manifest_approved_now = $false
    manifest_created_now = $false
    staging_manifest_created = $false
    staging_layout_created = $false
    staging_tree_created = $false
    staging_root_created = $false
    copy_allowed_now = $false
    copy_executed_now = $false
    copied_now = $false
    approved_for_package_now = $false
  }
}

$manifestPlan = [ordered]@{
  schema_version = "1"
  staging_manifest_plan_version = "v0.6.13"
  staging_manifest_plan_type = "controlled_tester_package_staging_manifest_plan_no_create_no_copy_no_build_no_distribution"
  status = "pass"
  staging_manifest_plan = [ordered]@{
    owner_controlled_staging_manifest_plan_created = $true
    manifest_plan_root = $manifestRoot
    manifest_plan_root_outside_repo = $true
    manifest_plan_json_created = $true
    readme_created = $true
    staging_manifest_plan_approved_now = $false
    manifest_approved_now = $false
    manifest_created_now = $false
    staging_manifest_created = $false
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
    next_step_policy = "STOP_OR_SEPARATE_STAGING_MANIFEST_VALIDATION_DRY_RUN_MILESTONE_ONLY"
  }
  planned_manifest_sections = $plannedSections
  planned_manifest_entries = $plannedEntries
  evidence = [ordered]@{
    previous_staging_layout_validation_version = "v0.6.12"
    previous_staging_layout_validation_check = "scripts/dev/check-controlled-tester-package-staging-layout-validation-dry-run-no-create-no-copy-no-build-no-distribution.ps1"
    previous_staging_layout_plan_version = "v0.6.11"
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
    staging_manifest_plan_only = $true
    manifest_plan_root_outside_repo = $true
    no_staging_manifest_plan_approval_now = $true
    no_manifest_approval_now = $true
    no_manifest_created_now = $true
    no_staging_manifest_created = $true
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
    creates_local_staging_manifest_plan_evidence = $true
    approves_staging_manifest_plan = $false
    approves_manifest = $false
    creates_staging_manifest = $false
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
  allowed_next_milestones = @("STOP", "v0.6.14-controlled-tester-package-staging-manifest-validation-dry-run-no-create-no-copy-no-build-no-distribution")
  blocked_next_actions = @(
    "direct_tester_activation",
    "public_ui_link",
    "public_release",
    "package_distribution",
    "onedrive_share_delivery",
    "github_release_publication",
    "paid_distribution",
    "staging_manifest_creation",
    "staging_manifest_approval",
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

$manifestJson = $manifestPlan | ConvertTo-Json -Depth 10
[System.IO.File]::WriteAllText($manifestPath, ($manifestJson + "`n"), [System.Text.UTF8Encoding]::new($false))

$readme = @"
Voila v0.6.13 controlled tester package staging manifest plan no-create no-copy no-build no-distribution

This directory is local evidence only.

It is not a tester package.
It is not a build output.
It is not a staging manifest.
It is not a staging tree.
It is not a staging layout.
It is not a release asset.
It is not a distribution folder.
It must not be uploaded to OneDrive.
It must not be published as a GitHub release.
It must not be shared with testers.

Allowed contents:
- STAGING-MANIFEST-PLAN-README.txt
- STAGING-MANIFEST-PLAN-DRY-RUN.json

Blocked:
- staging manifest creation, staging manifest approval, staging layout creation, staging tree creation, staging root creation, runtime file copy, package content copy, copy execution, package source approval, source allowlist approval, source allowlist enforcement, package build, ZIP, EXE, MSI, installer, runnable package, release archive, release asset staging, code signing, checksum publication, public UI, tester activation, submit flow, persistence, scoring, cloud/API.
"@

[System.IO.File]::WriteAllText($readmePath, ($readme.TrimEnd() + "`n"), [System.Text.UTF8Encoding]::new($false))

Write-Host "STAGING MANIFEST PLAN ROOT: $manifestRoot"
Write-Host "WROTE: $manifestPath"
Write-Host "WROTE: $readmePath"

Write-Host ""
Write-Host "=== Verify staging manifest plan evidence files ==="
$manifestFiles = @(Get-ChildItem -LiteralPath $manifestRoot -File | Select-Object -ExpandProperty Name | Sort-Object)
foreach ($name in $manifestFiles) { Write-Host $name }

$allowedManifestNames = @("STAGING-MANIFEST-PLAN-DRY-RUN.json", "STAGING-MANIFEST-PLAN-README.txt")
foreach ($name in $manifestFiles) {
  Assert-True ($allowedManifestNames -contains $name) "Unexpected file in local-only staging manifest plan evidence directory: $name"
  Assert-True (-not ($name -match "\.(zip|exe|msi)$")) "Forbidden package/release artifact in staging manifest plan evidence directory: $name"
}

Assert-True (Test-Path -LiteralPath $manifestPath) "Missing staging-manifest-plan JSON."
Assert-True (Test-Path -LiteralPath $readmePath) "Missing staging-manifest-plan README."

Write-Host ""
Write-Host "=== v0.6.13 staging manifest plan JSON ==="
$manifestJson

Write-Host ""
Write-Host "=== Repository diff whitespace check ==="
git diff --check

Write-Host ""
Write-Host "=== v0.6.13 CONTROLLED TESTER PACKAGE STAGING MANIFEST PLAN NO-CREATE NO-COPY NO-BUILD NO-DISTRIBUTION CHECK PASS ==="
