$ErrorActionPreference = "Stop"

$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
Set-Location $RepoRoot

Write-Host "=== v0.6.0 controlled tester candidate decision check ===" -ForegroundColor Cyan

$DecisionRoot = ".tmp\v060-controlled-tester-candidate-decision"
$SmokeReportPath = Join-Path $DecisionRoot "owner_preview_manual_smoke_report.json"
$DecisionPath = Join-Path $DecisionRoot "controlled_tester_candidate_decision.json"

if (Test-Path $DecisionRoot) {
  Remove-Item $DecisionRoot -Recurse -Force
}
New-Item -ItemType Directory -Path $DecisionRoot -Force | Out-Null

Write-Host "`n=== Build owner manual smoke report evidence ===" -ForegroundColor Yellow
$smokeJson = python "scripts/dev/build-owner-session-preview-manual-smoke-report.py" `
  --root "." `
  --output $SmokeReportPath `
  --expect-pass

$smoke = $smokeJson | ConvertFrom-Json

if ($smoke.status -ne "pass") {
  throw "Owner manual smoke report did not pass"
}
if ($smoke.question_count -ne 5) {
  throw "Expected 5 questions in smoke report"
}
if ($smoke.effective_source -ne "local_bank") {
  throw "Expected effective_source=local_bank"
}
if ($smoke.rollback_source -ne "legacy_fallback") {
  throw "Expected rollback_source=legacy_fallback"
}

Write-Host "`n=== Build v0.6.0 decision JSON ===" -ForegroundColor Yellow

$changed = @(git diff --name-only)
$changedText = $changed -join "`n"

$gates = [ordered]@{
  owner_manual_smoke_report_pass = ($smoke.status -eq "pass")
  hidden_owner_preview_exists = ($smoke.hidden_page -eq $true)
  hidden_json_route_exists = ($smoke.hidden_json_route -eq $true)
  question_count_is_5 = ($smoke.question_count -eq 5)
  effective_source_local_bank = ($smoke.effective_source -eq "local_bank")
  rollback_source_legacy_fallback = ($smoke.rollback_source -eq "legacy_fallback")
  romanian_polished_copy_visible = ($smoke.automated_browser_preview_checklist.romanian_copy_visible -eq $true)
  answers_explanations_hidden = ($smoke.automated_browser_preview_checklist.answer_policy_visible -eq $true)
  no_form = ($smoke.automated_browser_preview_checklist.no_form -eq $true)
  no_input = ($smoke.automated_browser_preview_checklist.no_input -eq $true)
  no_button = ($smoke.automated_browser_preview_checklist.no_button -eq $true)
  no_submit_supported = ($smoke.automated_browser_preview_checklist.no_submit_supported -eq $true)
  no_save_attempt_supported = ($smoke.automated_browser_preview_checklist.no_save_attempt_supported -eq $true)
  no_progress_update_supported = ($smoke.automated_browser_preview_checklist.no_progress_update_supported -eq $true)
  no_live_scoring_supported = ($smoke.automated_browser_preview_checklist.no_live_scoring_supported -eq $true)
  no_public_ui = ($smoke.safety.adds_public_ui -eq $false)
  no_public_navigation = ($smoke.safety.adds_public_navigation -eq $false)
  no_tester_ui = ($smoke.safety.adds_tester_ui -eq $false)
  no_attempt_persistence = ($smoke.safety.persists_attempts -eq $false)
  no_session_persistence = ($smoke.safety.persists_sessions -eq $false)
  no_progress_persistence = ($smoke.safety.updates_progress -eq $false)
  no_live_scoring_persistence = ($smoke.safety.scores_live_session -eq $false)
  no_cloud_or_api = ($smoke.safety.requires_cloud_or_api -eq $false)
  no_web_app_patch_in_v060 = ($changedText -notmatch "services/api/web_app.py")
  no_public_template_static_asset_patch_in_v060 = ($changedText -notmatch "templates|static|assets")
}

$failures = @()
foreach ($key in $gates.Keys) {
  if ($gates[$key] -ne $true) {
    $failures += $key
  }
}

$decisionStatus = if ($failures.Count -eq 0) { "pass" } else { "fail" }

