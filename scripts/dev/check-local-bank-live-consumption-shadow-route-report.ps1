param()

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

Write-Host "=== LOCAL BANK LIVE CONSUMPTION SHADOW ROUTE REPORT CHECK v0.4.73 ==="

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
  "VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_SHADOW_REPORT_ROUTE"
)

$oldFlags = @{}
foreach ($name in $flagNames) {
  $oldFlags[$name] = [Environment]::GetEnvironmentVariable($name, "Process")
}

try {
  & .\scripts\dev\stop-voila.ps1 | Out-Host

  foreach ($name in $flagNames) {
    Remove-Item "Env:\$name" -ErrorAction SilentlyContinue
  }

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

  $Url = "http://127.0.0.1:8787/exam-prep/local-bank/live-consumption-shadow-report"

  $DisabledResponse = Invoke-WebRequest -UseBasicParsing -Uri $Url -TimeoutSec 15
  Write-Host "disabled_shadow_report_status_code $($DisabledResponse.StatusCode)"
  Write-Host $DisabledResponse.Content

  $Disabled = $DisabledResponse.Content | ConvertFrom-Json

  & .\scripts\dev\stop-voila.ps1 | Out-Host

  foreach ($name in $flagNames) {
    [Environment]::SetEnvironmentVariable($name, "1", "Process")
  }

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
  if (-not $healthOk) { throw "Voila health endpoint did not become ready with shadow report flags." }

  $EnabledResponse = Invoke-WebRequest -UseBasicParsing -Uri $Url -TimeoutSec 30
  Write-Host "enabled_shadow_report_status_code $($EnabledResponse.StatusCode)"
  Write-Host $EnabledResponse.Content

  $Enabled = $EnabledResponse.Content | ConvertFrom-Json
  $serialized = $EnabledResponse.Content

  $disabled_ok = ($DisabledResponse.StatusCode -eq 200 -and $Disabled.status -eq "disabled" -and $Disabled.route_enabled -eq $false)
  $enabled_ok = ($EnabledResponse.StatusCode -eq 200 -and $Enabled.status -eq "ok" -and $Enabled.route_enabled -eq $true)
  $version_ok = ($Disabled.shadow_report_route_version -eq "v0.4.73" -and $Enabled.shadow_report_route_version -eq "v0.4.73")
  $mode_ok = ($Enabled.mode -eq "guarded_live_consumption_shadow_route_report")
  $json_only_ok = ($Enabled.route_kind -eq "internal_json_only")
  $sanitized_ok = (
    $Enabled.report_sanitized -eq $true -and
    $Enabled.raw_snapshots_included -eq $false -and
    $Enabled.answers_exposed -eq $false -and
    $Enabled.explanations_exposed -eq $false
  )
  $selector_ok = (
    $Enabled.selector_status -eq "shadow_selection_ready" -and
    $Enabled.effective_source -eq "legacy_fallback" -and
    $Enabled.shadow_source -eq "local_exercise_bank_adapter"
  )
  $coverage_ok = (
    [int]$Enabled.shadow_candidate_count -gt 0 -and
    [int]$Enabled.coverage_comparison.local_question_type_diversity -ge 2 -and
    [int]$Enabled.coverage_comparison.local_skill_diversity -ge 1
  )
  $profile_ok = (
    $Enabled.local_candidate_profile.available -eq $true -and
    [int]$Enabled.local_candidate_profile.question_count -eq [int]$Enabled.shadow_candidate_count
  )
  $questions_ok = (
    @($Enabled.selected_shadow_questions).Count -eq [int]$Enabled.shadow_candidate_count -and
    $Enabled.selected_shadow_questions[0].will_deliver_live -eq $false -and
    $Enabled.selected_shadow_questions[0].will_save_attempt -eq $false
  )
  $forbidden_key_patterns = @(
    '"correct_answer"\s*:',
    '"correct_answer_preview"\s*:',
    '"explanation"\s*:',
    '"explanation_preview"\s*:',
    '"source_excerpt"\s*:',
    '"adapter_noop_boundary"\s*:',
    '"decision_gate"\s*:',
    '"owner_enablement_checklist"\s*:',
    '"snapshots"\s*:',
    '"selected_questions"\s*:',
    '"dry_run_items"\s*:'
  )
  $leaked_tokens = @()
  foreach ($pattern in $forbidden_key_patterns) {
    if ($serialized -match $pattern) {
      $leaked_tokens += $pattern
    }
  }
  $no_leaks_ok = (@($leaked_tokens).Count -eq 0)
  $path_policy_ok = ($Enabled.path_policy -eq "no_user_provided_filesystem_root")
  $no_public_link_ok = ($Enabled.has_public_ui_link -eq $false)
  $no_consume_ok = ($Enabled.will_consume_local_bank_live -eq $false)
  $no_deliver_ok = ($Enabled.will_deliver_shadow_questions_live -eq $false)
  $no_start_live_ok = ($Enabled.will_start_live_session -eq $false)
  $no_replace_source_ok = ($Enabled.will_replace_effective_source -eq $false)
  $no_progress_persist_ok = ($Enabled.will_persist_progress -eq $false)
  $no_session_persist_ok = ($Enabled.will_persist_session -eq $false)
  $no_attempt_persist_ok = ($Enabled.will_persist_attempts -eq $false)
  $no_progress_update_ok = ($Enabled.will_update_progress -eq $false)
  $no_live_score_ok = ($Enabled.will_score_live_session -eq $false)
  $no_ui_ok = ($Enabled.will_modify_exam_prep_ui -eq $false)
  $no_weak_ok = ($Enabled.will_modify_weak_review -eq $false)
  $no_live_replace_ok = ($Enabled.will_replace_live_study_session -eq $false)
  $no_legacy_replace_ok = ($Enabled.will_replace_legacy_generator -eq $false)
  $no_live_consumption_ok = ($Enabled.will_enable_live_consumption -eq $false)
  $no_cloud_ok = ($Enabled.requires_cloud_or_api -eq $false)

  Write-Host "disabled_ok $disabled_ok"
  Write-Host "enabled_ok $enabled_ok"
  Write-Host "version_ok $version_ok"
  Write-Host "mode_ok $mode_ok"
  Write-Host "json_only_ok $json_only_ok"
  Write-Host "sanitized_ok $sanitized_ok"
  Write-Host "selector_ok $selector_ok"
  Write-Host "coverage_ok $coverage_ok"
  Write-Host "profile_ok $profile_ok"
  Write-Host "questions_ok $questions_ok"
  Write-Host "no_leaks_ok $no_leaks_ok"
  Write-Host "path_policy_ok $path_policy_ok"
  Write-Host "no_public_link_ok $no_public_link_ok"
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

  if (-not ($disabled_ok -and $enabled_ok -and $version_ok -and $mode_ok -and $json_only_ok -and $sanitized_ok -and $selector_ok -and $coverage_ok -and $profile_ok -and $questions_ok -and $no_leaks_ok -and $path_policy_ok -and $no_public_link_ok -and $no_consume_ok -and $no_deliver_ok -and $no_start_live_ok -and $no_replace_source_ok -and $no_progress_persist_ok -and $no_session_persist_ok -and $no_attempt_persist_ok -and $no_progress_update_ok -and $no_live_score_ok -and $no_ui_ok -and $no_weak_ok -and $no_live_replace_ok -and $no_legacy_replace_ok -and $no_live_consumption_ok -and $no_cloud_ok)) {
    throw "LOCAL BANK LIVE CONSUMPTION SHADOW ROUTE REPORT CHECK v0.4.73 FAILED"
  }

  Write-Host "LOCAL BANK LIVE CONSUMPTION SHADOW ROUTE REPORT CHECK v0.4.73 PASS"
} finally {
  & .\scripts\dev\stop-voila.ps1 | Out-Host

  foreach ($name in $flagNames) {
    if ($null -eq $oldFlags[$name]) {
      Remove-Item "Env:\$name" -ErrorAction SilentlyContinue
    } else {
      [Environment]::SetEnvironmentVariable($name, [string]$oldFlags[$name], "Process")
    }
  }
}
