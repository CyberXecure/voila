param()

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

Write-Host "=== LOCAL BANK FIRST LIVE TRIAL OWNER-READY CHECKPOINT CHECK v0.4.89 ==="

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
  "VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_FIRST_LIVE_TRIAL_NO_PERSISTENCE_DELIVERY_CONTRACT",
  "VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_FIRST_LIVE_TRIAL_NO_PERSISTENCE_DELIVERY_ADAPTER_NOOP",
  "VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_FIRST_LIVE_TRIAL_NO_PERSISTENCE_DECISION_GATE",
  "VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_FIRST_LIVE_TRIAL_OWNER_READY_CHECKPOINT"
)

$oldFlags = @{}
foreach ($name in $flagNames) {
  $oldFlags[$name] = [Environment]::GetEnvironmentVariable($name, "Process")
}

try {
  foreach ($name in $flagNames) {
    Remove-Item "Env:\$name" -ErrorAction SilentlyContinue
  }

  $DisabledRaw = python .\services\api\exam_prep_local_bank_first_live_trial_owner_checkpoint.py --course-id v089-smoke --skill-id local_concept_001_functiile --limit 5 --expect-disabled
  if ($LASTEXITCODE -ne 0) { throw "owner-ready checkpoint disabled sample failed" }
  Write-Host $DisabledRaw

  foreach ($name in $flagNames) {
    [Environment]::SetEnvironmentVariable($name, "1", "Process")
  }

  $ReadyRaw = python .\services\api\exam_prep_local_bank_first_live_trial_owner_checkpoint.py --course-id v089-smoke --skill-id local_concept_001_functiile --limit 5 --expect-ready
  if ($LASTEXITCODE -ne 0) { throw "owner-ready checkpoint ready sample failed" }
  Write-Host $ReadyRaw

  $Disabled = $DisabledRaw | ConvertFrom-Json
  $Ready = $ReadyRaw | ConvertFrom-Json

  $version_ok = ($Disabled.owner_ready_checkpoint_version -eq "v0.4.89" -and $Ready.owner_ready_checkpoint_version -eq "v0.4.89")
  $mode_ok = ($Ready.mode -eq "guarded_first_live_trial_owner_ready_checkpoint")
  $disabled_ok = ($Disabled.status -eq "disabled" -and $Disabled.checkpoint_flag_enabled -eq $false)
  $ready_ok = ($Ready.status -eq "owner_ready_checkpoint_complete_no_go_for_real_delivery" -and $Ready.owner_ready_checkpoint_complete -eq $true)
  $decision_ok = ($Ready.decision_gate_status -eq "decision_gate_ready_for_owner_review" -and $Ready.decision_gate_ready -eq $true)
  $source_ok = ($Ready.effective_source -eq "legacy_fallback" -and $Ready.candidate_source -eq "local_exercise_bank_adapter" -and $Ready.fallback_source -eq "legacy_fallback")
  $flags_ok = (@($Ready.missing_flags).Count -eq 0 -and @($Ready.required_owner_flags).Count -ge 17)
  $chain_ok = (@($Ready.chain_components).Count -ge 13)
  $checks_ok = (
    $Ready.checkpoint_checks.checkpoint_flag_enabled -eq $true -and
    $Ready.checkpoint_checks.all_required_owner_flags_enabled -eq $true -and
    $Ready.checkpoint_checks.decision_gate_ready -eq $true -and
    $Ready.checkpoint_checks.candidate_question_count_positive -eq $true -and
    $Ready.checkpoint_checks.real_delivery_allowed_now_false -eq $true -and
    $Ready.checkpoint_checks.delivery_performed_false -eq $true -and
    $Ready.checkpoint_checks.delivered_question_count_zero -eq $true -and
    $Ready.checkpoint_checks.effective_source_after_decision_legacy -eq $true -and
    $Ready.checkpoint_checks.requires_separate_real_delivery_milestone -eq $true
  )
  $stop_go_ok = (
    $Ready.stop_go_summary.owner_ready_checkpoint_complete -eq $true -and
    $Ready.stop_go_summary.stop_go_label -eq "STOP" -and
    $Ready.stop_go_summary.go_for_real_delivery_now -eq $false -and
    $Ready.stop_go_summary.real_delivery_allowed_now -eq $false -and
    $Ready.stop_go_summary.delivery_performed -eq $false -and
    [int]$Ready.stop_go_summary.delivered_question_count -eq 0 -and
    $Ready.stop_go_summary.requires_new_milestone_for_real_delivery -eq $true
  )
  $owner_readiness_ok = (
    $Ready.owner_readiness_summary.ready_for_next_decision -eq $true -and
    $Ready.owner_readiness_summary.accepted_decision -eq "keep_noop_only" -and
    $Ready.owner_readiness_summary.real_delivery_allowed_now -eq $false -and
    $Ready.owner_readiness_summary.go_for_real_delivery_now -eq $false -and
    $Ready.owner_readiness_summary.delivery_performed -eq $false -and
    [int]$Ready.owner_readiness_summary.delivered_question_count -eq 0 -and
    $Ready.owner_readiness_summary.safe_to_prepare_future_real_delivery_milestone -eq $true -and
    $Ready.owner_readiness_summary.safe_to_activate_real_delivery_in_this_milestone -eq $false
  )
  $required_ok = (
    @($Ready.required_before_real_delivery | Where-Object { $_ -eq "separate explicit real delivery milestone" }).Count -eq 1 -and
    @($Ready.required_before_real_delivery | Where-Object { $_ -eq "owner reconfirmation" }).Count -eq 1 -and
    @($Ready.required_before_real_delivery | Where-Object { $_ -eq "rollback path to legacy_fallback" }).Count -eq 1
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
  Write-Host "decision_ok $decision_ok"
  Write-Host "source_ok $source_ok"
  Write-Host "flags_ok $flags_ok"
  Write-Host "chain_ok $chain_ok"
  Write-Host "checks_ok $checks_ok"
  Write-Host "stop_go_ok $stop_go_ok"
  Write-Host "owner_readiness_ok $owner_readiness_ok"
  Write-Host "required_ok $required_ok"
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

  if (-not ($version_ok -and $mode_ok -and $disabled_ok -and $ready_ok -and $decision_ok -and $source_ok -and $flags_ok -and $chain_ok -and $checks_ok -and $stop_go_ok -and $owner_readiness_ok -and $required_ok -and $implementation_ok -and $path_policy_ok -and $no_consume_ok -and $no_deliver_ok -and $no_start_live_ok -and $no_replace_source_ok -and $no_progress_persist_ok -and $no_session_persist_ok -and $no_attempt_persist_ok -and $no_progress_update_ok -and $no_live_score_ok -and $no_ui_ok -and $no_weak_ok -and $no_live_replace_ok -and $no_legacy_replace_ok -and $no_live_consumption_ok -and $no_cloud_ok -and $no_web_app_change_ok)) {
    throw "LOCAL BANK FIRST LIVE TRIAL OWNER-READY CHECKPOINT CHECK v0.4.89 FAILED"
  }

  Write-Host "LOCAL BANK FIRST LIVE TRIAL OWNER-READY CHECKPOINT CHECK v0.4.89 PASS"
} finally {
  foreach ($name in $flagNames) {
    if ($null -eq $oldFlags[$name]) {
      Remove-Item "Env:\$name" -ErrorAction SilentlyContinue
    } else {
      [Environment]::SetEnvironmentVariable($name, [string]$oldFlags[$name], "Process")
    }
  }
}
