param()

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

Write-Host "=== LOCAL BANK GUARDED TRIAL CANDIDATE QUESTION PREVIEW ROUTE CHECK v0.4.66 ==="

$ProjectRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
Set-Location $ProjectRoot

$oldCandidate = $env:VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_GUARDED_TRIAL_CANDIDATES_ROUTE
$oldDiagnostics = $env:VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_GUARDED_TRIAL_DIAGNOSTICS_ROUTE
$oldTrial = $env:VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_GUARDED_LIVE_TRIAL

try {
  & .\scripts\dev\stop-voila.ps1 | Out-Host

  Remove-Item Env:\VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_GUARDED_TRIAL_CANDIDATES_ROUTE -ErrorAction SilentlyContinue
  Remove-Item Env:\VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_GUARDED_TRIAL_DIAGNOSTICS_ROUTE -ErrorAction SilentlyContinue
  Remove-Item Env:\VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_GUARDED_LIVE_TRIAL -ErrorAction SilentlyContinue

  & .\scripts\dev\start-voila.ps1 -Silent | Out-Host

  $healthOk = $false
  for ($i = 0; $i -lt 30; $i++) {
    try {
      $health = Invoke-WebRequest -UseBasicParsing -Uri "http://127.0.0.1:8787/health" -TimeoutSec 2
      if ($health.StatusCode -eq 200) { $healthOk = $true; break }
    } catch {
      Start-Sleep -Seconds 1
    }
  }
  if (-not $healthOk) { throw "Voila health endpoint did not become ready." }

  $Skill = [uri]::EscapeDataString("local_concept_001_functiile")
  $Url = "http://127.0.0.1:8787/exam-prep/local-bank/guarded-trial-candidates?course_id=v066-smoke&skill_id=$Skill&limit=5"

  $DisabledResponse = Invoke-WebRequest -UseBasicParsing -Uri $Url -TimeoutSec 15
  Write-Host "disabled_status_code $($DisabledResponse.StatusCode)"
  Write-Host $DisabledResponse.Content

  $Disabled = $DisabledResponse.Content | ConvertFrom-Json

  & .\scripts\dev\stop-voila.ps1 | Out-Host

  $env:VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_GUARDED_TRIAL_CANDIDATES_ROUTE = "1"
  $env:VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_GUARDED_LIVE_TRIAL = "1"

  & .\scripts\dev\start-voila.ps1 -Silent | Out-Host

  $healthOk = $false
  for ($i = 0; $i -lt 30; $i++) {
    try {
      $health = Invoke-WebRequest -UseBasicParsing -Uri "http://127.0.0.1:8787/health" -TimeoutSec 2
      if ($health.StatusCode -eq 200) { $healthOk = $true; break }
    } catch {
      Start-Sleep -Seconds 1
    }
  }
  if (-not $healthOk) { throw "Voila health endpoint did not become ready with candidate flag only." }

  $BlockedResponse = Invoke-WebRequest -UseBasicParsing -Uri $Url -TimeoutSec 15
  Write-Host "blocked_status_code $($BlockedResponse.StatusCode)"
  Write-Host $BlockedResponse.Content

  $Blocked = $BlockedResponse.Content | ConvertFrom-Json

  & .\scripts\dev\stop-voila.ps1 | Out-Host

  $env:VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_GUARDED_TRIAL_CANDIDATES_ROUTE = "1"
  $env:VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_GUARDED_TRIAL_DIAGNOSTICS_ROUTE = "1"
  $env:VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_GUARDED_LIVE_TRIAL = "1"

  & .\scripts\dev\start-voila.ps1 -Silent | Out-Host

  $healthOk = $false
  for ($i = 0; $i -lt 30; $i++) {
    try {
      $health = Invoke-WebRequest -UseBasicParsing -Uri "http://127.0.0.1:8787/health" -TimeoutSec 2
      if ($health.StatusCode -eq 200) { $healthOk = $true; break }
    } catch {
      Start-Sleep -Seconds 1
    }
  }
  if (-not $healthOk) { throw "Voila health endpoint did not become ready with all flags." }

  $EnabledResponse = Invoke-WebRequest -UseBasicParsing -Uri $Url -TimeoutSec 30
  Write-Host "enabled_status_code $($EnabledResponse.StatusCode)"
  Write-Host $EnabledResponse.Content

  $Enabled = $EnabledResponse.Content | ConvertFrom-Json

  $disabled_status_ok = ($DisabledResponse.StatusCode -eq 200 -and $Disabled.status -eq "disabled")
  $blocked_status_ok = ($BlockedResponse.StatusCode -eq 200 -and $Blocked.status -eq "blocked" -and $Blocked.candidate_status -eq "diagnostics_route_flag_required")
  $enabled_status_ok = ($EnabledResponse.StatusCode -eq 200 -and $Enabled.status -eq "ok")
  $version_ok = ($Disabled.candidate_route_version -eq "v0.4.66" -and $Enabled.candidate_route_version -eq "v0.4.66")
  $mode_ok = ($Enabled.mode -eq "guarded_trial_candidate_question_preview")
  $json_only_ok = ($Enabled.route_kind -eq "internal_json_only")
  $no_public_link_ok = ($Enabled.has_public_ui_link -eq $false -and $Disabled.has_public_ui_link -eq $false)
  $answer_hidden_ok = ($Enabled.answers_exposed -eq $false -and $Enabled.explanations_exposed -eq $false)
  $candidate_status_ok = ($Enabled.candidate_status -eq "candidate_questions_preview_ready")
  $chain_ok = (
    $Enabled.hook_status -eq "local_source_candidate_reported_noop" -and
    $Enabled.boundary_status -eq "local_source_candidate_available" -and
    $Enabled.readiness_status -eq "ready_for_guarded_live_trial" -and
    $Enabled.effective_source -eq "legacy_fallback" -and
    $Enabled.reported_candidate_available -eq $true
  )
  $questions_count_ok = ([int]$Enabled.candidate_question_count -gt 0 -and @($Enabled.candidate_questions).Count -eq [int]$Enabled.candidate_question_count)
  $first = $Enabled.candidate_questions[0]
  $question_shape_ok = (
    [string]$first.question_id -ne "" -and
    [string]$first.question_type -ne "" -and
    [string]$first.skill_id -eq "local_concept_001_functiile" -and
    [string]$first.question -ne "" -and
    $first.answer_preview_hidden -eq $true -and
    $first.explanation_preview_hidden -eq $true
  )
  $leaked_keys = @()
  foreach ($q in @($Enabled.candidate_questions)) {
    $names = @($q.PSObject.Properties.Name)
    foreach ($bad in @("correct_answer_preview", "correct_answer", "explanation_preview", "explanation")) {
      if ($names -contains $bad) { $leaked_keys += $bad }
    }
  }
  $no_answers_leaked_ok = (@($leaked_keys).Count -eq 0)
  $versions_ok = (
    $Enabled.versions.noop_hook_version -eq "v0.4.63" -and
    $Enabled.versions.adapter_boundary_version -eq "v0.4.62" -and
    $Enabled.versions.guarded_trial_version -eq "v0.4.61" -and
    $Enabled.versions.readiness_report_version -eq "v0.4.60"
  )
  $path_policy_ok = ($Enabled.path_policy -eq "no_user_provided_filesystem_root" -and $Disabled.path_policy -eq "no_user_provided_filesystem_root")
  $safety_ok = ($Enabled.safety_ok -eq $true)
  $no_consume_ok = ($Enabled.will_consume_local_bank_live -eq $false -and $Disabled.will_consume_local_bank_live -eq $false)
  $no_start_live_ok = ($Enabled.will_start_live_session -eq $false -and $Disabled.will_start_live_session -eq $false)
  $no_replace_source_ok = ($Enabled.will_replace_effective_source -eq $false -and $Disabled.will_replace_effective_source -eq $false)
  $no_progress_persist_ok = ($Enabled.will_persist_progress -eq $false -and $Disabled.will_persist_progress -eq $false)
  $no_session_persist_ok = ($Enabled.will_persist_session -eq $false -and $Disabled.will_persist_session -eq $false)
  $no_attempt_persist_ok = ($Enabled.will_persist_attempts -eq $false -and $Disabled.will_persist_attempts -eq $false)
  $no_progress_update_ok = ($Enabled.will_update_progress -eq $false -and $Disabled.will_update_progress -eq $false)
  $no_live_score_ok = ($Enabled.will_score_live_session -eq $false -and $Disabled.will_score_live_session -eq $false)
  $no_ui_ok = ($Enabled.will_modify_exam_prep_ui -eq $false -and $Disabled.will_modify_exam_prep_ui -eq $false)
  $no_weak_ok = ($Enabled.will_modify_weak_review -eq $false -and $Disabled.will_modify_weak_review -eq $false)
  $no_live_replace_ok = ($Enabled.will_replace_live_study_session -eq $false -and $Disabled.will_replace_live_study_session -eq $false)
  $no_legacy_replace_ok = ($Enabled.will_replace_legacy_generator -eq $false -and $Disabled.will_replace_legacy_generator -eq $false)
  $no_live_consumption_ok = ($Enabled.will_enable_live_consumption -eq $false -and $Disabled.will_enable_live_consumption -eq $false)
  $no_cloud_ok = ($Enabled.requires_cloud_or_api -eq $false -and $Disabled.requires_cloud_or_api -eq $false)

  Write-Host "disabled_status_ok $disabled_status_ok"
  Write-Host "blocked_status_ok $blocked_status_ok"
  Write-Host "enabled_status_ok $enabled_status_ok"
  Write-Host "version_ok $version_ok"
  Write-Host "mode_ok $mode_ok"
  Write-Host "json_only_ok $json_only_ok"
  Write-Host "no_public_link_ok $no_public_link_ok"
  Write-Host "answer_hidden_ok $answer_hidden_ok"
  Write-Host "candidate_status_ok $candidate_status_ok"
  Write-Host "chain_ok $chain_ok"
  Write-Host "questions_count_ok $questions_count_ok"
  Write-Host "question_shape_ok $question_shape_ok"
  Write-Host "no_answers_leaked_ok $no_answers_leaked_ok"
  Write-Host "versions_ok $versions_ok"
  Write-Host "path_policy_ok $path_policy_ok"
  Write-Host "safety_ok $safety_ok"
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

  if (-not ($disabled_status_ok -and $blocked_status_ok -and $enabled_status_ok -and $version_ok -and $mode_ok -and $json_only_ok -and $no_public_link_ok -and $answer_hidden_ok -and $candidate_status_ok -and $chain_ok -and $questions_count_ok -and $question_shape_ok -and $no_answers_leaked_ok -and $versions_ok -and $path_policy_ok -and $safety_ok -and $no_consume_ok -and $no_start_live_ok -and $no_replace_source_ok -and $no_progress_persist_ok -and $no_session_persist_ok -and $no_attempt_persist_ok -and $no_progress_update_ok -and $no_live_score_ok -and $no_ui_ok -and $no_weak_ok -and $no_live_replace_ok -and $no_legacy_replace_ok -and $no_live_consumption_ok -and $no_cloud_ok)) {
    throw "LOCAL BANK GUARDED TRIAL CANDIDATE QUESTION PREVIEW ROUTE CHECK v0.4.66 FAILED"
  }

  Write-Host "LOCAL BANK GUARDED TRIAL CANDIDATE QUESTION PREVIEW ROUTE CHECK v0.4.66 PASS"
} finally {
  & .\scripts\dev\stop-voila.ps1 | Out-Host

  if ($null -eq $oldCandidate) {
    Remove-Item Env:\VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_GUARDED_TRIAL_CANDIDATES_ROUTE -ErrorAction SilentlyContinue
  } else {
    $env:VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_GUARDED_TRIAL_CANDIDATES_ROUTE = $oldCandidate
  }

  if ($null -eq $oldDiagnostics) {
    Remove-Item Env:\VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_GUARDED_TRIAL_DIAGNOSTICS_ROUTE -ErrorAction SilentlyContinue
  } else {
    $env:VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_GUARDED_TRIAL_DIAGNOSTICS_ROUTE = $oldDiagnostics
  }

  if ($null -eq $oldTrial) {
    Remove-Item Env:\VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_GUARDED_LIVE_TRIAL -ErrorAction SilentlyContinue
  } else {
    $env:VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_GUARDED_LIVE_TRIAL = $oldTrial
  }
}
