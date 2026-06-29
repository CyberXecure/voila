param()
$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

Write-Host "=== LOCAL BANK FIRST LIVE TRIAL REAL-DELIVERY PROPOSAL GATE CHECK v0.4.91 ==="
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
  "VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_FIRST_LIVE_TRIAL_REAL_DELIVERY_PROPOSAL_GATE"
)

$oldFlags = @{}
foreach ($name in $flagNames) { $oldFlags[$name] = [Environment]::GetEnvironmentVariable($name, "Process") }

try {
  foreach ($name in $flagNames) { Remove-Item "Env:\$name" -ErrorAction SilentlyContinue }
  $DisabledRaw = python .\services\api\exam_prep_local_bank_first_live_trial_real_delivery_proposal.py --course-id v091-smoke --skill-id local_concept_001_functiile --limit 5 --expect-disabled
  if ($LASTEXITCODE -ne 0) { throw "proposal gate disabled sample failed" }
  Write-Host $DisabledRaw

  foreach ($name in $flagNames) { [Environment]::SetEnvironmentVariable($name, "1", "Process") }
  $ReadyRaw = python .\services\api\exam_prep_local_bank_first_live_trial_real_delivery_proposal.py --course-id v091-smoke --skill-id local_concept_001_functiile --limit 5 --expect-ready
  if ($LASTEXITCODE -ne 0) { throw "proposal gate ready sample failed" }
  Write-Host $ReadyRaw

  $Disabled = $DisabledRaw | ConvertFrom-Json
  $Ready = $ReadyRaw | ConvertFrom-Json
  $Proposal = $Ready.proposal

  $version_ok = ($Disabled.proposal_gate_version -eq "v0.4.91" -and $Ready.proposal_gate_version -eq "v0.4.91")
  $disabled_ok = ($Disabled.status -eq "disabled" -and $Disabled.proposal_gate_flag_enabled -eq $false)
  $ready_ok = ($Ready.status -eq "real_delivery_proposal_ready_waiting_for_owner_reconfirmation" -and $Ready.proposal_ready_waiting_for_owner_reconfirmation -eq $true)
  $preflight_ok = ($Ready.preflight_audit_status -eq "preflight_audit_complete_waiting_for_explicit_owner_reconfirmation" -and $Ready.preflight_audit_complete -eq $true)
  $source_ok = ($Ready.effective_source -eq "legacy_fallback" -and $Ready.candidate_source -eq "local_exercise_bank_adapter" -and $Ready.fallback_source -eq "legacy_fallback")
  $flags_ok = (@($Ready.missing_flags).Count -eq 0 -and @($Ready.required_owner_flags).Count -ge 19)
  $checks_ok = (
    $Ready.proposal_checks.proposal_gate_flag_enabled -eq $true -and
    $Ready.proposal_checks.all_required_owner_flags_enabled -eq $true -and
    $Ready.proposal_checks.preflight_audit_complete -eq $true -and
    $Ready.proposal_checks.preflight_requires_owner_reconfirmation -eq $true -and
    $Ready.proposal_checks.preflight_go_for_real_delivery_now_false -eq $true -and
    $Ready.proposal_checks.preflight_real_delivery_allowed_now_false -eq $true -and
    $Ready.proposal_checks.preflight_delivery_performed_false -eq $true -and
    $Ready.proposal_checks.effective_source_is_legacy -eq $true
  )
  $proposal_ok = (
    $Proposal.proposal_kind -eq "owner_only_no_persistence_real_delivery_proposal" -and
    $Proposal.may_deliver_live -eq $false -and
    $Proposal.go_for_real_delivery_now -eq $false -and
    $Proposal.real_delivery_allowed_now -eq $false -and
    $Proposal.delivery_performed -eq $false -and
    [int]$Proposal.delivered_question_count -eq 0 -and
    $Proposal.future_activation_scope.owner_only -eq $true -and
    $Proposal.future_activation_scope.max_questions -eq 5 -and
    $Proposal.future_activation_scope.no_attempt_persistence -eq $true -and
    $Proposal.future_rollback_plan.rollback_to_effective_source -eq "legacy_fallback"
  )
  $reconfirm_ok = (
    @($Proposal.exact_owner_reconfirmation_phrases | Where-Object { $_ -eq "CONFIRM OWNER-ONLY NO-PERSISTENCE REAL DELIVERY" }).Count -eq 1 -and
    @($Proposal.exact_owner_reconfirmation_phrases | Where-Object { $_ -eq "CONFIRM SEPARATE REAL-DELIVERY MILESTONE" }).Count -eq 1
  )
  $summary_ok = (
    $Ready.proposal_summary.may_deliver_live -eq $false -and
    $Ready.proposal_summary.go_for_real_delivery_now -eq $false -and
    $Ready.proposal_summary.real_delivery_allowed_now -eq $false -and
    $Ready.proposal_summary.delivery_performed -eq $false -and
    [int]$Ready.proposal_summary.delivered_question_count -eq 0 -and
    $Ready.proposal_summary.requires_separate_real_delivery_milestone -eq $true
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
  Write-Host "preflight_ok $preflight_ok"
  Write-Host "source_ok $source_ok"
  Write-Host "flags_ok $flags_ok"
  Write-Host "checks_ok $checks_ok"
  Write-Host "proposal_ok $proposal_ok"
  Write-Host "reconfirm_ok $reconfirm_ok"
  Write-Host "summary_ok $summary_ok"
  Write-Host "implementation_ok $implementation_ok"
  Write-Host "no_live_ok $no_live_ok"
  Write-Host "no_web_app_change_ok $no_web_app_change_ok"

  if (-not ($version_ok -and $disabled_ok -and $ready_ok -and $preflight_ok -and $source_ok -and $flags_ok -and $checks_ok -and $proposal_ok -and $reconfirm_ok -and $summary_ok -and $implementation_ok -and $no_live_ok -and $no_web_app_change_ok)) {
    throw "LOCAL BANK FIRST LIVE TRIAL REAL-DELIVERY PROPOSAL GATE CHECK v0.4.91 FAILED"
  }

  Write-Host "LOCAL BANK FIRST LIVE TRIAL REAL-DELIVERY PROPOSAL GATE CHECK v0.4.91 PASS"
} finally {
  foreach ($name in $flagNames) {
    if ($null -eq $oldFlags[$name]) { Remove-Item "Env:\$name" -ErrorAction SilentlyContinue } else { [Environment]::SetEnvironmentVariable($name, [string]$oldFlags[$name], "Process") }
  }
}
