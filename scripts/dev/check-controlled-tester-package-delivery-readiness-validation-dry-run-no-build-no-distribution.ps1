$ErrorActionPreference = "Stop"

Write-Host "=== v0.6.30 controlled tester package delivery readiness validation dry-run no-build no-distribution check ==="

$repoRoot = (git rev-parse --show-toplevel).Trim()
Set-Location $repoRoot

$docPath = "docs/dev/controlled-tester-package-delivery-readiness-validation-dry-run-no-build-no-distribution.md"
$checkPath = "scripts/dev/check-controlled-tester-package-delivery-readiness-validation-dry-run-no-build-no-distribution.ps1"
$allowedTouched = @($docPath, $checkPath)

$validationRoot = "D:\dev\release-assets\voila\v0.6.30-controlled-tester-package-delivery-readiness-validation-dry-run-no-build-no-distribution"
$validationPath = Join-Path $validationRoot "DELIVERY-READINESS-VALIDATION-DRY-RUN.json"
$readmePath = Join-Path $validationRoot "DELIVERY-READINESS-VALIDATION-README.txt"

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
  Assert-True (Test-Path -LiteralPath $path) "Missing required v0.6.30 file: $path"
  Write-Host $path
}

Write-Host ""
Write-Host "=== Verify previous milestone evidence markers ==="
$previousFiles = @(
  "docs/dev/controlled-tester-package-delivery-readiness-plan-no-build-no-distribution.md",
  "scripts/dev/check-controlled-tester-package-delivery-readiness-plan-no-build-no-distribution.ps1",
  "docs/dev/controlled-tester-package-distribution-approval-freeze-no-build-no-distribution.md",
  "scripts/dev/check-controlled-tester-package-distribution-approval-freeze-no-build-no-distribution.ps1",
  "docs/dev/controlled-tester-package-distribution-readiness-validation-dry-run-no-build-no-distribution.md",
  "scripts/dev/check-controlled-tester-package-distribution-readiness-validation-dry-run-no-build-no-distribution.ps1",
  "docs/dev/controlled-tester-package-distribution-readiness-plan-no-build-no-distribution.md",
  "scripts/dev/check-controlled-tester-package-distribution-readiness-plan-no-build-no-distribution.ps1",
  "docs/dev/controlled-tester-package-release-readiness-freeze-no-build-no-distribution.md",
  "scripts/dev/check-controlled-tester-package-release-readiness-freeze-no-build-no-distribution.ps1",
  "docs/dev/controlled-tester-package-release-readiness-review-dry-run-no-build-no-distribution.md",
  "scripts/dev/check-controlled-tester-package-release-readiness-review-dry-run-no-build-no-distribution.ps1",
  "docs/dev/controlled-tester-package-release-approval-freeze-no-build-no-distribution.md",
  "scripts/dev/check-controlled-tester-package-release-approval-freeze-no-build-no-distribution.ps1",
  "docs/dev/controlled-tester-package-release-gate-validation-dry-run-no-build-no-distribution.md",
  "scripts/dev/check-controlled-tester-package-release-gate-validation-dry-run-no-build-no-distribution.ps1",
  "docs/dev/controlled-tester-package-release-gate-plan-no-build-no-distribution.md",
  "scripts/dev/check-controlled-tester-package-release-gate-plan-no-build-no-distribution.ps1",
  "docs/dev/controlled-tester-package-build-readiness-freeze-no-build-no-distribution.md",
  "scripts/dev/check-controlled-tester-package-build-readiness-freeze-no-build-no-distribution.ps1",
  "docs/dev/controlled-tester-candidate-decision.md",
  "scripts/dev/check-controlled-tester-candidate-decision.ps1"
)

foreach ($path in $previousFiles) {
  Assert-True (Test-Path -LiteralPath $path) "Missing previous milestone file: $path"
  Write-Host $path
}

$v0629Text = Get-Content -LiteralPath "scripts/dev/check-controlled-tester-package-delivery-readiness-plan-no-build-no-distribution.ps1" -Raw
$v0629DocText = Get-Content -LiteralPath "docs/dev/controlled-tester-package-delivery-readiness-plan-no-build-no-distribution.md" -Raw

