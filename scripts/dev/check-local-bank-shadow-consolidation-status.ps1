param()

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

Write-Host "=== LOCAL BANK SHADOW CONSOLIDATION STATUS CHECK v0.4.75 ==="

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
  "VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_SHADOW_REPORT_OWNER_PANEL"
)

$oldFlags = @{}
foreach ($name in $flagNames) {
  $oldFlags[$name] = [Environment]::GetEnvironmentVariable($name, "Process")
}

try {
  foreach ($name in $flagNames) {
    Remove-Item "Env:\$name" -ErrorAction SilentlyContinue
  }

  $BlockedRaw = python .\services\api\exam_prep_local_bank_shadow_consolidation_status.py --course-id v075-smoke --skill-id local_concept_001_functiile --limit 5 --expect-blocked
  if ($LASTEXITCODE -ne 0) { throw "shadow consolidation blocked sample failed" }
  Write-Host $BlockedRaw

  foreach ($name in $flagNames) {
    [Environment]::SetEnvironmentVariable($name, "1", "Process")
  }

  $CompleteRaw = python .\services\api\exam_prep_local_bank_shadow_consolidation_status.py --course-id v075-smoke --skill-id local_concept_001_functiile --limit 5 --expect-complete
  if ($LASTEXITCODE -ne 0) { throw "shadow consolidation complete sample failed" }
  Write-Host $CompleteRaw

  $Blocked = $BlockedRaw | ConvertFrom-Json
  $Complete = $CompleteRaw | ConvertFrom-Json

  $version_ok = ($Blocked.shadow_consolidation_status_version -eq "v0.4.75" -and $Complete.shadow_consolidation_status_version -eq "v0.4.75")
  $mode_ok = ($Complete.mode -eq "guarded_live_consumption_shadow_consolidation_status")
  $blocked_ok = ($Blocked.status -eq "blocked" -and $Blocked.ready_for_next_guarded_phase_review -eq $false)
  $complete_ok = ($Complete.status -eq "complete_shadow_chain_ready_for_review" -and $Complete.ready_for_next_guarded_phase_review -eq $true)
  $range_ok = ($Complete.chain_range -eq "v0.4.60-v0.4.74")
  $milestones_ok = (@($Complete.chain_milestones).Count -eq 15)
  $routes_ok = (
    @($Complete.internal_routes_and_panels | Where-Object { $_.path -eq "/exam-prep/local-bank/live-consumption-shadow-report" }).Count -eq 1 -and
    @($Complete.internal_routes_and_panels | Where-Object { $_.path -eq "/exam-prep/local-bank/live-consumption-shadow-panel" }).Count -eq 1
  )
  $flags_ok = (@($Complete.missing_flags).Count -eq 0 -and @($Complete.required_shadow_flags).Count -ge 10)
  $checks_ok = ([int]$Complete.passed_count -eq [int]$Complete.total_count -and [int]$Complete.total_count -ge 8)
  $effective_ok = ($Complete.effective_source -eq "legacy_fallback")
  $shadow_ok = ($Complete.shadow_source -eq "local_exercise_bank_adapter")
  $summary_ok = (
    $Complete.shadow_selection_summary.selector_status -eq "shadow_selection_ready" -and
    [int]$Complete.shadow_selection_summary.shadow_candidate_count -gt 0 -and
    [int]$Complete.shadow_selection_summary.coverage_comparison.local_question_type_diversity -ge 2
  )
  $sanitized_ok = (
    $Complete.sanitization_status.answers_exposed -eq $false -and
    $Complete.sanitization_status.explanations_exposed -eq $false -and
    $Complete.sanitization_status.raw_snapshots_exposed -eq $false -and
    $Complete.sanitization_status.selected_shadow_questions_metadata_only -eq $true
  )
  $criteria_ok = (@($Complete.next_phase_criteria).Count -ge 8)
  $not_live_ok = (
    @($Complete.explicit_not_live_yet | Where-Object { $_ -match "not delivered live" }).Count -gt 0 -and
    @($Complete.explicit_not_live_yet | Where-Object { $_ -match "not consumed live" }).Count -gt 0 -and
    @($Complete.explicit_not_live_yet | Where-Object { $_ -match "legacy_fallback" }).Count -gt 0
  )
  $path_policy_ok = ($Complete.path_policy -eq "no_user_provided_filesystem_root")
  $no_consume_ok = ($Complete.will_consume_local_bank_live -eq $false)
  $no_deliver_ok = ($Complete.will_deliver_shadow_questions_live -eq $false)
  $no_start_live_ok = ($Complete.will_start_live_session -eq $false)
  $no_replace_source_ok = ($Complete.will_replace_effective_source -eq $false)
  $no_progress_persist_ok = ($Complete.will_persist_progress -eq $false)
  $no_session_persist_ok = ($Complete.will_persist_session -eq $false)
  $no_attempt_persist_ok = ($Complete.will_persist_attempts -eq $false)
  $no_progress_update_ok = ($Complete.will_update_progress -eq $false)
  $no_live_score_ok = ($Complete.will_score_live_session -eq $false)
  $no_ui_ok = ($Complete.will_modify_exam_prep_ui -eq $false)
  $no_weak_ok = ($Complete.will_modify_weak_review -eq $false)
  $no_live_replace_ok = ($Complete.will_replace_live_study_session -eq $false)
  $no_legacy_replace_ok = ($Complete.will_replace_legacy_generator -eq $false)
  $no_live_consumption_ok = ($Complete.will_enable_live_consumption -eq $false)
  $no_cloud_ok = ($Complete.requires_cloud_or_api -eq $false)

  Write-Host "version_ok $version_ok"
  Write-Host "mode_ok $mode_ok"
  Write-Host "blocked_ok $blocked_ok"
  Write-Host "complete_ok $complete_ok"
  Write-Host "range_ok $range_ok"
  Write-Host "milestones_ok $milestones_ok"
  Write-Host "routes_ok $routes_ok"
  Write-Host "flags_ok $flags_ok"
  Write-Host "checks_ok $checks_ok"
  Write-Host "effective_ok $effective_ok"
  Write-Host "shadow_ok $shadow_ok"
  Write-Host "summary_ok $summary_ok"
  Write-Host "sanitized_ok $sanitized_ok"
  Write-Host "criteria_ok $criteria_ok"
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

  if (-not ($version_ok -and $mode_ok -and $blocked_ok -and $complete_ok -and $range_ok -and $milestones_ok -and $routes_ok -and $flags_ok -and $checks_ok -and $effective_ok -and $shadow_ok -and $summary_ok -and $sanitized_ok -and $criteria_ok -and $not_live_ok -and $path_policy_ok -and $no_consume_ok -and $no_deliver_ok -and $no_start_live_ok -and $no_replace_source_ok -and $no_progress_persist_ok -and $no_session_persist_ok -and $no_attempt_persist_ok -and $no_progress_update_ok -and $no_live_score_ok -and $no_ui_ok -and $no_weak_ok -and $no_live_replace_ok -and $no_legacy_replace_ok -and $no_live_consumption_ok -and $no_cloud_ok)) {
    throw "LOCAL BANK SHADOW CONSOLIDATION STATUS CHECK v0.4.75 FAILED"
  }

  Write-Host "LOCAL BANK SHADOW CONSOLIDATION STATUS CHECK v0.4.75 PASS"
} finally {
  foreach ($name in $flagNames) {
    if ($null -eq $oldFlags[$name]) {
      Remove-Item "Env:\$name" -ErrorAction SilentlyContinue
    } else {
      [Environment]::SetEnvironmentVariable($name, [string]$oldFlags[$name], "Process")
    }
  }
}
