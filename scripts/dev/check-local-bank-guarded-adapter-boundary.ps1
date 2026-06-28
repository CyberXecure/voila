param()

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

Write-Host "=== LOCAL BANK GUARDED ADAPTER BOUNDARY CHECK v0.4.62 ==="

$ProjectRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
Set-Location $ProjectRoot

$oldFlag = $env:VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_GUARDED_LIVE_TRIAL

try {
  Remove-Item Env:\VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_GUARDED_LIVE_TRIAL -ErrorAction SilentlyContinue

  $FallbackRaw = python .\services\api\exam_prep_local_bank_guarded_adapter_boundary.py --course-id v062-smoke --skill-id local_concept_001_functiile --limit 5 --strict-fallback
  if ($LASTEXITCODE -ne 0) { throw "guarded adapter fallback check failed" }
  Write-Host $FallbackRaw

  $env:VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_GUARDED_LIVE_TRIAL = "1"

  $CandidateRaw = python .\services\api\exam_prep_local_bank_guarded_adapter_boundary.py --course-id v062-smoke --skill-id local_concept_001_functiile --limit 5 --strict-candidate
  if ($LASTEXITCODE -ne 0) { throw "guarded adapter candidate check failed" }
  Write-Host $CandidateRaw

  $Fallback = $FallbackRaw | ConvertFrom-Json
  $Candidate = $CandidateRaw | ConvertFrom-Json

  $version_ok = ($Fallback.adapter_boundary_version -eq "v0.4.62" -and $Candidate.adapter_boundary_version -eq "v0.4.62")
  $mode_ok = ($Fallback.mode -eq "guarded_live_trial_adapter_boundary" -and $Candidate.mode -eq "guarded_live_trial_adapter_boundary")
  $fallback_status_ok = ($Fallback.boundary_status -eq "legacy_fallback_only" -and $Fallback.local_source_candidate_available -eq $false)
  $candidate_status_ok = ($Candidate.boundary_status -eq "local_source_candidate_available" -and $Candidate.local_source_candidate_available -eq $true)
  $trial_ok = ($Candidate.trial_status -eq "guarded_trial_plan_ready")
  $candidate_ok = (
    $Candidate.local_source_candidate.candidate_source -eq "local_exercise_bank_adapter" -and
    $Candidate.local_source_candidate.adapter_mode -eq "guarded_boundary_candidate" -and
    $Candidate.local_source_candidate.will_start_live_session -eq $false
  )
  $contract_ok = (
    $Candidate.adapter_contract.future_live_adapter_must_check_flag -eq $true -and
    $Candidate.adapter_contract.future_live_adapter_must_check_readiness -eq $true -and
    $Candidate.adapter_contract.future_live_adapter_must_keep_legacy_fallback -eq $true
  )
  $path_policy_ok = ($Candidate.path_policy -eq "no_user_provided_filesystem_root" -and $Fallback.path_policy -eq "no_user_provided_filesystem_root")
  $no_start_live_ok = ($Candidate.will_start_live_session -eq $false -and $Fallback.will_start_live_session -eq $false)
  $no_progress_persist_ok = ($Candidate.will_persist_progress -eq $false -and $Fallback.will_persist_progress -eq $false)
  $no_session_persist_ok = ($Candidate.will_persist_session -eq $false -and $Fallback.will_persist_session -eq $false)
  $no_attempt_persist_ok = ($Candidate.will_persist_attempts -eq $false -and $Fallback.will_persist_attempts -eq $false)
  $no_progress_update_ok = ($Candidate.will_update_progress -eq $false -and $Fallback.will_update_progress -eq $false)
  $no_live_score_ok = ($Candidate.will_score_live_session -eq $false -and $Fallback.will_score_live_session -eq $false)
  $no_ui_ok = ($Candidate.will_modify_exam_prep_ui -eq $false -and $Fallback.will_modify_exam_prep_ui -eq $false)
  $no_weak_ok = ($Candidate.will_modify_weak_review -eq $false -and $Fallback.will_modify_weak_review -eq $false)
  $no_live_replace_ok = ($Candidate.will_replace_live_study_session -eq $false -and $Fallback.will_replace_live_study_session -eq $false)
  $no_legacy_replace_ok = ($Candidate.will_replace_legacy_generator -eq $false -and $Fallback.will_replace_legacy_generator -eq $false)
  $no_live_consumption_ok = ($Candidate.will_enable_live_consumption -eq $false -and $Fallback.will_enable_live_consumption -eq $false)
  $no_cloud_ok = ($Candidate.requires_cloud_or_api -eq $false -and $Fallback.requires_cloud_or_api -eq $false)

  Write-Host "version_ok $version_ok"
  Write-Host "mode_ok $mode_ok"
  Write-Host "fallback_status_ok $fallback_status_ok"
  Write-Host "candidate_status_ok $candidate_status_ok"
  Write-Host "trial_ok $trial_ok"
  Write-Host "candidate_ok $candidate_ok"
  Write-Host "contract_ok $contract_ok"
  Write-Host "path_policy_ok $path_policy_ok"
  Write-Host "no_start_live_ok $no_start_live_ok"
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

  if (-not ($version_ok -and $mode_ok -and $fallback_status_ok -and $candidate_status_ok -and $trial_ok -and $candidate_ok -and $contract_ok -and $path_policy_ok -and $no_start_live_ok -and $no_progress_persist_ok -and $no_session_persist_ok -and $no_attempt_persist_ok -and $no_progress_update_ok -and $no_live_score_ok -and $no_ui_ok -and $no_weak_ok -and $no_live_replace_ok -and $no_legacy_replace_ok -and $no_live_consumption_ok -and $no_cloud_ok)) {
    throw "LOCAL BANK GUARDED ADAPTER BOUNDARY CHECK v0.4.62 FAILED"
  }

  Write-Host "LOCAL BANK GUARDED ADAPTER BOUNDARY CHECK v0.4.62 PASS"
} finally {
  if ($null -eq $oldFlag) {
    Remove-Item Env:\VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_GUARDED_LIVE_TRIAL -ErrorAction SilentlyContinue
  } else {
    $env:VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_GUARDED_LIVE_TRIAL = $oldFlag
  }
}

