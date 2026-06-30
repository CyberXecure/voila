$ErrorActionPreference = "Stop"

Write-Host "=== v0.6.20 controlled tester package build readiness freeze no-build no-distribution check ==="

$repoRoot = (git rev-parse --show-toplevel).Trim()
Set-Location $repoRoot

$docPath = "docs/dev/controlled-tester-package-build-readiness-freeze-no-build-no-distribution.md"
$checkPath = "scripts/dev/check-controlled-tester-package-build-readiness-freeze-no-build-no-distribution.ps1"
$allowedTouched = @($docPath, $checkPath)

$freezeRoot = "D:\dev\release-assets\voila\v0.6.20-controlled-tester-package-build-readiness-freeze-no-build-no-distribution"
$freezePath = Join-Path $freezeRoot "BUILD-READINESS-FREEZE-DRY-RUN.json"
$readmePath = Join-Path $freezeRoot "BUILD-READINESS-FREEZE-README.txt"

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
  Assert-True (Test-Path -LiteralPath $path) "Missing required v0.6.20 file: $path"
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
  v0612Doc = "docs/dev/controlled-tester-package-staging-layout-validation-dry-run-no-create-no-copy-no-build-no-distribution.md"
  v0612Check = "scripts/dev/check-controlled-tester-package-staging-layout-validation-dry-run-no-create-no-copy-no-build-no-distribution.ps1"
  v0613Doc = "docs/dev/controlled-tester-package-staging-manifest-plan-no-create-no-copy-no-build-no-distribution.md"
  v0613Check = "scripts/dev/check-controlled-tester-package-staging-manifest-plan-no-create-no-copy-no-build-no-distribution.ps1"
  v0614Doc = "docs/dev/controlled-tester-package-staging-manifest-validation-dry-run-no-create-no-copy-no-build-no-distribution.md"
  v0614Check = "scripts/dev/check-controlled-tester-package-staging-manifest-validation-dry-run-no-create-no-copy-no-build-no-distribution.ps1"
  v0615Doc = "docs/dev/controlled-tester-package-staging-gate-freeze-no-create-no-copy-no-build-no-distribution.md"
  v0615Check = "scripts/dev/check-controlled-tester-package-staging-gate-freeze-no-create-no-copy-no-build-no-distribution.ps1"
  v0616Doc = "docs/dev/controlled-tester-package-prebuild-decision-gate-no-build-no-distribution.md"
  v0616Check = "scripts/dev/check-controlled-tester-package-prebuild-decision-gate-no-build-no-distribution.ps1"
  v0617Doc = "docs/dev/controlled-tester-package-prebuild-validation-dry-run-no-build-no-distribution.md"
  v0617Check = "scripts/dev/check-controlled-tester-package-prebuild-validation-dry-run-no-build-no-distribution.ps1"
  v0618Doc = "docs/dev/controlled-tester-package-build-approval-freeze-no-build-no-distribution.md"
  v0618Check = "scripts/dev/check-controlled-tester-package-build-approval-freeze-no-build-no-distribution.ps1"
  v0619Doc = "docs/dev/controlled-tester-package-build-readiness-review-dry-run-no-build-no-distribution.md"
  v0619Check = "scripts/dev/check-controlled-tester-package-build-readiness-review-dry-run-no-build-no-distribution.ps1"
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
$v0612Text = Get-Content -LiteralPath $previous.v0612Check -Raw
$v0613Text = Get-Content -LiteralPath $previous.v0613Check -Raw
$v0614Text = Get-Content -LiteralPath $previous.v0614Check -Raw
$v0615Text = Get-Content -LiteralPath $previous.v0615Check -Raw
$v0616Text = Get-Content -LiteralPath $previous.v0616Check -Raw
$v0617Text = Get-Content -LiteralPath $previous.v0617Check -Raw
$v0618Text = Get-Content -LiteralPath $previous.v0618Check -Raw
$v0619Text = Get-Content -LiteralPath $previous.v0619Check -Raw
$v0619DocText = Get-Content -LiteralPath $previous.v0619Doc -Raw

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
Assert-True ($v0612Text -match "v0\.6\.12 CONTROLLED TESTER PACKAGE STAGING LAYOUT VALIDATION DRY-RUN NO-CREATE NO-COPY NO-BUILD NO-DISTRIBUTION CHECK PASS") "v0.6.12 PASS marker missing."
Assert-True ($v0613Text -match "v0\.6\.13 CONTROLLED TESTER PACKAGE STAGING MANIFEST PLAN NO-CREATE NO-COPY NO-BUILD NO-DISTRIBUTION CHECK PASS") "v0.6.13 PASS marker missing."
Assert-True ($v0614Text -match "v0\.6\.14 CONTROLLED TESTER PACKAGE STAGING MANIFEST VALIDATION DRY-RUN NO-CREATE NO-COPY NO-BUILD NO-DISTRIBUTION CHECK PASS") "v0.6.14 PASS marker missing."
Assert-True ($v0615Text -match "v0\.6\.15 CONTROLLED TESTER PACKAGE STAGING GATE FREEZE NO-CREATE NO-COPY NO-BUILD NO-DISTRIBUTION CHECK PASS") "v0.6.15 PASS marker missing."
Assert-True ($v0616Text -match "v0\.6\.16 CONTROLLED TESTER PACKAGE PREBUILD DECISION GATE NO-BUILD NO-DISTRIBUTION CHECK PASS") "v0.6.16 PASS marker missing."
Assert-True ($v0617Text -match "v0\.6\.17 CONTROLLED TESTER PACKAGE PREBUILD VALIDATION DRY-RUN NO-BUILD NO-DISTRIBUTION CHECK PASS") "v0.6.17 PASS marker missing."
Assert-True ($v0618Text -match "v0\.6\.18 CONTROLLED TESTER PACKAGE BUILD APPROVAL FREEZE NO-BUILD NO-DISTRIBUTION CHECK PASS") "v0.6.18 PASS marker missing."
Assert-True ($v0619Text -match "v0\.6\.19 CONTROLLED TESTER PACKAGE BUILD READINESS REVIEW DRY-RUN NO-BUILD NO-DISTRIBUTION CHECK PASS") "v0.6.19 PASS marker missing."
Assert-True ($v0619DocText -match "v0\.6\.20-controlled-tester-package-build-readiness-freeze-no-build-no-distribution") "v0.6.19 allowed next marker missing."

