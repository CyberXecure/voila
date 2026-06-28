param()

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

Write-Host "=== LOCAL BANK GUARDED TRIAL CANDIDATE PREVIEW PANEL CHECK v0.4.67 ==="

$ProjectRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
Set-Location $ProjectRoot

$oldPanel = $env:VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_GUARDED_TRIAL_CANDIDATES_PANEL
$oldCandidate = $env:VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_GUARDED_TRIAL_CANDIDATES_ROUTE
$oldDiagnostics = $env:VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_GUARDED_TRIAL_DIAGNOSTICS_ROUTE
$oldTrial = $env:VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_GUARDED_LIVE_TRIAL

try {
  & .\scripts\dev\stop-voila.ps1 | Out-Host

  Remove-Item Env:\VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_GUARDED_TRIAL_CANDIDATES_PANEL -ErrorAction SilentlyContinue
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
  $PanelUrl = "http://127.0.0.1:8787/exam-prep/local-bank/guarded-trial-candidates-panel?course_id=v067-smoke&skill_id=$Skill&limit=5"

  $DisabledResponse = Invoke-WebRequest -UseBasicParsing -Uri $PanelUrl -TimeoutSec 15
  Write-Host "disabled_panel_status_code $($DisabledResponse.StatusCode)"
  Write-Host $DisabledResponse.Content

  & .\scripts\dev\stop-voila.ps1 | Out-Host

  $env:VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_GUARDED_TRIAL_CANDIDATES_PANEL = "1"
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
  if (-not $healthOk) { throw "Voila health endpoint did not become ready with panel flags." }

  $EnabledResponse = Invoke-WebRequest -UseBasicParsing -Uri $PanelUrl -TimeoutSec 15
  Write-Host "enabled_panel_status_code $($EnabledResponse.StatusCode)"
  Write-Host $EnabledResponse.Content

  $CandidateUrl = "http://127.0.0.1:8787/exam-prep/local-bank/guarded-trial-candidates?course_id=v067-smoke&skill_id=$Skill&limit=5"
  $CandidateResponse = Invoke-WebRequest -UseBasicParsing -Uri $CandidateUrl -TimeoutSec 30
  $Candidate = $CandidateResponse.Content | ConvertFrom-Json

  $disabled_status_ok = ($DisabledResponse.StatusCode -eq 200 -and $DisabledResponse.Content -match 'data-panel-status="disabled"')
  $enabled_status_ok = ($EnabledResponse.StatusCode -eq 200 -and $EnabledResponse.Content -match 'data-panel-status="enabled"')
  $version_ok = ($DisabledResponse.Content -match 'data-panel-version="v0.4.67"' -and $EnabledResponse.Content -match 'data-panel-version="v0.4.67"')
  $noindex_ok = ($EnabledResponse.Content -match 'noindex,nofollow')
  $internal_ok = ($EnabledResponse.Content -match 'internal_hidden_panel')
  $fetch_ok = ($EnabledResponse.Content -match '/exam-prep/local-bank/guarded-trial-candidates')
  $legacy_ok = ($EnabledResponse.Content -match 'legacy_fallback')
  $safety_text_ok = (
    $EnabledResponse.Content -match 'No live local-bank consumption' -and
    $EnabledResponse.Content -match 'No attempt, progress, or session persistence' -and
    $EnabledResponse.Content -match 'No live scoring'
  )
  $candidate_route_ok = (
    $Candidate.status -eq "ok" -and
    $Candidate.candidate_status -eq "candidate_questions_preview_ready" -and
    [int]$Candidate.candidate_question_count -gt 0 -and
    $Candidate.answers_exposed -eq $false -and
    $Candidate.explanations_exposed -eq $false
  )
  $forbidden_panel_tokens = @(
    'correct_answer_preview',
    'correct_answer',
    'explanation_preview"',
    'explanation":',
    'explanation =',
    'explanationPreview'
  )
  $leaked_panel_tokens = @()
  foreach ($token in $forbidden_panel_tokens) {
    if ($EnabledResponse.Content -match [regex]::Escape($token)) {
      $leaked_panel_tokens += $token
    }
  }
  $no_answer_text_ok = (@($leaked_panel_tokens).Count -eq 0)
  $no_public_link_ok = ($EnabledResponse.Content -match 'data-has-public-ui-link="false"')
  $no_consume_ok = ($EnabledResponse.Content -match 'data-will-consume-local-bank-live="false"')
  $no_persist_ok = ($EnabledResponse.Content -match 'data-will-persist-attempts="false"')
  $no_progress_ok = ($EnabledResponse.Content -match 'data-will-update-progress="false"')

  Write-Host "disabled_status_ok $disabled_status_ok"
  Write-Host "enabled_status_ok $enabled_status_ok"
  Write-Host "version_ok $version_ok"
  Write-Host "noindex_ok $noindex_ok"
  Write-Host "internal_ok $internal_ok"
  Write-Host "fetch_ok $fetch_ok"
  Write-Host "legacy_ok $legacy_ok"
  Write-Host "safety_text_ok $safety_text_ok"
  Write-Host "candidate_route_ok $candidate_route_ok"
  Write-Host "no_answer_text_ok $no_answer_text_ok"
  Write-Host "no_public_link_ok $no_public_link_ok"
  Write-Host "no_consume_ok $no_consume_ok"
  Write-Host "no_persist_ok $no_persist_ok"
  Write-Host "no_progress_ok $no_progress_ok"

  if (-not ($disabled_status_ok -and $enabled_status_ok -and $version_ok -and $noindex_ok -and $internal_ok -and $fetch_ok -and $legacy_ok -and $safety_text_ok -and $candidate_route_ok -and $no_answer_text_ok -and $no_public_link_ok -and $no_consume_ok -and $no_persist_ok -and $no_progress_ok)) {
    throw "LOCAL BANK GUARDED TRIAL CANDIDATE PREVIEW PANEL CHECK v0.4.67 FAILED"
  }

  Write-Host "LOCAL BANK GUARDED TRIAL CANDIDATE PREVIEW PANEL CHECK v0.4.67 PASS"
} finally {
  & .\scripts\dev\stop-voila.ps1 | Out-Host

  if ($null -eq $oldPanel) {
    Remove-Item Env:\VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_GUARDED_TRIAL_CANDIDATES_PANEL -ErrorAction SilentlyContinue
  } else {
    $env:VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_GUARDED_TRIAL_CANDIDATES_PANEL = $oldPanel
  }

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
