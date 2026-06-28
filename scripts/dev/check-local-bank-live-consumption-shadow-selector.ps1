param()

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

Write-Host "=== LOCAL BANK LIVE CONSUMPTION SHADOW SOURCE SELECTOR CHECK v0.4.72 ==="

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
  "VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_SHADOW_SOURCE_SELECTOR"
)

$oldFlags = @{}
foreach ($name in $flagNames) {
  $oldFlags[$name] = [Environment]::GetEnvironmentVariable($name, "Process")
}

try {
  foreach ($name in $flagNames) {
    Remove-Item "Env:\$name" -ErrorAction SilentlyContinue
  }

  $DisabledRaw = python .\services\api\exam_prep_local_bank_live_consumption_shadow_selector.py --course-id v072-smoke --skill-id local_concept_001_functiile --limit 5 --expect-disabled
  if ($LASTEXITCODE -ne 0) { throw "shadow selector disabled sample failed" }
  Write-Host $DisabledRaw

  foreach ($name in $flagNames) {
    [Environment]::SetEnvironmentVariable($name, "1", "Process")
  }

  $ReadyRaw = python .\services\api\exam_prep_local_bank_live_consumption_shadow_selector.py --course-id v072-smoke --skill-id local_concept_001_functiile --limit 5 --expect-shadow-ready
  if ($LASTEXITCODE -ne 0) { throw "shadow selector ready sample failed" }
  Write-Host $ReadyRaw

  $Disabled = $DisabledRaw | ConvertFrom-Json
  $Ready = $ReadyRaw | ConvertFrom-Json
  $Report = $Ready.shadow_selection_report
  $Profile = $Report.local_candidate_profile
  $Coverage = $Report.coverage_comparison

  $version_ok = ($Disabled.shadow_selector_version -eq "v0.4.72" -and $Ready.shadow_selector_version -eq "v0.4.72")
  $mode_ok = ($Ready.mode -eq "guarded_live_consumption_source_selector_shadow_mode")
  $disabled_ok = ($Disabled.selector_status -eq "disabled" -and $Disabled.shadow_selector_flag_enabled -eq $false)
  $ready_ok = ($Ready.selector_status -eq "shadow_selection_ready" -and $Ready.shadow_selector_flag_enabled -eq $true)
  $adapter_ok = ($Ready.adapter_boundary_status -eq "live_adapter_candidate_noop")
  $effective_source_ok = ($Ready.effective_source -eq "legacy_fallback" -and $Report.effective_source -eq "legacy_fallback")
  $shadow_source_ok = ($Ready.shadow_source -eq "local_exercise_bank_adapter" -and $Report.shadow_source -eq "local_exercise_bank_adapter")
  $report_ok = ($Report.shadow_mode_ready -eq $true -and [int]$Report.shadow_candidate_count -gt 0)
  $profile_ok = (
    $Profile.source -eq "local_exercise_bank_adapter" -and
    $Profile.available -eq $true -and
    [int]$Profile.question_count -eq [int]$Report.shadow_candidate_count
  )
  $coverage_ok = (
    $Coverage.compared_against_legacy_live_output -eq $false -and
    [int]$Coverage.local_question_type_diversity -ge 2 -and
    [int]$Coverage.local_skill_diversity -ge 1
  )
  $questions_ok = (
    @($Report.selected_shadow_questions).Count -eq [int]$Report.shadow_candidate_count -and
    $Report.selected_shadow_questions[0].will_deliver_live -eq $false -and
    $Report.selected_shadow_questions[0].will_save_attempt -eq $false
  )
  $not_live_ok = (
    @($Ready.explicit_not_live_yet | Where-Object { $_ -match "does not change effective_source" }).Count -gt 0 -and
    @($Ready.explicit_not_live_yet | Where-Object { $_ -match "not delivered live" }).Count -gt 0 -and
    @($Ready.explicit_not_live_yet | Where-Object { $_ -match "legacy_fallback" }).Count -gt 0
  )
  $path_policy_ok = ($Ready.path_policy -eq "no_user_provided_filesystem_root")
  $no_consume_ok = ($Ready.will_consume_local_bank_live -eq $false)
  $no_deliver_ok = ($Ready.will_deliver_shadow_questions_live -eq $false)
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

  Write-Host "version_ok $version_ok"
  Write-Host "mode_ok $mode_ok"
  Write-Host "disabled_ok $disabled_ok"
  Write-Host "ready_ok $ready_ok"
  Write-Host "adapter_ok $adapter_ok"
  Write-Host "effective_source_ok $effective_source_ok"
  Write-Host "shadow_source_ok $shadow_source_ok"
  Write-Host "report_ok $report_ok"
  Write-Host "profile_ok $profile_ok"
  Write-Host "coverage_ok $coverage_ok"
  Write-Host "questions_ok $questions_ok"
  Write-Host "not_live_ok $not_live_ok"
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

  if (-not ($version_ok -and $mode_ok -and $disabled_ok -and $ready_ok -and $adapter_ok -and $effective_source_ok -and $shadow_source_ok -and $report_ok -and $profile_ok -and $coverage_ok -and $questions_ok -and $not_live_ok -and $path_policy_ok -and $no_consume_ok -and $no_deliver_ok -and $no_start_live_ok -and $no_replace_source_ok -and $no_progress_persist_ok -and $no_session_persist_ok -and $no_attempt_persist_ok -and $no_progress_update_ok -and $no_live_score_ok -and $no_ui_ok -and $no_weak_ok -and $no_live_replace_ok -and $no_legacy_replace_ok -and $no_live_consumption_ok -and $no_cloud_ok)) {
    throw "LOCAL BANK LIVE CONSUMPTION SHADOW SOURCE SELECTOR CHECK v0.4.72 FAILED"
  }

  Write-Host "LOCAL BANK LIVE CONSUMPTION SHADOW SOURCE SELECTOR CHECK v0.4.72 PASS"
} finally {
  foreach ($name in $flagNames) {
    if ($null -eq $oldFlags[$name]) {
      Remove-Item "Env:\$name" -ErrorAction SilentlyContinue
    } else {
      [Environment]::SetEnvironmentVariable($name, [string]$oldFlags[$name], "Process")
    }
  }
}
