param()

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

Write-Host "=== LOCAL BANK FIRST LIVE TRIAL NO-PERSISTENCE DELIVERY CONTRACT CHECK v0.4.82 ==="

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
  "VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_FIRST_LIVE_TRIAL_DRY_RUN_SESSION_ENVELOPE",
  "VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_FIRST_LIVE_TRIAL_NO_PERSISTENCE_DELIVERY_CONTRACT"
)

$oldFlags = @{}
foreach ($name in $flagNames) {
  $oldFlags[$name] = [Environment]::GetEnvironmentVariable($name, "Process")
}

try {
  foreach ($name in $flagNames) {
    Remove-Item "Env:\$name" -ErrorAction SilentlyContinue
  }

  $DisabledRaw = python .\services\api\exam_prep_local_bank_first_live_trial_delivery_contract.py --course-id v082-smoke --skill-id local_concept_001_functiile --limit 5 --expect-disabled
  if ($LASTEXITCODE -ne 0) { throw "no-persistence delivery contract disabled sample failed" }
  Write-Host $DisabledRaw

  foreach ($name in $flagNames) {
    [Environment]::SetEnvironmentVariable($name, "1", "Process")
  }

  $ReadyRaw = python .\services\api\exam_prep_local_bank_first_live_trial_delivery_contract.py --course-id v082-smoke --skill-id local_concept_001_functiile --limit 5 --expect-ready
  if ($LASTEXITCODE -ne 0) { throw "no-persistence delivery contract ready sample failed" }
  Write-Host $ReadyRaw

  $Disabled = $DisabledRaw | ConvertFrom-Json
  $Ready = $ReadyRaw | ConvertFrom-Json
  $Contract = $Ready.delivery_contract

  $version_ok = ($Disabled.no_persistence_delivery_contract_version -eq "v0.4.82" -and $Ready.no_persistence_delivery_contract_version -eq "v0.4.82")
  $mode_ok = ($Ready.mode -eq "guarded_first_live_trial_no_persistence_delivery_contract")
  $disabled_ok = ($Disabled.status -eq "disabled" -and $Disabled.delivery_contract_flag_enabled -eq $false)
  $ready_ok = ($Ready.status -eq "no_persistence_delivery_contract_ready_for_owner_review" -and $Ready.ready_for_owner_review -eq $true)
  $dry_run_ok = ($Ready.dry_run_session_envelope_status -eq "dry_run_session_envelope_ready_for_owner_review" -and $Ready.dry_run_session_envelope_ready -eq $true)
  $source_ok = ($Ready.effective_source -eq "legacy_fallback" -and $Ready.candidate_source -eq "local_exercise_bank_adapter" -and $Ready.fallback_source -eq "legacy_fallback")
  $flags_ok = (@($Ready.missing_flags).Count -eq 0 -and @($Ready.required_owner_flags).Count -ge 14)
  $preconditions_ok = (
    $Ready.delivery_preconditions.owner_only_scope -eq $true -and
    $Ready.delivery_preconditions.dry_run_session_envelope_ready -eq $true -and
    $Ready.delivery_preconditions.sanitized_question_envelopes_available -eq $true -and
    $Ready.delivery_preconditions.attempt_persistence_disabled -eq $true -and
    $Ready.delivery_preconditions.progress_update_disabled -eq $true -and
    $Ready.delivery_preconditions.live_scoring_disabled -eq $true
  )
  $contract_shape_ok = (
    $Contract.contract_schema_version -eq "1" -and
    $Contract.delivery_contract_version -eq "v0.4.82" -and
    $Contract.delivery_contract_kind -eq "owner_only_no_persistence_delivery_contract" -and
    [int]$Contract.candidate_question_count -eq 5 -and
    $Contract.delivery_mode -eq "contract_only_not_live" -and
    $Contract.may_deliver_live_now -eq $false
  )
  $scope_ok = (
    $Contract.delivery_scope.owner_only -eq $true -and
    $Contract.delivery_scope.fixed_course_id -eq $true -and
    $Contract.delivery_scope.fixed_skill_id -eq $true -and
    $Contract.delivery_scope.public_ui -eq $false
  )
  $no_persistence_policy_ok = (
    $Contract.no_persistence_policy.persist_session -eq $false -and
    $Contract.no_persistence_policy.persist_attempts -eq $false -and
    $Contract.no_persistence_policy.persist_progress -eq $false -and
    $Contract.no_persistence_policy.update_progress -eq $false -and
    $Contract.no_persistence_policy.score_live_session -eq $false -and
    $Contract.no_persistence_policy.retain_user_answers -eq $false
  )
  $abort_policy_ok = (
    $Contract.abort_policy.abort_to_effective_source -eq "legacy_fallback" -and
    $Contract.abort_policy.abort_if_missing_owner_flag -eq $true -and
    $Contract.abort_policy.abort_if_dry_run_not_ready -eq $true -and
    $Contract.abort_policy.abort_if_forbidden_fields_detected -eq $true -and
    $Contract.abort_policy.abort_if_persistence_requested -eq $true
  )
  $summary_ok = (
    $Ready.contract_summary.may_deliver_live_now -eq $false -and
    $Ready.contract_summary.delivery_mode -eq "contract_only_not_live" -and
    [int]$Ready.contract_summary.candidate_question_count -eq 5 -and
    $Ready.contract_summary.no_persistence -eq $true
  )
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
  Write-Host "dry_run_ok $dry_run_ok"
  Write-Host "source_ok $source_ok"
  Write-Host "flags_ok $flags_ok"
  Write-Host "preconditions_ok $preconditions_ok"
  Write-Host "contract_shape_ok $contract_shape_ok"
  Write-Host "scope_ok $scope_ok"
  Write-Host "no_persistence_policy_ok $no_persistence_policy_ok"
  Write-Host "abort_policy_ok $abort_policy_ok"
  Write-Host "summary_ok $summary_ok"
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

  if (-not ($version_ok -and $mode_ok -and $disabled_ok -and $ready_ok -and $dry_run_ok -and $source_ok -and $flags_ok -and $preconditions_ok -and $contract_shape_ok -and $scope_ok -and $no_persistence_policy_ok -and $abort_policy_ok -and $summary_ok -and $implementation_ok -and $path_policy_ok -and $no_consume_ok -and $no_deliver_ok -and $no_start_live_ok -and $no_replace_source_ok -and $no_progress_persist_ok -and $no_session_persist_ok -and $no_attempt_persist_ok -and $no_progress_update_ok -and $no_live_score_ok -and $no_ui_ok -and $no_weak_ok -and $no_live_replace_ok -and $no_legacy_replace_ok -and $no_live_consumption_ok -and $no_cloud_ok -and $no_web_app_change_ok)) {
    throw "LOCAL BANK FIRST LIVE TRIAL NO-PERSISTENCE DELIVERY CONTRACT CHECK v0.4.82 FAILED"
  }

  Write-Host "LOCAL BANK FIRST LIVE TRIAL NO-PERSISTENCE DELIVERY CONTRACT CHECK v0.4.82 PASS"
} finally {
  foreach ($name in $flagNames) {
    if ($null -eq $oldFlags[$name]) {
      Remove-Item "Env:\$name" -ErrorAction SilentlyContinue
    } else {
      [Environment]::SetEnvironmentVariable($name, [string]$oldFlags[$name], "Process")
    }
  }
}
