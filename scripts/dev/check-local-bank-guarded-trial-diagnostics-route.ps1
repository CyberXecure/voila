param()

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

Write-Host "=== LOCAL BANK GUARDED TRIAL DIAGNOSTICS ROUTE CHECK v0.4.65 ==="

$ProjectRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
Set-Location $ProjectRoot

$oldDiagnostics = $env:VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_GUARDED_TRIAL_DIAGNOSTICS_ROUTE
$oldTrial = $env:VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_GUARDED_LIVE_TRIAL

try {
  & .\scripts\dev\stop-voila.ps1 | Out-Host

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
  $Url = "http://127.0.0.1:8787/exam-prep/local-bank/guarded-trial-diagnostics?course_id=v065-smoke&skill_id=$Skill&limit=5"

  $DisabledResponse = Invoke-WebRequest -UseBasicParsing -Uri $Url -TimeoutSec 15
  Write-Host "disabled_status_code $($DisabledResponse.StatusCode)"
  Write-Host $DisabledResponse.Content

  $Disabled = $DisabledResponse.Content | ConvertFrom-Json

  & .\scripts\dev\stop-voila.ps1 | Out-Host

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
  if (-not $healthOk) { throw "Voila health endpoint did not become ready with flags." }

  $EnabledResponse = Invoke-WebRequest -UseBasicParsing -Uri $Url -TimeoutSec 30
  Write-Host "enabled_status_code $($EnabledResponse.StatusCode)"
  Write-Host $EnabledResponse.Content

  $Enabled = $EnabledResponse.Content | ConvertFrom-Json

  $disabled_status_ok = ($DisabledResponse.StatusCode -eq 200 -and $Disabled.status -eq "disabled")
  $enabled_status_ok = ($EnabledResponse.StatusCode -eq 200 -and $Enabled.status -eq "ok")
  $version_ok = ($Disabled.diagnostics_route_version -eq "v0.4.65" -and $Enabled.diagnostics_route_version -eq "v0.4.65")
  $mode_ok = ($Enabled.mode -eq "guarded_trial_diagnostics_report")
  $json_only_ok = ($Enabled.route_kind -eq "internal_json_only")
  $no_public_link_ok = ($Enabled.has_public_ui_link -eq $false -and $Disabled.has_public_ui_link -eq $false)
  $summary_ok = (
    $Enabled.summary.diagnostics_status -eq "ok" -and
    $Enabled.summary.hook_status -eq "local_source_candidate_reported_noop" -and
    $Enabled.summary.boundary_status -eq "local_source_candidate_available" -and
    $Enabled.summary.readiness_status -eq "ready_for_guarded_live_trial" -and
    $Enabled.summary.candidate_available -eq $true -and
    $Enabled.summary.effective_source -eq "legacy_fallback" -and
    $Enabled.summary.safety_ok -eq $true
  )
  $versions_ok = (
    $Enabled.summary.versions.noop_hook_version -eq "v0.4.63" -and
    $Enabled.summary.versions.adapter_boundary_version -eq "v0.4.62" -and
    $Enabled.summary.versions.guarded_trial_version -eq "v0.4.61" -and
    $Enabled.summary.versions.readiness_report_version -eq "v0.4.60"
  )
  $path_policy_ok = ($Enabled.path_policy -eq "no_user_provided_filesystem_root" -and $Disabled.path_policy -eq "no_user_provided_filesystem_root")
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
  Write-Host "enabled_status_ok $enabled_status_ok"
  Write-Host "version_ok $version_ok"
  Write-Host "mode_ok $mode_ok"
  Write-Host "json_only_ok $json_only_ok"
  Write-Host "no_public_link_ok $no_public_link_ok"
  Write-Host "summary_ok $summary_ok"
  Write-Host "versions_ok $versions_ok"
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

  if (-not ($disabled_status_ok -and $enabled_status_ok -and $version_ok -and $mode_ok -and $json_only_ok -and $no_public_link_ok -and $summary_ok -and $versions_ok -and $path_policy_ok -and $no_consume_ok -and $no_start_live_ok -and $no_replace_source_ok -and $no_progress_persist_ok -and $no_session_persist_ok -and $no_attempt_persist_ok -and $no_progress_update_ok -and $no_live_score_ok -and $no_ui_ok -and $no_weak_ok -and $no_live_replace_ok -and $no_legacy_replace_ok -and $no_live_consumption_ok -and $no_cloud_ok)) {
    throw "LOCAL BANK GUARDED TRIAL DIAGNOSTICS ROUTE CHECK v0.4.65 FAILED"
  }

  Write-Host "LOCAL BANK GUARDED TRIAL DIAGNOSTICS ROUTE CHECK v0.4.65 PASS"
} finally {
  & .\scripts\dev\stop-voila.ps1 | Out-Host

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

