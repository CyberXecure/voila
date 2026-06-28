param()

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

Write-Host "=== LOCAL BANK FIRST LIVE TRIAL OWNER DECISION REPORT ROUTE CHECK v0.4.87 ==="

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
  "VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_FIRST_LIVE_TRIAL_QUESTION_ENVELOPE_SANITIZER",
  "VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_FIRST_LIVE_TRIAL_DRY_RUN_SESSION_ENVELOPE",
  "VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_FIRST_LIVE_TRIAL_NO_PERSISTENCE_DELIVERY_CONTRACT",
  "VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_FIRST_LIVE_TRIAL_NO_PERSISTENCE_DELIVERY_ADAPTER_NOOP",
  "VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_FIRST_LIVE_TRIAL_NO_PERSISTENCE_DECISION_GATE",
  "VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_FIRST_LIVE_TRIAL_OWNER_DECISION_REPORT_ROUTE"
)

$oldFlags = @{}
foreach ($name in $flagNames) {
  $oldFlags[$name] = [Environment]::GetEnvironmentVariable($name, "Process")
}

$TempPy = Join-Path $env:TEMP "voila-v087-owner-decision-report-route-check.py"

try {
  $pyLines = @(
    'import json',
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
    'response = client.get("/exam-prep/local-bank/first-live-trial-owner-decision-report")',
    'print(response.status_code)',
    'print(json.dumps(response.json(), sort_keys=True))'
  )
  $py = ($pyLines -join "`n") + "`n"
  [System.IO.File]::WriteAllText($TempPy, $py, [System.Text.UTF8Encoding]::new($false))

  foreach ($name in $flagNames) {
    Remove-Item "Env:\$name" -ErrorAction SilentlyContinue
  }

  $DisabledRaw = python $TempPy
  if ($LASTEXITCODE -ne 0) { throw "owner decision report disabled sample failed" }
  $DisabledStatusCode = [int]$DisabledRaw[0]
  $DisabledJson = $DisabledRaw[1]
  Write-Host "disabled_owner_decision_report_status_code $DisabledStatusCode"
  Write-Host $DisabledJson
  $Disabled = $DisabledJson | ConvertFrom-Json

  foreach ($name in $flagNames) {
    [Environment]::SetEnvironmentVariable($name, "1", "Process")
  }

  $EnabledRaw = python $TempPy
  if ($LASTEXITCODE -ne 0) { throw "owner decision report enabled sample failed" }
  $EnabledStatusCode = [int]$EnabledRaw[0]
  $EnabledJson = $EnabledRaw[1]
  Write-Host "enabled_owner_decision_report_status_code $EnabledStatusCode"
  Write-Host $EnabledJson
  $Enabled = $EnabledJson | ConvertFrom-Json

  $disabled_ok = ($DisabledStatusCode -eq 200 -and $Disabled.status -eq "disabled" -and $Disabled.route_enabled -eq $false)
  $enabled_ok = ($EnabledStatusCode -eq 200 -and $Enabled.status -eq "ok" -and $Enabled.route_enabled -eq $true)
  $version_ok = ($Disabled.owner_decision_report_route_version -eq "v0.4.87" -and $Enabled.owner_decision_report_route_version -eq "v0.4.87")
  $mode_ok = ($Enabled.mode -eq "guarded_first_live_trial_owner_decision_report_route")
  $json_only_ok = ($Enabled.route_kind -eq "internal_json_only")
  $sanitized_ok = (
    $Enabled.report_sanitized -eq $true -and
    $Enabled.raw_decision_gate_included -eq $false -and
    $Enabled.raw_adapter_result_included -eq $false -and
    $Enabled.raw_contract_included -eq $false -and
    $Enabled.raw_session_envelope_included -eq $false -and
    $Enabled.raw_question_envelopes_included -eq $false -and
    $Enabled.answers_exposed -eq $false -and
    $Enabled.explanations_exposed -eq $false
  )
  $decision_ok = (
    $Enabled.decision_gate_status -eq "decision_gate_ready_for_owner_review" -and
    $Enabled.decision_gate_ready_for_owner_review -eq $true -and
    $Enabled.ready_for_next_decision -eq $true -and
    $Enabled.accepted_decision -eq "keep_noop_only"
  )
  $readiness_ok = (
    $Enabled.readiness_checks.decision_gate_flag_enabled -eq $true -and
    $Enabled.readiness_checks.all_required_owner_flags_enabled -eq $true -and
    $Enabled.readiness_checks.noop_adapter_ready -eq $true -and
    $Enabled.readiness_checks.candidate_question_count_positive -eq $true -and
    $Enabled.readiness_checks.delivery_attempted_false -eq $true -and
    $Enabled.readiness_checks.delivery_performed_false -eq $true -and
    $Enabled.readiness_checks.delivered_question_count_zero -eq $true -and
    $Enabled.readiness_checks.legacy_fallback_available -eq $true
  )
  $policy_ok = (
    $Enabled.decision_gate_policy.real_delivery_allowed_now -eq $false -and
    $Enabled.decision_gate_policy.may_flip_effective_source_now -eq $false -and
    $Enabled.decision_gate_policy.may_start_live_session_now -eq $false -and
    $Enabled.decision_gate_policy.may_persist_session_now -eq $false -and
    $Enabled.decision_gate_policy.may_persist_attempts_now -eq $false -and
    $Enabled.decision_gate_policy.may_update_progress_now -eq $false -and
    $Enabled.decision_gate_policy.may_score_live_session_now -eq $false -and
    $Enabled.decision_gate_policy.requires_separate_real_delivery_milestone -eq $true
  )
  $source_ok = (
    $Enabled.effective_source -eq "legacy_fallback" -and
    $Enabled.candidate_source -eq "local_exercise_bank_adapter" -and
    $Enabled.fallback_source -eq "legacy_fallback"
  )
  $noop_ok = (
    $Enabled.real_delivery_allowed_now -eq $false -and
    $Enabled.delivery_attempted -eq $false -and
    $Enabled.delivery_performed -eq $false -and
    [int]$Enabled.delivered_question_count -eq 0 -and
    @($Enabled.delivered_question_ids).Count -eq 0
  )
  $summary_ok = (
    $Enabled.decision_summary.real_delivery_allowed_now -eq $false -and
    $Enabled.decision_summary.delivery_attempted -eq $false -and
    $Enabled.decision_summary.delivery_performed -eq $false -and
    [int]$Enabled.decision_summary.delivered_question_count -eq 0 -and
    $Enabled.decision_summary.effective_source_after_decision -eq "legacy_fallback"
  )
  $next_ok = (
    @($Enabled.next_decision_options | Where-Object { $_ -eq "keep_noop_only" }).Count -eq 1 -and
    @($Enabled.next_decision_options | Where-Object { $_ -eq "prepare_future_real_delivery_milestone" }).Count -eq 1
  )
  $implementation_ok = (
    $Enabled.implementation_scope.json_only_owner_decision_report_route -eq $true -and
    $Enabled.implementation_scope.calls_decision_gate -eq $true -and
    $Enabled.implementation_scope.adds_public_ui -eq $false -and
    $Enabled.implementation_scope.starts_live_session -eq $false -and
    $Enabled.implementation_scope.persists_sessions -eq $false -and
    $Enabled.implementation_scope.persists_attempts -eq $false -and
    $Enabled.implementation_scope.updates_progress -eq $false -and
    $Enabled.implementation_scope.scores_live_session -eq $false
  )

  $forbidden_key_patterns = @(
    '"correct_answer"\s*:',
    '"correct_answer_preview"\s*:',
    '"answer"\s*:',
    '"expected_answer"\s*:',
    '"solution"\s*:',
    '"explanation"\s*:',
    '"explanation_preview"\s*:',
    '"source_excerpt"\s*:',
    '"raw_decision_gate"\s*:',
    '"raw_adapter_result"\s*:',
    '"raw_contract"\s*:',
    '"raw_session_envelope"\s*:',
    '"raw_question_envelopes"\s*:',
    '"raw_snapshots"\s*:',
    '"dry_run_items"\s*:',
    '"selected_questions"\s*:'
  )
  $leaked = @()
  foreach ($pattern in $forbidden_key_patterns) {
    if ($EnabledJson -match $pattern) { $leaked += $pattern }
  }
  $no_leaks_ok = (@($leaked).Count -eq 0)

  $path_policy_ok = ($Enabled.path_policy -eq "no_user_provided_filesystem_root")
  $no_public_link_ok = ($Enabled.has_public_ui_link -eq $false)
  $no_consume_ok = ($Enabled.will_consume_local_bank_live -eq $false)
  $no_deliver_ok = ($Enabled.will_deliver_local_bank_questions_live -eq $false)
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
  Write-Host "decision_ok $decision_ok"
  Write-Host "readiness_ok $readiness_ok"
  Write-Host "policy_ok $policy_ok"
  Write-Host "source_ok $source_ok"
  Write-Host "noop_ok $noop_ok"
  Write-Host "summary_ok $summary_ok"
  Write-Host "next_ok $next_ok"
  Write-Host "implementation_ok $implementation_ok"
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

  if (-not ($disabled_ok -and $enabled_ok -and $version_ok -and $mode_ok -and $json_only_ok -and $sanitized_ok -and $decision_ok -and $readiness_ok -and $policy_ok -and $source_ok -and $noop_ok -and $summary_ok -and $next_ok -and $implementation_ok -and $no_leaks_ok -and $path_policy_ok -and $no_public_link_ok -and $no_consume_ok -and $no_deliver_ok -and $no_start_live_ok -and $no_replace_source_ok -and $no_progress_persist_ok -and $no_session_persist_ok -and $no_attempt_persist_ok -and $no_progress_update_ok -and $no_live_score_ok -and $no_ui_ok -and $no_weak_ok -and $no_live_replace_ok -and $no_legacy_replace_ok -and $no_live_consumption_ok -and $no_cloud_ok)) {
    throw "LOCAL BANK FIRST LIVE TRIAL OWNER DECISION REPORT ROUTE CHECK v0.4.87 FAILED"
  }

  Write-Host "LOCAL BANK FIRST LIVE TRIAL OWNER DECISION REPORT ROUTE CHECK v0.4.87 PASS"
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