$decision = [ordered]@{
  schema_version = "1"
  decision_version = "v0.6.0"
  decision_type = "controlled_tester_candidate_decision"
  status = $decisionStatus
  validation_failures = $failures
  candidate_readiness = [ordered]@{
    owner_controlled_tester_candidate_prep_allowed = ($decisionStatus -eq "pass")
    tester_activation_allowed_now = $false
    public_release_allowed_now = $false
    tester_package_created = $false
    tester_package_allowed_in_this_milestone = $false
    public_ui_allowed = $false
    external_distribution_allowed = $false
    next_step_policy = "STOP_OR_SEPARATE_TESTER_PACKAGE_DRY_RUN_MILESTONE_ONLY"
  }
  evidence = [ordered]@{
    manual_smoke_report_version = $smoke.report_version
    page_url = $smoke.page_url
    json_url = $smoke.json_url
    selected_real_course_path = $smoke.selected_real_course_path
    question_count = $smoke.question_count
    effective_source = $smoke.effective_source
    rollback_source = $smoke.rollback_source
    manual_screenshot_required = $smoke.manual_screenshot_required
    manual_screenshot_should_be_committed = $smoke.manual_screenshot_should_be_committed
  }
  gates = $gates
  safety = [ordered]@{
    owner_only = $true
    hidden_preview_only = $true
    max_questions = 5
    adds_public_ui = $false
    adds_public_navigation = $false
    adds_tester_ui = $false
    patches_web_app = $false
    creates_package = $false
    publishes_package = $false
    persists_sessions = $false
    persists_attempts = $false
    persists_progress = $false
    updates_progress = $false
    scores_live_session = $false
    requires_cloud_or_api = $false
  }
  allowed_next_milestones = @(
    "STOP",
    "v0.6.1-controlled-tester-package-dry-run-no-distribution"
  )
  blocked_next_actions = @(
    "direct_tester_activation",
    "public_ui_link",
    "public_release",
    "package_distribution",
    "attempt_persistence",
    "session_persistence",
    "progress_persistence",
    "live_scoring_persistence",
    "cloud_or_api_requirement"
  )
}

$decision | ConvertTo-Json -Depth 20 | Set-Content -Path $DecisionPath -Encoding UTF8
Get-Content $DecisionPath -Raw -Encoding UTF8 | Out-Host

if ($decision.status -ne "pass") {
  throw "Controlled tester candidate decision status is not pass"
}
if ($decision.candidate_readiness.owner_controlled_tester_candidate_prep_allowed -ne $true) {
  throw "Candidate package prep is not allowed"
}
if ($decision.candidate_readiness.tester_activation_allowed_now -ne $false) {
  throw "Tester activation must remain false"
}
if ($decision.candidate_readiness.public_release_allowed_now -ne $false) {
  throw "Public release must remain false"
}
if ($decision.candidate_readiness.tester_package_created -ne $false) {
  throw "Tester package must not be created in v0.6.0"
}
if ($decision.candidate_readiness.next_step_policy -ne "STOP_OR_SEPARATE_TESTER_PACKAGE_DRY_RUN_MILESTONE_ONLY") {
  throw "Unexpected next step policy"
}

Write-Host "`n=== Existing owner preview checks ===" -ForegroundColor Yellow
scripts/dev/check-owner-session-preview-manual-smoke-report.ps1

if (Test-Path ".tmp") {
  Remove-Item ".tmp" -Recurse -Force
}

Write-Host "`n=== Ensure no public UI/template/static asset was added ===" -ForegroundColor Yellow
$changed = git diff --name-only
$changed | Out-Host
$changedText = $changed -join "`n"

if ($changedText -match "templates|static|assets") {
  throw "Unexpected public UI/template/static asset change in v0.6.0"
}
if ($changedText -match "services/api/web_app.py") {
  throw "v0.6.0 must not patch web_app.py"
}

Write-Host "`n=== Diff whitespace check ===" -ForegroundColor Yellow
git diff --check

Write-Host "`n=== v0.6.0 CONTROLLED TESTER CANDIDATE DECISION CHECK PASS ===" -ForegroundColor Green
