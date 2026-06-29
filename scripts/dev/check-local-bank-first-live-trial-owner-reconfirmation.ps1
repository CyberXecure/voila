param()
$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

Write-Host "=== LOCAL BANK FIRST LIVE TRIAL OWNER RECONFIRMATION RECORD CHECK v0.4.92 ==="
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
  "VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_FIRST_LIVE_TRIAL_OWNER_RECONFIRMATION_RECORD"
)

$oldFlags = @{}
foreach ($name in $flagNames) { $oldFlags[$name] = [Environment]::GetEnvironmentVariable($name, "Process") }

try {
  foreach ($name in $flagNames) { Remove-Item "Env:\$name" -ErrorAction SilentlyContinue }
  $DisabledRaw = python .\services\api\exam_prep_local_bank_first_live_trial_owner_reconfirmation.py --course-id v092-smoke --skill-id local_concept_001_functiile --limit 5 --expect-disabled
  if ($LASTEXITCODE -ne 0) { throw "owner reconfirmation record disabled sample failed" }
  Write-Host $DisabledRaw

  foreach ($name in $flagNames) { [Environment]::SetEnvironmentVariable($name, "1", "Process") }
  $ReadyRaw = python .\services\api\exam_prep_local_bank_first_live_trial_owner_reconfirmation.py --course-id v092-smoke --skill-id local_concept_001_functiile --limit 5 --expect-ready
  if ($LASTEXITCODE -ne 0) { throw "owner reconfirmation record ready sample failed" }
  Write-Host $ReadyRaw

  $Disabled = $DisabledRaw | ConvertFrom-Json
  $Ready = $ReadyRaw | ConvertFrom-Json
  $Draft = $Ready.authorization_draft

  $version_ok = ($Disabled.owner_reconfirmation_record_version -eq "v0.4.92" -and $Ready.owner_reconfirmation_record_version -eq "v0.4.92")
  $disabled_ok = ($Disabled.status -eq "disabled" -and $Disabled.record_flag_enabled -eq $false)
  $ready_ok = ($Ready.status -eq "owner_reconfirmation_record_ready_authorization_not_effective" -and $Ready.owner_reconfirmation_record_ready -eq $true)
  $authorization_not_effective_ok = ($Ready.authorization_effective -eq $false -and $Draft.authorization_effective -eq $false -and $Draft.record_is_not_activation -eq $true)
  $proposal_ok = ($Ready.real_delivery_proposal_gate_status -eq "real_delivery_proposal_ready_waiting_for_owner_reconfirmation" -and $Ready.real_delivery_proposal_gate_ready -eq $true)
  $source_ok = ($Ready.effective_source -eq "legacy_fallback" -and $Ready.candidate_source -eq "local_exercise_bank_adapter" -and $Ready.fallback_source -eq "legacy_fallback")
  $flags_ok = (@($Ready.missing_flags).Count -eq 0 -and @($Ready.required_owner_flags).Count -ge 20)
  $checks_ok = (
    $Ready.record_checks.record_flag_enabled -eq $true -and
    $Ready.record_checks.all_required_owner_flags_enabled -eq $true -and
    $Ready.record_checks.proposal_gate_ready -eq $true -and
    $Ready.record_checks.proposal_may_deliver_live_false -eq $true -and
    $Ready.record_checks.proposal_go_for_real_delivery_now_false -eq $true -and
    $Ready.record_checks.proposal_real_delivery_allowed_now_false -eq $true -and
    $Ready.record_checks.proposal_delivery_performed_false -eq $true -and
    $Ready.record_checks.proposal_delivered_question_count_zero -eq $true -and
    $Ready.record_checks.effective_source_is_legacy -eq $true
  )
  $draft_ok = (
    $Draft.authorization_record_kind -eq "owner_reconfirmation_record_draft" -and
    $Draft.authorization_record_version -eq "v0.4.92" -and
    $Draft.may_deliver_live -eq $false -and
    $Draft.go_for_real_delivery_now -eq $false -and
    $Draft.real_delivery_allowed_now -eq $false -and
    $Draft.delivery_performed -eq $false -and
    [int]$Draft.delivered_question_count -eq 0 -and
    $Draft.future_authorized_scope.owner_only -eq $true -and
    $Draft.future_authorized_scope.max_questions -eq 5 -and
    $Draft.future_authorized_scope.no_attempt_persistence -eq $true -and
    $Draft.future_authorized_scope.rollback_to_legacy_fallback -eq $true
  )
  $phrases_ok = (
    @($Draft.required_exact_phrases | Where-Object { $_ -eq "CONFIRM OWNER-ONLY NO-PERSISTENCE REAL DELIVERY" }).Count -eq 1 -and
    @($Draft.required_exact_phrases | Where-Object { $_ -eq "CONFIRM SEPARATE REAL-DELIVERY MILESTONE" }).Count -eq 1
  )
  $summary_ok = (
    $Ready.record_summary.owner_reconfirmation_record_ready -eq $true -and
    $Ready.record_summary.authorization_effective -eq $false -and
    $Ready.record_summary.may_deliver_live -eq $false -and
    $Ready.record_summary.go_for_real_delivery_now -eq $false -and
    $Ready.record_summary.real_delivery_allowed_now -eq $false -and
    $Ready.record_summary.delivery_performed -eq $false -and
    [int]$Ready.record_summary.delivered_question_count -eq 0 -and
    $Ready.record_summary.requires_next_explicit_real_delivery_milestone -eq $true
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
  Write-Host "authorization_not_effective_ok $authorization_not_effective_ok"
  Write-Host "proposal_ok $proposal_ok"
  Write-Host "source_ok $source_ok"
  Write-Host "flags_ok $flags_ok"
  Write-Host "checks_ok $checks_ok"
  Write-Host "draft_ok $draft_ok"
  Write-Host "phrases_ok $phrases_ok"
  Write-Host "summary_ok $summary_ok"
  Write-Host "implementation_ok $implementation_ok"
  Write-Host "no_live_ok $no_live_ok"
  Write-Host "no_web_app_change_ok $no_web_app_change_ok"

  if (-not ($version_ok -and $disabled_ok -and $ready_ok -and $authorization_not_effective_ok -and $proposal_ok -and $source_ok -and $flags_ok -and $checks_ok -and $draft_ok -and $phrases_ok -and $summary_ok -and $implementation_ok -and $no_live_ok -and $no_web_app_change_ok)) {
    throw "LOCAL BANK FIRST LIVE TRIAL OWNER RECONFIRMATION RECORD CHECK v0.4.92 FAILED"
  }

  Write-Host "LOCAL BANK FIRST LIVE TRIAL OWNER RECONFIRMATION RECORD CHECK v0.4.92 PASS"
} finally {
  foreach ($name in $flagNames) {
    if ($null -eq $oldFlags[$name]) { Remove-Item "Env:\$name" -ErrorAction SilentlyContinue } else { [Environment]::SetEnvironmentVariable($name, [string]$oldFlags[$name], "Process") }
  }
}
