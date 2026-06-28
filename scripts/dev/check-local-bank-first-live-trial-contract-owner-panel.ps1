param()

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

Write-Host "=== LOCAL BANK FIRST LIVE TRIAL CONTRACT OWNER PANEL CHECK v0.4.79 ==="

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
  "VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_SHADOW_REPORT_OWNER_PANEL",
  "VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_FIRST_LIVE_TRIAL_CONTRACT",
  "VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_FIRST_LIVE_TRIAL_CONTRACT_REPORT_ROUTE",
  "VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_FIRST_LIVE_TRIAL_CONTRACT_OWNER_PANEL"
)

$oldFlags = @{}
foreach ($name in $flagNames) {
  $oldFlags[$name] = [Environment]::GetEnvironmentVariable($name, "Process")
}

$TempPy = Join-Path $env:TEMP "voila-v079-contract-owner-panel-check.py"

try {
  $pyLines = @(
    'import pathlib',
    'import sys',
    '',
    'root = pathlib.Path.cwd()',
    'sys.path.insert(0, str(root / "services" / "api"))',
    '',
    'from fastapi.testclient import TestClient',
    'import web_app',
    '',
    'client = TestClient(web_app.app)',
    'response = client.get("/exam-prep/local-bank/first-live-trial-contract-panel")',
    'print(response.status_code)',
    'print(response.text)'
  )
  $py = ($pyLines -join "`n") + "`n"
  [System.IO.File]::WriteAllText($TempPy, $py, [System.Text.UTF8Encoding]::new($false))

  foreach ($name in $flagNames) {
    Remove-Item "Env:\$name" -ErrorAction SilentlyContinue
  }

  $DisabledRaw = python $TempPy
  if ($LASTEXITCODE -ne 0) { throw "contract owner panel disabled sample failed" }
  $DisabledStatusCode = [int]$DisabledRaw[0]
  $DisabledHtml = ($DisabledRaw | Select-Object -Skip 1) -join "`n"
  Write-Host "disabled_contract_owner_panel_status_code $DisabledStatusCode"
  Write-Host $DisabledHtml

  foreach ($name in $flagNames) {
    [Environment]::SetEnvironmentVariable($name, "1", "Process")
  }

  $EnabledRaw = python $TempPy
  if ($LASTEXITCODE -ne 0) { throw "contract owner panel enabled sample failed" }
  $EnabledStatusCode = [int]$EnabledRaw[0]
  $EnabledHtml = ($EnabledRaw | Select-Object -Skip 1) -join "`n"
  Write-Host "enabled_contract_owner_panel_status_code $EnabledStatusCode"
  Write-Host $EnabledHtml

  $disabled_status_ok = ($DisabledStatusCode -eq 200 -and $DisabledHtml -match 'data-first-live-trial-contract-owner-panel-status="disabled"')
  $enabled_status_ok = ($EnabledStatusCode -eq 200 -and $EnabledHtml -match 'data-first-live-trial-contract-owner-panel-status="enabled"')
  $version_ok = ($DisabledHtml -match 'data-first-live-trial-contract-owner-panel-version="v0.4.79"' -and $EnabledHtml -match 'data-first-live-trial-contract-owner-panel-version="v0.4.79"')
  $noindex_ok = ($EnabledHtml -match 'noindex,nofollow')
  $internal_ok = ($EnabledHtml -match 'internal_hidden_owner_panel')
  $fetch_ok = ($EnabledHtml -match '/exam-prep/local-bank/first-live-trial-contract-report')
  $safe_dom_ok = (
    $EnabledHtml -match 'createElement' -and
    $EnabledHtml -match 'textContent' -and
    $EnabledHtml -match 'replaceChildren' -and
    $EnabledHtml -notmatch 'innerHTML'
  )
  $summary_ok = (
    $EnabledHtml -match 'Contract summary' -and
    $EnabledHtml -match 'Contract sections' -and
    $EnabledHtml -match 'Guardrails' -and
    $EnabledHtml -match 'Implementation scope'
  )
  $legacy_ok = ($EnabledHtml -match 'legacy_fallback')
  $forbidden_panel_patterns = @(
    '"correct_answer"\s*:',
    '"correct_answer_preview"\s*:',
    '"explanation"\s*:',
    '"explanation_preview"\s*:',
    '"source_excerpt"\s*:',
    '"raw_contract"\s*:',
    '"raw_snapshots"\s*:',
    '"dry_run_items"\s*:',
    '"selected_questions"\s*:'
  )
  $leaked = @()
  foreach ($pattern in $forbidden_panel_patterns) {
    if ($EnabledHtml -match $pattern) { $leaked += $pattern }
  }
  $no_leaks_ok = (@($leaked).Count -eq 0)
  $no_public_link_ok = ($EnabledHtml -match 'data-has-public-ui-link="false"')
  $no_consume_ok = ($EnabledHtml -match 'data-will-consume-local-bank-live="false"')
  $no_deliver_ok = ($EnabledHtml -match 'data-will-deliver-local-bank-questions-live="false"')
  $no_start_live_ok = ($EnabledHtml -match 'data-will-start-live-session="false"')
  $no_replace_source_ok = ($EnabledHtml -match 'data-will-replace-effective-source="false"')
  $no_persist_ok = ($EnabledHtml -match 'data-will-persist-attempts="false"')
  $no_progress_ok = ($EnabledHtml -match 'data-will-update-progress="false"')
  $no_score_ok = ($EnabledHtml -match 'data-will-score-live-session="false"')

  Write-Host "disabled_status_ok $disabled_status_ok"
  Write-Host "enabled_status_ok $enabled_status_ok"
  Write-Host "version_ok $version_ok"
  Write-Host "noindex_ok $noindex_ok"
  Write-Host "internal_ok $internal_ok"
  Write-Host "fetch_ok $fetch_ok"
  Write-Host "safe_dom_ok $safe_dom_ok"
  Write-Host "summary_ok $summary_ok"
  Write-Host "legacy_ok $legacy_ok"
  Write-Host "no_leaks_ok $no_leaks_ok"
  Write-Host "no_public_link_ok $no_public_link_ok"
  Write-Host "no_consume_ok $no_consume_ok"
  Write-Host "no_deliver_ok $no_deliver_ok"
  Write-Host "no_start_live_ok $no_start_live_ok"
  Write-Host "no_replace_source_ok $no_replace_source_ok"
  Write-Host "no_persist_ok $no_persist_ok"
  Write-Host "no_progress_ok $no_progress_ok"
  Write-Host "no_score_ok $no_score_ok"

  if (-not ($disabled_status_ok -and $enabled_status_ok -and $version_ok -and $noindex_ok -and $internal_ok -and $fetch_ok -and $safe_dom_ok -and $summary_ok -and $legacy_ok -and $no_leaks_ok -and $no_public_link_ok -and $no_consume_ok -and $no_deliver_ok -and $no_start_live_ok -and $no_replace_source_ok -and $no_persist_ok -and $no_progress_ok -and $no_score_ok)) {
    throw "LOCAL BANK FIRST LIVE TRIAL CONTRACT OWNER PANEL CHECK v0.4.79 FAILED"
  }

  Write-Host "LOCAL BANK FIRST LIVE TRIAL CONTRACT OWNER PANEL CHECK v0.4.79 PASS"
} finally {
  Remove-Item $TempPy -ErrorAction SilentlyContinue

  foreach ($name in $flagNames) {
    if ($null -eq $oldFlags[$name]) {
      Remove-Item "Env:\$name" -ErrorAction SilentlyContinue
    } else {
      [Environment]::SetEnvironmentVariable($name, [string]$oldFlags[$name], "Process")
    }
  }
}
