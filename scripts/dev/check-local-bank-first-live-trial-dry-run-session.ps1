param()

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

Write-Host "=== LOCAL BANK FIRST LIVE TRIAL DRY-RUN SESSION ENVELOPE CHECK v0.4.81 ==="

$ProjectRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
Set-Location $ProjectRoot

$flagNames = @(
  "VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_GUARDED_LIVE_TRIAL",
  "VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_GUARDED_TRIAL_DIAGNOSTICS_ROUTE",
  "VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_GUARDED_TRIAL_CANDIDATES_ROUTE",
  "VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_GUARDED_TRIAL_CANDIDATES_PANEL",
  "VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_GUARDED_TRIAL_CANDIDATES_PANEL_POLISH",
  "VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_LIVE_CONSUMPTION_DECISION_GATE",
  "VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_LIVE_CONSUMPTION_ADAPTER_NOOP_BOUNDARY",
  "VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_SHADOW_SOURCE_SELECTOR",
  "VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_SHADOW_REPORT_ROUTE",
  "VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_SHADOW_REPORT_OWNER_PANEL",
  "VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_FIRST_LIVE_TRIAL_CONTRACT",
  "VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_FIRST_LIVE_TRIAL_QUESTION_ENVELOPE_SANITIZER",
  "VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_FIRST_LIVE_TRIAL_DRY_RUN_SESSION_ENVELOPE"
)

$oldFlags = @{}
foreach ($name in $flagNames) {
  $oldFlags[$name] = [Environment]::GetEnvironmentVariable($name, "Process")
}

