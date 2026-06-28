param()

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

Write-Host "=== LOCAL BANK FIRST LIVE TRIAL CONTRACT SKELETON CHECK v0.4.77 ==="

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
  "VOILA_ENABLE_EXAM_PREP_LOCAL_BANK_FIRST_LIVE_TRIAL_CONTRACT"
)

$oldFlags = @{}
foreach ($name in $flagNames) {
  $oldFlags[$name] = [Environment]::GetEnvironmentVariable($name, "Process")
}

try {
  foreach ($name in $flagNames) { Remove-Item "Env:\$name" -ErrorAction SilentlyContinue }

  $DisabledRaw = python .\services\api\exam_prep_local_bank_first_live_trial_contract.py --course-id v077-smoke --skill-id local_concept_001_functiile --limit 5 --expect-disabled
  if ($LASTEXITCODE -ne 0) { throw "contract disabled sample failed" }
  Write-Host $DisabledRaw

  foreach ($name in $flagNames) { [Environment]::SetEnvironmentVariable($name, "1", "Process") }

  $ReadyRaw = python .\services\api\exam_prep_local_bank_first_live_trial_contract.py --course-id v077-smoke --skill-id local_concept_001_functiile --limit 5 --expect-ready
  if ($LASTEXITCODE -ne 0) { throw "contract ready sample failed" }
  Write-Host $ReadyRaw

  $Disabled = $DisabledRaw | ConvertFrom-Json
  $Ready = $ReadyRaw | ConvertFrom-Json
  $Sections = $Ready.contract_sections

  $version_ok = ($Disabled.first_live_trial_contract_version -eq "v0.4.77" -and $Ready.first_live_trial_contract_version -eq "v0.4.77")
  $mode_ok = ($Ready.mode -eq "guarded_first_live_trial_contract_skeleton")
  $disabled_ok = ($Disabled.contract_status -eq "disabled" -and $Disabled.contract_flag_enabled -eq $false)
  $ready_ok = ($Ready.contract_status -eq "contract_skeleton_ready_for_owner_review" -and $Ready.contract_flag_enabled -eq $true)
  $shadow_ok = ($Ready.shadow_consolidation_status -eq "complete_shadow_chain_ready_for_review" -and $Ready.shadow_consolidation_ready -eq $true)
  $source_ok = ($Ready.effective_source -eq "legacy_fallback" -and $Ready.candidate_source -eq "local_exercise_bank_adapter" -and $Ready.fallback_source -eq "legacy_fallback")
  $flags_ok = (@($Ready.missing_flags).Count -eq 0 -and @($Ready.required_owner_review_flags).Count -eq 11)
  $sections_ok = ($null -ne $Sections.source_selection -and $null -ne $Sections.session_boundary -and $null -ne $Sections.attempt_persistence -and $null -ne $Sections.progress_updates -and $null -ne $Sections.live_scoring -and $null -ne $Sections.sanitization)
  $source_section_ok = ($Sections.source_selection.current_effective_source -eq "legacy_fallback" -and $Sections.source_selection.may_select_candidate_live_now -eq $false)
  $session_section_ok = ($Sections.session_boundary.will_start_live_session -eq $false -and $Sections.session_boundary.will_replace_live_study_session -eq $false)
  $attempt_section_ok = ($Sections.attempt_persistence.will_persist_attempts -eq $false -and $Sections.attempt_persistence.requires_separate_milestone -eq $true)
  $progress_section_ok = ($Sections.progress_updates.will_update_progress -eq $false -and $Sections.progress_updates.will_persist_progress -eq $false)
  $scoring_section_ok = ($Sections.live_scoring.will_score_live_session -eq $false -and $Sections.live_scoring.requires_separate_milestone -eq $true)
  $sanitization_ok = ($Sections.sanitization.answers_exposed_before_submission -eq $false -and $Sections.sanitization.explanations_exposed_before_submission -eq $false -and $Sections.sanitization.raw_snapshots_exposed -eq $false -and @($Sections.sanitization.forbidden_pre_live_keys | Where-Object { $_ -eq "correct_answer" }).Count -eq 1)
  $implementation_ok = ($Ready.implementation_scope.json_only_contract_object -eq $true -and $Ready.implementation_scope.adds_web_route -eq $false -and $Ready.implementation_scope.patches_web_app -eq $false -and $Ready.implementation_scope.adds_public_ui -eq $false)
  $not_live_ok = (@($Ready.explicit_not_live_yet | Where-Object { $_ -match "not delivered live" }).Count -gt 0 -and @($Ready.explicit_not_live_yet | Where-Object { $_ -match "not consumed live" }).Count -gt 0 -and @($Ready.explicit_not_live_yet | Where-Object { $_ -match "legacy_fallback" }).Count -gt 0)
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

  $statusNames = @(git status --porcelain | ForEach-Object { $line = [string]$_; if ($line.Length -ge 4) { ($line.Substring(3).Trim() -replace "\\", "/") } } | Where-Object { $_ })
  $statusNameText = ($statusNames -join "`n")
  $no_web_app_change_ok = ($statusNameText -notmatch '(^|`n)services/api/web_app\.py($|`n)')

  Write-Host "version_ok $version_ok"
  Write-Host "mode_ok $mode_ok"
  Write-Host "disabled_ok $disabled_ok"
  Write-Host "ready_ok $ready_ok"
  Write-Host "shadow_ok $shadow_ok"
  Write-Host "source_ok $source_ok"
  Write-Host "flags_ok $flags_ok"
  Write-Host "sections_ok $sections_ok"
  Write-Host "source_section_ok $source_section_ok"
  Write-Host "session_section_ok $session_section_ok"
  Write-Host "attempt_section_ok $attempt_section_ok"
  Write-Host "progress_section_ok $progress_section_ok"
  Write-Host "scoring_section_ok $scoring_section_ok"
  Write-Host "sanitization_ok $sanitization_ok"
  Write-Host "implementation_ok $implementation_ok"
  Write-Host "not_live_ok $not_live_ok"
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

  if (-not ($version_ok -and $mode_ok -and $disabled_ok -and $ready_ok -and $shadow_ok -and $source_ok -and $flags_ok -and $sections_ok -and $source_section_ok -and $session_section_ok -and $attempt_section_ok -and $progress_section_ok -and $scoring_section_ok -and $sanitization_ok -and $implementation_ok -and $not_live_ok -and $path_policy_ok -and $no_consume_ok -and $no_deliver_ok -and $no_start_live_ok -and $no_replace_source_ok -and $no_progress_persist_ok -and $no_session_persist_ok -and $no_attempt_persist_ok -and $no_progress_update_ok -and $no_live_score_ok -and $no_ui_ok -and $no_weak_ok -and $no_live_replace_ok -and $no_legacy_replace_ok -and $no_live_consumption_ok -and $no_cloud_ok -and $no_web_app_change_ok)) {
    throw "LOCAL BANK FIRST LIVE TRIAL CONTRACT SKELETON CHECK v0.4.77 FAILED"
  }

  Write-Host "LOCAL BANK FIRST LIVE TRIAL CONTRACT SKELETON CHECK v0.4.77 PASS"
} finally {
  foreach ($name in $flagNames) {
    if ($null -eq $oldFlags[$name]) { Remove-Item "Env:\$name" -ErrorAction SilentlyContinue }
    else { [Environment]::SetEnvironmentVariable($name, [string]$oldFlags[$name], "Process") }
  }
}
