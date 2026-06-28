param()

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

Write-Host "=== LOCAL BANK INTEGRATION READINESS REPORT CHECK v0.4.60 ==="

$ProjectRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
Set-Location $ProjectRoot

$Raw = python .\services\api\exam_prep_local_bank_integration_readiness.py --course-id v060-smoke --skill-id local_concept_001_functiile --limit 5 --old-mastery-preview 0.40 --expect-ready
if ($LASTEXITCODE -ne 0) { throw "integration readiness report failed" }
Write-Host $Raw

$Report = $Raw | ConvertFrom-Json

$version_ok = ($Report.readiness_report_version -eq "v0.4.60")
$mode_ok = ($Report.mode -eq "local_bank_integration_readiness_report")
$status_ok = ($Report.readiness_status -eq "ready_for_guarded_live_trial")
$ready_ok = ($Report.ready_for_guarded_live_trial -eq $true)
$blocking_empty_ok = (@($Report.blocking_checks).Count -eq 0)
$checks_ok = (@($Report.checks).Count -ge 7 -and @($Report.checks | Where-Object { $_.passed -eq $true }).Count -eq @($Report.checks).Count)
$guardrails_ok = (
  $Report.guardrails.requires_future_live_trial_milestone -eq $true -and
  $Report.guardrails.requires_explicit_live_flag -eq $true -and
  $Report.guardrails.legacy_fallback_must_remain_available -eq $true
)
$snapshots_ok = (
  $Report.snapshots.quality_gate.quality_status -eq "pass" -and
  $Report.snapshots.progress_impact.impact_direction -eq "increase" -and
  $Report.snapshots.session_summary.session_summary_version -eq "v0.4.58"
)
$path_policy_ok = ($Report.path_policy -eq "no_user_provided_filesystem_root")
$no_progress_persist_ok = ($Report.will_persist_progress -eq $false)
$no_session_persist_ok = ($Report.will_persist_session -eq $false)
$no_attempt_persist_ok = ($Report.will_persist_attempts -eq $false)
$no_progress_update_ok = ($Report.will_update_progress -eq $false)
$no_live_score_ok = ($Report.will_score_live_session -eq $false)
$no_ui_ok = ($Report.will_modify_exam_prep_ui -eq $false)
$no_weak_ok = ($Report.will_modify_weak_review -eq $false)
$no_live_replace_ok = ($Report.will_replace_live_study_session -eq $false)
$no_legacy_replace_ok = ($Report.will_replace_legacy_generator -eq $false)
$no_live_consumption_ok = ($Report.will_enable_live_consumption -eq $false)
$no_cloud_ok = ($Report.requires_cloud_or_api -eq $false)

Write-Host "version_ok $version_ok"
Write-Host "mode_ok $mode_ok"
Write-Host "status_ok $status_ok"
Write-Host "ready_ok $ready_ok"
Write-Host "blocking_empty_ok $blocking_empty_ok"
Write-Host "checks_ok $checks_ok"
Write-Host "guardrails_ok $guardrails_ok"
Write-Host "snapshots_ok $snapshots_ok"
Write-Host "path_policy_ok $path_policy_ok"
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

if (-not ($version_ok -and $mode_ok -and $status_ok -and $ready_ok -and $blocking_empty_ok -and $checks_ok -and $guardrails_ok -and $snapshots_ok -and $path_policy_ok -and $no_progress_persist_ok -and $no_session_persist_ok -and $no_attempt_persist_ok -and $no_progress_update_ok -and $no_live_score_ok -and $no_ui_ok -and $no_weak_ok -and $no_live_replace_ok -and $no_legacy_replace_ok -and $no_live_consumption_ok -and $no_cloud_ok)) {
  throw "LOCAL BANK INTEGRATION READINESS REPORT CHECK v0.4.60 FAILED"
}

Write-Host "LOCAL BANK INTEGRATION READINESS REPORT CHECK v0.4.60 PASS"

