$ErrorActionPreference = "Stop"

Write-Host "=== v0.6.26 controlled tester package distribution readiness plan no-build no-distribution check ==="

$repoRoot = (git rev-parse --show-toplevel).Trim()
Set-Location $repoRoot

$docPath = "docs/dev/controlled-tester-package-distribution-readiness-plan-no-build-no-distribution.md"
$checkPath = "scripts/dev/check-controlled-tester-package-distribution-readiness-plan-no-build-no-distribution.ps1"
$allowedTouched = @($docPath, $checkPath)

$planRoot = "D:\dev\release-assets\voila\v0.6.26-controlled-tester-package-distribution-readiness-plan-no-build-no-distribution"
$planPath = Join-Path $planRoot "DISTRIBUTION-READINESS-PLAN-DRY-RUN.json"
$readmePath = Join-Path $planRoot "DISTRIBUTION-READINESS-PLAN-README.txt"

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
  Assert-True (Test-Path -LiteralPath $path) "Missing required v0.6.26 file: $path"
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
  v0620Doc = "docs/dev/controlled-tester-package-build-readiness-freeze-no-build-no-distribution.md"
  v0620Check = "scripts/dev/check-controlled-tester-package-build-readiness-freeze-no-build-no-distribution.ps1"
  v0621Doc = "docs/dev/controlled-tester-package-release-gate-plan-no-build-no-distribution.md"
  v0621Check = "scripts/dev/check-controlled-tester-package-release-gate-plan-no-build-no-distribution.ps1"
  v0622Doc = "docs/dev/controlled-tester-package-release-gate-validation-dry-run-no-build-no-distribution.md"
  v0622Check = "scripts/dev/check-controlled-tester-package-release-gate-validation-dry-run-no-build-no-distribution.ps1"
  v0623Doc = "docs/dev/controlled-tester-package-release-approval-freeze-no-build-no-distribution.md"
  v0623Check = "scripts/dev/check-controlled-tester-package-release-approval-freeze-no-build-no-distribution.ps1"
  v0624Doc = "docs/dev/controlled-tester-package-release-readiness-review-dry-run-no-build-no-distribution.md"
  v0624Check = "scripts/dev/check-controlled-tester-package-release-readiness-review-dry-run-no-build-no-distribution.ps1"
  v0625Doc = "docs/dev/controlled-tester-package-release-readiness-freeze-no-build-no-distribution.md"
  v0625Check = "scripts/dev/check-controlled-tester-package-release-readiness-freeze-no-build-no-distribution.ps1"
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
$v0620Text = Get-Content -LiteralPath $previous.v0620Check -Raw
$v0621Text = Get-Content -LiteralPath $previous.v0621Check -Raw
$v0622Text = Get-Content -LiteralPath $previous.v0622Check -Raw
$v0623Text = Get-Content -LiteralPath $previous.v0623Check -Raw
$v0624Text = Get-Content -LiteralPath $previous.v0624Check -Raw
$v0625Text = Get-Content -LiteralPath $previous.v0625Check -Raw
$v0625DocText = Get-Content -LiteralPath $previous.v0625Doc -Raw

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
Assert-True ($v0620Text -match "v0\.6\.20 CONTROLLED TESTER PACKAGE BUILD READINESS FREEZE NO-BUILD NO-DISTRIBUTION CHECK PASS") "v0.6.20 PASS marker missing."
Assert-True ($v0621Text -match "v0\.6\.21 CONTROLLED TESTER PACKAGE RELEASE GATE PLAN NO-BUILD NO-DISTRIBUTION CHECK PASS") "v0.6.21 PASS marker missing."
Assert-True ($v0622Text -match "v0\.6\.22 CONTROLLED TESTER PACKAGE RELEASE GATE VALIDATION DRY-RUN NO-BUILD NO-DISTRIBUTION CHECK PASS") "v0.6.22 PASS marker missing."
Assert-True ($v0623Text -match "v0\.6\.23 CONTROLLED TESTER PACKAGE RELEASE APPROVAL FREEZE NO-BUILD NO-DISTRIBUTION CHECK PASS") "v0.6.23 PASS marker missing."
Assert-True ($v0624Text -match "v0\.6\.24 CONTROLLED TESTER PACKAGE RELEASE READINESS REVIEW DRY-RUN NO-BUILD NO-DISTRIBUTION CHECK PASS") "v0.6.24 PASS marker missing."
Assert-True ($v0625Text -match "v0\.6\.25 CONTROLLED TESTER PACKAGE RELEASE READINESS FREEZE NO-BUILD NO-DISTRIBUTION CHECK PASS") "v0.6.25 PASS marker missing."
Assert-True ($v0625DocText -match "v0\.6\.26-controlled-tester-package-distribution-readiness-plan-no-build-no-distribution") "v0.6.25 allowed next marker missing."