try {
  foreach ($name in $flagNames) {
    Remove-Item "Env:\$name" -ErrorAction SilentlyContinue
  }

  $DisabledRaw = python .\services\api\exam_prep_local_bank_first_live_trial_dry_run_session.py --course-id v081-smoke --skill-id local_concept_001_functiile --limit 5 --expect-disabled
  if ($LASTEXITCODE -ne 0) { throw "dry-run session envelope disabled sample failed" }
  Write-Host $DisabledRaw

  foreach ($name in $flagNames) {
    [Environment]::SetEnvironmentVariable($name, "1", "Process")
  }

  $ReadyRaw = python .\services\api\exam_prep_local_bank_first_live_trial_dry_run_session.py --course-id v081-smoke --skill-id local_concept_001_functiile --limit 5 --expect-ready
  if ($LASTEXITCODE -ne 0) { throw "dry-run session envelope ready sample failed" }
  Write-Host $ReadyRaw

  $Disabled = $DisabledRaw | ConvertFrom-Json
  $Ready = $ReadyRaw | ConvertFrom-Json
  $Session = $Ready.session_envelope

  $version_ok = ($Disabled.dry_run_session_envelope_version -eq "v0.4.81" -and $Ready.dry_run_session_envelope_version -eq "v0.4.81")
  $mode_ok = ($Ready.mode -eq "guarded_first_live_trial_dry_run_session_envelope")
  $disabled_ok = ($Disabled.status -eq "disabled" -and $Disabled.session_flag_enabled -eq $false)
  $ready_ok = ($Ready.status -eq "dry_run_session_envelope_ready_for_owner_review" -and $Ready.session_flag_enabled -eq $true)
  $sanitizer_ok = ($Ready.question_envelope_sanitizer_status -eq "question_envelope_sanitizer_ready_for_owner_review" -and $Ready.question_envelope_sanitizer_ready -eq $true)
  $source_ok = ($Ready.effective_source -eq "legacy_fallback" -and $Ready.candidate_source -eq "local_exercise_bank_adapter" -and $Ready.fallback_source -eq "legacy_fallback")
  $flags_ok = (@($Ready.missing_flags).Count -eq 0 -and @($Ready.required_owner_flags).Count -ge 13)
  $session_available_ok = ($Ready.session_envelope_available_for_owner_review -eq $true)
  $session_shape_ok = (
    $Session.session_schema_version -eq "1" -and
    $Session.session_envelope_version -eq "v0.4.81" -and
    $Session.session_kind -eq "owner_only_dry_run_session_envelope" -and
    [int]$Session.question_count -eq 5 -and
    @($Session.question_envelopes).Count -eq 5
  )
  $session_guardrails_ok = (
    $Session.metadata_only -eq $true -and
    $Session.will_deliver_live -eq $false -and
    $Session.will_start_live_session -eq $false -and
    $Session.will_persist_session -eq $false -and
    $Session.will_save_attempts -eq $false -and
    $Session.will_update_progress -eq $false -and
    $Session.will_score_answers -eq $false
  )
  $questions_ok = (
    @($Session.question_envelopes | Where-Object { $_.metadata_only -eq $true }).Count -eq 5 -and
    @($Session.question_envelopes | Where-Object { $_.will_deliver_live -eq $false -and $_.will_save_attempt -eq $false -and $_.will_update_progress -eq $false -and $_.will_score_answer -eq $false }).Count -eq 5
  )
  $profile_ok = (
    [int]$Ready.session_profile.question_count -eq 5 -and
    $Ready.session_profile.all_questions_metadata_only -eq $true
  )
  $sanitization_ok = (
    [int]$Ready.sanitization_status.leaked_forbidden_field_count -eq 0 -and
    $Ready.sanitization_status.answers_exposed_before_submission -eq $false -and
    $Ready.sanitization_status.explanations_exposed_before_submission -eq $false -and
    $Ready.sanitization_status.raw_snapshots_exposed -eq $false -and
    $Ready.sanitization_status.raw_contract_exposed -eq $false
  )

  $sessionJson = $Session | ConvertTo-Json -Depth 30 -Compress
  $forbiddenKeyPatterns = @(
    '"correct_answer"\s*:',
    '"correct_answer_preview"\s*:',
    '"answer"\s*:',
    '"expected_answer"\s*:',
    '"solution"\s*:',
    '"explanation"\s*:',
    '"explanation_preview"\s*:',
    '"source_excerpt"\s*:',
    '"raw_snapshots"\s*:',
    '"raw_contract"\s*:',
    '"dry_run_items"\s*:',
    '"selected_questions"\s*:'
  )
  $leaked = @()
  foreach ($pattern in $forbiddenKeyPatterns) {
    if ($sessionJson -match $pattern) { $leaked += $pattern }
  }
  $no_session_leaks_ok = (@($leaked).Count -eq 0)

  $implementation_ok = (
    $Ready.implementation_scope.json_only_local_module -eq $true -and
    $Ready.implementation_scope.adds_web_route -eq $false -and
    $Ready.implementation_scope.patches_web_app -eq $false -and
    $Ready.implementation_scope.adds_public_ui -eq $false -and
    $Ready.implementation_scope.delivers_local_bank_questions_live -eq $false -and
    $Ready.implementation_scope.persists_sessions -eq $false
  )
  $path_policy_ok = ($Ready.path_policy -eq "no_user_provided_filesystem_root")
  $no_consume_ok = ($Ready.will_consume_local_bank_live -eq $false)
  $no_deliver_ok = ($Ready.will_deliver_local_bank_questions_live -eq $false)
  $no_start_live_ok = ($Ready.will_start_live_session -eq $false)
  $no_replace_source_ok = ($Ready.will_replace_effective_source -eq $false)
  $no_progress_persist_ok = ($Ready.will_persist_progress -eq $false)
  $no_session_persist_ok = ($Ready.will_persist_session -eq $false)
  $no_attempt_persist_ok = ($Ready.will_persist_attempts -eq $false)
  $no_progress_update_ok = ($Ready.will_update_progress -eq $false)
  $no_live_score_ok = ($Ready.will_score_live_session -eq $false)
  $no_ui_ok = ($Ready.will_modify_exam_prep_ui -eq $false)
  $no_weak_ok = ($Ready.will_modify_weak_review -eq $false)
  $no_live_replace_ok = ($Ready.will_replace_live_study_session -eq $false)
  $no_legacy_replace_ok = ($Ready.will_replace_legacy_generator -eq $false)
  $no_live_consumption_ok = ($Ready.will_enable_live_consumption -eq $false)
  $no_cloud_ok = ($Ready.requires_cloud_or_api -eq $false)

  $statusNames = @(
    git status --porcelain | ForEach-Object {
      $line = [string]$_
      if ($line.Length -ge 4) { ($line.Substring(3).Trim() -replace "\\", "/") }
    } | Where-Object { $_ }
  )
  $statusNameText = ($statusNames -join "`n")
  $no_web_app_change_ok = ($statusNameText -notmatch '(^|`n)services/api/web_app\.py($|`n)')

  Write-Host "version_ok $version_ok"
  Write-Host "mode_ok $mode_ok"
  Write-Host "disabled_ok $disabled_ok"
  Write-Host "ready_ok $ready_ok"
  Write-Host "sanitizer_ok $sanitizer_ok"
  Write-Host "source_ok $source_ok"
  Write-Host "flags_ok $flags_ok"
  Write-Host "session_available_ok $session_available_ok"
  Write-Host "session_shape_ok $session_shape_ok"
  Write-Host "session_guardrails_ok $session_guardrails_ok"
  Write-Host "questions_ok $questions_ok"
  Write-Host "profile_ok $profile_ok"
  Write-Host "sanitization_ok $sanitization_ok"
  Write-Host "no_session_leaks_ok $no_session_leaks_ok"
  Write-Host "implementation_ok $implementation_ok"
  Write-Host "path_policy_ok $path_policy_ok"
  Write-Host "no_consume_ok $no_consume_ok"
  Write-Host "no_deliver_ok $no_deliver_ok"
  Write-Host "no_start_live_ok $no_start_live_ok"
  Write-Host "no_replace_source_ok $no_replace_source_ok"
  Write-Host "no_progress_persist_ok $no_progress_persist_ok"
  Write-Host "no_session_persist_ok $no_session_persist_ok"
  Write-Host "no_attempt_persist_ok $no_attempt_persist_ok"
  Write-Host "no_progress_update_ok $no_progress_update_ok"
  Write-Host "no_live_score_ok $no_live_score_ok"
  Write-Host "no_ui_ok $no_ui_ok"
  Write-Host "no_weak_ok $no_weak_ok"
  Write-Host "no_live_replace_ok $no_live_replace_ok"
  Write-Host "no_legacy_replace_ok $no_legacy_replace_ok"
  Write-Host "no_live_consumption_ok $no_live_consumption_ok"
  Write-Host "no_cloud_ok $no_cloud_ok"
  Write-Host "no_web_app_change_ok $no_web_app_change_ok"

  if (-not ($version_ok -and $mode_ok -and $disabled_ok -and $ready_ok -and $sanitizer_ok -and $source_ok -and $flags_ok -and $session_available_ok -and $session_shape_ok -and $session_guardrails_ok -and $questions_ok -and $profile_ok -and $sanitization_ok -and $no_session_leaks_ok -and $implementation_ok -and $path_policy_ok -and $no_consume_ok -and $no_deliver_ok -and $no_start_live_ok -and $no_replace_source_ok -and $no_progress_persist_ok -and $no_session_persist_ok -and $no_attempt_persist_ok -and $no_progress_update_ok -and $no_live_score_ok -and $no_ui_ok -and $no_weak_ok -and $no_live_replace_ok -and $no_legacy_replace_ok -and $no_live_consumption_ok -and $no_cloud_ok -and $no_web_app_change_ok)) {
    throw "LOCAL BANK FIRST LIVE TRIAL DRY-RUN SESSION ENVELOPE CHECK v0.4.81 FAILED"
  }

  Write-Host "LOCAL BANK FIRST LIVE TRIAL DRY-RUN SESSION ENVELOPE CHECK v0.4.81 PASS"
} finally {
  foreach ($name in $flagNames) {
    if ($null -eq $oldFlags[$name]) {
      Remove-Item "Env:\$name" -ErrorAction SilentlyContinue
    } else {
      [Environment]::SetEnvironmentVariable($name, [string]$oldFlags[$name], "Process")
    }
  }
}
