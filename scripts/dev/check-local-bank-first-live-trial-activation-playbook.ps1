param()
$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

Write-Host "=== LOCAL BANK FIRST LIVE TRIAL ACTIVATION ROLLBACK PLAYBOOK CHECK v0.4.93 ==="
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
  "VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_FIRST_LIVE_TRIAL_ACTIVATION_ROLLBACK_PLAYBOOK"
)

$oldFlags = @{}
foreach ($name in $flagNames) { $oldFlags[$name] = [Environment]::GetEnvironmentVariable($name, "Process") }

try {
  foreach ($name in $flagNames) { Remove-Item "Env:\$name" -ErrorAction SilentlyContinue }
  $DisabledRaw = python .\services\api\exam_prep_local_bank_first_live_trial_activation_playbook.py --course-id v093-smoke --skill-id local_concept_001_functiile --limit 5 --expect-disabled
  if ($LASTEXITCODE -ne 0) { throw "activation playbook disabled sample failed" }
  Write-Host $DisabledRaw

  foreach ($name in $flagNames) { [Environment]::SetEnvironmentVariable($name, "1", "Process") }
  $ReadyRaw = python .\services\api\exam_prep_local_bank_first_live_trial_activation_playbook.py --course-id v093-smoke --skill-id local_concept_001_functiile --limit 5 --expect-ready
  if ($LASTEXITCODE -ne 0) { throw "activation playbook ready sample failed" }
  Write-Host $ReadyRaw

  $Disabled = $DisabledRaw | ConvertFrom-Json
  $Ready = $ReadyRaw | ConvertFrom-Json
  $Playbook = $Ready.activation_playbook

  $version_ok = ($Disabled.activation_playbook_version -eq "v0.4.93" -and $Ready.activation_playbook_version -eq "v0.4.93")
  $disabled_ok = ($Disabled.status -eq "disabled" -and $Disabled.playbook_flag_enabled -eq $false)
  $ready_ok = ($Ready.status -eq "activation_rollback_playbook_ready_activation_not_effective" -and $Ready.activation_rollback_playbook_ready -eq $true)
  $activation_not_effective_ok = ($Ready.activation_effective -eq $false -and $Playbook.activation_effective -eq $false -and $Playbook.activation_is_not_approved_here -eq $true)
  $record_ok = ($Ready.owner_reconfirmation_record_status -eq "owner_reconfirmation_record_ready_authorization_not_effective" -and $Ready.owner_reconfirmation_record_ready -eq $true)
  $source_ok = ($Ready.effective_source -eq "legacy_fallback" -and $Ready.candidate_source -eq "local_exercise_bank_adapter" -and $Ready.fallback_source -eq "legacy_fallback")
  $flags_ok = (@($Ready.missing_flags).Count -eq 0 -and @($Ready.required_owner_flags).Count -ge 21)
  $checks_ok = (
    $Ready.playbook_checks.playbook_flag_enabled -eq $true -and
    $Ready.playbook_checks.all_required_owner_flags_enabled -eq $true -and
    $Ready.playbook_checks.owner_reconfirmation_record_ready -eq $true -and
    $Ready.playbook_checks.authorization_effective_false -eq $true -and
    $Ready.playbook_checks.record_may_deliver_live_false -eq $true -and
    $Ready.playbook_checks.record_go_for_real_delivery_now_false -eq $true -and
    $Ready.playbook_checks.record_real_delivery_allowed_now_false -eq $true -and
    $Ready.playbook_checks.record_delivery_performed_false -eq $true -and
    $Ready.playbook_checks.record_delivered_question_count_zero -eq $true -and
    $Ready.playbook_checks.effective_source_is_legacy -eq $true
  )
  $playbook_ok = (
    $Playbook.playbook_kind -eq "owner_only_no_persistence_real_delivery_activation_rollback_playbook" -and
    $Playbook.may_deliver_live -eq $false -and
    $Playbook.go_for_real_delivery_now -eq $false -and
    $Playbook.real_delivery_allowed_now -eq $false -and
    $Playbook.delivery_performed -eq $false -and
    [int]$Playbook.delivered_question_count -eq 0 -and
    $Playbook.future_real_delivery_milestone_constraints.must_be_separate_milestone -eq $true -and
    $Playbook.future_real_delivery_milestone_constraints.max_questions -eq 5 -and
    $Playbook.future_real_delivery_milestone_constraints.must_not_persist_attempts -eq $true -and
    $Playbook.future_real_delivery_milestone_constraints.must_not_update_progress -eq $true
  )
  $rollback_ok = (
    @($Playbook.rollback_sequence | Where-Object { $_ -eq "force effective_source back to legacy_fallback" }).Count -eq 1 -and
    @($Playbook.rollback_smoke_requirements | Where-Object { $_ -eq "verify effective_source=legacy_fallback" }).Count -eq 1 -and
    @($Playbook.rollback_smoke_requirements | Where-Object { $_ -eq "verify no attempts were persisted" }).Count -eq 1
  )
  $summary_ok = (
    $Ready.playbook_summary.activation_rollback_playbook_ready -eq $true -and
    $Ready.playbook_summary.activation_effective -eq $false -and
    $Ready.playbook_summary.may_deliver_live -eq $false -and
    $Ready.playbook_summary.go_for_real_delivery_now -eq $false -and
    $Ready.playbook_summary.real_delivery_allowed_now -eq $false -and
    $Ready.playbook_summary.delivery_performed -eq $false -and
    [int]$Ready.playbook_summary.delivered_question_count -eq 0 -and
    $Ready.playbook_summary.requires_new_explicit_real_delivery_milestone -eq $true -and
    $Ready.playbook_summary.requires_rollback_smoke -eq $true
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
  Write-Host "record_ok $record_ok"
  Write-Host "source_ok $source_ok"
  Write-Host "flags_ok $flags_ok"
  Write-Host "checks_ok $checks_ok"
  Write-Host "playbook_ok $playbook_ok"
  Write-Host "rollback_ok $rollback_ok"
  Write-Host "summary_ok $summary_ok"
  Write-Host "implementation_ok $implementation_ok"
  Write-Host "no_live_ok $no_live_ok"
  Write-Host "no_web_app_change_ok $no_web_app_change_ok"

  if (-not ($version_ok -and $disabled_ok -and $ready_ok -and $activation_not_effective_ok -and $record_ok -and $source_ok -and $flags_ok -and $checks_ok -and $playbook_ok -and $rollback_ok -and $summary_ok -and $implementation_ok -and $no_live_ok -and $no_web_app_change_ok)) {
    throw "LOCAL BANK FIRST LIVE TRIAL ACTIVATION ROLLBACK PLAYBOOK CHECK v0.4.93 FAILED"
  }

  Write-Host "LOCAL BANK FIRST LIVE TRIAL ACTIVATION ROLLBACK PLAYBOOK CHECK v0.4.93 PASS"
} finally {
  foreach ($name in $flagNames) {
    if ($null -eq $oldFlags[$name]) { Remove-Item "Env:\$name" -ErrorAction SilentlyContinue } else { [Environment]::SetEnvironmentVariable($name, [string]$oldFlags[$name], "Process") }
  }
}
