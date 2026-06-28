param()

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

Write-Host "=== LOCAL BANK LIVE CONSUMPTION DECISION GATE CHECK v0.4.70 ==="

$ProjectRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
Set-Location $ProjectRoot

$flagNames = @(
  "VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_GUARDED_LIVE_TRIAL",
  "VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_GUARDED_TRIAL_DIAGNOSTICS_ROUTE",
  "VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_GUARDED_TRIAL_CANDIDATES_ROUTE",
  "VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_GUARDED_TRIAL_CANDIDATES_PANEL",
  "VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_GUARDED_TRIAL_CANDIDATES_PANEL_POLISH",
  "VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_LIVE_CONSUMPTION_DECISION_GATE"
)

$oldFlags = @{}
foreach ($name in $flagNames) {
  $oldFlags[$name] = [Environment]::GetEnvironmentVariable($name, "Process")
}

try {
  foreach ($name in $flagNames) {
    Remove-Item "Env:\$name" -ErrorAction SilentlyContinue
  }

  $BlockedRaw = python .\services\api\exam_prep_local_bank_live_consumption_decision_gate.py --course-id v070-smoke --skill-id local_concept_001_functiile --limit 5 --expect-blocked
  if ($LASTEXITCODE -ne 0) { throw "decision gate blocked sample failed" }
  Write-Host $BlockedRaw

  foreach ($name in $flagNames) {
    [Environment]::SetEnvironmentVariable($name, "1", "Process")
  }

  $EligibleRaw = python .\services\api\exam_prep_local_bank_live_consumption_decision_gate.py --course-id v070-smoke --skill-id local_concept_001_functiile --limit 5 --expect-eligible
  if ($LASTEXITCODE -ne 0) { throw "decision gate eligible sample failed" }
  Write-Host $EligibleRaw

  $Blocked = $BlockedRaw | ConvertFrom-Json
  $Eligible = $EligibleRaw | ConvertFrom-Json

  $version_ok = ($Blocked.decision_gate_version -eq "v0.4.70" -and $Eligible.decision_gate_version -eq "v0.4.70")
  $mode_ok = ($Eligible.mode -eq "guarded_local_bank_live_consumption_decision_gate")
  $blocked_ok = ($Blocked.decision_status -eq "blocked" -and $Blocked.eligible_for_owner_decision -eq $false -and @($Blocked.blocking_reasons).Count -gt 0)
  $eligible_ok = ($Eligible.decision_status -eq "eligible_for_owner_decision" -and $Eligible.eligible_for_owner_decision -eq $true)
  $decision_flag_ok = ($Eligible.decision_flag_enabled -eq $true -and $Eligible.decision_flag_name -eq "VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_LIVE_CONSUMPTION_DECISION_GATE")
  $flags_ok = (@($Eligible.missing_flags).Count -eq 0)
  $owner_ok = ($Eligible.owner_enablement_status -eq "ready_for_owner_review" -and $Eligible.owner_enablement_ready -eq $true)
  $options_ok = (
    @($Eligible.owner_decision_options | Where-Object { $_ -eq "keep_disabled" }).Count -eq 1 -and
    @($Eligible.owner_decision_options | Where-Object { $_ -eq "continue_preview_only" }).Count -eq 1
  )
  $recommendation_ok = ($Eligible.recommended_owner_decision -eq "continue_preview_only")
  $not_live_ok = (
    @($Eligible.explicit_not_live_yet | Where-Object { $_ -match "does not enable live consumption" }).Count -gt 0 -and
    @($Eligible.explicit_not_live_yet | Where-Object { $_ -match "legacy_fallback" }).Count -gt 0
  )
  $path_policy_ok = ($Eligible.path_policy -eq "no_user_provided_filesystem_root")
  $no_consume_ok = ($Eligible.will_consume_local_bank_live -eq $false)
  $no_start_live_ok = ($Eligible.will_start_live_session -eq $false)
  $no_replace_source_ok = ($Eligible.will_replace_effective_source -eq $false)
  $no_progress_persist_ok = ($Eligible.will_persist_progress -eq $false)
  $no_session_persist_ok = ($Eligible.will_persist_session -eq $false)
  $no_attempt_persist_ok = ($Eligible.will_persist_attempts -eq $false)
  $no_progress_update_ok = ($Eligible.will_update_progress -eq $false)
  $no_live_score_ok = ($Eligible.will_score_live_session -eq $false)
  $no_ui_ok = ($Eligible.will_modify_exam_prep_ui -eq $false)
  $no_weak_ok = ($Eligible.will_modify_weak_review -eq $false)
  $no_live_replace_ok = ($Eligible.will_replace_live_study_session -eq $false)
  $no_legacy_replace_ok = ($Eligible.will_replace_legacy_generator -eq $false)
  $no_live_consumption_ok = ($Eligible.will_enable_live_consumption -eq $false)
  $no_cloud_ok = ($Eligible.requires_cloud_or_api -eq $false)

  Write-Host "version_ok $version_ok"
  Write-Host "mode_ok $mode_ok"
  Write-Host "blocked_ok $blocked_ok"
  Write-Host "eligible_ok $eligible_ok"
  Write-Host "decision_flag_ok $decision_flag_ok"
  Write-Host "flags_ok $flags_ok"
  Write-Host "owner_ok $owner_ok"
  Write-Host "options_ok $options_ok"
  Write-Host "recommendation_ok $recommendation_ok"
  Write-Host "not_live_ok $not_live_ok"
  Write-Host "path_policy_ok $path_policy_ok"
  Write-Host "no_consume_ok $no_consume_ok"
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

  if (-not ($version_ok -and $mode_ok -and $blocked_ok -and $eligible_ok -and $decision_flag_ok -and $flags_ok -and $owner_ok -and $options_ok -and $recommendation_ok -and $not_live_ok -and $path_policy_ok -and $no_consume_ok -and $no_start_live_ok -and $no_replace_source_ok -and $no_progress_persist_ok -and $no_session_persist_ok -and $no_attempt_persist_ok -and $no_progress_update_ok -and $no_live_score_ok -and $no_ui_ok -and $no_weak_ok -and $no_live_replace_ok -and $no_legacy_replace_ok -and $no_live_consumption_ok -and $no_cloud_ok)) {
    throw "LOCAL BANK LIVE CONSUMPTION DECISION GATE CHECK v0.4.70 FAILED"
  }

  Write-Host "LOCAL BANK LIVE CONSUMPTION DECISION GATE CHECK v0.4.70 PASS"
} finally {
  foreach ($name in $flagNames) {
    if ($null -eq $oldFlags[$name]) {
      Remove-Item "Env:\$name" -ErrorAction SilentlyContinue
    } else {
      [Environment]::SetEnvironmentVariable($name, [string]$oldFlags[$name], "Process")
    }
  }
}
