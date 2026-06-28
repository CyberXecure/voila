param()

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

Write-Host "=== LOCAL BANK GUARDED LIVE TRIAL SCAFFOLD CHECK v0.4.61 ==="

$ProjectRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
Set-Location $ProjectRoot

$oldFlag = $env:VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_GUARDED_LIVE_TRIAL

try {
  Remove-Item Env:\VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_GUARDED_LIVE_TRIAL -ErrorAction SilentlyContinue

  $DisabledRaw = python .\services\api\exam_prep_local_bank_guarded_live_trial.py --course-id v061-smoke --skill-id local_concept_001_functiile --limit 5 --strict-disabled
  if ($LASTEXITCODE -ne 0) { throw "guarded live trial disabled check failed" }
  Write-Host $DisabledRaw

  $env:VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_GUARDED_LIVE_TRIAL = "1"

  $PlanRaw = python .\services\api\exam_prep_local_bank_guarded_live_trial.py --course-id v061-smoke --skill-id local_concept_001_functiile --limit 5 --strict-plan-ready
  if ($LASTEXITCODE -ne 0) { throw "guarded live trial plan-ready check failed" }
  Write-Host $PlanRaw

  $Disabled = $DisabledRaw | ConvertFrom-Json
  $Plan = $PlanRaw | ConvertFrom-Json

  $version_ok = ($Disabled.guarded_trial_version -eq "v0.4.61" -and $Plan.guarded_trial_version -eq "v0.4.61")
  $mode_ok = ($Disabled.mode -eq "guarded_live_trial_scaffold" -and $Plan.mode -eq "guarded_live_trial_scaffold")
  $flag_name_ok = ($Plan.flag_name -eq "VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_GUARDED_LIVE_TRIAL")
  $disabled_ok = ($Disabled.flag_enabled -eq $false -and $Disabled.trial_status -eq "disabled")
  $disabled_reason_ok = ($Disabled.blocking_reason -eq "guarded_live_trial_flag_disabled")
  $plan_ready_ok = ($Plan.flag_enabled -eq $true -and $Plan.trial_status -eq "guarded_trial_plan_ready")
  $readiness_ok = ($Plan.readiness_status -eq "ready_for_guarded_live_trial")
  $trial_plan_ok = ($null -ne $Plan.trial_plan -and $Plan.trial_plan.source -eq "local_exercise_bank_adapter")
  $live_not_touched_ok = ($Plan.trial_plan.live_integration_touched -eq $false)
  $guardrails_ok = (
    $Plan.guardrails.default_disabled -eq $true -and
    $Plan.guardrails.requires_readiness_ready -eq $true -and
    $Plan.guardrails.requires_explicit_live_trial_flag -eq $true -and
    $Plan.guardrails.legacy_fallback_must_remain_available -eq $true
  )
  $path_policy_ok = ($Plan.path_policy -eq "no_user_provided_filesystem_root" -and $Disabled.path_policy -eq "no_user_provided_filesystem_root")
  $no_progress_persist_ok = ($Plan.will_persist_progress -eq $false -and $Disabled.will_persist_progress -eq $false)
  $no_session_persist_ok = ($Plan.will_persist_session -eq $false -and $Disabled.will_persist_session -eq $false)
  $no_attempt_persist_ok = ($Plan.will_persist_attempts -eq $false -and $Disabled.will_persist_attempts -eq $false)
  $no_progress_update_ok = ($Plan.will_update_progress -eq $false -and $Disabled.will_update_progress -eq $false)
  $no_live_score_ok = ($Plan.will_score_live_session -eq $false -and $Disabled.will_score_live_session -eq $false)
  $no_ui_ok = ($Plan.will_modify_exam_prep_ui -eq $false -and $Disabled.will_modify_exam_prep_ui -eq $false)
  $no_weak_ok = ($Plan.will_modify_weak_review -eq $false -and $Disabled.will_modify_weak_review -eq $false)
  $no_live_replace_ok = ($Plan.will_replace_live_study_session -eq $false -and $Disabled.will_replace_live_study_session -eq $false)
  $no_legacy_replace_ok = ($Plan.will_replace_legacy_generator -eq $false -and $Disabled.will_replace_legacy_generator -eq $false)
  $no_live_consumption_ok = ($Plan.will_enable_live_consumption -eq $false -and $Disabled.will_enable_live_consumption -eq $false)
  $no_cloud_ok = ($Plan.requires_cloud_or_api -eq $false -and $Disabled.requires_cloud_or_api -eq $false)

  Write-Host "version_ok $version_ok"
  Write-Host "mode_ok $mode_ok"
  Write-Host "flag_name_ok $flag_name_ok"
  Write-Host "disabled_ok $disabled_ok"
  Write-Host "disabled_reason_ok $disabled_reason_ok"
  Write-Host "plan_ready_ok $plan_ready_ok"
  Write-Host "readiness_ok $readiness_ok"
  Write-Host "trial_plan_ok $trial_plan_ok"
  Write-Host "live_not_touched_ok $live_not_touched_ok"
  Write-Host "guardrails_ok $guardrails_ok"
  Write-Host "path_policy_ok $path_policy_ok"
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

  if (-not ($version_ok -and $mode_ok -and $flag_name_ok -and $disabled_ok -and $disabled_reason_ok -and $plan_ready_ok -and $readiness_ok -and $trial_plan_ok -and $live_not_touched_ok -and $guardrails_ok -and $path_policy_ok -and $no_progress_persist_ok -and $no_session_persist_ok -and $no_attempt_persist_ok -and $no_progress_update_ok -and $no_live_score_ok -and $no_ui_ok -and $no_weak_ok -and $no_live_replace_ok -and $no_legacy_replace_ok -and $no_live_consumption_ok -and $no_cloud_ok)) {
    throw "LOCAL BANK GUARDED LIVE TRIAL SCAFFOLD CHECK v0.4.61 FAILED"
  }

  Write-Host "LOCAL BANK GUARDED LIVE TRIAL SCAFFOLD CHECK v0.4.61 PASS"
} finally {
  if ($null -eq $oldFlag) {
    Remove-Item Env:\VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_GUARDED_LIVE_TRIAL -ErrorAction SilentlyContinue
  } else {
    $env:VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_GUARDED_LIVE_TRIAL = $oldFlag
  }
}