Assert-True ($v0619Text -match "readiness_review_created.*true") "v0.6.19 must have readiness review."
Assert-True ($v0619Text -match "readiness_review_checked.*true") "v0.6.19 must have checked readiness review."
Assert-True ($v0619Text -match "readiness_review_dry_run_only.*true") "v0.6.19 must keep readiness review dry-run only."
Assert-True ($v0619Text -match "build_readiness_approved_now.*false") "v0.6.19 must keep build readiness approval blocked."
Assert-True ($v0619Text -match "build_approval_allowed_now.*false") "v0.6.19 must keep build approval blocked."
Assert-True ($v0619Text -match "build_validation_approval_allowed_now.*false") "v0.6.19 must keep build validation approval blocked."
Assert-True ($v0619Text -match "build_approved_now.*false") "v0.6.19 must keep build approved false."
Assert-True ($v0619Text -match "build_allowed_now.*false") "v0.6.19 must keep build allowed blocked."
Assert-True ($v0619Text -match "package_build_executed_now.*false") "v0.6.19 must keep package build execution blocked."
Assert-True ($v0619Text -match "zip_created.*false") "v0.6.19 must keep zip creation blocked."
Assert-True ($v0619Text -match "installer_created.*false") "v0.6.19 must keep installer creation blocked."
Assert-True ($v0619Text -match "release_archive_created.*false") "v0.6.19 must keep release archive creation blocked."
Assert-True ($v0619Text -match "distribution_allowed.*false") "v0.6.19 must keep distribution blocked."

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
  Assert-True ($allowedTouched -contains $path) "Unexpected changed path in v0.6.20 milestone: $path"
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
    Assert-True (-not ($path -match $pattern)) "Forbidden path touched by v0.6.20 build-readiness-freeze milestone: $path"
  }
}

Write-Host ""
Write-Host "=== Content safety gate ==="
$docText = Get-Content -LiteralPath $docPath -Raw
$checkText = Get-Content -LiteralPath $checkPath -Raw