Assert-True ($v0625Text -match "release_readiness_freeze_active.*true") "v0.6.25 must keep release readiness freeze active."
Assert-True ($v0625Text -match "release_readiness_frozen.*true") "v0.6.25 must keep release readiness frozen."
Assert-True ($v0625Text -match "release_readiness_review_checked.*true") "v0.6.25 must keep release readiness review checked."
Assert-True ($v0625Text -match "release_readiness_review_dry_run_only.*true") "v0.6.25 must keep release readiness review dry-run only."
Assert-True ($v0625Text -match "release_readiness_approved_now.*false") "v0.6.25 must keep release readiness approval blocked."
Assert-True ($v0625Text -match "release_readiness_unfreeze_allowed_now.*false") "v0.6.25 must keep release readiness unfreeze blocked."
Assert-True ($v0625Text -match "release_approval_allowed_now.*false") "v0.6.25 must keep release approval blocked."
Assert-True ($v0625Text -match "public_release_allowed_now.*false") "v0.6.25 must keep public release blocked."
Assert-True ($v0625Text -match "tester_delivery_allowed_now.*false") "v0.6.25 must keep tester delivery blocked."
Assert-True ($v0625Text -match "distribution_allowed.*false") "v0.6.25 must keep distribution blocked."
Assert-True ($v0625Text -match "onedrive_upload_allowed_now.*false") "v0.6.25 must keep OneDrive upload blocked."
Assert-True ($v0625Text -match "github_release_allowed_now.*false") "v0.6.25 must keep GitHub release blocked."
Assert-True ($v0625Text -match "public_website_upload_allowed_now.*false") "v0.6.25 must keep public website upload blocked."
Assert-True ($v0625Text -match "package_build_executed_now.*false") "v0.6.25 must keep package build blocked."
Assert-True ($v0625Text -match "zip_created.*false") "v0.6.25 must keep zip creation blocked."
Assert-True ($v0625Text -match "release_archive_created.*false") "v0.6.25 must keep release archive blocked."

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
  Assert-True ($allowedTouched -contains $path) "Unexpected changed path in v0.6.26 milestone: $path"
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
    Assert-True (-not ($path -match $pattern)) "Forbidden path touched by v0.6.26 distribution-readiness-plan milestone: $path"
  }
}

Write-Host ""
Write-Host "=== Content safety gate ==="
$docText = Get-Content -LiteralPath $docPath -Raw
$checkText = Get-Content -LiteralPath $checkPath -Raw

$requiredDocMarkers = @(
  "No distribution readiness approval",
  "No distribution readiness validation approval",
  "No distribution approval",
  "No package distribution",
  "No controlled tester delivery",
  "No OneDrive share delivery",
  "No OneDrive upload",
  "No GitHub release publication",
  "No GitHub release approval",
  "No public website upload",
  "No public website upload approval",
  "No public release",
  "No public release approval",
  "No paid distribution",
  "No release readiness approval",
  "No release readiness unfreeze",
  "No release approval",
  "No release approval unfreeze",
  "No build approval",
  "No package build",
  "No ZIP creation",
  "No installer creation",
  "No release archive creation",
  "No code signing",
  "No checksum publication",
  "No public UI",
  "No session persistence",
  "No live scoring",
  "distribution_readiness_plan_created = true",
  "distribution_readiness_plan_dry_run_only = true",
  "distribution_readiness_approved_now = false",
  "distribution_readiness_validation_approved_now = false",
  "distribution_approval_allowed_now = false",
  "distribution_allowed = false",
  "package_distribution_allowed_now = false",
  "tester_delivery_allowed_now = false",
  "onedrive_share_delivery_allowed_now = false",
  "onedrive_upload_allowed_now = false",
  "github_release_allowed_now = false",
  "public_website_upload_allowed_now = false",
  "public_release_allowed_now = false",
  "release_readiness_unfreeze_allowed_now = false",
  "release_approval_unfreeze_allowed_now = false",
  "release_approval_allowed_now = false",
  "build_allowed_now = false",
  "package_build_executed_now = false",
  "This milestone records a distribution readiness plan only"
)
foreach ($marker in $requiredDocMarkers) {
  Assert-True ($docText -match [regex]::Escape($marker)) "Doc missing safety marker: $marker"
}

