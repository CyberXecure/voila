param()

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

Write-Host "=== LOCAL BANK OWNER ENABLEMENT CHECKLIST CHECK v0.4.69 ==="

$ProjectRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
Set-Location $ProjectRoot

$flagNames = @(
  "VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_GUARDED_LIVE_TRIAL",
  "VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_GUARDED_TRIAL_DIAGNOSTICS_ROUTE",
  "VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_GUARDED_TRIAL_CANDIDATES_ROUTE",
  "VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_GUARDED_TRIAL_CANDIDATES_PANEL",
  "VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_GUARDED_TRIAL_CANDIDATES_PANEL_POLISH"
)

$oldFlags = @{}
foreach ($name in $flagNames) {
  $oldFlags[$name] = [Environment]::GetEnvironmentVariable($name, "Process")
}

try {
  foreach ($name in $flagNames) {
    Remove-Item "Env:\$name" -ErrorAction SilentlyContinue
  }

  $BlockedRaw = python .\services\api\exam_prep_local_bank_owner_enablement_checklist.py --course-id v069-smoke --skill-id local_concept_001_functiile --limit 5
  if ($LASTEXITCODE -ne 0) { throw "owner checklist blocked sample failed" }
  Write-Host $BlockedRaw

  foreach ($name in $flagNames) {
    [Environment]::SetEnvironmentVariable($name, "1", "Process")
  }

  $ReadyRaw = python .\services\api\exam_prep_local_bank_owner_enablement_checklist.py --course-id v069-smoke --skill-id local_concept_001_functiile --limit 5 --expect-ready
  if ($LASTEXITCODE -ne 0) { throw "owner checklist ready sample failed" }
  Write-Host $ReadyRaw

  $Blocked = $BlockedRaw | ConvertFrom-Json
  $Ready = $ReadyRaw | ConvertFrom-Json

  $version_ok = ($Blocked.owner_enablement_checklist_version -eq "v0.4.69" -and $Ready.owner_enablement_checklist_version -eq "v0.4.69")
  $mode_ok = ($Ready.mode -eq "guarded_local_bank_owner_enablement_checklist")
  $blocked_ok = ($Blocked.checklist_status -eq "blocked" -and $Blocked.ready_for_owner_review -eq $false -and @($Blocked.missing_flags).Count -gt 0)
  $ready_ok = ($Ready.checklist_status -eq "ready_for_owner_review" -and $Ready.ready_for_owner_review -eq $true)
  $counts_ok = ([int]$Ready.passed_count -eq [int]$Ready.total_count -and [int]$Ready.total_count -ge 8)
  $flags_ok = (@($Ready.missing_flags).Count -eq 0)
  $items_ok = (@($Ready.checklist_items | Where-Object { $_.passed -eq $true }).Count -eq @($Ready.checklist_items).Count)
  $readiness_ok = ($Ready.snapshots.readiness.readiness_status -eq "ready_for_guarded_live_trial")
  $trial_ok = ($Ready.snapshots.guarded_trial.trial_status -eq "guarded_trial_plan_ready")
  $boundary_ok = ($Ready.snapshots.adapter_boundary.boundary_status -eq "local_source_candidate_available")
  $hook_ok = ($Ready.snapshots.noop_hook.hook_status -eq "local_source_candidate_reported_noop" -and $Ready.snapshots.noop_hook.effective_source -eq "legacy_fallback")
  $criteria_ok = (@($Ready.minimum_criteria_for_v0_4_70).Count -ge 8)
  $not_live_ok = (
    @($Ready.explicit_not_live_yet | Where-Object { $_ -match "not consumed live" }).Count -gt 0 -and
    @($Ready.explicit_not_live_yet | Where-Object { $_ -match "legacy_fallback" }).Count -gt 0
  )
  $path_policy_ok = ($Ready.path_policy -eq "no_user_provided_filesystem_root")
  $no_consume_ok = ($Ready.will_consume_local_bank_live -eq $false)
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
  Write-Host "blocked_ok $blocked_ok"
  Write-Host "ready_ok $ready_ok"
  Write-Host "counts_ok $counts_ok"
  Write-Host "flags_ok $flags_ok"
  Write-Host "items_ok $items_ok"
  Write-Host "readiness_ok $readiness_ok"
  Write-Host "trial_ok $trial_ok"
  Write-Host "boundary_ok $boundary_ok"
  Write-Host "hook_ok $hook_ok"
  Write-Host "criteria_ok $criteria_ok"
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

  if (-not ($version_ok -and $mode_ok -and $blocked_ok -and $ready_ok -and $counts_ok -and $flags_ok -and $items_ok -and $readiness_ok -and $trial_ok -and $boundary_ok -and $hook_ok -and $criteria_ok -and $not_live_ok -and $path_policy_ok -and $no_consume_ok -and $no_start_live_ok -and $no_replace_source_ok -and $no_progress_persist_ok -and $no_session_persist_ok -and $no_attempt_persist_ok -and $no_progress_update_ok -and $no_live_score_ok -and $no_ui_ok -and $no_weak_ok -and $no_live_replace_ok -and $no_legacy_replace_ok -and $no_live_consumption_ok -and $no_cloud_ok)) {
    throw "LOCAL BANK OWNER ENABLEMENT CHECKLIST CHECK v0.4.69 FAILED"
  }

  Write-Host "LOCAL BANK OWNER ENABLEMENT CHECKLIST CHECK v0.4.69 PASS"
} finally {
  foreach ($name in $flagNames) {
    if ($null -eq $oldFlags[$name]) {
      Remove-Item "Env:\$name" -ErrorAction SilentlyContinue
    } else {
      [Environment]::SetEnvironmentVariable($name, [string]$oldFlags[$name], "Process")
    }
  }
}
