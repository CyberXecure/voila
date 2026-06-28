param()

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

Write-Host "=== LOCAL BANK NO-OP STUDY SESSION HOOK CHECK v0.4.63 ==="

$ProjectRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
Set-Location $ProjectRoot

$oldFlag = $env:VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_GUARDED_LIVE_TRIAL

try {
  Remove-Item Env:\VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_GUARDED_LIVE_TRIAL -ErrorAction SilentlyContinue

  $LegacyRaw = python .\services\api\exam_prep_local_bank_noop_study_session_hook.py --course-id v063-smoke --skill-id local_concept_001_functiile --limit 5 --strict-legacy
  if ($LASTEXITCODE -ne 0) { throw "no-op hook legacy check failed" }
  Write-Host $LegacyRaw

  $env:VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_GUARDED_LIVE_TRIAL = "1"

  $CandidateRaw = python .\services\api\exam_prep_local_bank_noop_study_session_hook.py --course-id v063-smoke --skill-id local_concept_001_functiile --limit 5 --strict-candidate-report
  if ($LASTEXITCODE -ne 0) { throw "no-op hook candidate-report check failed" }
  Write-Host $CandidateRaw

  $Legacy = $LegacyRaw | ConvertFrom-Json
  $Candidate = $CandidateRaw | ConvertFrom-Json

  $version_ok = ($Legacy.noop_hook_version -eq "v0.4.63" -and $Candidate.noop_hook_version -eq "v0.4.63")
  $mode_ok = ($Legacy.mode -eq "guarded_live_trial_noop_study_session_hook" -and $Candidate.mode -eq "guarded_live_trial_noop_study_session_hook")
  $legacy_status_ok = ($Legacy.hook_status -eq "legacy_path_unchanged" -and $Legacy.effective_source -eq "legacy_fallback")
  $candidate_status_ok = ($Candidate.hook_status -eq "local_source_candidate_reported_noop" -and $Candidate.reported_candidate_available -eq $true)
  $candidate_ok = ($Candidate.reported_local_source_candidate.candidate_source -eq "local_exercise_bank_adapter")
  $contract_ok = (
    $Candidate.study_session_contract.legacy_path_unchanged -eq $true -and
    $Candidate.study_session_contract.local_candidate_report_only -eq $true -and
    $Candidate.study_session_contract.future_live_hook_must_keep_legacy_fallback -eq $true
  )
  $boundary_ok = ($Candidate.adapter_boundary.adapter_boundary_version -eq "v0.4.62")
  $path_policy_ok = ($Candidate.path_policy -eq "no_user_provided_filesystem_root" -and $Legacy.path_policy -eq "no_user_provided_filesystem_root")
  $no_consume_ok = ($Candidate.will_consume_local_bank_live -eq $false -and $Legacy.will_consume_local_bank_live -eq $false)
  $no_start_live_ok = ($Candidate.will_start_live_session -eq $false -and $Legacy.will_start_live_session -eq $false)
  $no_replace_source_ok = ($Candidate.will_replace_effective_source -eq $false -and $Legacy.will_replace_effective_source -eq $false)
  $no_progress_persist_ok = ($Candidate.will_persist_progress -eq $false -and $Legacy.will_persist_progress -eq $false)
  $no_session_persist_ok = ($Candidate.will_persist_session -eq $false -and $Legacy.will_persist_session -eq $false)
  $no_attempt_persist_ok = ($Candidate.will_persist_attempts -eq $false -and $Legacy.will_persist_attempts -eq $false)
  $no_progress_update_ok = ($Candidate.will_update_progress -eq $false -and $Legacy.will_update_progress -eq $false)
  $no_live_score_ok = ($Candidate.will_score_live_session -eq $false -and $Legacy.will_score_live_session -eq $false)
  $no_ui_ok = ($Candidate.will_modify_exam_prep_ui -eq $false -and $Legacy.will_modify_exam_prep_ui -eq $false)
  $no_weak_ok = ($Candidate.will_modify_weak_review -eq $false -and $Legacy.will_modify_weak_review -eq $false)
  $no_live_replace_ok = ($Candidate.will_replace_live_study_session -eq $false -and $Legacy.will_replace_live_study_session -eq $false)
  $no_legacy_replace_ok = ($Candidate.will_replace_legacy_generator -eq $false -and $Legacy.will_replace_legacy_generator -eq $false)
  $no_live_consumption_ok = ($Candidate.will_enable_live_consumption -eq $false -and $Legacy.will_enable_live_consumption -eq $false)
  $no_cloud_ok = ($Candidate.requires_cloud_or_api -eq $false -and $Legacy.requires_cloud_or_api -eq $false)

  Write-Host "version_ok $version_ok"
  Write-Host "mode_ok $mode_ok"
  Write-Host "legacy_status_ok $legacy_status_ok"
  Write-Host "candidate_status_ok $candidate_status_ok"
  Write-Host "candidate_ok $candidate_ok"
  Write-Host "contract_ok $contract_ok"
  Write-Host "boundary_ok $boundary_ok"
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

  if (-not ($version_ok -and $mode_ok -and $legacy_status_ok -and $candidate_status_ok -and $candidate_ok -and $contract_ok -and $boundary_ok -and $path_policy_ok -and $no_consume_ok -and $no_start_live_ok -and $no_replace_source_ok -and $no_progress_persist_ok -and $no_session_persist_ok -and $no_attempt_persist_ok -and $no_progress_update_ok -and $no_live_score_ok -and $no_ui_ok -and $no_weak_ok -and $no_live_replace_ok -and $no_legacy_replace_ok -and $no_live_consumption_ok -and $no_cloud_ok)) {
    throw "LOCAL BANK NO-OP STUDY SESSION HOOK CHECK v0.4.63 FAILED"
  }

  Write-Host "LOCAL BANK NO-OP STUDY SESSION HOOK CHECK v0.4.63 PASS"
} finally {
  if ($null -eq $oldFlag) {
    Remove-Item Env:\VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_GUARDED_LIVE_TRIAL -ErrorAction SilentlyContinue
  } else {
    $env:VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_GUARDED_LIVE_TRIAL = $oldFlag
  }
}