Assert-True ($checkText -match "distribution_readiness_plan_created.*true") "Check must set distribution_readiness_plan_created true."
Assert-True ($checkText -match "distribution_readiness_plan_dry_run_only.*true") "Check must set distribution_readiness_plan_dry_run_only true."
Assert-True ($checkText -match "distribution_readiness_approved_now.*false") "Check must keep distribution_readiness_approved_now false."
Assert-True ($checkText -match "distribution_readiness_validation_approved_now.*false") "Check must keep distribution_readiness_validation_approved_now false."
Assert-True ($checkText -match "distribution_approval_allowed_now.*false") "Check must keep distribution_approval_allowed_now false."
Assert-True ($checkText -match "distribution_allowed.*false") "Check must keep distribution_allowed false."
Assert-True ($checkText -match "package_distribution_allowed_now.*false") "Check must keep package_distribution_allowed_now false."
Assert-True ($checkText -match "tester_delivery_allowed_now.*false") "Check must keep tester_delivery_allowed_now false."
Assert-True ($checkText -match "onedrive_share_delivery_allowed_now.*false") "Check must keep onedrive_share_delivery_allowed_now false."
Assert-True ($checkText -match "onedrive_upload_allowed_now.*false") "Check must keep onedrive_upload_allowed_now false."
Assert-True ($checkText -match "github_release_allowed_now.*false") "Check must keep github_release_allowed_now false."
Assert-True ($checkText -match "public_website_upload_allowed_now.*false") "Check must keep public_website_upload_allowed_now false."
Assert-True ($checkText -match "public_release_allowed_now.*false") "Check must keep public_release_allowed_now false."
Assert-True ($checkText -match "release_readiness_unfreeze_allowed_now.*false") "Check must keep release_readiness_unfreeze_allowed_now false."
Assert-True ($checkText -match "release_approval_unfreeze_allowed_now.*false") "Check must keep release_approval_unfreeze_allowed_now false."
Assert-True ($checkText -match "release_approval_allowed_now.*false") "Check must keep release_approval_allowed_now false."
Assert-True ($checkText -match "release_gate_approved_now.*false") "Check must keep release_gate_approved_now false."
Assert-True ($checkText -match "release_gate_enforced_now.*false") "Check must keep release_gate_enforced_now false."
Assert-True ($checkText -match "build_readiness_unfreeze_allowed_now.*false") "Check must keep build_readiness_unfreeze_allowed_now false."
Assert-True ($checkText -match "build_approval_allowed_now.*false") "Check must keep build_approval_allowed_now false."
Assert-True ($checkText -match "build_validation_approval_allowed_now.*false") "Check must keep build_validation_approval_allowed_now false."
Assert-True ($checkText -match "build_approved_now.*false") "Check must keep build_approved_now false."
Assert-True ($checkText -match "build_allowed_now.*false") "Check must keep build_allowed_now false."
Assert-True ($checkText -match "package_build_executed_now.*false") "Check must keep package_build_executed_now false."
Assert-True ($checkText -match "zip_created.*false") "Check must keep zip_created false."
Assert-True ($checkText -match "installer_created.*false") "Check must keep installer_created false."
Assert-True ($checkText -match "release_archive_created.*false") "Check must keep release_archive_created false."
Assert-True ($checkText -match "checksum_publication_allowed.*false") "Check must keep checksum_publication_allowed false."
Assert-True ($checkText -match "code_signing_allowed.*false") "Check must keep code_signing_allowed false."

Write-Host ""
Write-Host "=== Create local-only distribution readiness plan evidence directory ==="
New-Item -ItemType Directory -Force -Path $planRoot | Out-Null

$repoFull = Resolve-FullPathSafe $repoRoot
$planFull = Resolve-FullPathSafe $planRoot
Assert-True (-not ($planFull.StartsWith($repoFull, [System.StringComparison]::OrdinalIgnoreCase))) "Distribution readiness plan root must be outside repository."