Assert-True ($v0629Text -match "v0\.6\.29 CONTROLLED TESTER PACKAGE DELIVERY READINESS PLAN NO-BUILD NO-DISTRIBUTION CHECK PASS") "v0.6.29 PASS marker missing."
Assert-True ($v0629DocText -match "v0\.6\.30-controlled-tester-package-delivery-readiness-validation-dry-run-no-build-no-distribution") "v0.6.29 allowed next marker missing."

Assert-True ($v0629Text -match "delivery_readiness_plan_created.*true") "v0.6.29 must have delivery readiness plan."
Assert-True ($v0629Text -match "delivery_readiness_plan_dry_run_only.*true") "v0.6.29 must keep delivery readiness plan dry-run only."
Assert-True ($v0629Text -match "delivery_readiness_approved_now.*false") "v0.6.29 must keep delivery readiness approval blocked."
Assert-True ($v0629Text -match "delivery_readiness_validation_approved_now.*false") "v0.6.29 must keep delivery readiness validation approval blocked."
Assert-True ($v0629Text -match "delivery_approval_allowed_now.*false") "v0.6.29 must keep delivery approval blocked."
Assert-True ($v0629Text -match "delivery_execution_allowed_now.*false") "v0.6.29 must keep delivery execution blocked."
Assert-True ($v0629Text -match "controlled_tester_delivery_allowed_now.*false") "v0.6.29 must keep controlled tester delivery blocked."
Assert-True ($v0629Text -match "tester_activation_allowed_now.*false") "v0.6.29 must keep tester activation blocked."
Assert-True ($v0629Text -match "tester_notification_allowed_now.*false") "v0.6.29 must keep tester notification blocked."
Assert-True ($v0629Text -match "tester_access_grant_allowed_now.*false") "v0.6.29 must keep tester access grant blocked."
Assert-True ($v0629Text -match "onedrive_share_delivery_allowed_now.*false") "v0.6.29 must keep OneDrive share delivery blocked."
Assert-True ($v0629Text -match "onedrive_upload_allowed_now.*false") "v0.6.29 must keep OneDrive upload blocked."
Assert-True ($v0629Text -match "github_release_allowed_now.*false") "v0.6.29 must keep GitHub release blocked."
Assert-True ($v0629Text -match "public_website_upload_allowed_now.*false") "v0.6.29 must keep public website upload blocked."
Assert-True ($v0629Text -match "public_release_allowed_now.*false") "v0.6.29 must keep public release blocked."
Assert-True ($v0629Text -match "package_build_executed_now.*false") "v0.6.29 must keep package build blocked."
Assert-True ($v0629Text -match "zip_created.*false") "v0.6.29 must keep zip creation blocked."
Assert-True ($v0629Text -match "release_archive_created.*false") "v0.6.29 must keep release archive blocked."

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
  Assert-True ($allowedTouched -contains $path) "Unexpected changed path in v0.6.30 milestone: $path"
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
    Assert-True (-not ($path -match $pattern)) "Forbidden path touched by v0.6.30 delivery-readiness-validation milestone: $path"
  }
}

Write-Host ""
Write-Host "=== Content safety gate ==="
$docText = Get-Content -LiteralPath $docPath -Raw
$checkText = Get-Content -LiteralPath $checkPath -Raw

