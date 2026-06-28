param()

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

Write-Host "=== LOCAL BANK GUARDED TRIAL ROUTE SMOKE CHECK v0.4.64 ==="

$ProjectRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
Set-Location $ProjectRoot

$oldSmoke = $env:VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_GUARDED_TRIAL_SMOKE_ROUTE
$oldTrial = $env:VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_GUARDED_LIVE_TRIAL

try {
  & .\scripts\dev\stop-voila.ps1 | Out-Host

  Remove-Item Env:\VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_GUARDED_TRIAL_SMOKE_ROUTE -ErrorAction SilentlyContinue
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
  $Url = "http://127.0.0.1:8787/exam-prep/local-bank/guarded-trial-smoke?course_id=v064-smoke&skill_id=$Skill&limit=5"

  $DisabledResponse = Invoke-WebRequest -UseBasicParsing -Uri $Url -TimeoutSec 15
  Write-Host "disabled_status_code $($DisabledResponse.StatusCode)"
  Write-Host $DisabledResponse.Content

  $Disabled = $DisabledResponse.Content | ConvertFrom-Json

  & .\scripts\dev\stop-voila.ps1 | Out-Host

  $env:VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_GUARDED_TRIAL_SMOKE_ROUTE = "1"
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
  $version_ok = ($Disabled.route_version -eq "v0.4.64" -and $Enabled.route_version -eq "v0.4.64")
  $mode_ok = ($Enabled.mode -eq "guarded_trial_smoke_route")
  $json_only_ok = ($Enabled.route_kind -eq "internal_json_only")
  $no_public_link_ok = ($Enabled.has_public_ui_link -eq $false -and $Disabled.has_public_ui_link -eq $false)
  $hook_ok = ($Enabled.hook.noop_hook_version -eq "v0.4.63")
  $candidate_ok = (
    $Enabled.hook_status -eq "local_source_candidate_reported_noop" -and
    $Enabled.effective_source -eq "legacy_fallback" -and
    $Enabled.reported_candidate_available -eq $true
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
  Write-Host "hook_ok $hook_ok"
  Write-Host "candidate_ok $candidate_ok"
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

  if (-not ($disabled_status_ok -and $enabled_status_ok -and $version_ok -and $mode_ok -and $json_only_ok -and $no_public_link_ok -and $hook_ok -and $candidate_ok -and $path_policy_ok -and $no_consume_ok -and $no_start_live_ok -and $no_replace_source_ok -and $no_progress_persist_ok -and $no_session_persist_ok -and $no_attempt_persist_ok -and $no_progress_update_ok -and $no_live_score_ok -and $no_ui_ok -and $no_weak_ok -and $no_live_replace_ok -and $no_legacy_replace_ok -and $no_live_consumption_ok -and $no_cloud_ok)) {
    throw "LOCAL BANK GUARDED TRIAL ROUTE SMOKE CHECK v0.4.64 FAILED"
  }

  Write-Host "LOCAL BANK GUARDED TRIAL ROUTE SMOKE CHECK v0.4.64 PASS"
} finally {
  & .\scripts\dev\stop-voila.ps1 | Out-Host

  if ($null -eq $oldSmoke) {
    Remove-Item Env:\VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_GUARDED_TRIAL_SMOKE_ROUTE -ErrorAction SilentlyContinue
  } else {
    $env:VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_GUARDED_TRIAL_SMOKE_ROUTE = $oldSmoke
  }

  if ($null -eq $oldTrial) {
    Remove-Item Env:\VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_GUARDED_LIVE_TRIAL -ErrorAction SilentlyContinue
  } else {
    $env:VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_GUARDED_LIVE_TRIAL = $oldTrial
  }
}