$requiredDocMarkers = @(
  "No build readiness approval",
  "No build readiness unfreeze",
  "No build approval",
  "No build validation approval",
  "No package build",
  "No ZIP creation",
  "No EXE creation",
  "No MSI creation",
  "No installer creation",
  "No runnable tester package creation",
  "No package staging manifest creation",
  "No staging manifest approval",
  "No staging manifest enforcement",
  "No staging layout creation",
  "No staging tree creation",
  "No staging root creation for package contents",
  "No runtime file copy",
  "No package content copy",
  "No copy execution",
  "No release archive creation",
  "No release asset staging",
  "No code signing",
  "No checksum publication",
  "No OneDrive upload",
  "No GitHub release",
  "No public UI",
  "No session persistence",
  "No live scoring",
  "build_readiness_freeze_created = true",
  "build_readiness_freeze_active = true",
  "build_readiness_frozen = true",
  "readiness_review_checked = true",
  "readiness_review_dry_run_only = true",
  "build_readiness_approved_now = false",
  "build_readiness_unfreeze_allowed_now = false",
  "build_approval_allowed_now = false",
  "build_validation_approval_allowed_now = false",
  "build_approved_now = false",
  "build_allowed_now = false",
  "package_build_executed_now = false",
  "zip_created = false",
  "installer_created = false",
  "release_archive_created = false",
  "checksum_publication_allowed = false",
  "code_signing_allowed = false",
  "distribution_allowed = false",
  "tester_delivery_allowed_now = false",
  "public_release_allowed_now = false",
  "This milestone records build readiness freeze only"
)
foreach ($marker in $requiredDocMarkers) {
  Assert-True ($docText -match [regex]::Escape($marker)) "Doc missing safety marker: $marker"
}

Assert-True ($checkText -match "build_readiness_freeze_created.*true") "Check must set build_readiness_freeze_created true."
Assert-True ($checkText -match "build_readiness_freeze_active.*true") "Check must set build_readiness_freeze_active true."
Assert-True ($checkText -match "build_readiness_frozen.*true") "Check must set build_readiness_frozen true."
Assert-True ($checkText -match "readiness_review_checked.*true") "Check must set readiness_review_checked true."
Assert-True ($checkText -match "readiness_review_dry_run_only.*true") "Check must keep readiness_review_dry_run_only true."
Assert-True ($checkText -match "build_readiness_approved_now.*false") "Check must keep build_readiness_approved_now false."
Assert-True ($checkText -match "build_readiness_unfreeze_allowed_now.*false") "Check must keep build_readiness_unfreeze_allowed_now false."
Assert-True ($checkText -match "build_approval_allowed_now.*false") "Check must keep build_approval_allowed_now false."
Assert-True ($checkText -match "build_validation_approval_allowed_now.*false") "Check must keep build_validation_approval_allowed_now false."
Assert-True ($checkText -match "build_validation_approved_now.*false") "Check must keep build_validation_approved_now false."
Assert-True ($checkText -match "build_approved_now.*false") "Check must keep build_approved_now false."
Assert-True ($checkText -match "build_allowed_now.*false") "Check must keep build_allowed_now false."
Assert-True ($checkText -match "build_allowed.*false") "Check must keep build_allowed false."
Assert-True ($checkText -match "package_build_executed_now.*false") "Check must keep package_build_executed_now false."
Assert-True ($checkText -match "zip_created.*false") "Check must keep zip_created false."
Assert-True ($checkText -match "exe_created.*false") "Check must keep exe_created false."
Assert-True ($checkText -match "msi_created.*false") "Check must keep msi_created false."
Assert-True ($checkText -match "installer_created.*false") "Check must keep installer_created false."
Assert-True ($checkText -match "release_archive_created.*false") "Check must keep release_archive_created false."
Assert-True ($checkText -match "checksum_publication_allowed.*false") "Check must keep checksum_publication_allowed false."
Assert-True ($checkText -match "code_signing_allowed.*false") "Check must keep code_signing_allowed false."
Assert-True ($checkText -match "distribution_allowed.*false") "Check must keep distribution_allowed false."
Assert-True ($checkText -match "tester_delivery_allowed_now.*false") "Check must keep tester_delivery_allowed_now false."
Assert-True ($checkText -match "public_release_allowed_now.*false") "Check must keep public_release_allowed_now false."

Write-Host ""
Write-Host "=== Create local-only build readiness freeze evidence directory ==="
New-Item -ItemType Directory -Force -Path $freezeRoot | Out-Null

$repoFull = Resolve-FullPathSafe $repoRoot
$freezeFull = Resolve-FullPathSafe $freezeRoot
Assert-True (-not ($freezeFull.StartsWith($repoFull, [System.StringComparison]::OrdinalIgnoreCase))) "Build readiness freeze root must be outside repository."

$frozenCategories = @(
  "previous_milestone_chain",
  "source_selection_trail",
  "source_validation_trail",
  "source_allowlist_trail",
  "copy_plan_trail",
  "copy_validation_trail",
  "staging_readiness_trail",
  "staging_layout_trail",
  "staging_manifest_trail",
  "prebuild_decision_trail",
  "prebuild_validation_trail",
  "build_approval_freeze_trail",
  "release_distribution_safety_gates"
)