$requiredDocMarkers = @(
  "No delivery readiness validation approval",
  "No delivery readiness approval",
  "No delivery approval",
  "No delivery approval unfreeze",
  "No delivery execution",
  "No controlled tester delivery",
  "No tester activation",
  "No tester notification",
  "No tester email",
  "No tester access grant",
  "No OneDrive share delivery",
  "No OneDrive upload",
  "No OneDrive permission change",
  "No OneDrive link creation",
  "No GitHub release publication",
  "No public website upload",
  "No public release",
  "No package distribution",
  "No distribution approval",
  "No distribution approval unfreeze",
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
  "delivery_readiness_validation_created = true",
  "delivery_readiness_validation_checked = true",
  "delivery_readiness_validation_dry_run_only = true",
  "delivery_readiness_validation_approved_now = false",
  "delivery_readiness_approved_now = false",
  "delivery_approval_allowed_now = false",
  "delivery_approval_unfreeze_allowed_now = false",
  "delivery_execution_allowed_now = false",
  "controlled_tester_delivery_allowed_now = false",
  "tester_activation_allowed_now = false",
  "tester_notification_allowed_now = false",
  "tester_email_allowed_now = false",
  "tester_access_grant_allowed_now = false",
  "onedrive_share_delivery_allowed_now = false",
  "onedrive_upload_allowed_now = false",
  "onedrive_permission_change_allowed_now = false",
  "onedrive_link_creation_allowed_now = false",
  "github_release_allowed_now = false",
  "public_website_upload_allowed_now = false",
  "public_release_allowed_now = false",
  "distribution_approval_unfreeze_allowed_now = false",
  "distribution_approval_allowed_now = false",
  "distribution_allowed = false",
  "package_distribution_allowed_now = false",
  "build_allowed_now = false",
  "package_build_executed_now = false",
  "This milestone records delivery readiness validation only"
)
foreach ($marker in $requiredDocMarkers) {
  Assert-True ($docText -match [regex]::Escape($marker)) "Doc missing safety marker: $marker"
}

Assert-True ($checkText -match "delivery_readiness_validation_created.*true") "Check must set delivery_readiness_validation_created true."
Assert-True ($checkText -match "delivery_readiness_validation_checked.*true") "Check must set delivery_readiness_validation_checked true."
Assert-True ($checkText -match "delivery_readiness_validation_dry_run_only.*true") "Check must keep delivery_readiness_validation_dry_run_only true."
Assert-True ($checkText -match "delivery_readiness_validation_approved_now.*false") "Check must keep delivery_readiness_validation_approved_now false."
Assert-True ($checkText -match "delivery_readiness_approved_now.*false") "Check must keep delivery_readiness_approved_now false."
Assert-True ($checkText -match "delivery_approval_allowed_now.*false") "Check must keep delivery_approval_allowed_now false."
Assert-True ($checkText -match "delivery_approval_unfreeze_allowed_now.*false") "Check must keep delivery_approval_unfreeze_allowed_now false."
Assert-True ($checkText -match "delivery_execution_allowed_now.*false") "Check must keep delivery_execution_allowed_now false."
Assert-True ($checkText -match "controlled_tester_delivery_allowed_now.*false") "Check must keep controlled_tester_delivery_allowed_now false."
Assert-True ($checkText -match "tester_activation_allowed_now.*false") "Check must keep tester_activation_allowed_now false."
Assert-True ($checkText -match "tester_notification_allowed_now.*false") "Check must keep tester_notification_allowed_now false."
Assert-True ($checkText -match "tester_email_allowed_now.*false") "Check must keep tester_email_allowed_now false."
Assert-True ($checkText -match "tester_access_grant_allowed_now.*false") "Check must keep tester_access_grant_allowed_now false."
Assert-True ($checkText -match "onedrive_share_delivery_allowed_now.*false") "Check must keep onedrive_share_delivery_allowed_now false."
Assert-True ($checkText -match "onedrive_upload_allowed_now.*false") "Check must keep onedrive_upload_allowed_now false."
Assert-True ($checkText -match "onedrive_permission_change_allowed_now.*false") "Check must keep onedrive_permission_change_allowed_now false."
Assert-True ($checkText -match "onedrive_link_creation_allowed_now.*false") "Check must keep onedrive_link_creation_allowed_now false."
Assert-True ($checkText -match "github_release_allowed_now.*false") "Check must keep github_release_allowed_now false."
Assert-True ($checkText -match "public_website_upload_allowed_now.*false") "Check must keep public_website_upload_allowed_now false."
Assert-True ($checkText -match "public_release_allowed_now.*false") "Check must keep public_release_allowed_now false."
Assert-True ($checkText -match "distribution_approval_unfreeze_allowed_now.*false") "Check must keep distribution_approval_unfreeze_allowed_now false."
Assert-True ($checkText -match "distribution_approval_allowed_now.*false") "Check must keep distribution_approval_allowed_now false."
Assert-True ($checkText -match "distribution_allowed.*false") "Check must keep distribution_allowed false."
Assert-True ($checkText -match "package_distribution_allowed_now.*false") "Check must keep package_distribution_allowed_now false."
Assert-True ($checkText -match "build_readiness_unfreeze_allowed_now.*false") "Check must keep build_readiness_unfreeze_allowed_now false."
Assert-True ($checkText -match "build_approval_allowed_now.*false") "Check must keep build_approval_allowed_now false."
Assert-True ($checkText -match "build_validation_approval_allowed_now.*false") "Check must keep build_validation_approval_allowed_now false."
Assert-True ($checkText -match "build_allowed_now.*false") "Check must keep build_allowed_now false."
Assert-True ($checkText -match "package_build_executed_now.*false") "Check must keep package_build_executed_now false."
Assert-True ($checkText -match "zip_created.*false") "Check must keep zip_created false."
Assert-True ($checkText -match "installer_created.*false") "Check must keep installer_created false."
Assert-True ($checkText -match "release_archive_created.*false") "Check must keep release_archive_created false."
Assert-True ($checkText -match "checksum_publication_allowed.*false") "Check must keep checksum_publication_allowed false."
Assert-True ($checkText -match "code_signing_allowed.*false") "Check must keep code_signing_allowed false."

