param()

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

Write-Host "=== LOCAL BANK FIRST LIVE TRIAL DELIVERY ADAPTER NO-OP CHECK v0.4.83 ==="

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
  "VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_FIRST_LIVE_TRIAL_NO_PERSISTENCE_DELIVERY_ADAPTER_NOOP"
)

$oldFlags = @{}
foreach ($name in $flagNames) {
  $oldFlags[$name] = [Environment]::GetEnvironmentVariable($name, "Process")
}

try {
  foreach ($name in $flagNames) {
    Remove-Item "Env:\$name" -ErrorAction SilentlyContinue
  }

  $DisabledRaw = python .\services\api\exam_prep_local_bank_first_live_trial_delivery_adapter.py --course-id v083-smoke --skill-id local_concept_001_functiile --limit 5 --expect-disabled
  if ($LASTEXITCODE -ne 0) { throw "delivery adapter noop disabled sample failed" }
  Write-Host $DisabledRaw

  foreach ($name in $flagNames) {
    [Environment]::SetEnvironmentVariable($name, "1", "Process")
  }

  $ReadyRaw = python .\services\api\exam_prep_local_bank_first_live_trial_delivery_adapter.py --course-id v083-smoke --skill-id local_concept_001_functiile --limit 5 --expect-ready
  if ($LASTEXITCODE -ne 0) { throw "delivery adapter noop ready sample failed" }
  Write-Host $ReadyRaw

  $Disabled = $DisabledRaw | ConvertFrom-Json
  $Ready = $ReadyRaw | ConvertFrom-Json
  $Adapter = $Ready.adapter_result

  $version_ok = ($Disabled.noop_delivery_adapter_version -eq "v0.4.83" -and $Ready.noop_delivery_adapter_version -eq "v0.4.83")
  $mode_ok = ($Ready.mode -eq "guarded_first_live_trial_no_persistence_delivery_adapter_noop")
  $disabled_ok = ($Disabled.status -eq "disabled" -and $Disabled.adapter_flag_enabled -eq $false)
  $ready_ok = ($Ready.status -eq "noop_delivery_adapter_ready_for_owner_review" -and $Ready.ready_for_owner_review -eq $true)
  $contract_ok = ($Ready.no_persistence_delivery_contract_status -eq "no_persistence_delivery_contract_ready_for_owner_review" -and $Ready.no_persistence_delivery_contract_ready -eq $true)
  $source_ok = ($Ready.effective_source -eq "legacy_fallback" -and $Ready.candidate_source -eq "local_exercise_bank_adapter" -and $Ready.fallback_source -eq "legacy_fallback")
  $flags_ok = (@($Ready.missing_flags).Count -eq 0 -and @($Ready.required_owner_flags).Count -ge 15)
  $boundary_ok = (
    $Ready.adapter_contract_boundary.accepts_delivery_contract -eq $true -and
    $Ready.adapter_contract_boundary.requires_no_persistence_policy -eq $true -and
    $Ready.adapter_contract_boundary.requires_abort_policy -eq $true -and
    $Ready.adapter_contract_boundary.blocks_delivery_now -eq $true -and
    $Ready.adapter_contract_boundary.returns_noop_result -eq $true
  )
  $adapter_shape_ok = (
    $Adapter.adapter_schema_version -eq "1" -and
    $Adapter.noop_delivery_adapter_version -eq "v0.4.83" -and
    $Adapter.adapter_kind -eq "owner_only_no_persistence_delivery_adapter_noop" -and
    [int]$Adapter.candidate_question_count -eq 5 -and
    $Adapter.requested_delivery_mode -eq "contract_only_not_live"
  )
  $noop_result_ok = (
    $Adapter.delivery_attempted -eq $false -and
    $Adapter.delivery_performed -eq $false -and
    [int]$Adapter.delivered_question_count -eq 0 -and
    @($Adapter.delivered_question_ids).Count -eq 0 -and
    $Adapter.would_deliver_if_future_enabled -eq $true -and
    $Adapter.abort_to_effective_source -eq "legacy_fallback"
  )
  $adapter_no_persistence_ok = (
    $Adapter.will_start_live_session -eq $false -and
    $Adapter.will_replace_effective_source -eq $false -and
    $Adapter.will_persist_session -eq $false -and
    $Adapter.will_persist_attempts -eq $false -and
    $Adapter.will_update_progress -eq $false -and
    $Adapter.will_score_live_session -eq $false
  )
  $summary_ok = (
    $Ready.adapter_summary.delivery_attempted -eq $false -and
    $Ready.adapter_summary.delivery_performed -eq $false -and
    [int]$Ready.adapter_summary.delivered_question_count -eq 0 -and
    [int]$Ready.adapter_summary.candidate_question_count -eq 5 -and
    $Ready.adapter_summary.noop_only -eq $true
  )
  $implementation_ok = (
    $Ready.implementation_scope.json_only_local_module -eq $true -and
    $Ready.implementation_scope.adds_web_route -eq $false -and
    $Ready.implementation_scope.patches_web_app -eq $false -and
    $Ready.implementation_scope.adds_public_ui -eq $false -and
    $Ready.implementation_scope.delivers_local_bank_questions_live -eq $false -and
    $Ready.implementation_scope.persists_sessions -eq $false
  )
  $path_policy_ok = ($Ready.path_policy -eq "no_user_provided_filesystem_root")
  $no_consume_ok = ($Ready.will_consume_local_bank_live -eq $false)
  $no_deliver_ok = ($Ready.will_deliver_local_bank_questions_live -eq $false)
  $no_start_live_ok = ($Ready.will_start_live_session -eq $false)
  $no_replace_source_ok = ($Ready.will_replace_effective_source -eq $false)
  $no_progress_persist_ok = ($Ready.will_persist_progress -eq $false)
  $no_session_persist_ok = ($Ready.will_persist_session -eq $false)
  $no_attempt_persist_ok = ($Ready.will_persist_attempts -eq $false)
  $no_progress_update_ok = ($Ready.will_update_progress -eq $false)
  $no_live_score_ok = ($Ready.will_score_live_session -eq $false)
  $no_ui_ok = ($Ready.will_modify_exam_prep_ui -eq $false)
  $no_weak_ok = ($Ready.will_modify_weak_review -eq $false)
  $no_live_replace_ok = ($Ready.will_replace_live_study_session -eq $false)
  $no_legacy_replace_ok = ($Ready.will_replace_legacy_generator -eq $false)
  $no_live_consumption_ok = ($Ready.will_enable_live_consumption -eq $false)
  $no_cloud_ok = ($Ready.requires_cloud_or_api -eq $false)

  $statusNames = @(
    git status --porcelain | ForEach-Object {
      $line = [string]$_
      if ($line.Length -ge 4) { ($line.Substring(3).Trim() -replace "\\", "/") }
    } | Where-Object { $_ }
  )
  $statusNameText = ($statusNames -join "`n")
  $no_web_app_change_ok = ($statusNameText -notmatch '(^|`n)services/api/web_app\.py($|`n)')

  Write-Host "version_ok $version_ok"
  Write-Host "mode_ok $mode_ok"
  Write-Host "disabled_ok $disabled_ok"
  Write-Host "ready_ok $ready_ok"
  Write-Host "contract_ok $contract_ok"
  Write-Host "source_ok $source_ok"
  Write-Host "flags_ok $flags_ok"
  Write-Host "boundary_ok $boundary_ok"
  Write-Host "adapter_shape_ok $adapter_shape_ok"
  Write-Host "noop_result_ok $noop_result_ok"
  Write-Host "adapter_no_persistence_ok $adapter_no_persistence_ok"
  Write-Host "summary_ok $summary_ok"
  Write-Host "implementation_ok $implementation_ok"
  Write-Host "path_policy_ok $path_policy_ok"
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
  Write-Host "no_web_app_change_ok $no_web_app_change_ok"

  if (-not ($version_ok -and $mode_ok -and $disabled_ok -and $ready_ok -and $contract_ok -and $source_ok -and $flags_ok -and $boundary_ok -and $adapter_shape_ok -and $noop_result_ok -and $adapter_no_persistence_ok -and $summary_ok -and $implementation_ok -and $path_policy_ok -and $no_consume_ok -and $no_deliver_ok -and $no_start_live_ok -and $no_replace_source_ok -and $no_progress_persist_ok -and $no_session_persist_ok -and $no_attempt_persist_ok -and $no_progress_update_ok -and $no_live_score_ok -and $no_ui_ok -and $no_weak_ok -and $no_live_replace_ok -and $no_legacy_replace_ok -and $no_live_consumption_ok -and $no_cloud_ok -and $no_web_app_change_ok)) {
    throw "LOCAL BANK FIRST LIVE TRIAL DELIVERY ADAPTER NO-OP CHECK v0.4.83 FAILED"
  }

  Write-Host "LOCAL BANK FIRST LIVE TRIAL DELIVERY ADAPTER NO-OP CHECK v0.4.83 PASS"
} finally {
  foreach ($name in $flagNames) {
    if ($null -eq $oldFlags[$name]) {
      Remove-Item "Env:\$name" -ErrorAction SilentlyContinue
    } else {
      [Environment]::SetEnvironmentVariable($name, [string]$oldFlags[$name], "Process")
    }
  }
}