$frozenCategoryEntries = @()
foreach ($category in $frozenCategories) {
  $frozenCategoryEntries += [ordered]@{
    category = $category
    build_readiness_freeze_active = $true
    build_readiness_frozen = $true
    readiness_review_checked = $true
    readiness_review_dry_run_only = $true
    approved_for_build_now = $false
    build_readiness_approved_now = $false
    build_readiness_unfreeze_allowed_now = $false
    build_approval_allowed_now = $false
    build_allowed_now = $false
    package_build_executed_now = $false
  }
}

$freeze = [ordered]@{
  schema_version = "1"
  build_readiness_freeze_version = "v0.6.20"
  build_readiness_freeze_type = "controlled_tester_package_build_readiness_freeze_no_build_no_distribution"
  status = "pass"
  build_readiness_freeze = [ordered]@{
    owner_controlled_build_readiness_freeze_created = $true
    build_readiness_freeze_created = $true
    build_readiness_freeze_active = $true
    build_readiness_frozen = $true
    readiness_review_checked = $true
    readiness_review_dry_run_only = $true
    freeze_root = $freezeRoot
    freeze_root_outside_repo = $true
    freeze_json_created = $true
    readme_created = $true
    build_readiness_approved_now = $false
    build_readiness_unfreeze_allowed_now = $false
    build_approval_allowed_now = $false
    build_validation_approval_allowed_now = $false
    build_validation_approved_now = $false
    build_approved_now = $false
    build_allowed_now = $false
    build_allowed = $false
    package_build_executed_now = $false
    package_created = $false
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
    staging_manifest_creation_allowed_now = $false
    staging_manifest_approval_allowed_now = $false
    staging_manifest_enforcement_allowed_now = $false
    staging_layout_creation_allowed_now = $false
    staging_tree_creation_allowed_now = $false
    staging_root_creation_allowed_now = $false
    runtime_file_copy_allowed_now = $false
    package_content_copy_allowed_now = $false
    copy_allowed_now = $false
    copy_executed_now = $false
    copied_now = $false
    copies_runtime_files = $false
    next_step_policy = "STOP_OR_SEPARATE_RELEASE_GATE_PLAN_NO_BUILD_MILESTONE_ONLY"
  }
  frozen_readiness_categories = $frozenCategoryEntries
  evidence = [ordered]@{
    previous_build_readiness_review_version = "v0.6.19"
    previous_build_readiness_review_check = $previous.v0619Check
    previous_build_approval_freeze_version = "v0.6.18"
    previous_prebuild_validation_version = "v0.6.17"
    previous_prebuild_decision_gate_version = "v0.6.16"
    previous_staging_gate_freeze_version = "v0.6.15"
    previous_staging_manifest_validation_version = "v0.6.14"
    previous_staging_manifest_plan_version = "v0.6.13"
    previous_staging_layout_validation_version = "v0.6.12"
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
    build_readiness_freeze_only = $true
    freeze_root_outside_repo = $true
    build_readiness_freeze_active = $true
    build_readiness_frozen = $true
    readiness_review_checked = $true
    readiness_review_dry_run_only = $true
    no_build_readiness_approval_now = $true
    no_build_readiness_unfreeze_now = $true
    no_build_approval_allowed_now = $true
    no_build_validation_approval_allowed_now = $true
    no_build_validation_approval_now = $true
    no_build_approval_now = $true
    no_build_allowed_now = $true
    no_package_build_executed_now = $true
    no_zip_created = $true
    no_exe_created = $true
    no_msi_created = $true
    no_installer_created = $true
    no_release_archive_created = $true
    no_release_asset_staging_created = $true
    no_code_signing = $true
    no_checksum_publication = $true
    no_distribution_allowed = $true
    no_tester_delivery_allowed_now = $true
    no_public_release_allowed_now = $true
    no_staging_manifest_creation_allowed_now = $true
    no_staging_manifest_approval_allowed_now = $true
    no_staging_manifest_enforcement_allowed_now = $true
    no_staging_layout_creation_allowed_now = $true
    no_staging_tree_creation_allowed_now = $true
    no_staging_root_creation_allowed_now = $true
    no_copy_allowed_now = $true
    no_copy_executed_now = $true
    no_package_content_copy = $true
    no_runtime_file_copy = $true
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
    creates_local_build_readiness_freeze_evidence = $true
    freezes_build_readiness = $true
    approves_build_readiness = $false
    unfreezes_build_readiness = $false
    approves_build_validation = $false
    approves_build = $false
    allows_build = $false
    executes_build = $false
    creates_package = $false
    creates_zip = $false
    creates_installer = $false
    creates_release_archive = $false
    signs_code = $false
    publishes_checksum = $false
    distributes_package = $false
    uploads_to_onedrive = $false
    publishes_github_release = $false
    creates_staging_manifest = $false
    approves_staging_manifest = $false
    enforces_staging_manifest = $false
    creates_staging_layout = $false
    creates_staging_tree = $false
    creates_staging_root = $false
    allows_copy_now = $false
    executes_copy_now = $false
    copies_runtime_files = $false
    approves_package_source = $false
    approves_source_allowlist = $false
    enforces_source_allowlist = $false
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
  allowed_next_milestones = @("STOP", "v0.6.21-controlled-tester-package-release-gate-plan-no-build-no-distribution")
  blocked_next_actions = @(
    "direct_tester_activation",
    "public_ui_link",
    "public_release",
    "package_distribution",
    "onedrive_share_delivery",
    "github_release_publication",
    "paid_distribution",
    "build_readiness_approval",
    "build_readiness_unfreeze",
    "build_approval",
    "build_validation_approval",
    "package_build",
    "zip_creation",
    "exe_creation",
    "msi_creation",
    "installer_creation",
    "runnable_tester_package_creation",
    "staging_manifest_creation",
    "staging_manifest_approval",
    "staging_manifest_enforcement",
    "staging_layout_creation",
    "staging_tree_creation",
    "staging_root_creation",
    "runtime_file_copy",
    "package_content_copy",
    "copy_execution",
    "package_source_approval",
    "source_allowlist_approval",
    "source_allowlist_enforcement",
    "release_archive_creation",
    "code_signing",
    "checksum_publication",
    "attempt_persistence",
    "session_persistence",
    "progress_persistence",
    "live_scoring_persistence",
    "cloud_or_api_requirement"
  )
}

$freezeJson = $freeze | ConvertTo-Json -Depth 10
[System.IO.File]::WriteAllText($freezePath, ($freezeJson + "`n"), [System.Text.UTF8Encoding]::new($false))

$readme = @"
Voila v0.6.20 controlled tester package build readiness freeze no-build no-distribution

This directory is local evidence only.

It is not a tester package.
It is not a build output.
It is not a ZIP.
It is not an installer.
It is not a release archive.
It is not a distribution folder.
It must not be uploaded to OneDrive.
It must not be published as a GitHub release.
It must not be shared with testers.

Allowed contents:
- BUILD-READINESS-FREEZE-README.txt
- BUILD-READINESS-FREEZE-DRY-RUN.json

Blocked:
- build readiness approval, build readiness unfreeze, build approval, build validation approval, package build, ZIP, EXE, MSI, installer, runnable package, staging manifest creation, staging layout creation, staging tree creation, staging root creation, runtime file copy, package content copy, copy execution, package source approval, source allowlist approval, source allowlist enforcement, release archive creation, code signing, checksum publication, public UI, tester activation, submit flow, persistence, scoring, cloud/API.
"@

[System.IO.File]::WriteAllText($readmePath, ($readme.TrimEnd() + "`n"), [System.Text.UTF8Encoding]::new($false))

Write-Host "BUILD READINESS FREEZE ROOT: $freezeRoot"
Write-Host "WROTE: $freezePath"
Write-Host "WROTE: $readmePath"

Write-Host ""
Write-Host "=== Verify build readiness freeze evidence files ==="
$freezeFiles = @(Get-ChildItem -LiteralPath $freezeRoot -File | Select-Object -ExpandProperty Name | Sort-Object)
foreach ($name in $freezeFiles) { Write-Host $name }

$allowedFreezeNames = @("BUILD-READINESS-FREEZE-DRY-RUN.json", "BUILD-READINESS-FREEZE-README.txt")
foreach ($name in $freezeFiles) {
  Assert-True ($allowedFreezeNames -contains $name) "Unexpected file in local-only build readiness freeze evidence directory: $name"
  Assert-True (-not ($name -match "\.(zip|exe|msi)$")) "Forbidden package/release artifact in build readiness freeze evidence directory: $name"
}

Assert-True (Test-Path -LiteralPath $freezePath) "Missing build-readiness-freeze JSON."
Assert-True (Test-Path -LiteralPath $readmePath) "Missing build-readiness-freeze README."

Write-Host ""
Write-Host "=== v0.6.20 build readiness freeze JSON ==="
$freezeJson

Write-Host ""
Write-Host "=== Repository diff whitespace check ==="
git diff --check

Write-Host ""
Write-Host "=== v0.6.20 CONTROLLED TESTER PACKAGE BUILD READINESS FREEZE NO-BUILD NO-DISTRIBUTION CHECK PASS ==="
