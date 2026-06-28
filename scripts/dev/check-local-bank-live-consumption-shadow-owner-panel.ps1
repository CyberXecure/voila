param()

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

Write-Host "=== LOCAL BANK LIVE CONSUMPTION SHADOW OWNER PANEL CHECK v0.4.74 ==="

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

  $PanelUrl = "http://127.0.0.1:8787/exam-prep/local-bank/live-consumption-shadow-panel"

  $DisabledResponse = Invoke-WebRequest -UseBasicParsing -Uri $PanelUrl -TimeoutSec 15
  Write-Host "disabled_shadow_owner_panel_status_code $($DisabledResponse.StatusCode)"
  Write-Host $DisabledResponse.Content

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
  if (-not $healthOk) { throw "Voila health endpoint did not become ready with shadow owner panel flags." }

  $EnabledResponse = Invoke-WebRequest -UseBasicParsing -Uri $PanelUrl -TimeoutSec 15
  Write-Host "enabled_shadow_owner_panel_status_code $($EnabledResponse.StatusCode)"
  Write-Host $EnabledResponse.Content

  $ReportUrl = "http://127.0.0.1:8787/exam-prep/local-bank/live-consumption-shadow-report"
  $ReportResponse = Invoke-WebRequest -UseBasicParsing -Uri $ReportUrl -TimeoutSec 30
  $Report = $ReportResponse.Content | ConvertFrom-Json

  $disabled_status_ok = ($DisabledResponse.StatusCode -eq 200 -and $DisabledResponse.Content -match 'data-shadow-owner-panel-status="disabled"')
  $enabled_status_ok = ($EnabledResponse.StatusCode -eq 200 -and $EnabledResponse.Content -match 'data-shadow-owner-panel-status="enabled"')
  $version_ok = ($DisabledResponse.Content -match 'data-shadow-owner-panel-version="v0.4.74"' -and $EnabledResponse.Content -match 'data-shadow-owner-panel-version="v0.4.74"')
  $noindex_ok = ($EnabledResponse.Content -match 'noindex,nofollow')
  $internal_ok = ($EnabledResponse.Content -match 'internal_hidden_owner_panel')
  $fetch_ok = ($EnabledResponse.Content -match '/exam-prep/local-bank/live-consumption-shadow-report')
  $safe_dom_ok = (
    $EnabledResponse.Content -match 'createElement' -and
    $EnabledResponse.Content -match 'textContent' -and
    $EnabledResponse.Content -match 'replaceChildren' -and
    $EnabledResponse.Content -notmatch 'innerHTML'
  )
  $summary_ok = (
    $EnabledResponse.Content -match 'Shadow summary' -and
    $EnabledResponse.Content -match 'Coverage comparison' -and
    $EnabledResponse.Content -match 'Selected shadow question metadata'
  )
  $report_ok = (
    $Report.status -eq "ok" -and
    $Report.selector_status -eq "shadow_selection_ready" -and
    $Report.effective_source -eq "legacy_fallback" -and
    $Report.shadow_source -eq "local_exercise_bank_adapter" -and
    [int]$Report.shadow_candidate_count -gt 0
  )
  $forbidden_panel_tokens = @(
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
  $leaked_panel_tokens = @()
  foreach ($pattern in $forbidden_panel_tokens) {
    if ($EnabledResponse.Content -match $pattern) {
      $leaked_panel_tokens += $pattern
    }
  }
  $no_leaks_ok = (@($leaked_panel_tokens).Count -eq 0)
  $no_public_link_ok = ($EnabledResponse.Content -match 'data-has-public-ui-link="false"')
  $no_consume_ok = ($EnabledResponse.Content -match 'data-will-consume-local-bank-live="false"')
  $no_deliver_ok = ($EnabledResponse.Content -match 'data-will-deliver-shadow-questions-live="false"')
  $no_start_live_ok = ($EnabledResponse.Content -match 'data-will-start-live-session="false"')
  $no_replace_source_ok = ($EnabledResponse.Content -match 'data-will-replace-effective-source="false"')
  $no_persist_ok = ($EnabledResponse.Content -match 'data-will-persist-attempts="false"')
  $no_progress_ok = ($EnabledResponse.Content -match 'data-will-update-progress="false"')
  $no_score_ok = ($EnabledResponse.Content -match 'data-will-score-live-session="false"')

  Write-Host "disabled_status_ok $disabled_status_ok"
  Write-Host "enabled_status_ok $enabled_status_ok"
  Write-Host "version_ok $version_ok"
  Write-Host "noindex_ok $noindex_ok"
  Write-Host "internal_ok $internal_ok"
  Write-Host "fetch_ok $fetch_ok"
  Write-Host "safe_dom_ok $safe_dom_ok"
  Write-Host "summary_ok $summary_ok"
  Write-Host "report_ok $report_ok"
  Write-Host "no_leaks_ok $no_leaks_ok"
  Write-Host "no_public_link_ok $no_public_link_ok"
  Write-Host "no_consume_ok $no_consume_ok"
  Write-Host "no_deliver_ok $no_deliver_ok"
  Write-Host "no_start_live_ok $no_start_live_ok"
  Write-Host "no_replace_source_ok $no_replace_source_ok"
  Write-Host "no_persist_ok $no_persist_ok"
  Write-Host "no_progress_ok $no_progress_ok"
  Write-Host "no_score_ok $no_score_ok"

  if (-not ($disabled_status_ok -and $enabled_status_ok -and $version_ok -and $noindex_ok -and $internal_ok -and $fetch_ok -and $safe_dom_ok -and $summary_ok -and $report_ok -and $no_leaks_ok -and $no_public_link_ok -and $no_consume_ok -and $no_deliver_ok -and $no_start_live_ok -and $no_replace_source_ok -and $no_persist_ok -and $no_progress_ok -and $no_score_ok)) {
    throw "LOCAL BANK LIVE CONSUMPTION SHADOW OWNER PANEL CHECK v0.4.74 FAILED"
  }

  Write-Host "LOCAL BANK LIVE CONSUMPTION SHADOW OWNER PANEL CHECK v0.4.74 PASS"
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