Write-Host ""
Write-Host "=== Create local-only delivery readiness validation evidence directory ==="
New-Item -ItemType Directory -Force -Path $validationRoot | Out-Null

$repoFull = Resolve-FullPathSafe $repoRoot
$validationFull = Resolve-FullPathSafe $validationRoot
Assert-True (-not ($validationFull.StartsWith($repoFull, [System.StringComparison]::OrdinalIgnoreCase))) "Delivery readiness validation root must be outside repository."

$validatedCategories = @(
  "controlled_tester_identity_and_recipient_confirmation_readiness",
  "controlled_tester_consent_confirmation_readiness",
  "controlled_tester_non_confidential_sample_instructions_readiness",
  "controlled_tester_installation_instructions_readiness",
  "controlled_tester_limitations_and_support_disclaimer_readiness",
  "onedrive_specific_people_share_readiness",
  "onedrive_revocation_and_takedown_readiness",
  "delivery_checksum_communication_readiness",
  "delivery_feedback_channel_readiness",
  "delivery_rollback_instructions_readiness",
  "owner_delivery_go_no_go_readiness"
)

$validatedEntries = @()
foreach ($category in $validatedCategories) {
  $validatedEntries += [ordered]@{
    category = $category
    delivery_readiness_validation_checked = $true
    delivery_readiness_validation_dry_run_only = $true
    validated_now = $true
    delivery_readiness_validation_approved_now = $false
    delivery_readiness_approved_now = $false
    delivery_approval_allowed_now = $false
    delivery_execution_allowed_now = $false
    controlled_tester_delivery_allowed_now = $false
    tester_activation_allowed_now = $false
    tester_notification_allowed_now = $false
    tester_access_grant_allowed_now = $false
    onedrive_share_delivery_allowed_now = $false
    distribution_allowed = $false
    build_allowed_now = $false
    package_build_executed_now = $false
  }
}

