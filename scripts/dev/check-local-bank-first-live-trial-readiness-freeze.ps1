param()
$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

Write-Host "=== LOCAL BANK FIRST LIVE TRIAL READINESS FREEZE CHECK v0.4.94 ==="
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
  "VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_FIRST_LIVE_TRIAL_OWNER_READY_CHECKPOINT",
  "VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_FIRST_LIVE_TRIAL_PREFLIGHT_AUDIT",
  "VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_FIRST_LIVE_TRIAL_REAL_DELIVERY_PROPOSAL_GATE",
  "VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_FIRST_LIVE_TRIAL_OWNER_RECONFIRMATION_RECORD",
  "VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_FIRST_LIVE_TRIAL_ACTIVATION_ROLLBACK_PLAYBOOK",
  "VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_FIRST_LIVE_TRIAL_READINESS_FREEZE"
)

$oldFlags = @{}
foreach ($name in $flagNames) { $oldFlags[$name] = [Environment]::GetEnvironmentVariable($name, "Process") }

try {
  foreach ($name in $flagNames) { Remove-Item "Env:\$name" -ErrorAction SilentlyContinue }
  $DisabledRaw = python .\services\api\exam_prep_local_bank_first_live_trial_readiness_freeze.py --course-id v094-smoke --skill-id local_concept_001_functiile --limit 5 --expect-disabled
  if ($LASTEXITCODE -ne 0) { throw "readiness freeze disabled sample failed" }
  Write-Host $DisabledRaw

  foreach ($name in $flagNames) { [Environment]::SetEnvironmentVariable($name, "1", "Process") }
  $ReadyRaw = python .\services\api\exam_prep_local_bank_first_live_trial_readiness_freeze.py --course-id v094-smoke --skill-id local_concept_001_functiile --limit 5 --expect-ready
  if ($LASTEXITCODE -ne 0) { throw "readiness freeze ready sample failed" }
  Write-Host $ReadyRaw

  $Disabled = $DisabledRaw | ConvertFrom-Json
  $Ready = $ReadyRaw | ConvertFrom-Json
  $Freeze = $Ready.readiness_freeze

  $version_ok = ($Disabled.readiness_freeze_version -eq "v0.4.94" -and $Ready.readiness_freeze_version -eq "v0.4.94")
  $disabled_ok = ($Disabled.status -eq "disabled" -and $Disabled.freeze_flag_enabled -eq $false)
  $ready_ok = ($Ready.status -eq "implementation_readiness_frozen_waiting_for_stop_or_real_delivery_milestone" -and $Ready.implementation_readiness_frozen -eq $true)
  $activation_not_effective_ok = ($Ready.activation_effective -eq $false -and $Freeze.activation_effective -eq $false)
  $playbook_ok = ($Ready.activation_rollback_playbook_status -eq "activation_rollback_playbook_ready_activation_not_effective" -and $Ready.activation_rollback_playbook_ready -eq $true)
  $source_ok = ($Ready.effective_source -eq "legacy_fallback" -and $Ready.candidate_source -eq "local_exercise_bank_adapter" -and $Ready.fallback_source -eq "legacy_fallback")
  $flags_ok = (@($Ready.missing_flags).Count -eq 0 -and @($Ready.required_owner_flags).Count -ge 22)
  $checks_ok = (
    $Ready.freeze_checks.freeze_flag_enabled -eq $true -and
    $Ready.freeze_checks.all_required_owner_flags_enabled -eq $true -and
    $Ready.freeze_checks.activation_playbook_ready -eq $true -and
    $Ready.freeze_checks.activation_effective_false -eq $true -and
    $Ready.freeze_checks.playbook_may_deliver_live_false -eq $true -and
    $Ready.freeze_checks.playbook_go_for_real_delivery_now_false -eq $true -and
    $Ready.freeze_checks.playbook_real_delivery_allowed_now_false -eq $true -and
    $Ready.freeze_checks.playbook_delivery_performed_false -eq $true -and
    $Ready.freeze_checks.playbook_delivered_question_count_zero -eq $true -and
    $Ready.freeze_checks.effective_source_is_legacy -eq $true
  )
  $freeze_ok = (
    $Freeze.freeze_kind -eq "implementation_readiness_freeze" -and
    $Freeze.readiness_frozen -eq $true -and
    $Freeze.no_more_gate_milestones_recommended -eq $true -and
    $Freeze.next_step_policy -eq "STOP_OR_SEPARATE_REAL_DELIVERY_MILESTONE_ONLY" -and
    $Freeze.may_deliver_live -eq $false -and
    $Freeze.go_for_real_delivery_now -eq $false -and
    $Freeze.real_delivery_allowed_now -eq $false -and
    $Freeze.delivery_performed -eq $false -and
    [int]$Freeze.delivered_question_count -eq 0 -and
    $Freeze.do_not_continue_with_more_gates -eq $true
  )
  $allowed_next_ok = (
    @($Freeze.allowed_next_steps | Where-Object { $_ -eq "STOP" }).Count -eq 1 -and
    @($Freeze.allowed_next_steps | Where-Object { $_ -eq "separate_explicit_owner_only_real_delivery_implementation_milestone" }).Count -eq 1
  )
  $requirements_ok = (
    @($Freeze.real_delivery_requires | Where-Object { $_ -eq "new separately named milestone" }).Count -eq 1 -and
    @($Freeze.real_delivery_requires | Where-Object { $_ -eq "explicit owner approval in chat" }).Count -eq 1 -and
    @($Freeze.real_delivery_requires | Where-Object { $_ -eq "legacy_fallback rollback path" }).Count -eq 1
  )
  $summary_ok = (
    $Ready.freeze_summary.implementation_readiness_frozen -eq $true -and
    $Ready.freeze_summary.no_more_gate_milestones_recommended -eq $true -and
    $Ready.freeze_summary.next_step_policy -eq "STOP_OR_SEPARATE_REAL_DELIVERY_MILESTONE_ONLY" -and
    $Ready.freeze_summary.activation_effective -eq $false -and
    $Ready.freeze_summary.may_deliver_live -eq $false -and
    $Ready.freeze_summary.go_for_real_delivery_now -eq $false -and
    $Ready.freeze_summary.real_delivery_allowed_now -eq $false -and
    $Ready.freeze_summary.delivery_performed -eq $false -and
    [int]$Ready.freeze_summary.delivered_question_count -eq 0
  )
  $implementation_ok = (
    $Ready.implementation_scope.json_only_local_module -eq $true -and
    $Ready.implementation_scope.adds_web_route -eq $false -and
    $Ready.implementation_scope.patches_web_app -eq $false -and
    $Ready.implementation_scope.adds_public_ui -eq $false -and
    $Ready.implementation_scope.delivers_local_bank_questions_live -eq $false
  )
  $no_live_ok = (
    $Ready.will_consume_local_bank_live -eq $false -and
    $Ready.will_deliver_local_bank_questions_live -eq $false -and
    $Ready.will_start_live_session -eq $false -and
    $Ready.will_persist_attempts -eq $false -and
    $Ready.will_update_progress -eq $false -and
    $Ready.will_score_live_session -eq $false -and
    $Ready.requires_cloud_or_api -eq $false
  )

  $statusText = (git status --short | Out-String)
  $no_web_app_change_ok = ($statusText -notmatch "services/api/web_app.py")

  Write-Host "version_ok $version_ok"
  Write-Host "disabled_ok $disabled_ok"
  Write-Host "ready_ok $ready_ok"
  Write-Host "activation_not_effective_ok $activation_not_effective_ok"
  Write-Host "playbook_ok $playbook_ok"
  Write-Host "source_ok $source_ok"
  Write-Host "flags_ok $flags_ok"
  Write-Host "checks_ok $checks_ok"
  Write-Host "freeze_ok $freeze_ok"
  Write-Host "allowed_next_ok $allowed_next_ok"
  Write-Host "requirements_ok $requirements_ok"
  Write-Host "summary_ok $summary_ok"
  Write-Host "implementation_ok $implementation_ok"
  Write-Host "no_live_ok $no_live_ok"
  Write-Host "no_web_app_change_ok $no_web_app_change_ok"

  if (-not ($version_ok -and $disabled_ok -and $ready_ok -and $activation_not_effective_ok -and $playbook_ok -and $source_ok -and $flags_ok -and $checks_ok -and $freeze_ok -and $allowed_next_ok -and $requirements_ok -and $summary_ok -and $implementation_ok -and $no_live_ok -and $no_web_app_change_ok)) {
    throw "LOCAL BANK FIRST LIVE TRIAL READINESS FREEZE CHECK v0.4.94 FAILED"
  }

  Write-Host "LOCAL BANK FIRST LIVE TRIAL READINESS FREEZE CHECK v0.4.94 PASS"
} finally {
  foreach ($name in $flagNames) {
    if ($null -eq $oldFlags[$name]) { Remove-Item "Env:\$name" -ErrorAction SilentlyContinue } else { [Environment]::SetEnvironmentVariable($name, [string]$oldFlags[$name], "Process") }
  }
}