$plannedCategories = @(
  "controlled_tester_recipient_list_readiness",
  "controlled_tester_consent_and_instructions_readiness",
  "onedrive_folder_readiness",
  "onedrive_permission_model_readiness",
  "onedrive_revocation_model_readiness",
  "github_release_draft_readiness",
  "public_website_no_download_readiness",
  "checksum_communication_readiness",
  "package_identity_and_version_label_readiness",
  "support_and_feedback_channel_readiness",
  "rollback_and_takedown_readiness",
  "owner_final_distribution_go_no_go_readiness"
)

$plannedEntries = @()
foreach ($category in $plannedCategories) {
  $plannedEntries += [ordered]@{
    category = $category
    distribution_readiness_plan_created = $true
    distribution_readiness_plan_dry_run_only = $true
    planned_now = $true
    distribution_readiness_approved_now = $false
    distribution_readiness_validation_approved_now = $false
    distribution_approval_allowed_now = $false
    package_distribution_allowed_now = $false
    tester_delivery_allowed_now = $false
    public_release_allowed_now = $false
    distribution_allowed = $false
    build_allowed_now = $false
    package_build_executed_now = $false
  }
}

$plan = [ordered]@{
  schema_version = "1"
  distribution_readiness_plan_version = "v0.6.26"
  distribution_readiness_plan_type = "controlled_tester_package_distribution_readiness_plan_no_build_no_distribution"
  status = "pass"
  distribution_readiness_plan = [ordered]@{
    owner_controlled_distribution_readiness_plan_created = $true
    distribution_readiness_plan_created = $true
    distribution_readiness_plan_dry_run_only = $true
    plan_root = $planRoot
    plan_root_outside_repo = $true
    plan_json_created = $true
    readme_created = $true
    distribution_readiness_approved_now = $false
    distribution_readiness_validation_approved_now = $false
    distribution_approval_allowed_now = $false
    distribution_allowed = $false
    package_distribution_allowed_now = $false
    tester_delivery_allowed_now = $false
    controlled_tester_delivery_allowed_now = $false
    onedrive_share_delivery_allowed_now = $false
    onedrive_upload_allowed_now = $false
    github_release_allowed_now = $false
    public_website_upload_allowed_now = $false
    public_release_allowed_now = $false
    paid_distribution_allowed_now = $false
    release_readiness_unfreeze_allowed_now = $false
    release_readiness_approved_now = $false
    release_approval_unfreeze_allowed_now = $false
    release_approval_allowed_now = $false
    release_gate_validation_approved_now = $false
    release_gate_approved_now = $false
    release_gate_enforced_now = $false
    build_readiness_unfreeze_allowed_now = $false
    build_readiness_approved_now = $false
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
    next_step_policy = "STOP_OR_SEPARATE_DISTRIBUTION_READINESS_VALIDATION_DRY_RUN_NO_BUILD_MILESTONE_ONLY"
  }
  planned_distribution_readiness_categories = $plannedEntries
  evidence = [ordered]@{
    previous_release_readiness_freeze_version = "v0.6.25"
    previous_release_readiness_freeze_check = $previous.v0625Check
    previous_release_readiness_review_version = "v0.6.24"
    previous_release_approval_freeze_version = "v0.6.23"
    previous_release_gate_validation_version = "v0.6.22"
    previous_release_gate_plan_version = "v0.6.21"
    previous_build_readiness_freeze_version = "v0.6.20"
    previous_build_readiness_review_version = "v0.6.19"
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
    distribution_readiness_plan_only = $true
    plan_root_outside_repo = $true
    distribution_readiness_plan_created = $true
    distribution_readiness_plan_dry_run_only = $true
    no_distribution_readiness_approval_now = $true
    no_distribution_readiness_validation_approval_now = $true
    no_distribution_approval_allowed_now = $true
    no_distribution_allowed = $true
    no_package_distribution_allowed_now = $true
    no_tester_delivery_allowed_now = $true
    no_onedrive_share_delivery_allowed_now = $true
    no_onedrive_upload_allowed_now = $true
    no_github_release_allowed_now = $true
    no_public_website_upload_allowed_now = $true
    no_public_release_allowed_now = $true
    no_paid_distribution_allowed_now = $true
    no_release_readiness_unfreeze_now = $true
    no_release_readiness_approval_now = $true
    no_release_approval_unfreeze_now = $true
    no_release_approval_allowed_now = $true
    no_release_gate_validation_approval_now = $true
    no_release_gate_approval_now = $true
    no_release_gate_enforcement_now = $true
    no_build_readiness_unfreeze_now = $true
    no_build_readiness_approval_now = $true
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
    creates_local_distribution_readiness_plan_evidence = $true
    approves_distribution_readiness = $false
    approves_distribution_readiness_validation = $false
    approves_distribution = $false
    allows_distribution = $false
    allows_package_distribution = $false
    allows_tester_delivery = $false
    allows_onedrive_share_delivery = $false
    allows_onedrive_upload = $false
    allows_github_release = $false
    allows_public_website_upload = $false
    allows_public_release = $false
    allows_paid_distribution = $false
    approves_release_readiness = $false
    unfreezes_release_readiness = $false
    approves_release = $false
    unfreezes_release_approval = $false
    approves_release_gate_validation = $false
    approves_release_gate = $false
    enforces_release_gate = $false
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
  allowed_next_milestones = @("STOP", "v0.6.27-controlled-tester-package-distribution-readiness-validation-dry-run-no-build-no-distribution")
  blocked_next_actions = @(
    "direct_tester_activation",
    "public_ui_link",
    "public_release",
    "package_distribution",
    "onedrive_share_delivery",
    "github_release_publication",
    "paid_distribution",
    "distribution_readiness_approval",
    "distribution_readiness_validation_approval",
    "distribution_approval",
    "tester_delivery_approval",
    "onedrive_delivery_approval",
    "github_release_approval",
    "public_website_upload_approval",
    "release_readiness_approval",
    "release_readiness_unfreeze",
    "release_approval",
    "release_approval_unfreeze",
    "release_gate_approval",
    "release_gate_validation_approval",
    "release_gate_enforcement",
    "public_release_approval",
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

$planJson = $plan | ConvertTo-Json -Depth 10
[System.IO.File]::WriteAllText($planPath, ($planJson + "`n"), [System.Text.UTF8Encoding]::new($false))

$readme = @"
Voila v0.6.26 controlled tester package distribution readiness plan no-build no-distribution

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
- DISTRIBUTION-READINESS-PLAN-README.txt
- DISTRIBUTION-READINESS-PLAN-DRY-RUN.json

Blocked:
- distribution readiness approval, distribution readiness validation approval, distribution approval, package distribution, controlled tester delivery, OneDrive share delivery/upload, GitHub release publication/approval, public website upload/approval, public release, paid distribution, release readiness approval/unfreeze, release approval/unfreeze, release gate validation approval, release gate approval/enforcement, build readiness approval/unfreeze, build approval, build validation approval, package build, ZIP, EXE, MSI, installer, runnable package, staging manifest creation, staging layout creation, staging tree creation, runtime file copy, package content copy, copy execution, release archive creation, code signing, checksum publication, public UI, tester activation, submit flow, persistence, scoring, cloud/API.
"@

[System.IO.File]::WriteAllText($readmePath, ($readme.TrimEnd() + "`n"), [System.Text.UTF8Encoding]::new($false))

Write-Host "DISTRIBUTION READINESS PLAN ROOT: $planRoot"
Write-Host "WROTE: $planPath"
Write-Host "WROTE: $readmePath"

Write-Host ""
Write-Host "=== Verify distribution readiness plan evidence files ==="
$planFiles = @(Get-ChildItem -LiteralPath $planRoot -File | Select-Object -ExpandProperty Name | Sort-Object)
foreach ($name in $planFiles) { Write-Host $name }

$allowedPlanNames = @("DISTRIBUTION-READINESS-PLAN-DRY-RUN.json", "DISTRIBUTION-READINESS-PLAN-README.txt")
foreach ($name in $planFiles) {
  Assert-True ($allowedPlanNames -contains $name) "Unexpected file in local-only distribution readiness plan evidence directory: $name"
  Assert-True (-not ($name -match "\.(zip|exe|msi)$")) "Forbidden package/release artifact in distribution readiness plan evidence directory: $name"
}

Assert-True (Test-Path -LiteralPath $planPath) "Missing distribution-readiness-plan JSON."
Assert-True (Test-Path -LiteralPath $readmePath) "Missing distribution-readiness-plan README."

Write-Host ""
Write-Host "=== v0.6.26 distribution readiness plan JSON ==="
$planJson

Write-Host ""
Write-Host "=== Repository diff whitespace check ==="
git diff --check

Write-Host ""
Write-Host "=== v0.6.26 CONTROLLED TESTER PACKAGE DISTRIBUTION READINESS PLAN NO-BUILD NO-DISTRIBUTION CHECK PASS ==="