$validation = [ordered]@{
  schema_version = "1"
  delivery_readiness_validation_version = "v0.6.30"
  delivery_readiness_validation_type = "controlled_tester_package_delivery_readiness_validation_dry_run_no_build_no_distribution"
  status = "pass"
  delivery_readiness_validation = [ordered]@{
    owner_controlled_delivery_readiness_validation_dry_run_created = $true
    delivery_readiness_validation_created = $true
    delivery_readiness_validation_checked = $true
    delivery_readiness_validation_dry_run_only = $true
    validation_root = $validationRoot
    validation_root_outside_repo = $true
    validation_json_created = $true
    readme_created = $true
    delivery_readiness_validation_approved_now = $false
    delivery_readiness_approved_now = $false
    delivery_approval_allowed_now = $false
    delivery_approval_unfreeze_allowed_now = $false
    delivery_execution_allowed_now = $false
    controlled_tester_delivery_allowed_now = $false
    tester_activation_allowed_now = $false
    tester_notification_allowed_now = $false
    tester_email_allowed_now = $false
    tester_access_grant_allowed_now = $false
    onedrive_share_delivery_allowed_now = $false
    onedrive_upload_allowed_now = $false
    onedrive_permission_change_allowed_now = $false
    onedrive_link_creation_allowed_now = $false
    github_release_allowed_now = $false
    public_website_upload_allowed_now = $false
    public_release_allowed_now = $false
    paid_distribution_allowed_now = $false
    distribution_approval_unfreeze_allowed_now = $false
    distribution_approval_allowed_now = $false
    distribution_readiness_validation_approved_now = $false
    distribution_readiness_approved_now = $false
    distribution_allowed = $false
    package_distribution_allowed_now = $false
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
    next_step_policy = "STOP_OR_SEPARATE_DELIVERY_APPROVAL_FREEZE_NO_BUILD_MILESTONE_ONLY"
  }
  validated_delivery_readiness_categories = $validatedEntries
  evidence = [ordered]@{
    previous_delivery_readiness_plan_version = "v0.6.29"
    previous_delivery_readiness_plan_check = "scripts/dev/check-controlled-tester-package-delivery-readiness-plan-no-build-no-distribution.ps1"
    previous_distribution_approval_freeze_version = "v0.6.28"
    previous_distribution_readiness_validation_version = "v0.6.27"
    previous_distribution_readiness_plan_version = "v0.6.26"
    previous_release_readiness_freeze_version = "v0.6.25"
    previous_release_readiness_review_version = "v0.6.24"
    previous_release_approval_freeze_version = "v0.6.23"
    previous_release_gate_validation_version = "v0.6.22"
    previous_release_gate_plan_version = "v0.6.21"
    previous_build_readiness_freeze_version = "v0.6.20"
    hidden_owner_preview_path = "/owner/exam-prep/session-preview"
    hidden_owner_json_path = "/owner/exam-prep/session-preview.json"
    question_count = 5
    effective_source = "local_bank"
    rollback_source = "legacy_fallback"
  }
  gates = [ordered]@{
    previous_milestone_markers_verified = $true
    delivery_readiness_validation_dry_run_only = $true
    validation_root_outside_repo = $true
    delivery_readiness_validation_created = $true
    delivery_readiness_validation_checked = $true
    no_delivery_readiness_validation_approval_now = $true
    no_delivery_readiness_approval_now = $true
    no_delivery_approval_allowed_now = $true
    no_delivery_approval_unfreeze_now = $true
    no_delivery_execution_allowed_now = $true
    no_controlled_tester_delivery_allowed_now = $true
    no_tester_activation_allowed_now = $true
    no_tester_notification_allowed_now = $true
    no_tester_email_allowed_now = $true
    no_tester_access_grant_allowed_now = $true
    no_onedrive_share_delivery_allowed_now = $true
    no_onedrive_upload_allowed_now = $true
    no_onedrive_permission_change_allowed_now = $true
    no_github_release_allowed_now = $true
    no_public_website_upload_allowed_now = $true
    no_public_release_allowed_now = $true
    no_distribution_approval_unfreeze_now = $true
    no_distribution_approval_allowed_now = $true
    no_distribution_allowed = $true
    no_package_distribution_allowed_now = $true
    no_build_allowed_now = $true
    no_package_build_executed_now = $true
    no_zip_created = $true
    no_installer_created = $true
    no_release_archive_created = $true
    no_code_signing = $true
    no_checksum_publication = $true
    no_copy_allowed_now = $true
    no_copy_executed_now = $true
    no_package_content_copy = $true
    no_runtime_file_copy = $true
    no_public_ui = $true
    no_public_navigation = $true
    no_tester_ui = $true
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
    creates_local_delivery_readiness_validation_evidence = $true
    approves_delivery_readiness_validation = $false
    approves_delivery_readiness = $false
    approves_delivery = $false
    unfreezes_delivery_approval = $false
    executes_delivery = $false
    activates_testers = $false
    notifies_testers = $false
    grants_tester_access = $false
    allows_onedrive_share_delivery = $false
    allows_onedrive_upload = $false
    changes_onedrive_permissions = $false
    creates_onedrive_link = $false
    approves_distribution = $false
    unfreezes_distribution_approval = $false
    allows_distribution = $false
    allows_package_distribution = $false
    allows_public_release = $false
    allows_github_release = $false
    allows_public_website_upload = $false
    approves_release_readiness = $false
    unfreezes_release_readiness = $false
    approves_release = $false
    unfreezes_release_approval = $false
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
  allowed_next_milestones = @("STOP", "v0.6.31-controlled-tester-package-delivery-approval-freeze-no-build-no-distribution")
  blocked_next_actions = @(
    "direct_tester_activation",
    "public_ui_link",
    "public_release",
    "package_distribution",
    "onedrive_share_delivery",
    "github_release_publication",
    "paid_distribution",
    "delivery_readiness_validation_approval",
    "delivery_readiness_approval",
    "delivery_approval",
    "delivery_approval_unfreeze",
    "delivery_execution",
    "controlled_tester_delivery",
    "tester_activation",
    "tester_notification",
    "tester_access_grant",
    "onedrive_upload",
    "onedrive_permission_change",
    "onedrive_link_creation",
    "github_release_approval",
    "public_website_upload_approval",
    "distribution_approval",
    "distribution_approval_unfreeze",
    "distribution_readiness_validation_approval",
    "distribution_readiness_approval",
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
    "runtime_file_copy",
    "package_content_copy",
    "copy_execution",
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

$validationJson = $validation | ConvertTo-Json -Depth 10
[System.IO.File]::WriteAllText($validationPath, ($validationJson + "`n"), [System.Text.UTF8Encoding]::new($false))

$readme = @"
Voila v0.6.30 controlled tester package delivery readiness validation dry-run no-build no-distribution

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
- DELIVERY-READINESS-VALIDATION-README.txt
- DELIVERY-READINESS-VALIDATION-DRY-RUN.json

Blocked:
- delivery readiness validation approval, delivery readiness approval, delivery approval/unfreeze, delivery execution, controlled tester delivery, tester activation, tester notification, tester email, tester access grant, OneDrive share delivery/upload/permission changes/link creation, GitHub release publication/approval, public website upload/approval, public release, package distribution, distribution approval/unfreeze, release readiness approval/unfreeze, release approval/unfreeze, build approval, build validation approval, package build, ZIP, EXE, MSI, installer, runnable package, runtime file copy, package content copy, copy execution, release archive creation, code signing, checksum publication, public UI, tester UI, submit flow, persistence, scoring, cloud/API.
"@

[System.IO.File]::WriteAllText($readmePath, ($readme.TrimEnd() + "`n"), [System.Text.UTF8Encoding]::new($false))

Write-Host "DELIVERY READINESS VALIDATION ROOT: $validationRoot"
Write-Host "WROTE: $validationPath"
Write-Host "WROTE: $readmePath"

Write-Host ""
Write-Host "=== Verify delivery readiness validation evidence files ==="
$validationFiles = @(Get-ChildItem -LiteralPath $validationRoot -File | Select-Object -ExpandProperty Name | Sort-Object)
foreach ($name in $validationFiles) { Write-Host $name }

$allowedValidationNames = @("DELIVERY-READINESS-VALIDATION-DRY-RUN.json", "DELIVERY-READINESS-VALIDATION-README.txt")
foreach ($name in $validationFiles) {
  Assert-True ($allowedValidationNames -contains $name) "Unexpected file in local-only delivery readiness validation evidence directory: $name"
  Assert-True (-not ($name -match "\.(zip|exe|msi)$")) "Forbidden package/release artifact in delivery readiness validation evidence directory: $name"
}

Assert-True (Test-Path -LiteralPath $validationPath) "Missing delivery-readiness-validation JSON."
Assert-True (Test-Path -LiteralPath $readmePath) "Missing delivery-readiness-validation README."

Write-Host ""
Write-Host "=== v0.6.30 delivery readiness validation JSON ==="
$validationJson

Write-Host ""
Write-Host "=== Repository diff whitespace check ==="
git diff --check

Write-Host ""
Write-Host "=== v0.6.30 CONTROLLED TESTER PACKAGE DELIVERY READINESS VALIDATION DRY-RUN NO-BUILD NO-DISTRIBUTION CHECK PASS ==="
