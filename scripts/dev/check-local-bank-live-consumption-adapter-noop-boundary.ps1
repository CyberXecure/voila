param()

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

Write-Host "=== LOCAL BANK LIVE CONSUMPTION ADAPTER NO-OP BOUNDARY CHECK v0.4.71 ==="

$ProjectRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
Set-Location $ProjectRoot

$flagNames = @(
  "VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_GUARDED_LIVE_TRIAL",
  "VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_GUARDED_TRIAL_DIAGNOSTICS_ROUTE",
  "VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_GUARDED_TRIAL_CANDIDATES_ROUTE",
  "VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_GUARDED_TRIAL_CANDIDATES_PANEL",
  "VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_GUARDED_TRIAL_CANDIDATES_PANEL_POLISH",
  "VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_LIVE_CONSUMPTION_DECISION_GATE",
  "VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_LIVE_CONSUMPTION_ADAPTER_NOOP_BOUNDARY"
)

$oldFlags = @{}
foreach ($name in $flagNames) {
  $oldFlags[$name] = [Environment]::GetEnvironmentVariable($name, "Process")
}

try {
  foreach ($name in $flagNames) {
    Remove-Item "Env:\$name" -ErrorAction SilentlyContinue
  }

  $FallbackRaw = python .\services\api\exam_prep_local_bank_live_consumption_adapter_noop_boundary.py --course-id v071-smoke --skill-id local_concept_001_functiile --limit 5 --expect-legacy-fallback
  if ($LASTEXITCODE -ne 0) { throw "adapter no-op boundary fallback sample failed" }
  Write-Host $FallbackRaw

  foreach ($name in $flagNames) {
    [Environment]::SetEnvironmentVariable($name, "1", "Process")
  }

  $CandidateRaw = python .\services\api\exam_prep_local_bank_live_consumption_adapter_noop_boundary.py --course-id v071-smoke --skill-id local_concept_001_functiile --limit 5 --expect-noop-candidate
  if ($LASTEXITCODE -ne 0) { throw "adapter no-op boundary candidate sample failed" }
  Write-Host $CandidateRaw

  $Fallback = $FallbackRaw | ConvertFrom-Json
  $Candidate = $CandidateRaw | ConvertFrom-Json

  $version_ok = ($Fallback.adapter_noop_boundary_version -eq "v0.4.71" -and $Candidate.adapter_noop_boundary_version -eq "v0.4.71")
  $mode_ok = ($Candidate.mode -eq "guarded_live_consumption_adapter_noop_boundary")
  $fallback_ok = ($Fallback.adapter_status -eq "legacy_fallback_only" -and $Fallback.eligible_for_noop_adapter_candidate -eq $false)
  $candidate_ok = ($Candidate.adapter_status -eq "live_adapter_candidate_noop" -and $Candidate.eligible_for_noop_adapter_candidate -eq $true)
  $adapter_flag_ok = ($Candidate.adapter_flag_enabled -eq $true -and $Candidate.adapter_flag_name -eq "VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_LIVE_CONSUMPTION_ADAPTER_NOOP_BOUNDARY")
  $decision_ok = ($Candidate.decision_status -eq "eligible_for_owner_decision")
  $flags_ok = (@($Candidate.missing_flags).Count -eq 0)
  $source_ok = ($Candidate.effective_source -eq "legacy_fallback" -and $Candidate.fallback_source -eq "legacy_fallback")
  $live_candidate_ok = (
    $null -ne $Candidate.live_adapter_candidate -and
    $Candidate.live_adapter_candidate.candidate_mode -eq "noop_boundary_only" -and
    $Candidate.live_adapter_candidate.effective_source -eq "legacy_fallback" -and
    $Candidate.live_adapter_candidate.will_consume_local_bank_live -eq $false
  )
  $contract_ok = (@($Candidate.minimum_contract_for_first_real_live_trial).Count -ge 8)
  $not_live_ok = (
    @($Candidate.explicit_not_live_yet | Where-Object { $_ -match "no-op only" }).Count -gt 0 -and
    @($Candidate.explicit_not_live_yet | Where-Object { $_ -match "legacy_fallback" }).Count -gt 0
  )
  $path_policy_ok = ($Candidate.path_policy -eq "no_user_provided_filesystem_root")
  $no_consume_ok = ($Candidate.will_consume_local_bank_live -eq $false)
  $no_start_live_ok = ($Candidate.will_start_live_session -eq $false)
  $no_replace_source_ok = ($Candidate.will_replace_effective_source -eq $false)
  $no_progress_persist_ok = ($Candidate.will_persist_progress -eq $false)
  $no_session_persist_ok = ($Candidate.will_persist_session -eq $false)
  $no_attempt_persist_ok = ($Candidate.will_persist_attempts -eq $false)
  $no_progress_update_ok = ($Candidate.will_update_progress -eq $false)
  $no_live_score_ok = ($Candidate.will_score_live_session -eq $false)
  $no_ui_ok = ($Candidate.will_modify_exam_prep_ui -eq $false)
  $no_weak_ok = ($Candidate.will_modify_weak_review -eq $false)
  $no_live_replace_ok = ($Candidate.will_replace_live_study_session -eq $false)
  $no_legacy_replace_ok = ($Candidate.will_replace_legacy_generator -eq $false)
  $no_live_consumption_ok = ($Candidate.will_enable_live_consumption -eq $false)
  $no_cloud_ok = ($Candidate.requires_cloud_or_api -eq $false)

  Write-Host "version_ok $version_ok"
  Write-Host "mode_ok $mode_ok"
  Write-Host "fallback_ok $fallback_ok"
  Write-Host "candidate_ok $candidate_ok"
  Write-Host "adapter_flag_ok $adapter_flag_ok"
  Write-Host "decision_ok $decision_ok"
  Write-Host "flags_ok $flags_ok"
  Write-Host "source_ok $source_ok"
  Write-Host "live_candidate_ok $live_candidate_ok"
  Write-Host "contract_ok $contract_ok"
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

  if (-not ($version_ok -and $mode_ok -and $fallback_ok -and $candidate_ok -and $adapter_flag_ok -and $decision_ok -and $flags_ok -and $source_ok -and $live_candidate_ok -and $contract_ok -and $not_live_ok -and $path_policy_ok -and $no_consume_ok -and $no_start_live_ok -and $no_replace_source_ok -and $no_progress_persist_ok -and $no_session_persist_ok -and $no_attempt_persist_ok -and $no_progress_update_ok -and $no_live_score_ok -and $no_ui_ok -and $no_weak_ok -and $no_live_replace_ok -and $no_legacy_replace_ok -and $no_live_consumption_ok -and $no_cloud_ok)) {
    throw "LOCAL BANK LIVE CONSUMPTION ADAPTER NO-OP BOUNDARY CHECK v0.4.71 FAILED"
  }

  Write-Host "LOCAL BANK LIVE CONSUMPTION ADAPTER NO-OP BOUNDARY CHECK v0.4.71 PASS"
} finally {
  foreach ($name in $flagNames) {
    if ($null -eq $oldFlags[$name]) {
      Remove-Item "Env:\$name" -ErrorAction SilentlyContinue
    } else {
      [Environment]::SetEnvironmentVariable($name, [string]$oldFlags[$name], "Process")
    }
  }
}
